import json, os
from glob import glob
from typing import Generator, Dict

from infherno.samples.text2fhir import (
    sample01,
    sample02,
    sample03,
    sample04,
)

dpath = os.path.dirname(os.path.realpath(__file__))

SAMPLES = [
    # "Magenschmerzen" (without context)
    sample01,
    # Patient John Doe with hypertension and chest pain Conditions
    sample02,
    # MedicationStatement with Tylenol PM
    sample03,
    # Procedure Appendectomy
    sample04,
]

def prepareSample(system_prompt: str, raw_sample_obj: Dict) -> Dict:
    sample_dict = raw_sample_obj.copy()

    # Add system prompt to sample
    sample_dict["system"] = system_prompt

    # Transform FHIR resources into text
    if "fhir" in sample_dict and sample_dict["fhir"] is not None:
        sample_dict["fhir"] = [
            json.dumps(resource, indent=2)
            for resource in sample_dict["fhir"]
        ]

    return sample_dict

def getSamples(system_prompt: str) -> Generator[Dict, None, None]:
    for sample in SAMPLES:
        sample_obj = sample.getSample()
        yield prepareSample(system_prompt, sample_obj)