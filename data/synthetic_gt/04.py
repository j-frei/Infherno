from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.medicationstatement import MedicationStatement
# Bundle
from fhir.resources.R4B.bundle import Bundle, BundleEntry
# HumanName
from fhir.resources.R4B.humanname import HumanName

notes = """
- Herr Alexander Wechsler, geboren 24.06.1960
- Beschwerden im Bereich des Herzens (zu unspezifisch)
- Atemnot und Müdigkeit
- koronare Herzerkrankung und eine Hypertonie
- Raucher und führt einen sitzenden Lebensstil.
- Anzeichen einer linksventrikulären Hypertrophie.
- stabile Angina pectoris, eine Hypertonie sowie eine linksventrikuläre Hypertrophie
- Ramipril, Metoprolol, Nitroglycerin

- Der Blutdruck hat sich auf durchschnittlich 130/80 mmHg normalisiert
- leichte Rückbildung der linksventrikulären Hypertrophie.
"""

patient = Patient(
    id="pat-1",
    name=[HumanName(family="Wechsler", given=["Alexander"])],
    birthDate="1960-06-24",
    gender="male",
)

# Atemnot
condition_dyspnoe = Condition(
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
            "code": "unconformed",
            "display": "Unconfirmed"
        }]
    },
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "404684003",
            "display": "Dyspnoe"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

# Müdigkeit
condition_fatigue = Condition(
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
            "code": "84229001",
            "display": "Fatigue"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

# Koronare Herzerkrankung
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
            "code": "unconfirmed",
            "display": "Unconfirmed"
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

# Hypertonie (eigentlich aber Observation)
condition_hypertension_minor = Condition(
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
            "code": "38341003",
            "display": "Hypertension"
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

# Raucher
condition_smoker = Condition(
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
            "code": "unconfirmed",
            "display": "Unconfirmed"
        }]
    },
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "77176002",
            "display": "Smoker (finding)"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

# Sitzender Lebensstil
condition_sedentary = Condition(
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
            "code": "unconfirmed",
            "display": "Unconfirmed"
        }]
    },
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "415510005",
            "display": "Sedentary lifestyle"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

# linksventrikuläre Hypertrophie
condition_lvh = Condition(
    id="cond-7",
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
            "code": "55827005",
            "display": "Left ventricular hypertrophy"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

# Stabile Angina pectoris
condition_angina = Condition(
    id="cond-8",
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
            "code": "233819005",
            "display": "Stable angina"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

# Ramipril
medication_ramipril = MedicationStatement(
    id="med-1",
    status="active",
    medicationCodeableConcept={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "386872004",
            "display": "Ramipril"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

# Metoprolol
medication_metoprolol = MedicationStatement(
    id="med-2",
    status="active",
    medicationCodeableConcept={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "372826007",
            "display": "Metoprolol"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

# Nitroglycerin
medication_nitroglycerin = MedicationStatement(
    id="med-3",
    status="active",
    medicationCodeableConcept={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "387404004",
            "display": "Nitroglycerin"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)


bundle = Bundle(
    type = "collection",
    entry=[
        BundleEntry(resource=patient),
        BundleEntry(resource=condition_dyspnoe),
        BundleEntry(resource=condition_fatigue),
        BundleEntry(resource=condition_coronary),
        BundleEntry(resource=condition_hypertension_minor),
        BundleEntry(resource=condition_smoker),
        BundleEntry(resource=condition_sedentary),
        BundleEntry(resource=condition_lvh),
        BundleEntry(resource=condition_angina),
        BundleEntry(resource=medication_ramipril),
        BundleEntry(resource=medication_metoprolol),
        BundleEntry(resource=medication_nitroglycerin)
    ]
)

print(bundle.json(indent=2))
# Verify with:
# $> echo "$(python3 data/synthetic_gt/04.py)" | curl -X POST -H "Content-Type: application/fhir+json" -d @- http://hapi.fhir.org/baseR4/Bundle