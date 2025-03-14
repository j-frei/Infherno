# Infherno

## How to Use

Install the dependencies first.

```bash
python3 -m venv env
source env/bin/activate

python3 -m pip install -r requirements.txt
```

### Generate FHIR Grammar

The FHIR grammar in Outlines' EBNF format can be generated with `./scripts/generate_FHIR_grammar.sh`.

### Outlines Basic Demo

Run the demo using `PYTHONPATH=./scripts python3 scripts/outlines_demo.py`.

### XGrammar Basic Demo

Run the demo using `PYTHONPATH=./scripts python3 scripts/xgrammar_demo.py`.

### Code Search
```
# Set the Snowstorm Instance via ENV
export SNOWSTORM_URL="http://snowstorm-uk.misit-augsburg.de"
# If needed, set the branch as well
# export SNOWSTORM_BRANCH="MAIN/2025-03-01"
# otherwise, it will query the SNOWSTORM instance and take the first branch.

# Run the code search demo
PYTHONPATH=. python3 infherno/codesearch.py
```

### Text2FHIR
```
# Set the Snowstorm Instance via ENV
export SNOWSTORM_URL="http://snowstorm-uk.misit-augsburg.de"
# If needed, set the branch as well
# export SNOWSTORM_BRANCH="MAIN/2025-03-01"
# otherwise, it will query the SNOWSTORM instance and take the first branch.

# Update the input text:
nano infherno/text2fhir.py

# Run the Text2FHIR code
PYTHONPATH=. python3 infherno/text2fhir.py
```

