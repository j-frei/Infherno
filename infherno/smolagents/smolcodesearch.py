import json
from smolagents import CodeAgent, ToolCallingAgent, HfApiModel, TransformersModel, tool

from infherno.tools.fhircodes.instance import GenericSnomedInstance
from infherno.tools.fhircodes.codings import listSupportedCodings, getValueSet, ValueSetLoader
from infherno.tools.fhircodes.codings import listSupportedCodings
from infherno.defaults import determine_snowstorm_url, determine_snowstorm_branch

# Setup the SNOMED CT instance
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


def create_codesearch_agent(model) -> ToolCallingAgent:
    """
    Create a ToolCallingAgent that can search for codes and codings in FHIR ValueSets.
    The FHIR ValueSets are loaded from the SNOMED CT or HL7 ValueSets.
    """
    return ToolCallingAgent(
        tools=[
            search_for_code_or_coding,
        ],
        model=model,
        max_steps=10,
        name="FHIR_Code_Search_Agent",
        description="Searches for codes and codings in FHIR ValueSets (SNOMED CT or HL7 ValueSets) for a certain search term and for a certain FHIR path (e.g. Condition.code)."
    )
