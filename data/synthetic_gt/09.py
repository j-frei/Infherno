from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.medicationstatement import MedicationStatement
# Bundle
from fhir.resources.R4B.bundle import Bundle, BundleEntry
# HumanName
from fhir.resources.R4B.humanname import HumanName

notes = """
- Frau Ute Traugott, 14.05.1978
- Schmerzen im linken Knie bei Sport
- Schwellung, Instabilitätsgefühl im Knie (Basissymptome)
- Untersuchung: Schwellung und Druckschmerzhaftigkeit (Observation)
- Patellofemoralgelenksathrose (Verdacht)
- Entzündungshemmende Medikamente
"""

patient = Patient(
    id="pat-1",
    name=[HumanName(family="Traugott", given=["Ute"])],
    birthDate="1978-05-14",
    gender="female",
)

# Kniebeschwerden (linkes Knie)
condition_knee_pain = Condition(
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
            "code": "1003722009",
            "display": "Pain of knee region"
        }]
    },
    bodySite=[{
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "82169009",
            "display": "Structure of left knee region"
        }]
    }]
)

# Patellofemoralgelenksathrose (Verdacht)
condition_patellofemoral_osteoarthritis = Condition(
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
            "code": "provisional",
            "display": "Provisional"
        }]
    },
    subject={"reference": "Patient/pat-1"},
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "450521003",
            "display": "Patellofemoral osteoarthritis"
        }]
    }
)

# Entzündungshemmende Medikamente
medication_antiinflammatory = MedicationStatement(
    id="med-1",
    status="active",
    medicationCodeableConcept={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "372665008",
            "display": "Non-steroidal anti-inflammatory agent"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)


bundle = Bundle(
    type = "collection",
    entry=[
        BundleEntry(resource=patient),
        BundleEntry(resource=condition_knee_pain),
        BundleEntry(resource=condition_patellofemoral_osteoarthritis),
        BundleEntry(resource=medication_antiinflammatory)
    ]
)

print(bundle.json(indent=2))
# Verify with:
# $> echo "$(python3 data/synthetic_gt/09.py)" | curl -X POST -H "Content-Type: application/fhir+json" -d @- http://hapi.fhir.org/baseR4/Bundle