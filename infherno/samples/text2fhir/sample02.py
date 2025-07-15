from typing import Dict
from textwrap import indent, dedent
import json

def getSample() -> Dict:
    return {
        "system": None,
        "input_text": "The patient, John Doe, is a 45-year-old male with a history of hypertension. He reports experiencing chest pain.",
        "codes": [
            {
                "quote": "",
                "query": "normal",
                "path": "Patient.name.use",
                "code": "usual",
                "system": "http://hl7.org/fhir/name-use",
                "description": "Usual"
            },
            {
                "quote": "45-year-old male",
                "query": "male",
                "path": "Patient.gender",
                "code": "male",
                "system": "http://hl7.org/fhir/administrative-gender",
                "description": "Male"
            },
            {
                "quote": "",
                "query": "active",
                "path": "Condition.clinicalStatus",
                "code": "active",
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "description": "Active"
            },
            {
                "quote": "hypertension",
                "query": "hypertension",
                "path": "Condition.code",
                "code": "38341003",
                "system": "http://snomed.info/sct",
                "description": "Hypertensive disorder, systemic arterial (disorder)"
            },
            {
                "quote": "chest pain",
                "query": "chest pain",
                "path": "Condition.code",
                "code": "29857009",
                "system": "http://snomed.info/sct",
                "description": "Chest pain (finding)"
            }
        ],
        "fhir": [
            {
                "resourceType": "Patient",
                "name": [
                    {
                        "resourceType": "HumanName",
                        "use": "usual",
                        "family": "Doe",
                        "given": ["John"]
                    }
                ],
                "gender": "male",
                # We cannot calculate the age from the input text
                # "birthDate": "1978-01-01"
            },
            {
                "resourceType": "Condition",
                "clinicalStatus": {
                    "resourceType": "CodeableConcept",
                    "coding": [
                        {
                            "resourceType": "Coding",
                            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                            "code": "active",
                            "display": "Active"
                        }
                    ]
                },
                "code": {
                    "resourceType": "CodeableConcept",
                    "coding": [
                        {
                            "resourceType": "Coding",
                            "system": "http://snomed.info/sct",
                            "code": "38341003",
                            "display": "Hypertensive disorder, systemic arterial (disorder)"
                        }
                    ]
                }
            },
            {
                "resourceType": "Condition",
                "clinicalStatus": {
                    "resourceType": "CodeableConcept",
                    "coding": [
                        {
                            "resourceType": "Coding",
                            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                            "code": "active",
                            "display": "Active"
                        }
                    ]
                },
                "code": {
                    "resourceType": "CodeableConcept",
                    "coding": [
                        {
                            "resourceType": "Coding",
                            "system": "http://snomed.info/sct",
                            "code": "29857009",
                            "display": "Chest pain (finding)"
                        }
                    ]
                }
            }
        ],
        "finished": True
    }
