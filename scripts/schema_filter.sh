#!/usr/bin/env bash

SCHEMA_PATH_IN="$1"
SCHEMA_PATH_OUT="$2"

echo "Filtering the schema... $SCHEMA_PATH_IN -> $SCHEMA_PATH_OUT"

# Copy the input schema to the output schema
cp "$SCHEMA_PATH_IN" "$SCHEMA_PATH_OUT"

# Patient
echo "[Patient] Remove the 'photo' property"
jq 'del(."$defs".Patient.properties.photo)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Patient] Remove the 'contact' property"
jq 'del(."$defs".Patient.properties.contact)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Patient] Remove the 'communication' property"
jq 'del(."$defs".Patient.properties.communication)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Patient] Remove the 'generalPractitioner' property"
jq 'del(."$defs".Patient.properties.generalPractitioner)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Patient] Remove the 'managingOrganization' property"
jq 'del(."$defs".Patient.properties.managingOrganization)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Patient] Remove the 'link' property"
jq 'del(."$defs".Patient.properties.link)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

# Encounter
echo "[Encounter] Remove the 'class' property"
jq 'del(."$defs".Encounter.properties.class)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'priority' property"
jq 'del(."$defs".Encounter.properties.priority)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'type' property"
jq 'del(."$defs".Encounter.properties.type)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'serviceType' property"
jq 'del(."$defs".Encounter.properties.serviceType)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'subjectStatus' property"
jq 'del(."$defs".Encounter.properties.subjectStatus)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'episodeOfCare' property"
jq 'del(."$defs".Encounter.properties.episodeOfCare)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'basedOn' property"
jq 'del(."$defs".Encounter.properties.basedOn)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'careTeam' property"
jq 'del(."$defs".Encounter.properties.careTeam)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'partOf' property"
jq 'del(."$defs".Encounter.properties.partOf)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'serviceProvider' property"
jq 'del(."$defs".Encounter.properties.serviceProvider)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'participant' property"
jq 'del(."$defs".Encounter.properties.participant)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[EncounterParticipant] Remove the 'type' property"
jq 'del(."$defs".EncounterParticipant.properties.type)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'appointment' property"
jq 'del(."$defs".Encounter.properties.appointment)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'virtualService' property"
jq 'del(."$defs".Encounter.properties.virtualService)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'reason' property"
jq 'del(."$defs".Encounter.properties.reason)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'diagnosis' property"
jq 'del(."$defs".Encounter.properties.diagnosis)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'account' property"
jq 'del(."$defs".Encounter.properties.account)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'dietPreference' property"
jq 'del(."$defs".Encounter.properties.dietPreference)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'specialArrangement' property"
jq 'del(."$defs".Encounter.properties.specialArrangement)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'specialCourtesy' property"
jq 'del(."$defs".Encounter.properties.specialCourtesy)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'admission' property"
jq 'del(."$defs".Encounter.properties.admission)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Encounter] Remove the 'location' property"
jq 'del(."$defs".Encounter.properties.location)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

# Procedure
echo "[Procedure] Remove the 'instantiatesCanonical' property"
jq 'del(."$defs".Procedure.properties.instantiatesCanonical)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Procedure] Remove the 'instantiatesUri' property"
jq 'del(."$defs".Procedure.properties.instantiatesUri)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Procedure] Remove the 'basedOn' property"
jq 'del(."$defs".Procedure.properties.basedOn)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Procedure] Remove the 'partOf' property"
jq 'del(."$defs".Procedure.properties.partOf)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Procedure] Remove the 'focus' property"
jq 'del(."$defs".Procedure.properties.focus)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Procedure] Remove the 'recorded' property"
jq 'del(."$defs".Procedure.properties.recorded)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Procedure] Remove the 'recorder' property"
jq 'del(."$defs".Procedure.properties.recorder)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Procedure] Remove the 'reported' property"
jq 'del(."$defs".Procedure.properties.reported)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Procedure] Remove the 'performer' property"
jq 'del(."$defs".Procedure.properties.performer)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Procedure] Remove the 'location' property"
jq 'del(."$defs".Procedure.properties.location)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Procedure] Remove the 'report' property"
jq 'del(."$defs".Procedure.properties.report)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Procedure] Remove the 'note' property"
jq 'del(."$defs".Procedure.properties.note)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Procedure] Remove the 'focalDevice' property"
jq 'del(."$defs".Procedure.properties.focalDevice)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Procedure] Remove the 'used' property"
jq 'del(."$defs".Procedure.properties.used)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Procedure] Remove the 'supportingInfo' property"
jq 'del(."$defs".Procedure.properties.supportingInfo)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

# Condition
echo "[Condition] Remove the 'category' property"
jq 'del(."$defs".Condition.properties.category)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Condition] Remove the abatement' property"
jq 'del(."$defs".Condition.properties.abatement)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Condition] Remove the 'recordedDate' property"
jq 'del(."$defs".Condition.properties.recordedDate)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Condition] Remove the 'participant' property"
jq 'del(."$defs".Condition.properties.participant)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Condition] Remove the 'stage' property"
jq 'del(."$defs".Condition.properties.stage)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Condition] Remove the 'note' property"
jq 'del(."$defs".Condition.properties.note)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

# MedicationStatement
echo "[MedicationStatement] Remove the 'partOf' property"
jq 'del(."$defs".MedicationStatement.properties.partOf)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[MedicationStatement] Remove the 'dateAsserted' property"
jq 'del(."$defs".MedicationStatement.properties.dateAsserted)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[MedicationStatement] Remove the 'informationSource' property"
jq 'del(."$defs".MedicationStatement.properties.informationSource)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[MedicationStatement] Remove the 'derivedFrom' property"
jq 'del(."$defs".MedicationStatement.properties.derivedFrom)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[MedicationStatement] Remove the 'note' property"
jq 'del(."$defs".MedicationStatement.properties.note)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[MedicationStatement] Remove the 'relatedClinicalInformation' property"
jq 'del(."$defs".MedicationStatement.properties.relatedClinicalInformation)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[MedicationStatement] Remove the 'renderedDosageInstruction' property"
jq 'del(."$defs".MedicationStatement.properties.renderedDosageInstruction)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"

echo "[Dosage] Remove the 'additionalInstruction' property"
jq 'del(."$defs".Dosage.properties.additionalInstruction)' "$SCHEMA_PATH_OUT" > "$SCHEMA_PATH_OUT".tmp && mv "$SCHEMA_PATH_OUT".tmp "$SCHEMA_PATH_OUT"
