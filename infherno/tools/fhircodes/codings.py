from __future__ import annotations
import os, re, json, sqlite3
from functools import reduce
from urllib.parse import urlparse
from collections import OrderedDict
from typing import Dict, List, Optional, TypedDict

import requests
from infherno.defaults import determine_snowstorm_url, determine_snowstorm_branch
from infherno.tools.fhircodes.instance import GenericSnomedInstance, getECLfromConceptRoots

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(os.path.dirname(os.path.dirname(THIS_DIR)))

# Caching
CACHE_DIR = os.path.join(REPO_DIR, "cache")
CODINGS_CACHE = os.path.join(CACHE_DIR, "codings")
if not os.path.exists(CODINGS_CACHE):
    os.makedirs(CODINGS_CACHE, exist_ok=True)

# URL fixes
_CODESYSTEM_REDIRECT = {
    "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus": "http://terminology.hl7.org/4.0.0/CodeSystem-v3-MaritalStatus.json",
    "http://terminology.hl7.org/CodeSystem/v3-NullFlavor": "http://terminology.hl7.org/4.0.0/CodeSystem-v3-NullFlavor.json",
    "http://terminology.hl7.org/CodeSystem/condition-clinical": "http://hl7.org/fhir/R4/codesystem-condition-clinical.json",
    "http://terminology.hl7.org/CodeSystem/condition-ver-status": "http://hl7.org/fhir/R4/codesystem-condition-ver-status.json",
    "http://terminology.hl7.org/CodeSystem/dose-rate-type": "http://hl7.org/fhir/R4/codesystem-dose-rate-type.json",
    "http://terminology.hl7.org/CodeSystem/v3-TimingEvent": "http://terminology.hl7.org/4.0.0/CodeSystem-v3-TimingEvent.json",
    "http://terminology.hl7.org/CodeSystem/v3-GTSAbbreviation": "http://terminology.hl7.org/4.0.0/CodeSystem-v3-GTSAbbreviation.json",

    # Fix for CodeSystem-allergyintolerance-clinical (broken concept JSON list)
    "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical": "https://myweb.rz.uni-augsburg.de/~freijoha/fhir/CodeSystem-allergyintolerance-clinical.json",
    "http://terminology.hl7.org/CodeSystem/medication-statement-category": "http://hl7.org/fhir/R4/codesystem-medication-statement-category.json",
}

