import os
import time
from tqdm import tqdm

from infherno import default_config as config
from infherno.constants import LOGS_PATH
from infherno.data_utils import apply_partitioning, load_dummy, load_cardiode, load_n2c2, load_synthetic
from infherno.defaults import determine_snowstorm_url, determine_snowstorm_branch
from infherno.models import load_model
from infherno.smolagents_utils.fhiragent import FHIRAgent, FHIRAgentLogger
from infherno.smolagents_utils.smolcodesearch import search_for_code_or_coding
from infherno.tools.fhircodes.instance import GenericSnomedInstance
from infherno.utils import setup_logging


SNOMED_INSTANCE = GenericSnomedInstance(determine_snowstorm_url(), branch=determine_snowstorm_branch())

if config.TARGET_DATA == "dummy":
    data = load_dummy()
elif config.TARGET_DATA == "n2c2":
    data = load_n2c2(data_path=f"{config.DATA_DIRECTORY}")
elif config.TARGET_DATA == "cardiode":
    data = load_cardiode(data_path=f"{config.DATA_DIRECTORY}")
elif config.TARGET_DATA == "synthetic":
    data = load_synthetic(data_path=f"{config.DATA_DIRECTORY}")
else:
    raise ValueError(f"Target data {config.TARGET_DATA} is not supported!")

if len(data) > 1:
    if config.SHORTEST_FIRST:
        lengths = [len(t) for t in data["text"]]
        # Get the sorted ordering of indices, shortest first
        sorted_idx = sorted(range(len(lengths)), key=lambda i: lengths[i])
        # Reorder dataset
        data = data.select(sorted_idx)

    elif config.RANDOMIZE_DATA:
        data = data.shuffle(seed=42)

    if config.TAKE_SUBSAMPLE:
        data = data.select(range(config.SUBSAMPLE_SIZE))

if config.APPLY_PARTITIONING:
    data = apply_partitioning(data)

for instance_id, instance in enumerate(tqdm(data, total=len(data), desc=f"\nInstances {config.TARGET_DATA}")):
    config.INSTANCE_ID = str(instance_id + 1).zfill(2)

    if any(f"{config.TARGET_DATA}_{instance_id}" in filename for filename in os.listdir(LOGS_PATH)):
        # Skip already processed instances
        continue

    logger, log_file = setup_logging(config)
    logger.info(f"Analysis results will be saved to: {log_file}")

    agent_logger = FHIRAgentLogger(logger, level=1)

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

    instance_text = instance["text"]
    result = agent.run(
        f"The input text is as follows:\n```\n{instance_text}\n```",
        max_steps=config.MAX_STEPS,
        callback=lambda log_message: tqdm.write(log_message)
    )
    time.sleep(config.API_SLEEP_SECONDS)
