from smolagents import CodeAgent

from infherno.smolagents.smolcodesearch import search_for_code_or_coding

def create_text2fhir_agent(model) -> CodeAgent:
    """
    Create a CodeAgent that translated a given input text into a list of FHIR resources accurately matching facts stated in the input text.
    The agent uses the fhir.resources library to create FHIR resources.
    The agent may call a ToolCalling agent multiple times to resolve codes and coding systems for Codes and CodeableConcepts in FHIR.

    """
    return CodeAgent(
        tools=[search_for_code_or_coding],
        model=model,
        additional_authorized_imports=["fhir.resources", "datetime", "time", "dateutil"],
        name="Text2FHIR_Agent",
        description="Translate a given input text into a list of FHIR resources accurately matching facts stated in the input text.",
        verbosity_level=2,
    )

