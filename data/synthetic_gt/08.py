from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.medicationstatement import MedicationStatement
# Bundle
from fhir.resources.R4B.bundle import Bundle, BundleEntry
# HumanName
from fhir.resources.R4B.humanname import HumanName

notes = """
- Frau Uta Herz, geb 09.12.1991
- Anhaltende Kopfschmerzen bei Stirn und Schläfen
- Schwindelgefühl bei schnellen Kopfbewegungen
- leichte Übelkeit
- Verdachtsdiagnose: migräneartige Zephalalgie
- Ibuprofen 400mg bei Kopfschmerzen
"""

patient = Patient(
    id="pat-1",
    name=[HumanName(family="Busch", given=["Anke"])],
    birthDate="1986-04-06",
    gender="female",
)

# Kopfschmerzen bei Stirn und Schläfen
condition_headache = Condition(
    id="cond-1",
    clinicalStatus={
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
            "code": "active",
            "display": "Active"
        }]
    },
    verificationStatus={
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
            "code": "unconfirmed",
            "display": "Unconfirmed"
        }]
    },
    subject={"reference": "Patient/pat-1"},
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "25064002",
            "display": "Headache"
        }]
    },
    bodySite=[{
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "52795006",
            "display": "Forehead structure"
        }]
    }, {
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "450721000",
            "display": "Structure of temporal region"
        }]
    }]
)

# Schwindelgefühl bei schnellen Kopfbewegungen
condition_dizziness = Condition(
    id="cond-2",
    clinicalStatus={
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
            "code": "active",
            "display": "Active"
        }]
    },
    verificationStatus={
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
            "code": "unconfirmed",
            "display": "Unconfirmed"
        }]
    },
    subject={"reference": "Patient/pat-1"},
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "404640003",
            "display": "Dizziness"
        }]
    }
)

# leichte Übelkeit
condition_nausea = Condition(
    id="cond-3",
    # clinicalStatus unbekannt.
    verificationStatus={
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
            "code": "unconfirmed",
            "display": "Unconfirmed"
        }]
    },
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "422587007",
            "display": "Nausea"
        }]
    },
    subject={"reference": "Patient/pat-1"},
    severity={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "255604002",
            "display": "Mild"
        }]
    }
)

# Verdachtsdiagnose: migräneartige Zephalalgie
condition_migraine_like_headache = Condition(
    id="cond-4",
    clinicalStatus={
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
            "code": "active",
            "display": "Active"
        }]
    },
    verificationStatus={
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
            "code": "provisional",
            "display": "Provisional"
        }]
    },
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "38823002",
            "display": "Aural headache"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

bundle = Bundle(
    type = "collection",
    entry=[
        BundleEntry(resource=patient),
        BundleEntry(resource=condition_headache),
        BundleEntry(resource=condition_dizziness),
        BundleEntry(resource=condition_nausea),
        BundleEntry(resource=condition_migraine_like_headache),
    ]
)

print(bundle.json(indent=2))
# Verify with:
# $> echo "$(python3 data/synthetic_gt/08.py)" | curl -X POST -H "Content-Type: application/fhir+json" -d @- http://hapi.fhir.org/baseR4/Bundle