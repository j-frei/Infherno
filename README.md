---  
title: Infherno  
emoji: 🔥  
colorFrom: yellow  
colorTo: red  
sdk: gradio  
sdk_version: 5.0.1  
app_file: app.py  
pinned: false  
---

# 🔥 Infherno

Infherno is an end-to-end agent that transforms unstructured clinical notes into structured FHIR (Fast Healthcare Interoperability Resources) format. It automates the parsing and mapping of free-text medical documentation into standardized FHIR resources, enabling interoperability across healthcare systems.

<p align="center">
  <img src="assets/overview.png" height="350">
</p>

Built on Hugging Face’s SmolAgents library, Infherno supports multi-step reasoning, tool use, and modular extensibility for complex clinical information extraction.

Infherno also provides ontology support for SNOMED CT and HL7 ValueSets using Retrieval-Augmented Generation (RAG). This allows the agent to ground extracted medical concepts in standardized terminologies, ensuring semantic consistency and accurate coding in line with clinical data standards.

## Live Demo

**Gradio Demo Video**: [See the clip here](https://myweb.rz.uni-augsburg.de/~freijoha/Infherno_Gradio_Demo.mp4).  
Our Gradio demo is accessible via [Hugging Face Spaces](https://huggingface.co/spaces/nfel/infherno).  
Due to resource and context limitations with open-source models, we recommend launching Infherno locally with a proprietary model via API.


## Run Infherno locally

Install the dependencies first.

```bash
python3 -m venv env
source env/bin/activate

python3 -m pip install -r requirements.txt
```

Run the Infherno agent as follows:
```bash
# Define self-hosted Snowstorm instance
export SNOWSTORM_URL="http://<SNOMED-Instance>"

# Set Ollama endpoint
export OLLAMA_ENDPOINT="http://127.0.0.1:11434"

# Define custom open-weights model from Ollama to be used.
# MAKE SURE THAT THE MODEL IS ALREADY PULLED!
cat > local_config.py <<EOF
MODEL_ID = "ollama_chat/deepseek-r1:32b"
EOF

# Run the agent with dummy data
PYTHONPATH=. python3 infherno/smol_fhiragent.py

# Check the results in the logs:
cat logs/*.log
```
