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
            }
        ],
        "fhir": [
            {
                "resourceType": "Condition",
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