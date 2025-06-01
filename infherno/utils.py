import datetime
import importlib.util
import inspect
import json
import logging
import torch
from pathlib import Path

from infherno import constants
from infherno import default_config as config


def setup_logging(
    config_module_path: str,
    log_dir: str = constants.LOGS_PATH,
) -> tuple[logging.Logger, str]:
    """Set up logging to both console and file with configs at the beginning.

    Args:
        config_module_path: Path to the Python config script
        log_dir: Directory to save log files

    Returns:
        logger: Configured logger object
        log_filename: Path to the created log file
    """
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Import the config module
    if isinstance(config_module_path, str):
        # If a path is provided, import it
        spec = importlib.util.spec_from_file_location("config", config_module_path)
        if spec is None:
            raise ImportError(f"Cannot import module from {config_module_path}")
        config_id = importlib.util.module_from_spec(spec)
        if spec.loader is None:
            raise ImportError(f"Cannot load module from {config_module_path}")
        spec.loader.exec_module(config_id)
    else:
        # If the module is already imported, use it directly
        config_id = config_module_path

    # Generate timestamped filename
    try:
        timestamp = datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%d_%H-%M-%S")
    except AttributeError:
        timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d_%H-%M-%S")

    model_name = getattr(config, "MODEL_ID", "unknown_model")
    safe_model_name = model_name.replace("/", "_")
    data_name = getattr(config, "TARGET_DATA", "unknown_data")
    log_filename = f"{log_dir}/{safe_model_name}_{data_name}_{timestamp}.log"

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Ensure smolagents logs propagate and are at INFO level
    for name in logging.root.manager.loggerDict:
        if "smol" in name.lower():
            logging.getLogger(name).setLevel(logging.INFO)
            logging.getLogger(name).propagate = True

    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create file handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Log config at the beginning of the file
    logger.info("=" * 80)
    logger.info("CONFIGURATION PARAMETERS")
    logger.info("=" * 80)

    # Get all uppercase variables from the config module
    config_dict = {
        name: value
        for name, value in inspect.getmembers(config_id)
        if name.isupper() and not callable(value)
    }

    # Define sensitive keys to exclude
    sensitive_keys = {"API_KEY"}

    # Log each config parameter, excluding sensitive ones
    for key, value in sorted(config_dict.items()):
        if key in sensitive_keys:
            continue
        try:
            # Try to convert to JSON for cleaner formatting of complex objects
            value_str = json.dumps(value) if isinstance(value, list | dict | tuple) else str(value)
            logger.info(f"{key} = {value_str}")
        except (TypeError, json.JSONDecodeError):
            logger.info(f"{key} = {value!s}")

    logger.info("=" * 80)
    logger.info("ANALYSIS RESULTS")
    logger.info("=" * 80)

    return logger, log_filename


def determine_device():
    # Determine the device to use
    if torch.cuda.is_available():
        device = "cuda"  # CUDA (NVIDIA GPU)
    elif torch.backends.mps.is_available():
        device = "mps"   # MPS (Apple GPU)
    else:
        device = "cpu"   # CPU fallback
    return device
