from typing import Dict, List, Optional, Tuple
import sys
import os
import json
import zipfile
import urllib.parse

import requests

from infherno.defaults import determine_snowstorm_url, determine_snowstorm_branch
from infherno.tools.fhircodes.instance import GenericSnomedInstance

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(os.path.dirname(os.path.dirname(THIS_DIR)))

# Caching
CACHE_DIR = os.path.join(REPO_DIR, "cache")
TERMINOLOGY_BINDINGS_CACHE = os.path.join(CACHE_DIR, "terminology_bindings")
if not os.path.exists(TERMINOLOGY_BINDINGS_CACHE):
    os.makedirs(TERMINOLOGY_BINDINGS_CACHE, exist_ok=True)

RELEASE_BASE_URL = {
    "R4": "https://hl7.org/fhir/R4", # Only R4 was tested.
    "R5": "https://hl7.org/fhir/R5",
}

def downloadTerminologyDefinitionFile(release: str = "R4"):
    RELEASE_DIR = os.path.join(TERMINOLOGY_BINDINGS_CACHE, release)
    if not os.path.exists(RELEASE_DIR):
        os.makedirs(RELEASE_DIR, exist_ok=True)

    # Download the FHIR release definitions
    definitions_filepath = os.path.join(RELEASE_DIR, f"definitions_{release}.zip")
    if not os.path.exists(definitions_filepath):
        # Use streaming to handle larger files efficiently
        url = f"{RELEASE_BASE_URL[release]}/definitions.json.zip"
        with requests.get(url, stream=True) as response:
            response.raise_for_status()

            with open(definitions_filepath, "wb") as f:
                # Download in chunks of 8KB to avoid memory issues with large files
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)

    # Extract the dataelements.json file
    dataelements_path = os.path.join(RELEASE_DIR, 'dataelements.json')
    if not os.path.exists(dataelements_path):
        with zipfile.ZipFile(definitions_filepath) as definitions:
            try:
                with definitions.open('dataelements.json') as dataelements_json:
                    with open(dataelements_path, 'wb') as f:
                        # Read and write in chunks to handle large files
                        chunk_size = 8192
                        while True:
                            chunk = dataelements_json.read(chunk_size)
                            if not chunk:
                                break
                            f.write(chunk)
            except KeyError:
                raise Exception(f"dataelements.json not found in {definitions_filepath}")

    # Parse the terminology bindings for all FHIR paths
    bindings_path = os.path.join(RELEASE_DIR, "path_bindings.json")
    if not os.path.exists(bindings_path):
        with open(dataelements_path, "r") as f:
            dataelements = json.load(f)

        # Extract the terminology bindings
        bindings = {}
        for entry in dataelements.get("entry", []):
            # elements
            for element in entry.get("resource", {}).get("snapshot", {}).get("element", []):
                if "path" in element and "binding" in element:
                    # We have some binding info
                    path = element.get("path")
                    type_info = list(set(([ t.get("code") for t in element.get("type", []) if "code" in t ])))
                    valueSet = element.get("binding", {}).get("valueSet", None)
                    strength = element.get("binding", {}).get("strength", None)

                    # Only process elements with a valueSet and path
                    if valueSet and path:
                        # Remove the suffix from the valueSet
                        valueSet, *_ = valueSet.rsplit("|", 1)

                        if path not in bindings:
                            bindings[path] = {"vs": valueSet, "type": type_info, "strength": strength}
                        else:
                            # Check if the existing binding is the same
                            print("Found duplicate binding for path:", path, file=sys.stderr)
                            existing_binding = bindings[path]
                            if existing_binding["vs"] != valueSet:
                                print(f"Warning: Different valueSet found for path {path}.", file=sys.stderr)
                            if existing_binding["type"] != type_info:
                                print(f"Warning: Different type found for path {path}.", file=sys.stderr)
                            if existing_binding["strength"] != strength:
                                print(f"Warning: Different strength found for path {path}.", file=sys.stderr)

        # Save the bindings to a file
        with open(bindings_path, "w") as f:
            json.dump(bindings, f, indent=2)

BINDINGS = {}
def getTerminologyBindings(release: str = "R4"):
    global BINDINGS
    if release in BINDINGS:
        return BINDINGS[release]

    downloadTerminologyDefinitionFile(release)
    # Load the bindings from the file
    bindings_path = os.path.join(TERMINOLOGY_BINDINGS_CACHE, release, "path_bindings.json")
    if os.path.exists(bindings_path):
        with open(bindings_path, "r") as f:
            BINDINGS[release] = json.load(f)
            return BINDINGS[release]
    else:
        raise Exception(f"Bindings file not found: {bindings_path}")


def search_for_path(
        fhir_path: str,
        search_term: str,
        limit: int = 10,
        max_nosearch: int = 10,
        snomed_instance: GenericSnomedInstance = None,
        release: str = "R4") -> Tuple[str, List[Dict]]:
    # Get the terminology bindings
    bindings = getTerminologyBindings(release)

    if snomed_instance is None:
        # Create a new instance of GenericSnomedInstance
        snomed_instance = GenericSnomedInstance(determine_snowstorm_url(), determine_snowstorm_branch())

    # Check if the path exists in the bindings
    if fhir_path not in bindings:
        return f"Unsupported FHIR path: {fhir_path}", []

    # Get the valueSet and type
    valueSet = bindings[fhir_path]["vs"]
    type_info = bindings[fhir_path]["type"]

    fhir_base_url = snomed_instance.base_url + "/fhir"
    search_path = f"{fhir_base_url}/ValueSet/$expand"

    # Check #total items first
    args = {
        "url": valueSet,
        "count": 1, # 0 leads to an arithmetic error in Snowstorm (breaking the FHIR specs)
    }
    response = requests.get(search_path, params=args)
    if response.status_code != 200: print(response.text, file=sys.stderr)
    response.raise_for_status()
    response_data = response.json()
    n_total = response_data.get("expansion", {}).get("total", 0)

    if n_total > max_nosearch:
        # We search for the given search term with a limit
        args["count"] = max(1, limit)
        if search_term:
            args["filter"] = search_term

        response = requests.get(search_path, params=args)
        response.raise_for_status()
        response_data = response.json()

        n_hits = response_data.get("expansion", {}).get("total", 0)
        hits = response_data.get("expansion", {}).get("contains", [])
    else:
        # Just show all results
        args["count"] = max(1, n_total)
        response = requests.get(search_path, params=args)
        response.raise_for_status()
        response_data = response.json()

        n_hits = response_data.get("expansion", {}).get("total", 0)
        hits = response_data.get("expansion", {}).get("contains", [])

    if n_hits == 0:
        # Check number of non-filtered items
        return f"No hits found for {search_term} in {fhir_path}", []
    else:
        return f"Found {n_hits} hits for {search_term} in {fhir_path}", hits