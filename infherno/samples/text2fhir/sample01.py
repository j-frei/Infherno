from typing import Dict
from textwrap import indent, dedent
import json

def getSample() -> Dict:
    return {
        "system": None,
        "input_text": dedent("""\
            Es wurde von Magenbesechwerden berichtet.
            """
        ),
        "codes": [
            {
                "quote": "Magenbeschwerden",
                "query": "Stomach ache",
                "path": "Condition.code",
                "code": "271681002",
                "system": "http://snomed.info/sct",
                "description": "Stomach ache (finding)"
            },
            {
                "quote": "",
                "query": "unknown",
                "path": "Condition.clinicalStatus",
                "code": "unknown",
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "description": "Unknown"
            }
        ],
        "fhir": [
            {
                "resourceType": "Condition",
                "clinicalStatus" : {
                    "resourceType": "CodeableConcept",
                    "coding" : [{
                        "resourceType": "Coding",
                        "system" : "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code" : "active",
                        "display" : "Active"
                    }]
                },
                "code": {
                    "resourceType": "CodeableConcept",
                    "coding": [
                        {
                            "resourceType": "Coding",
                            "system": "http://snomed.info/sct",
                            "code": "271681002",
                            "display": "Stomach ache (finding)"
                        }
                    ]
                }
            }
        ],
        "finished": True
    }