# Supported Codes/Codings
_CODINGS = OrderedDict({
    "Patient.name.use": {"vs": "http://hl7.org/fhir/R4/valueset-name-use.json", "type": "code"},
    "Patient.contact.system": {"vs": "http://hl7.org/fhir/R4/valueset-contact-point-system.json", "type": "code"},
    "Patient.contact.use": {"vs": "http://hl7.org/fhir/R4/valueset-contact-point-use.json", "type": "code"},
    "Patient.gender": {"vs": "http://hl7.org/fhir/R4/valueset-administrative-gender.json", "type": "code"},
    "Patient.address.use": {"vs": "http://hl7.org/fhir/R4/valueset-address-use.json", "type": "code"},
    "Patient.address.type": {"vs": "http://hl7.org/fhir/R4/valueset-address-type.json", "type": "code"},
    "Patient.maritalStatus": {"vs": "http://hl7.org/fhir/R4/valueset-marital-status.json", "type": "coding"},
    # IGNORE Patient.contact.relationship
    "Condition.clinicalStatus": {"vs": "http://hl7.org/fhir/R4/valueset-condition-clinical.json", "type": "coding"},
    "Condition.verificationStatus": {"vs": "http://hl7.org/fhir/R4/valueset-condition-ver-status.json", "type": "coding"},
    # IGNORE Condition.category / Condition Category Codes
    "Condition.severity": {"vs": "http://hl7.org/fhir/R4/valueset-condition-severity.json", "type": "coding"},
    "Condition.code": {"vs": "http://hl7.org/fhir/R4/valueset-condition-code.json", "type": "coding"},
    "Condition.bodySite": {"vs": "http://hl7.org/fhir/R4/valueset-body-site.json", "type": "coding"},
    # IGNORE Condition.participant.function
    "Condition.stage.summary": {"vs": "http://hl7.org/fhir/R4/valueset-condition-stage.json", "type": "coding"},
    "Condition.stage.type": {"vs": "http://hl7.org/fhir/R4/valueset-condition-stage-type.json", "type": "coding"},
    "Condition.evidence": {"vs": "http://hl7.org/fhir/R4/valueset-clinical-findings.json", "type": "coding"},
    "MedicationStatement.status": {"vs": "http://hl7.org/fhir/R4/valueset-medication-statement-status.json", "type": "code"},
    # IGNORE MedicationStatement.category
    "MedicationStatement.category": {"vs": "http://hl7.org/fhir/R4/valueset-medication-statement-category.json", "type": "coding"},
    "MedicationStatement.medication": {"vs": "http://hl7.org/fhir/R4/valueset-medication-codes.json", "type": "coding"},
    "MedicationStatement.effectiveTiming.repeat.dayOfWeek": {"vs": "http://hl7.org/fhir/R4/valueset-days-of-week.json", "type": "coding"},
    "MedicationStatement.effectiveTiming.repeat.when": {"vs": "http://hl7.org/fhir/R4/valueset-event-timing.json", "type": "coding"},
    "MedicationStatement.effectiveTiming.code": {"vs": "http://hl7.org/fhir/R4/valueset-timing-abbreviation.json", "type": "coding"},
    ## "MedicationStatement.reason": {"vs": "http://hl7.org/fhir/ValueSet/condition-code", "type": "coding"},
    # IGNORE MedicationStatement.dosage.additionalInstruction
    # Unsupported UnitsOfMeasure "MedicationStatement.dosage.timing.repeat.durationUnit": {"vs": "http://hl7.org/fhir/ValueSet/units-of-time", "type": "coding"},
    # Unsupported UnitsOfMeasure "MedicationStatement.dosage.timing.repeat.periodUnit": {"vs": "http://hl7.org/fhir/ValueSet/units-of-time", "type": "coding"},

    "MedicationStatement.dosage.timing.repeat.dayOfWeek": {"vs": "http://hl7.org/fhir/R4/valueset-days-of-week.json", "type": "code"},
    "MedicationStatement.dosage.timing.repeat.when": {"vs": "http://hl7.org/fhir/R4/valueset-event-timing.json", "type": "code"},
    "MedicationStatement.dosage.timing.code": {"vs": "http://hl7.org/fhir/R4/valueset-timing-abbreviation.json", "type": "coding"},
    "MedicationStatement.dosage.asNeededFor": {"vs": "http://hl7.org/fhir/R4/valueset-medication-as-needed-reason.json", "type": "coding"},
    "MedicationStatement.dosage.site": {"vs": "http://hl7.org/fhir/R4/valueset-approach-site-codes.json", "type": "coding"},
    "MedicationStatement.dosage.route": {"vs": "http://hl7.org/fhir/R4/valueset-route-codes.json", "type": "coding"},
    "MedicationStatement.dosage.method": {"vs": "http://hl7.org/fhir/R4/valueset-administration-method-codes.json", "type": "coding"},
    "MedicationStatement.dosage.doseAndRate.type": {"vs": "http://hl7.org/fhir/R4/valueset-dose-rate-type.json", "type": "coding"},
    "Procedure.status": {"vs": "http://hl7.org/fhir/R4/valueset-event-status.json", "type": "code"},
    "Procedure.statusReason": {"vs": "http://hl7.org/fhir/R4/valueset-procedure-not-performed-reason.json", "type": "coding"},
    "Procedure.category": {"vs": "http://hl7.org/fhir/R4/valueset-procedure-category.json", "type": "coding"},
    "Procedure.code": {"vs": "http://hl7.org/fhir/R4/valueset-procedure-code.json", "type": "coding"},
    # Unsupported UnitsOfMeasure "Procedure.occurrenceTiming.repeat.durationUnit": {"vs": "http://hl7.org/fhir/ValueSet/units-of-time", "type": "coding"},
    # Unsupported UnitsOfMeasure "Procedure.occurrenceTiming.repeat.periodUnit": {"vs": "http://hl7.org/fhir/ValueSet/units-of-time", "type": "coding"},
    "Procedure.occurrenceTiming.repeat.dayOfWeek": {"vs": "http://hl7.org/fhir/R4/valueset-days-of-week.json", "type": "coding"},
    "Procedure.occurrenceTiming.repeat.when": {"vs": "http://hl7.org/fhir/R4/valueset-event-timing.json", "type": "coding"},
    "Procedure.occurrenceTiming.code": {"vs": "http://hl7.org/fhir/R4/valueset-timing-abbreviation.json", "type": "coding"},
    ## "Procedure.reason": {"vs": "http://hl7.org/fhir/ValueSet/procedure-reason", "type": "coding"},
    "Procedure.bodySite": {"vs": "http://hl7.org/fhir/R4/valueset-body-site.json", "type": "coding"},
    "Procedure.outcome": {"vs": "http://hl7.org/fhir/R4/valueset-procedure-outcome.json", "type": "coding"},
    "Procedure.complications": {"vs": "http://hl7.org/fhir/R4/valueset-condition-code.json", "type": "coding"},
    "Procedure.followUp": {"vs": "http://hl7.org/fhir/R4/valueset-procedure-followup.json", "type": "coding"},
    # IGNORE Procedure.focalDevice
    # IGNORE Procedure.used
    "Encounter.status": {"vs": "http://hl7.org/fhir/R4/valueset-encounter-status.json", "type": "code"},
    # IGNORE Encounter.class
    # IGNORE Encounter.priority
    # IGNORE Encounter.type
    # IGNORE Encounter.serviceType
    # IGNORE Encounter.subjectStatus
    # IGNORE Encounter.participant.type

    # clinicalStatus is broken in the concept JSON property: https://terminology.hl7.org/6.2.0/CodeSystem-allergyintolerance-clinical.json.html
    "AllergyIntolerance.clinicalStatus": {"vs": "http://hl7.org/fhir/R4/valueset-allergyintolerance-clinical.json", "type": "coding"},
    "AllergyIntolerance.verificationStatus": {"vs": "http://hl7.org/fhir/R4/valueset-allergyintolerance-verification.json", "type": "coding"},
    "AllergyIntolerance.type": {"vs": "http://hl7.org/fhir/R4/valueset-allergy-intolerance-type.json", "type": "code"},
    "AllergyIntolerance.category": {"vs": "http://hl7.org/fhir/R4/valueset-allergy-intolerance-category.json", "type": "code"},
    "AllergyIntolerance.criticality": {"vs": "http://hl7.org/fhir/R4/valueset-allergy-intolerance-criticality.json", "type": "code"},
    "AllergyIntolerance.code": {"vs": "http://hl7.org/fhir/R4/valueset-allergyintolerance-code.json", "type": "coding"},
    "AllergyIntolerance.bodySite": {"vs": "http://hl7.org/fhir/R4/valueset-body-site.json", "type": "coding"},

})

