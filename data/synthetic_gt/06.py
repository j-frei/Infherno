from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.medicationstatement import MedicationStatement
# Bundle
from fhir.resources.R4B.bundle import Bundle, BundleEntry
# HumanName
from fhir.resources.R4B.humanname import HumanName

notes = """
- Frau Uta Herz, geb 09.12.1991
- Akute Bauchschmerzen im rechten Unterbauch
- Übelkeit, leichtes Fieber
- Aktue Appendizitis (resolved)
- Antibiotika regelmäßig
"""

patient = Patient(
    id="pat-1",
    name=[HumanName(family="Herz", given=["Uta"])],
    birthDate="1991-12-09",
    gender="female",
)

# Akute Bauchschmerzen im rechten Unterbauch
condition_abdominal_pain = Condition(
    id="cond-1",
    # clinicalStatus unbekannt, vermutlich zwar resolved, aber nicht explizit erwähnt
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
            "display": "Abdominal pain"
        }]
    },
    subject={"reference": "Patient/pat-1"},
    bodySite=[{
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "48544008",
            "display": "Structure of right lower quadrant of abdomen"
        }]
    }]
)

# Übelkeit
condition_nausea = Condition(
    id="cond-2",
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
    subject={"reference": "Patient/pat-1"}
)

# Leichtes Fieber
condition_fever = Condition(
    id="cond-3",
    # clinicalStatus unbekannt...
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
            "code": "386661006",
            "display": "Fever"
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

# Akute Appendizitis (resolved)
condition_appendicitis = Condition(
    id="cond-4",
    clinicalStatus={
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
            "code": "resolved",
            "display": "Resolved"
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
            "code": "85189001",
            "display": "Acute appendicitis"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

# Antibiotika regelmäßig
medication_antibiotic = MedicationStatement(
    id="med-4",
    status="active",
    medicationCodeableConcept={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "419241000",
            "display": "Antibacterial"
        }]
    },
    # or via additionalInstruction -> SNOMEDCT@418577003???
    dosage={
        "text": "regelmäßig"
    },
    subject={"reference": "Patient/pat-1"}
)

bundle = Bundle(
    type = "collection",
    entry=[
        BundleEntry(resource=patient),
        BundleEntry(resource=condition_abdominal_pain),
        BundleEntry(resource=condition_nausea),
        BundleEntry(resource=condition_fever),
        BundleEntry(resource=condition_appendicitis),
        BundleEntry(resource=medication_antibiotic)
    ]
)

print(bundle.json(indent=2))
# Verify with:
# $> echo "$(python3 data/synthetic_gt/06.py)" | curl -X POST -H "Content-Type: application/fhir+json" -d @- http://hapi.fhir.org/baseR4/Bundle