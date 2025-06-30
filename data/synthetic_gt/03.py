from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.medicationstatement import MedicationStatement
# Bundle
from fhir.resources.R4B.bundle import Bundle, BundleEntry
# HumanName
from fhir.resources.R4B.humanname import HumanName

notes = """
- Frau Lea Lange, 3.10.1971
- Starke Kopfschmerzen, vorwiegend im Stirnbereich.
- Übelkeit, Schwindel
- Linkes Auge: Sehschärfe eingeschränkt
- leichte Einschränkungen der Sensibilität auf der linken Gesichtshälfte.
- Pupillenreaktion beidseitig vorhanden, jedoch geringfügig verlangsamt auf der linken Seite.
- Vorläufig: Migräne mit Aura
"""

patient = Patient(
    id="pat-1",
    name=[HumanName(family="Lange", given=["Lea"])],
    birthDate="1971-10-03",
    gender="female",
)

# starke Kopfschmerzen, vorwiegend im Stirnbereich
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
            "code": "unconformed",
            "display": "Unconfirmed"
        }]
    },
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "25064002",
            "display": "Headache"
        }]
    },
    bodySite=[
        {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "52795006",
                "display": "Forehead structure",
            }]
        },
        {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "69536005",
                "display": "Head structure"
            }]
        },
    ],
    severity={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "24484000",
            "display": "Severe"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)

condition_nausea = Condition(
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
            "code": "422587007",
            "display": "Nausea (finding)"
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

# Schwindelgefühl
condition_dizziness = Condition(
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
            "code": "404640003",
            "display": "Dizziness (finding)"
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

# Eingeschränkte Sehschärfe im linken Auge
condition_leftvision = Condition(
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
            "code": "unconfirmed",
            "display": "Unconfirmed"
        }]
    },
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "13164000",
            "display": "Reduced visual acuity (finding)"
        }]
    },
    subject={"reference": "Patient/pat-1"},
    bodySite=[{
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "1290031003",
            "display": "Structure of left eye proper"
        }]
    }]
)

# leichte Einschränkungen der Sensibilität auf der linken Gesichtshälfte.
condition_leftfacial = Condition(
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
            "code": "425403003",
            "display": "Limited sensory perception"#
        }]
    },
    subject={"reference": "Patient/pat-1"},
    bodySite=[{
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "423781004",
            "display": "Structure of left half of face"
        }]
    }],
    severity={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "255604002",
            "display": "Mild"
        }]
    }
)

# Left pupil reaction is present but slightly delayed
condition_leftpupil = Condition(
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
            "code": "confirmed",
            "display": "Confirmed"
        }]
    },
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "301948009",
            "display": "Delayed pupil near reaction"
        }]
    },
    subject={"reference": "Patient/pat-1"},
    bodySite=[{
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "1290031003",
            "display": "Structure of left eye proper"
        }]
    }],
    severity={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "255604002",
            "display": "Mild"
        }]
    }
)

condition_migraine_aura = Condition(
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
            "code": "provisional",
            "display": "Provisional"
        }]
    },
    code={
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "4473006",
            "display": "Migraine with aura"
        }]
    },
    subject={"reference": "Patient/pat-1"}
)


bundle = Bundle(
    type = "collection",
    entry=[
        BundleEntry(resource=patient),
        BundleEntry(resource=condition_headache),
        BundleEntry(resource=condition_nausea),
        BundleEntry(resource=condition_dizziness),
        BundleEntry(resource=condition_leftvision),
        BundleEntry(resource=condition_leftfacial),
        BundleEntry(resource=condition_leftpupil),
        BundleEntry(resource=condition_migraine_aura),
    ]
)

print(bundle.json(indent=2))
# Verify with:
# $> echo "$(python3 data/synthetic_gt/03.py)" | curl -X POST -H "Content-Type: application/fhir+json" -d @- http://hapi.fhir.org/baseR4/Bundle