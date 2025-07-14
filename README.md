# Infherno

## How to Use

Install the dependencies first.

```bash
python3 -m venv env
source env/bin/activate

python3 -m pip install -r requirements.txt
```

#### Tests
Most tests rely on [NL-Augmenter](https://github.com/GEM-benchmark/NL-Augmenter).

1. Download glove into nlaugmenter folder: http://nlp.stanford.edu/data/glove.6B.zip
2. Install spaCy core model 
```bash
python -m spacy download en_core_web_sm
```

### Smolagent

Run the agent using `SNOWSTORM_URL="http://<SNOMED-Instance>" PYTHONPATH=. python3 infherno/smol_fhiragent.py`


## Live Demo

Our Gradio demo will be accessible via [Hugging Face Spaces](https://huggingface.co/spaces/nfel/infherno) very shortly.
However, due to resource and context limitations with open-source models, we recommend launching Infherno locally with a proprietary model via API.