def safe_filename(filename):
    """Return a safe filename that can be used on most filesystems."""

    return "".join([c for c in filename if c.isalpha() or c.isdigit() or c==' ']).rstrip()

def cachedRequest(url):
    global CODINGS_CACHE
    """Request a URL and cache the result in a file."""
    cache_filename = safe_filename(url)
    cache_path = os.path.join(CODINGS_CACHE, cache_filename + ".json")
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)
    else:
        print(f"Requesting {url}")
        response = requests.get(url, headers={
            "Accept": "application/json, */*",
            # We somehow need to set a User Agent.
            # E.g. 'http://terminology.hl7.org/4.0.0/CodeSystem-v3-MaritalStatus.json' is sometimes not available using Curl or requests.get() w/o User-Agent
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        })
        try:
            response.raise_for_status()
        except:
            print(f"URL {url} raised an error with status code: {response.status_code}")

        r_obj = response.json()
        with open(cache_path, "w") as f:
            json.dump(r_obj, f)
        return r_obj

class Concept(TypedDict):
    code: str
    system: str
    description: Optional[str]

class CodeSystemStaticLoader:
    def __init__(self, concepts) -> None:
        self.concepts = concepts

        # Setup db for search
        self.db = sqlite3.connect(":memory:")
        self.db.execute("CREATE TABLE IF NOT EXISTS concept (\
                        code TEXT PRIMARY KEY, system TEXT NOT NULL DEFAULT '', \
                        description TEXT NOT NULL DEFAULT '', \
                        search TEXT NOT NULL DEFAULT '');")
        self.db.executemany("INSERT INTO concept VALUES (?, ?, ?, ?)", [
            (
                c["code"],
                c["system"],
                (c["description"] if c["description"] is not None else ''),
                re.sub(r'[^0-9a-zA-Z\s]+', '', c["code"] + "\n" + (c["description"] if c["description"] is not None else '')).lower()
            )
            for c in self.getConcepts()
        ])
        self.db.commit()

    def count(self):
        return len(self.concepts)

    def isStored(self):
        return True

    def getConcepts(self):
        return self.concepts

    def search(self, query: str = None, limit: int = None):
        query_words = [ re.sub(r'[^0-9a-zA-Z]+', '', q).lower() for q in query.split() ] if query is not None else []
        # filter for empty words
        query_words = [ q for q in query_words if q ]
        # We can build this query because the terms are cleands for azAZ09
        sub_stmd = " AND ".join([
            f"instr(search, '{q}')"
            for q in query_words
        ])
        stmd = "SELECT code, system, description FROM concept"
        if sub_stmd:
            stmd += " WHERE " + sub_stmd

        if limit:
            stmd += f" LIMIT {limit}"
        result = self.db.execute(stmd)
        result_items = [
            {"code": code, "system": system, "description": description}
            for code, system, description in result.fetchall()
        ]
        return result_items

    def getByCode(self, code: str):
        code_list = [ c for c in self.getConcepts() if c["code"] == code ]
        if len(code_list) == 1: return code_list[0]
        elif len(code_list) == 0: return None
        else: raise ValueError(f"Multiple entries found for code {code}")

    @classmethod
    def from_url(cls, system_url: str, filter_type: str, filter_info: str):
        try:
            cs_doc = cachedRequest(system_url)
        except Exception as e:
            print("URL:", system_url)
            return CodeSystemStaticLoader([])

        assert "concept" in cs_doc
        assert "url" in cs_doc
        advertised_url = cs_doc["url"]
        all_concepts = [
            {
                "code": concept["code"],
                "system": advertised_url,
                "actual_system_url": system_url,
                "description": concept.get("definition")
            }
            for concept in cs_doc["concept"]
        ]

        if filter_type == "all":
            concepts = all_concepts
        elif filter_type == "filter":
            raise Exception("Filter type 'filter' not supported.")
        elif filter_type == "explicit":
            allowed_codes = [ fi["code"] for fi in filter_info ]
            concepts = [ concept for concept in all_concepts if concept["code"] in allowed_codes ]

        return CodeSystemStaticLoader(concepts)

