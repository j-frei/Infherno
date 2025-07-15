from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.medicationstatement import MedicationStatement
# Bundle
from fhir.resources.R4B.bundle import Bundle, BundleEntry
# HumanName
from fhir.resources.R4B.humanname import HumanName

notes = """
- Uwe Jaeger, geboren 10.02.1975
  -> birthDate, Name, Geschlecht
- Beschwerden im Magen-Darm-Bereich
- starke Bauchschmerzen, Übelkeit, Erbrechen und Gewichtsverlust
- Herr Jaeger ist Nichtraucher und konsumiert keinen Alkohol.
- allgemeine Schwäche und ein mäßig abgeschwächter Allgemeinzustand. Der Bauch war diffus druckempfindlich
- Blutuntersuchung ergab eine erhöhte Anzahl weißer Blutkörperchen und eine leichte Anämie.
- erosive Gastritis
- Protonenpumpenhemmer (PPI) für acht Wochen,
- Antazidum
"""

patient = Patient(
    id="pat-1",
    name=[HumanName(family="Jaeger", given=["Uwe"])],
    birthDate="1975-02-10",
    gender="male"
)

# Gastritis
condition_gastritis = Condition(
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
    subject={"reference": "Patient/pat-1"},
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "1086791000119100",
            "display": "Erosive gastritis (disorder)"
        }]
    }
)

# Nichtraucher
condition_nonsmoker = Condition(
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
            "code": "8392000",
            "display": "Non-smoker (finding)"
        }]
    },
    subject={"reference": "Patient/pat-1"},
)

condition_noalcohol = Condition(
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
            "code": "105542008",
            "display": "Non-drinker (finding)"
        }]
    },
    subject={"reference": "Patient/pat-1"},
)

condition_anemia = Condition(
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
            "code": "271737000",
            "display": "Anemia (disorder)"
        }]
    },
    severity={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "255604002",
            "display": "Mild"
        }]
    },
    subject={"reference": "Patient/pat-1"},
)

medication_ppi = MedicationStatement(
    id="med-1",
    status="active",
    subject={"reference": "Patient/pat-1"},
    medicationCodeableConcept={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "372525000",
            "display": "Proton pump inhibitor"
        }]
    },
    dosage=[{
        "timing": {
            "repeat": {
                "duration": 8,
                "durationUnit": "wk",
            }

        }
    }]
    # ReasonReference wäre ggf. auf "Magensäureproduktion zu reduzieren" bezogen?
    # Aber einiges davon wäre eine Observation, und keine Condition.
)

medication_adantacid = MedicationStatement(
    id="med-2",
    status="active",
    subject={"reference": "Patient/pat-1"},
    medicationCodeableConcept={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "372794006",
            "display": "Antacid"
        }]
    }
    # Keine Dosierung, unklare Dauer
    # ReasonReference ist etwas unklar/unspezifisch zum Codieren
)

condition_abdominalpain = Condition(
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
            "code": "21522001",
            "display": "Abdominal pain (finding)"
        }]
    },
    subject={"reference": "Patient/pat-1"},
    severity={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "24484000",
            "display": "Severe"
        }]
    }
)

condition_nausea = Condition(
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
            "code": "422587007",
            "display": "Nausea (finding)"
        }]
    },
    subject={"reference": "Patient/pat-1"},
)

condition_vomiting = Condition(
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
            "code": "unconfirmed",
            "display": "Unconfirmed"
        }]
    },
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "422587007",
            "display": "Vomiting"
        }]
    },
    subject={"reference": "Patient/pat-1"},
)

condition_weightloss = Condition(
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
            "code": "unconfirmed",
            "display": "Unconfirmed"
        }]
    },
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "89362005",
            "display": "Weight loss"
        }]
    },
    subject={"reference": "Patient/pat-1"},
)

condition_weakness = Condition(
    id="cond-9",
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
            "code": "13791008",
            "display": "Asthenia (finding)"
        }]
    },
    subject={"reference": "Patient/pat-1"},
)

# Diffus druckempfindlicher Bauch -> Unklar zu encodieren?
# Allgemein abgeschwächter Allgemeinzustand -> Redundant zu "allgemeiner Schwäche"?

bundle = Bundle(
    type = "collection",
    entry=[
        BundleEntry(resource=patient),
        BundleEntry(resource=condition_gastritis),
        BundleEntry(resource=condition_nonsmoker), # Gehört das in Condition?!
        BundleEntry(resource=condition_noalcohol), # Gehört das in Condition?!
        BundleEntry(resource=condition_anemia),
        BundleEntry(resource=medication_ppi),
        BundleEntry(resource=medication_adantacid),
        BundleEntry(resource=condition_abdominalpain),
        BundleEntry(resource=condition_nausea),
        BundleEntry(resource=condition_vomiting),
        BundleEntry(resource=condition_weightloss),
        BundleEntry(resource=condition_weakness),
    ]
)

print(bundle.json(indent=2))
# Verify with:
# $> echo "$(python3 data/synthetic_gt/01.py)" | curl -X POST -H "Content-Type: application/fhir+json" -d @- http://hapi.fhir.org/baseR4/Bundle