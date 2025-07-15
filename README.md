---  
title: Infherno  
emoji: 🔥  
colorFrom: yellow  
colorTo: red  
sdk: gradio  
sdk_version: 5.0.1  
python_version: 3.10  
app_file: app.py  
pinned: false  
---

# 🔥 Infherno

Infherno is an end-to-end agent that transforms unstructured clinical notes into structured FHIR (Fast Healthcare Interoperability Resources) format. It automates the parsing and mapping of free-text medical documentation into standardized FHIR resources, enabling interoperability across healthcare systems.

Built on Hugging Face’s SmolAgents library, Infherno supports multi-step reasoning, tool use, and modular extensibility for complex clinical information extraction.

Infherno also provides ontology support for SNOMED CT and HL7 ValueSets using Retrieval-Augmented Generation (RAG). This allows the agent to ground extracted medical concepts in standardized terminologies, ensuring semantic consistency and accurate coding in line with clinical data standards.