class CodeSystemSNOMEDLoader:
    system = "http://snomed.info/sct"
    def __init__(self, n_counts: int, filter: str, snomed_instance: GenericSnomedInstance) -> None:
        self.n_counts = n_counts
        self.filter = filter
        self.snomed_instance = snomed_instance

    def count(self):
        return self.n_counts

    def getConcepts(self, query: str = None, limit: int = None):
        return [
            {
                "code": concept["id"],
                "system": self.system,
                "description": concept["term"],
            }
            for concept in self.snomed_instance.search_by_concepts(query, ecl=self.filter, limit=limit)
        ]

    def search(self, query: str = None, limit: int = None):
        return self.getConcepts(query=query, limit=limit)

    def getByCode(self, code: str):
        code_list = [
            {
                "code": concept["id"],
                "system": self.system,
                "description": concept["term"],
            }
            for concept in self.snomed_instance.search_by_concepts(None, conceptIds=[code], limit=1)
        ]
        if len(code_list) == 1: return code_list[0]
        elif len(code_list) == 0: return None
        else: raise ValueError(f"Multiple entries found for code {code}")

    @classmethod
    def from_snomed(cls,  store_threshold: int, snomed_instance: GenericSnomedInstance, filter_type: str = "all", filter_info: object = None) -> CodeSystemSNOMEDLoader:
        filter_ecl = None
        n_counts = None
        concepts = None

        if filter_type == "all":
            assert filter_info is None
            # We essentially cover all SNOMEDs concepts
            n_counts = snomed_instance.search_by_concepts(getRawResponse=True, limit=1)["total"]
            if n_counts <= store_threshold:
                # we should explicitly keep the results
                concepts = snomed_instance.search_by_concepts()
                assert len(concepts) == n_counts

        elif filter_type == "filter":
            assert filter_info is not None
            # check format
            assert len(filter_info) == len([ filter_obj for filter_obj in filter_info if filter_obj["op"] == "is-a" and filter_obj["property"] == "concept"])

            # We cover a limited set of SNOMEDs concepts
            try:
                filter_ecl = getECLfromConceptRoots([ filter_obj["value"] for filter_obj in filter_info ])
                n_counts = snomed_instance.search_by_concepts(getRawResponse=True, limit=1, ecl=filter_ecl)["total"]
            except:
                # ECL filter fails. Probably the concept ID is disabled?!
                print(f"We failed to query SNOMED with filter ECL: {filter_ecl}")
                return None
            if n_counts <= store_threshold:
                # we should explicitly keep the results
                concepts = snomed_instance.search_by_concepts(limit=None, ecl=filter_ecl)

        elif filter_type == "explicit":
            assert filter_info is not None
            # check format
            assert len(filter_info) == len([ filter_obj for filter_obj in filter_info if "code" in filter_obj])

            #n_counts = snomed_instance.search_by_concepts(getRawResponse=True, limit=1)["total"]
            n_counts = len(filter_info)
            concepts = snomed_instance.search_by_concepts(limit=None, conceptIds=[ filter_obj["code"] for filter_obj in filter_info ])

            if len(concepts) != n_counts:
                missing_items = [ filter_obj["code"] for filter_obj in filter_info if filter_obj["code"] not in [ c["id"] for c in concepts ] ]
                print(f"The following items could not be found in SNOMED: {','.join(missing_items)}")
        else:
            raise Exception("Unknown state")

        if concepts is not None:
            concepts = [
                {
                    "code": concept["id"],
                    "system": cls.system,
                    "description": concept["term"],
                }
                for concept in concepts
            ]
            return CodeSystemStaticLoader(concepts=concepts)
        else:
            return CodeSystemSNOMEDLoader(n_counts=n_counts, filter=filter_ecl, snomed_instance=snomed_instance)

