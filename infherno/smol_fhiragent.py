import json

# from smolagents.agents import ToolCallingAgent
from smolagents import CodeAgent, ToolCallingAgent, HfApiModel, TransformersModel, tool

from infherno.smolagents.fhiragent import FHIRAgent
from infherno.smolagents.smolcodesearch import search_for_code_or_coding
from infherno.tools.fhircodes.instance import GenericSnomedInstance
from infherno.tools.fhircodes.codings import listSupportedCodings, getValueSet, ValueSetLoader
from infherno.tools.fhircodes.codings import listSupportedCodings
from infherno.utils import determine_device
from infherno.defaults import determine_snowstorm_url, determine_snowstorm_branch
SNOMED_INSTANCE = GenericSnomedInstance(determine_snowstorm_url(), branch=determine_snowstorm_branch())

MAX_COUNT_NOSEARCH = 10 # If <=10, just paste all results in the chat
MAX_SEARCH_RESULTS = 10 # If >10, only show 10 results (truncated)

# Choose which LLM engine to use!
# model = HfApiModel()
# model = TransformersModel(model_id="meta-llama/Llama-3.2-2B-Instruct")

# For anthropic: change model_id below to 'anthropic/claude-3-5-sonnet-20240620'
# model = LiteLLMModel(model_id="gpt-4o")

# Or just stick to the HF model
model = TransformersModel(
    model_id="meta-llama/Llama-3.1-8B-Instruct",
    #model_id="Qwen/Qwen2.5-VL-7B-Instruct",
    max_new_tokens=32000,
)

agent = FHIRAgent(
    tools=[
        search_for_code_or_coding,
    ],
    model=model,
    verbosity_level=2
)

agent.run("""
The input text is as follows:
```
Magenbeschwerden seit 2 Tagen, Übelkeit, Erbrechen, kein Durchfall.
Patient hat eine Allergie gegen Penicillin, keine weiteren Allergien bekannt.
```
"""
)
