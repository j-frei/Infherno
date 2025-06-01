from infherno import default_config as config
from infherno.defaults import determine_snowstorm_url, determine_snowstorm_branch
from infherno.models import load_model
from infherno.smolagents_utils.fhiragent import FHIRAgent, FHIRAgentLogger
from infherno.smolagents_utils.smolcodesearch import search_for_code_or_coding
from infherno.tools.fhircodes.instance import GenericSnomedInstance
from infherno.utils import setup_logging


logger, log_file = setup_logging(config)
logger.info(f"Analysis results will be saved to: {log_file}")

SNOMED_INSTANCE = GenericSnomedInstance(determine_snowstorm_url(), branch=determine_snowstorm_branch())

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
)

result = agent.run("""
The input text is as follows:
```
Magenbeschwerden seit 2 Tagen, Übelkeit, Erbrechen, kein Durchfall.
Patient hat eine Allergie gegen Penicillin, keine weiteren Allergien bekannt.
Verschrieben wurde deshalb Pantoprazol 20mg 1-0-1.
```
"""
)