_VSL_ = {}
class ValueSetLoader:
    def __init__(self, url: str, cs: List) -> None:
        self.url: str = url
        self.cs: List = cs

    @classmethod
    def from_url(cls, url, store_threshold: int, snomed_instance: GenericSnomedInstance) -> ValueSetLoader:
        global _VSL_
        if (url, store_threshold) in _VSL_:
            return _VSL_[(url, store_threshold)]

        vs_doc = cachedRequest(url)

        cs = []

        all_cs = vs_doc["compose"]["include"]
        for cs_item in all_cs:
            if "system" in cs_item:
                # The CS seems to be a direct reference
                filter_type = "all"
                filter_info = None

                if "filter" in cs_item:
                    filter_type = "filter"
                    filter_info = cs_item["filter"]
                elif "concept" in cs_item:
                    filter_type = "explicit"
                    filter_info = cs_item["concept"]

                # find loader
                ref_url = cs_item["system"]
                ref_url = _CODESYSTEM_REDIRECT.get(ref_url, ref_url)

                if ref_url == "http://snomed.info/sct":
                    cs_loader = CodeSystemSNOMEDLoader.from_snomed(store_threshold, snomed_instance, filter_type, filter_info)
                    if cs_loader: cs.append(cs_loader)
                elif urlparse(ref_url).netloc.endswith("hl7.org") or urlparse(ref_url).netloc.endswith("myweb.rz.uni-augsburg.de"):
                    cs.append(CodeSystemStaticLoader.from_url(ref_url, filter_type, filter_info))
                else:
                    raise NotImplementedError(f"Unhandled URL: {ref_url}")
            elif "valueSet" in cs_item:
                # Apparently, the CS can also be a reference to another value set
                # We use a recursive ValueSetLoader here, and just append the codesystems to the root cs list
                rec_vs_urls = cs_item["valueSet"]
                for rec_vs_url in rec_vs_urls:
                    rec_vs_url = _CODESYSTEM_REDIRECT.get(rec_vs_url, rec_vs_url)
                    rec_vsl = ValueSetLoader.from_url(rec_vs_url, store_threshold=store_threshold, snomed_instance=snomed_instance)
                    cs.extend(rec_vsl.cs)
            else:
                raise NotImplementedError(f"Unhandled Item: {cs_item}")

        vsl = ValueSetLoader(url, cs)
        _VSL_[(url, store_threshold)] = vsl
        return vsl

    def getConcepts(self):
        return reduce(lambda x,y: x+y, [
            cs.getConcepts() if isinstance(cs, CodeSystemSNOMEDLoader) \
            else cs.getConcepts() for cs in self.cs
        ], [])

    def search(self, query: str = None, limit: int = None):
        return reduce(lambda x,y: x+y, [
            cs.search(query, limit) for cs in self.cs
        ], [])

    def getByCode(self, code: str):
        code_list = [ e for e in [
            cs.getByCode(code) for cs in self.cs
        ] if e]
        if len(code_list) == 1: return code_list[0]
        elif len(code_list) == 0: return None
        else:
            print(f"Multiple entries found for code {code}:", code_list)
            return code_list[0]

    def count(self):
        return reduce(lambda x,y: x+y, [ cs.count() for cs in self.cs], 0)

def getValueSet(fhirpath):
    if fhirpath not in _CODINGS:
        raise ValueError(f"{fhirpath} does not exist.\nCodings available:\n" + "\n".join([ f"- {q}" for q,_ in _CODINGS.items() ]))
    return _CODINGS.get(fhirpath)

def listSupportedCodings():
    global _CODINGS
    return _CODINGS.keys()

if __name__ == "__main__":
    vs_loaders = {}
    snomed_instance = GenericSnomedInstance(determine_snowstorm_url(), branch=determine_snowstorm_branch())
    for query, coding_info in _CODINGS.items():
        url = coding_info["vs"]
        code_type = coding_info["type"]
        print(f"Checking {query} @ {url}")
        vsl = ValueSetLoader.from_url(url, store_threshold=20, snomed_instance=snomed_instance)
        vs_loaders[query] = vsl

        print(f"-> {vsl.count()} entries found.")
        print("-"*5)
