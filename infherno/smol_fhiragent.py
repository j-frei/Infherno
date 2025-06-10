from infherno import default_config as config
from infherno.data_utils import load_cardiode, load_n2c2
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

if config.TARGET_DATA == "dummy":
    result = agent.run("""
        The input text is as follows:
        ```
        Magenbeschwerden seit 2 Tagen, Übelkeit, Erbrechen, kein Durchfall.
        Patient hat eine Allergie gegen Penicillin, keine weiteren Allergien bekannt.
        Verschrieben wurde deshalb Pantoprazol 20mg 1-0-1.
        ```
        """
    )
elif config.TARGET_DATA in ["cardiode", "n2c2"]:
    if config.TARGET_DATA == "n2c2":
        data = load_n2c2()
    elif config.TARGET_DATA == "cardiode":
        data = load_cardiode()
    else:
        raise ValueError(f"Target data {config.TARGET_DATA} is not supported!")

    if config.RANDOMIZE_DATA:
        data = data.shuffle(seed=42)

    for instance in data:
        instance_text = instance["text"]
        result = agent.run(f"The input text is as follows:\n```\n{instance_text}\n```")
