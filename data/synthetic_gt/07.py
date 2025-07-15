from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.medicationstatement import MedicationStatement
# Bundle
from fhir.resources.R4B.bundle import Bundle, BundleEntry
# HumanName
from fhir.resources.R4B.humanname import HumanName

notes = """
- Frau Susanne Scholz, 05.03.1983
- Kopfschmerzen bei Stirn und Schläfen
- Schlafstörungen, Müdigkeit, Erschöpfung
- Antriebslosigkeit
"""

patient = Patient(
    id="pat-1",
    name=[HumanName(family="Scholz", given=["Susanne"])],
    birthDate="1983-03-05",
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

# Schlafstörungen
condition_insomnia = Condition(
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
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "193462001",
            "display": "Insomnia"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

# Müdigkeit, Erschöpfung
condition_fatigue = Condition(
    id="cond-3",
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
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "84229001",
            "display": "Fatigue"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)
bundle = Bundle(
    type = "collection",
    entry=[
        BundleEntry(resource=patient),
        BundleEntry(resource=condition_headache),
        BundleEntry(resource=condition_insomnia),
        BundleEntry(resource=condition_fatigue)
    ]
)

print(bundle.json(indent=2))
# Verify with:
# $> echo "$(python3 data/synthetic_gt/07.py)" | curl -X POST -H "Content-Type: application/fhir+json" -d @- http://hapi.fhir.org/baseR4/Bundle