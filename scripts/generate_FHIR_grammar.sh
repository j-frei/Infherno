#!/usr/bin/env bash
cd "$(dirname "$0")"

set -e

# Move into the cache dir
REPO_DIR="$(pwd)/.."
GRAMMAR_DIR="$REPO_DIR/grammar"
mkdir -p "$GRAMMAR_DIR"

# Generate the FHIR JSON schema for the resources Patient, MedicationStatement and Condition
echo "Generating FHIR JSON schema..."
python3 schema/fhir_json_schema.py \
    --root-resources \
        "Patient" \
        "Encounter" \
        "Procedure" \
        "Condition" \
        "MedicationStatement" \
        `# "Organization" "Practitioner" "Observation"` \
    --blocked-types \
        'Meta' '.*Extension.*' 'Attachment' 'Annotation' \
    --blocked-properties \
        '^\_.*' "extension" "fhir_comments" "renderedDosageInstruction" \
        "contained" "text" "modifierExtension" "meta" "language" "id" "implicitRules" \
    --blocked-str-formats "binary" \
    --replace-property-names 'resource_type->resourceType' \
    --output "$GRAMMAR_DIR/fhir_schema.raw.json"

echo "Filtering the schema..."
./schema_filter.sh "$GRAMMAR_DIR/fhir_schema.raw.json" "$GRAMMAR_DIR/fhir_schema.json"

# Translate the schema into a BNF grammar
echo "Generating FHIR GBNF grammar..."
python3 schema/json_schema_to_grammar.py \
    "$GRAMMAR_DIR/fhir_schema.json" \
    > "$GRAMMAR_DIR/fhir_grammar.gbnf"

echo "Add empty space to the space rule in the grammar... (required for XGrammar)"
sed 's/space ::= | " "/space ::= "" | " "/g' "$GRAMMAR_DIR/fhir_grammar.gbnf" > "$GRAMMAR_DIR/fhir_grammar_xgrammar.gbnf"

# Convert the BNF grammar into an EBNF grammar
echo "Converting into FHIR EBNF grammar... (Outlines)"
python3 grammar/bnf_to_ebnf.py \
    "$GRAMMAR_DIR/fhir_grammar.gbnf" \
    "$GRAMMAR_DIR/fhir_grammar.ebnf"

# Done :)
echo "FHIR grammar generated successfully. For Outlines, use the file: fhir_grammar.ebnf"