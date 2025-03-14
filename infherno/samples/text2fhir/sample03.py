from typing import Dict
from textwrap import indent, dedent
import json

def getSample() -> Dict:
    return {
        "system": None,
        "input_text": "The patient reports taking Tylenol PM for sleep.",
        "codes": [
            {
                "quote": "",
                "query": "done",
                "path": "MedicationStatement.status",
                "code": "recorded",
                "system": "http://hl7.org/fhir/CodeSystem/medication-statement-status",
                "description": "Recorded"
            },
            {
                "quote": "Tylenol PM",
                "query": "Acetaminophen",
                "path": "MedicationStatement.medication",
                "code": "387517004",
                "system": "http://snomed.info/sct",
                "description": "Paracetamol (substance)"
            }
            #{
            #    "quote": "for sleep",
            #    "query": "sleep",
            #    "path": "MedicationStatement.reasonCode",
            #    "code": "4224004",
            #    "system": "http://snomed.info/sct",
            #    "description": "Sleep disorder (disorder)"
            #}
        ],
        "fhir": [
            {
                "resourceType": "MedicationStatement",
                "status": "recorded",
                "medicationCodeableConcept": {
                    "resourceType": "CodeableConcept",
                    "coding": [
                        {
                            "resourceType": "Coding",
                            "system": "http://snomed.info/sct",
                            "code": "387517004",
                            "display": "Paracetamol (substance)"
                        }
                    ]
                },
            }
        ],
        "finished": True
    }

