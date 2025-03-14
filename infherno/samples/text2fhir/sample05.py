from typing import Dict
from textwrap import indent, dedent
import json

def getSample() -> Dict:
    return {
        "system": None,
        "input_text": "Basierend auf den klinischen Symptomen und den durchgeführten Untersuchungen wird bei Frau Achen eine Migräne mit episodischen neurologischen Symptomen (Migräne mit Aura) diagnostiziert.",
        "codes": [
            {
                "quote": "",
                "query": "usual",
                "path": "Patient.name.use",
                "code": "usual",
                "system": "http://hl7.org/fhir/name-use",
                "description": "Usual"
            },
            {
                "quote": "Frau Achen",
                "query": "female",
                "path": "Patient.gender",
                "code": "female",
                "system": "http://hl7.org/fhir/administrative-gender",
                "description": "Female"
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
                "quote": "Migräne mit episodischen neurologischen Symptomen (Migräne mit Aura)",
                "query": "migraine with aura",
                "path": "Condition.code",
                "code": "4473006",
                "system": "http://snomed.info/sct",
                "description": "Migraine with aura (disorder)"
            },
        ],
        "fhir": [
            {
                "resourceType": "Patient",
                "name": [
                    {
                        "resourceType": "HumanName",
                        "use": "usual",
                        "family": "Achen",
                    }
                ],
                "gender": "female"
            },
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
                            "code": "4473006",
                            "display": "Migraine with aura (disorder)"
                        }
                    ]
                }
            }
        ],
        "finished": True
    }
