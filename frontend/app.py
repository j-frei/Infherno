import gradio as gr
import json

from infherno import default_config as config
from infherno.data_utils import load_dummy, load_synthetic
from infherno.defaults import determine_snowstorm_url, determine_snowstorm_branch
from infherno.models import load_model
from infherno.smolagents_utils.fhiragent import FHIRAgent, FHIRAgentLogger
from infherno.smolagents_utils.smolcodesearch import search_for_code_or_coding
from infherno.tools.fhircodes.instance import GenericSnomedInstance
from infherno.utils import setup_logging

def respond(
    message,
    history: list[tuple[str, str]],
    system_message,
    max_tokens,
    temperature,
    top_p,
):
    try:
        logger, log_file = setup_logging(config)
        logger.info(f"Analysis results will be saved to: {log_file}")

        agent_logger = FHIRAgentLogger(logger, level=2)

        agent = FHIRAgent(
            tools=[
                search_for_code_or_coding,
            ],
            model=load_model(
                model_class=config.MODEL_CLASS,
                model_id=config.MODEL_ID,
                context_length=config.CONTEXT_LENGTH,
                max_new_tokens=config.MAX_NEW_TOKENS,
                device_map=config.DEVICE_MAP,
                api_key=config.API_KEY,
            ),
            logger=agent_logger,
            fhir_config=config,
        )

        result = agent.run(f"The input text is as follows:\n```\n{message}\n```")
        return result

    except Exception as e:
        raise gr.Error(str(e))


SNOMED_INSTANCE = GenericSnomedInstance(determine_snowstorm_url(), branch=determine_snowstorm_branch())

chatbot = gr.Chatbot(type="messages", scale=9)

demo = gr.ChatInterface(respond,
    title="Infherno",
    examples=load_dummy()["text"],
    chatbot=chatbot
)

if __name__ == "__main__":
    demo.queue(default_concurrency_limit=40)
    demo.launch(max_threads=40)
