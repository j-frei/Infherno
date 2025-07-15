from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.medicationstatement import MedicationStatement
# Bundle
from fhir.resources.R4B.bundle import Bundle, BundleEntry
# HumanName
from fhir.resources.R4B.humanname import HumanName

notes = """
- Frau Christine Bürger, 12.3.1985 geboren
- Symptome seit drei Tagen: Fieber, Halsschmerzen, Unwohlsein
- leichte Rötung des Rachens, vergrößerte Halslymphknoten
- Körpertemperatur 38,5 °C (ist aber eig. eher Observation)
- Vorläufige Diagnose: virale Pharyngitis oder Infektion mit tropischen Erregern
- Paracetamol 500mg – Bei Bedarf zur Fiebersenkung, maximal 3x täglich
- Ibuprofen 400mg – Bei Bedarf zur Schmerzlinderung, maximal 3x täglich
"""

patient = Patient(
    id="pat-1",
    name=[HumanName(family="Bürger", given=["Christine"])],
    birthDate="1985-03-12",
    gender="female",
)

# Fieber
condition_fever = Condition(
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
            "code": "386661006",
            "display": "Fever"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

# Halsschmerzen
condition_paininthroat = Condition(
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
            "code": "162397003",
            "display": "Pain in throat"
        }]
    },
    subject={"reference": "Patient/pat-1"},
)

# Allgemeines Unwohlsein
condition_generaldiscomfort = Condition(
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
            "code": "213257006",
            "display": "Generally unwell"
        }]
    },
    subject={"reference": "Patient/pat-1"},
)

# Rötung des Rachens
condition_throatredness = Condition(
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
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "126662008",
            "display": "Redness of throat"
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

condition_lymphadenopathy = Condition(
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
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "30746006",
            "display": "Lymphadenopathy"
        }]
    },
    subject={"reference": "Patient/pat-1"},
    bodySite=[{
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "81105003",
            "display": "Cervical lymph node structure"
        }]
    }]
)

condition_pharyngitis = Condition(
    id="cond-6",
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
            "code": "1532007",
            "display": "Viral pharyngitis"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

# Tropical infection ist zu unspezifisch


medication_pracetamol = MedicationStatement(
    id="med-1",
    status="active",
    subject={"reference": "Patient/pat-1"},
    medicationCodeableConcept={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "387517004",
            "display": "Paracetamol"
        }]
    },
    dosage=[{
        "asNeededBoolean": True,
        "doseAndRate": [{
            "type": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/dose-rate-type",
                    "code": "ordered",
                    "display": "Ordered"
                }]
            },
            "doseQuantity": {
                "value": 500,
                "unit": "mg",
                "system": "http://unitsofmeasure.org",
                "code": "mg"
            }
        }],
        "maxDosePerPeriod": {
            "numerator": {
                "value": 3,
            },
            "denominator": {
                "value": 1,
                "system": "http://unitsofmeasure.org",
                "code": "d"
            }
        }
    }]
)

medication_ibuprofen = MedicationStatement(
    id="med-2",
    status="active",
    subject={"reference": "Patient/pat-1"},
    medicationCodeableConcept={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "387207008",
            "display": "Ibuprofen"
        }]
    },
    dosage=[{
        "asNeededBoolean": True,
        "doseAndRate": [{
            "type": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/dose-rate-type",
                    "code": "ordered",
                    "display": "Ordered"
                }]
            },
            "doseQuantity": {
                "value": 400,
                "unit": "mg",
                "system": "http://unitsofmeasure.org",
                "code": "mg"
            }
        }],
        "maxDosePerPeriod": {
            "numerator": {
                "value": 3,
            },
            "denominator": {
                "value": 1,
                "system": "http://unitsofmeasure.org",
                "code": "d"
            }
        }
    }]
)

bundle = Bundle(
    type = "collection",
    entry=[
        BundleEntry(resource=patient),
        BundleEntry(resource=condition_fever),
        BundleEntry(resource=condition_paininthroat),
        BundleEntry(resource=condition_generaldiscomfort),
        BundleEntry(resource=condition_throatredness),
        BundleEntry(resource=condition_lymphadenopathy),
        BundleEntry(resource=condition_pharyngitis),
        BundleEntry(resource=medication_pracetamol),
        BundleEntry(resource=medication_ibuprofen),
    ]
)

print(bundle.json(indent=2))
# Verify with:
# $> echo "$(python3 data/synthetic_gt/02.py)" | curl -X POST -H "Content-Type: application/fhir+json" -d @- http://hapi.fhir.org/baseR4/Bundle