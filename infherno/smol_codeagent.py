import json

# from smolagents.agents import ToolCallingAgent
from smolagents import CodeAgent, ToolCallingAgent, HfApiModel, TransformersModel, tool

from infherno.tools.fhircodes.instance import GenericSnomedInstance
from infherno.tools.fhircodes.codings import listSupportedCodings, getValueSet, ValueSetLoader
from infherno.tools.fhircodes.codings import _CODINGS
from infherno.utils import determine_device
from infherno.defaults import determine_snowstorm_url, determine_snowstorm_branch
from infherno.smolagents_utils.smoltext2fhir import create_text2fhir_agent

# Or just stick to the HF model
model = TransformersModel(
    model_id="meta-llama/Llama-3.1-8B-Instruct",
    #model_id="Qwen/Qwen2.5-VL-7B-Instruct",
    max_new_tokens=32000,
)

agent = create_text2fhir_agent(model)

agent.run("""
Translate the input text into a set of FHIR resources.

Plan ahead which mentions should be looked up.
Plan ahead which FHIR resources are needed and which properties need to be set.

Eventually compose a FHIR Bundle that contains all resources.
Make sure to use the FHIR Code Search Agent tool to determine the actual codes present in HL7 ValueSets or SNOMED CT ontologies, mentioning the search item and the intent to search for the code for a certain FHIR property (e.g. Condition.code).

FHIR Resource objects can be instantiated using the fhir.resources library and imported as follows.
```python
from fhir.resources.bundle import Bundle
from fhir.resources.patient import Patient
```

The input text is as follows:
```
Magenbeschwerden seit 2 Tagen, Übelkeit, Erbrechen, kein Durchfall.
Patient hat eine Allergie gegen Penicillin, keine weiteren Allergien bekannt.
```
"""
)
