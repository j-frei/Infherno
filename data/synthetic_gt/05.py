from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.medicationstatement import MedicationStatement
# Bundle
from fhir.resources.R4B.bundle import Bundle, BundleEntry
# HumanName
from fhir.resources.R4B.humanname import HumanName

notes = """
- Herr Robert Kappel, 1965/02/21
- Koronare Herzerkrankung, Hypertonie
- Brustschmerzen (incl. linker Arm)
- Engegefühl im Brustkorb und Dyspnoe

- Systolikum
- ST-Streckenveränderungen, schwache linksventrikuläre Funktion mit einer Auswurffraktion (eher Observation)
- Stenose in prximaler linken Herzkranzarterie (Observation?)
- PCI Stent (Procedure)
- Brustschmerzen verschwunden
- keine Dyspnoe mehr

- Aspirin 100mg täglich
- Clopidogrel 75mg täglich
- Bisoprolol 5mg täglich
- Ramipril 2,5mg täglich
"""

patient = Patient(
    id="pat-1",
    name=[HumanName(family="Kappel", given=["Robert"])],
    birthDate="1965-02-21",
    gender="male",
)

# Koronare Herzerkrankung
condition_coronary = Condition(
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
            "code": "confirmed",
            "display": "Confirmed"
        }]
    },
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "53741008",
            "display": "Coronary artery disease"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

# Hypertonie
condition_hypertension = Condition(
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
            "code": "confirmed",
            "display": "Confirmed"
        }]
    },
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "38341003",
            "display": "Hypertension"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

# Brustschmerzen (inkl. linker Arm)
condition_chest_pain = Condition(
    id="cond-3",
    clinicalStatus={
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
            "code": "remission",
            "display": "Remission"
        }]
    },
    verificationStatus={
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
            "code": "confirmed",
            "display": "Confirmed"
        }]
    },
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "29857009",
            "display": "Chest pain"
        }]
    },
    subject={"reference": "Patient/pat-1"},
    bodySite=[{
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "72098002",
            "display": "Entire left upper arm"
        }]},
        {
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "302551006",
            "display": "Entire thorax"
        }]
    }]
)

# Dyspnoe
condition_dyspnoe = Condition(
    id="cond-4",
    clinicalStatus={
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
            "code": "remission",
            "display": "Remission"
        }]
    },
    verificationStatus={
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
            "code": "confirmed",
            "display": "Confirmed"
        }]
    },
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "267036007",
            "display": "Dyspnoea"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

# Aspirin 100mg täglich
medication_aspirin = MedicationStatement(
    id="med-1",
    status="active",
    medicationCodeableConcept={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "387458008",
            "display": "Aspirin"
        }]
    },
    subject={"reference": "Patient/pat-1"},
    dosage=[{
        "timing": {
            "repeat": {
                "frequency": 1,
                "period": 1,
                "periodUnit": "d"
            }
        },
        "doseAndRate": [{
            "type": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/dose-rate-type",
                    "code": "ordered",
                    "display": "Ordered"
                }]
            },
            "doseQuantity": {
                "value": 100,
                "unit": "mg",
                "system": "http://unitsofmeasure.org",
                "code": "mg"
            }
        }]
    }]
)

# Clopidogrel 75mg täglich
medication_clopidogrel = MedicationStatement(
    id="med-2",
    status="active",
    medicationCodeableConcept={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "386952008",
            "display": "Clopidogrel"
        }]
    },
    subject={"reference": "Patient/pat-1"},
    dosage=[{
        "timing": {
            "repeat": {
                "frequency": 1,
                "period": 1,
                "periodUnit": "d"
            }
        },
        "doseAndRate": [{
            "type": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/dose-rate-type",
                    "code": "ordered",
                    "display": "Ordered"
                }]
            },
            "doseQuantity": {
                "value": 75,
                "unit": "mg",
                "system": "http://unitsofmeasure.org",
                "code": "mg"
            }
        }]
    }]
)

# Bisoprolol 5mg täglich
medication_bisoprolol = MedicationStatement(
    id="med-3",
    status="active",
    medicationCodeableConcept={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "386868003",
            "display": "Bisoprolol"
        }]
    },
    subject={"reference": "Patient/pat-1"},
    dosage=[{
        "timing": {
            "repeat": {
                "frequency": 1,
                "period": 1,
                "periodUnit": "d"
            }
        },
        "doseAndRate": [{
            "type": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/dose-rate-type",
                    "code": "ordered",
                    "display": "Ordered"
                }]
            },
            "doseQuantity": {
                "value": 5,
                "unit": "mg",
                "system": "http://unitsofmeasure.org",
                "code": "mg"
            }
        }]
    }]
)

# Ramipril 2,5mg täglich
medication_ramipril = MedicationStatement(
    id="med-4",
    status="active",
    medicationCodeableConcept={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "386872004",
            "display": "Ramipril"
        }]
    },
    subject={"reference": "Patient/pat-1"},
    dosage=[{
        "timing": {
            "repeat": {
                "frequency": 1,
                "period": 1,
                "periodUnit": "d"
            }
        },
        "doseAndRate": [{
            "type": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/dose-rate-type",
                    "code": "ordered",
                    "display": "Ordered"
                }]
            },
            "doseQuantity": {
                "value": 2.5,
                "unit": "mg",
                "system": "http://unitsofmeasure.org",
                "code": "mg"
            }
        }]
    }]
)

bundle = Bundle(
    type = "collection",
    entry=[
        BundleEntry(resource=patient),
        BundleEntry(resource=condition_coronary),
        BundleEntry(resource=condition_hypertension),
        BundleEntry(resource=condition_chest_pain),
        BundleEntry(resource=condition_dyspnoe),
        BundleEntry(resource=medication_aspirin),
        BundleEntry(resource=medication_clopidogrel),
        BundleEntry(resource=medication_bisoprolol),
        BundleEntry(resource=medication_ramipril),
    ]
)

print(bundle.json(indent=2))
# Verify with:
# $> echo "$(python3 data/synthetic_gt/05.py)" | curl -X POST -H "Content-Type: application/fhir+json" -d @- http://hapi.fhir.org/baseR4/Bundle