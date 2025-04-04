import json
from smolagents import CodeAgent, ToolCallingAgent, HfApiModel, TransformersModel, tool

from infherno.tools.fhircodes.instance import GenericSnomedInstance
from infherno.tools.fhircodes.codings import listSupportedCodings, getValueSet, ValueSetLoader
from infherno.tools.fhircodes.codings import listSupportedCodings
from infherno.defaults import determine_snowstorm_url, determine_snowstorm_branch
from infherno.smolagents.smolcodesearch import create_codesearch_agent

def create_text2fhir_agent(model) -> CodeAgent:
    """
    Create a CodeAgent that translated a given input text into a list of FHIR resources accurately matching facts stated in the input text.
    The agent uses the fhir.resources library to create FHIR resources.
    The agent may call a ToolCalling agent multiple times to resolve codes and coding systems for Codes and CodeableConcepts in FHIR.

    """
    return CodeAgent(
        tools=[],
        model=model,
        managed_agents=[create_codesearch_agent(model)],
        additional_authorized_imports=["fhir.resources", "datetime", "time", "dateutil"],
        name="Text2FHIR_Agent",
        description="Translate a given input text into a list of FHIR resources accurately matching facts stated in the input text.",
    )

