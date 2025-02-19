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
Update the `GenericSnomedInstance("http://snowstorm-uk.misit-augsburg.de", branch="MAIN/2023-08-30", branch_encode=False)` codes to an accessible Snowstorm instance in `infherno/codesearch.py`.

Run the code search demo: `PYTHONPATH=. python3 infherno/codesearch.py`.

### Text2FHIR

Update the `GenericSnomedInstance("http://snowstorm-uk.misit-augsburg.de", branch="MAIN/2023-08-30", branch_encode=False)` codes to an accessible Snowstorm instance in `infherno/codesearch.py`.

Update the input text in `infherno/text2fhir.py`.
Run the Text2FHIR code: `PYTHONPATH=. python3 infherno/text2fhir.py`.