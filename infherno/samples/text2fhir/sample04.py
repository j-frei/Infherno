from typing import Dict
from textwrap import indent, dedent
import json

def getSample() -> Dict:
    return {
        "system": None,
        "input_text": "The patient underwent an appendectomy on March 10, 2023.",
        "codes": [
            {
                "quote": "",
                "query": "completed",
                "path": "Procedure.status",
                "code": "completed",
                "system": "http://hl7.org/fhir/event-status",
                "description": "Completed"
            },
            {
                "quote": "appendectomy",
                "query": "appendectomy",
                "path": "Procedure.code",
                "code": "80146002",
                "system": "http://snomed.info/sct",
                "description": "Excision of appendix (procedure)"
            }
        ],
        "fhir": [
            {
                "resourceType": "Procedure",
                "status": "completed",
                "code": {
                    "resourceType": "CodeableConcept",
                    "coding": [
                        {
                            "resourceType": "Coding",
                            "system": "http://snomed.info/sct",
                            "code": "80146002",
                            "display": "Excision of appendix (procedure)"
                        }
                    ]
                },
                "performedDateTime": "2023-03-10"
            }
        ],
        "finished": True
    }
