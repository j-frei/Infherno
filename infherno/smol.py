import json

# from smolagents.agents import ToolCallingAgent
from smolagents import CodeAgent, ToolCallingAgent, HfApiModel, TransformersModel, tool

from infherno.tools.fhircodes.instance import GenericSnomedInstance
from infherno.tools.fhircodes.codings import listSupportedCodings, getValueSet, ValueSetLoader
from infherno.tools.fhircodes.codings import listSupportedCodings
from infherno.utils import determine_device
from infherno.defaults import determine_snowstorm_url, determine_snowstorm_branch
SNOMED_INSTANCE = GenericSnomedInstance(determine_snowstorm_url(), branch=determine_snowstorm_branch(), branch_encode=False)

MAX_COUNT_NOSEARCH = 10 # If <=10, just paste all results in the chat
MAX_SEARCH_RESULTS = 10 # If >10, only show 10 results (truncated)

@tool
def search_for_code_or_coding(fhir_attribute_path: str, search_term: str) -> str:
    """
    Search for a code/coding in a FHIR ValueSet using the SNOMED CT or HL7 ValueSets.

    Args:
        fhir_attribute_path: The FHIR attribute path to search in (e.g., "Condition.code").
        search_term: The formal, English term to search for in the ValueSet (string-matching) in SNOMED CT or HL7 ValueSets.

    Returns:
        A string describing the search results.
    """
    if not fhir_attribute_path in listSupportedCodings():
        return f'Path "{fhir_attribute_path}" is not supported. Supported paths are: {json.dumps(listSupportedCodings())}'


    vs_info = getValueSet(fhir_attribute_path)
    vsl = ValueSetLoader.from_url(vs_info["vs"], store_threshold=20, snomed_instance=SNOMED_INSTANCE)
    try:
        # Search for term....
        if vsl.count() < MAX_COUNT_NOSEARCH:
            # Just show all results
            results = vsl.search("")
        else:
            # Search for term
            results = vsl.search(search_term, limit=MAX_SEARCH_RESULTS)

        # Render results
        if not results:
            return f'No results found for `{search_term}` in `{fhir_attribute_path}`'
        else:
            result_text = f'Results for `{search_term}` in `{fhir_attribute_path}`: '
            for resultItem in results:
                if vs_info["type"] == "coding":
                    # Coding / CodableConcept -> with system and display description
                    result_text += f'<Item><Coding>{resultItem["code"]}</Coding><System>{resultItem["system"]}</System><Display>{resultItem["description"]}</Display></Item>'
                elif vs_info["type"] == "string":
                    # String -> just the code
                    result_text += f'<Item><Code>{resultItem["code"]}</Code></Item>'

            result_text = result_text.rstrip()
            return result_text
    except Exception as e:
        return f'Error searching for `{search_term}` in `{fhir_attribute_path}`: {str(e)}'


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

#agent = CodeAgent(
agent = ToolCallingAgent(
    tools=[
        search_for_code_or_coding,
    ],
    model=model,
)

agent.run("""
Translate the input text into a set of FHIR resources.
Make use of the search_for_code_or_coding tool to determine the actual code.
Plan ahead which mentions should be looked up.
Plan ahead which FHIR resources are needed and which properties need to be set.

Finally, provide a list of YAML-encoded FHIR resources as final result.

The input text is as follows:
```
Magenbeschwerden seit 2 Tagen, Übelkeit, Erbrechen, kein Durchfall.
Patient hat eine Allergie gegen Penicillin, keine weiteren Allergien bekannt.
```
"""
)
