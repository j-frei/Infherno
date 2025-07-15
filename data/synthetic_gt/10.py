from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.medicationstatement import MedicationStatement
# Bundle
from fhir.resources.R4B.bundle import Bundle, BundleEntry
# HumanName
from fhir.resources.R4B.humanname import HumanName

notes = """
- Herr Matthias Weissmuller, 30.06.1964
- Brustschmerzen
- Atemnot
- Koronare Herzkrankheit
- Diabetes mellitus Typ 2
- Hypertonie
- Adipositas
- medikamentöse Therapie zur Stabilisierung seiner Herzfunktion und zur Blutzuckereinstellung

- Metformin
- Sulfonylharnstoffe
"""

patient = Patient(
    id="pat-1",
    name=[HumanName(family="Weissmuller", given=["Matthias"])],
    birthDate="1964-06-30",
    gender="male",
)

# Brustschmerzen
condition_chest_pain = Condition(
    id="cond-1",
    clinicalStatus={
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
            "code": "remission",
            "display": "Remission"
        }]
    },
    # verificationStatus unklar?!
    subject={"reference": "Patient/pat-1"},
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "29857009",
            "display": "Chest pain"
        }]
    }
)

# Atemnot
condition_dyspnoe = Condition(
    id="cond-2",
    clinicalStatus={
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
            "code": "remission",
            "display": "Remission"
        }]
    },
    # verificationStatus unklar?!
    subject={"reference": "Patient/pat-1"},
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "267036007",
            "display": "Dyspnea"
        }]
    }
)

# Koronare Herzkrankheit
condition_coronary = Condition(
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
            "code": "confirmed",
            "display": "Confirmed"
        }]
    },
    subject={"reference": "Patient/pat-1"},
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "53741008",
            "display": "Coronary arteriosclerosis"
        }]
    }
)

# Hypertonie
condition_hypertension = Condition(
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
            "code": "confirmed",
            "display": "Confirmed"
        }]
    },
    subject={"reference": "Patient/pat-1"},
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "38341003",
            "display": "Hypertensive disorder"
        }]
    }
)

# Adipositas
condition_obesity = Condition(
    id="cond-5",
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
            "code": "confirmed",
            "display": "Confirmed"
        }]
    },
    subject={"reference": "Patient/pat-1"},
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "414916001",
            "display": "Obesity"
        }]
    }
)

# Medikamentöse Therapie zur Stabilisierung der Herzfunktion
medication_heart_stabilization = MedicationStatement(
    id="med-1",
    status="active",
    medicationCodeableConcept={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "373247007",
            "display": "Cardiovascular agent"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

# Metformin
medication_metformin = MedicationStatement(
    id="med-2",
    status="active",
    medicationCodeableConcept={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "372567009",
            "display": "Metformin"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

# Sulfonylharnstoffe
medication_sulfonylureas = MedicationStatement(
    id="med-3",
    status="active",
    medicationCodeableConcept={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "34012005",
            "display": "Sulfonylurea-containing product"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

bundle = Bundle(
    type = "collection",
    entry=[
        BundleEntry(resource=patient),
        BundleEntry(resource=condition_chest_pain),
        BundleEntry(resource=condition_dyspnoe),
        BundleEntry(resource=condition_coronary),
        BundleEntry(resource=condition_hypertension),
        BundleEntry(resource=condition_obesity),
        BundleEntry(resource=medication_heart_stabilization),
        BundleEntry(resource=medication_metformin),
        BundleEntry(resource=medication_sulfonylureas)
    ]
)

print(bundle.json(indent=2))
# Verify with:
# $> echo "$(python3 data/synthetic_gt/10.py)" | curl -X POST -H "Content-Type: application/fhir+json" -d @- http://hapi.fhir.org/baseR4/Bundle