import os
import getpass

from smolagents import CodeAgent, ToolCallingAgent, HfApiModel, TransformersModel, tool, LiteLLMModel

from infherno.smolagents.fhiragent import FHIRAgent
from infherno.smolagents.smolcodesearch import search_for_code_or_coding
from infherno.tools.fhircodes.instance import GenericSnomedInstance
from infherno.tools.fhircodes.codings import listSupportedCodings, getValueSet, ValueSetLoader
from infherno.tools.fhircodes.codings import listSupportedCodings
from infherno.utils import determine_device
from infherno.defaults import determine_snowstorm_url, determine_snowstorm_branch
from infherno.smolagents.academiccloud.model import AcademicCloudModel
from infherno.smolagents.academiccloud.auth import AcademicAuth, AcademicUniAugsburgCredentialsFlow
SNOMED_INSTANCE = GenericSnomedInstance(determine_snowstorm_url(), branch=determine_snowstorm_branch())

MAX_COUNT_NOSEARCH = 10 # If <=10, just paste all results in the chat
MAX_SEARCH_RESULTS = 10 # If >10, only show 10 results (truncated)

# Choose which LLM engine to use!
# model = HfApiModel()
# model = TransformersModel(model_id="meta-llama/Llama-3.2-2B-Instruct")

# For anthropic: change model_id below to 'anthropic/claude-3-5-sonnet-20240620'
# model = LiteLLMModel(model_id="gpt-4o")

# Or just stick to the HF model
# model = TransformersModel(
#     model_id="meta-llama/Llama-3.1-8B-Instruct",
#     #model_id="Qwen/Qwen2.5-7B-Instruct",
#     #model_id="Qwen/Qwen2.5-14B-Instruct",
#     #model_id="google/gemma-3-12b-it",
#     #model_id="meta-llama/Llama-4-Maverick-17B-128E-Instruct",
#     #model_id="bartowski/Llama-3.3-70B-Instruct-GGUF",
#     max_new_tokens=32000,
# )

model = AcademicCloudModel(
    #model_id="meta-llama-3.1-8b-instruct",
    #model_id="llama-4-scout-17b-16e-instruct",
    model_id="llama-3.3-70b-instruct",
    openidc_session_cookie=AcademicAuth().authenticate(
        AcademicUniAugsburgCredentialsFlow(
            username=input("UAux Academic username: "),
            password=getpass.getpass(prompt="UAux Academic password: "),
        )
    ),
)

# Ollama model
# model = LiteLLMModel(
#     #model_id="ollama/gemma3:12b",
#     model_id="ollama/llama3.3:70b-instruct-q4_K_M",
#     num_ctx=131072, # 128k context
#     api_key="ollama",
#     api_base=os.environ.get("OLLAMA_ENDPOINT", "http://localhost:11434")
# )

agent = FHIRAgent(
    tools=[
        search_for_code_or_coding,
    ],
    model=model,
    verbosity_level=2
)

result = agent.run("""
The input text is as follows:
```
Magenbeschwerden seit 2 Tagen, Übelkeit, Erbrechen, kein Durchfall.
Patient hat eine Allergie gegen Penicillin, keine weiteren Allergien bekannt.
```
"""
)
