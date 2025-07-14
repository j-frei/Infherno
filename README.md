# Infherno

## How to Use

Install the dependencies first.

```bash
python3 -m venv env
source env/bin/activate

python3 -m pip install -r requirements.txt
```

### Smolagent

Run the Infherno agent as follows:
```bash
# Define custom Ollama model to be used
# MAKE SURE THAT THE MODEL IS ALREADY PULLED!
cat > local_config.py <<EOF
MODEL_ID = "ollama_chat/deepseek:70b"
EOF

# Define self-hosted Snowstorm instance
export SNOWSTORM_URL="http://<SNOMED-Instance>"

# Set Ollama endpoint
export OLLAMA_ENDPOINT="http://127.0.0.1:11434"

# Run the agent with dummy data
PYTHONPATH=. python3 infherno/smol_fhiragent.py

# Check the results in the logs:
ls logs/*.log
```

## Live Demo

Our Gradio demo will be accessible via [Hugging Face Spaces](https://huggingface.co/spaces/nfel/infherno) very shortly.
However, due to resource and context limitations with open-source models, we recommend launching Infherno locally with a proprietary model via API.
