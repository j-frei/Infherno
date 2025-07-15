import datetime
from datetime import timezone
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
        timestamp = datetime.datetime.now(tz=timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    except AttributeError:
        timestamp = datetime.datetime.now(tz=timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")

    model_name = getattr(config, "MODEL_ID", "unknown_model")
    safe_model_name = model_name.replace("/", "_")
    data_name = getattr(config, "TARGET_DATA", "unknown_data")
    data_instance_id = config.INSTANCE_ID
    log_filename = f"{log_dir}/{safe_model_name}_{data_name}_{data_instance_id}_{timestamp}.log"

    # Configure root logger
    logger = logging.getLogger(log_filename)
    logger.setLevel(logging.INFO)

    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    # Create file handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)

    # Log config at the beginning of the file
    logger.info("")
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
    logger.sensitive_keys = {
        "API_KEY": config.API_KEY,
    }

    class RedactFilter(logging.Filter):
        def __init__(self, tokens_to_redact):
            super().__init__()
            self.tokens_to_redact = tokens_to_redact

        def filter(self, record: logging.LogRecord) -> bool:
            if hasattr(record, "args") and isinstance(record.args, tuple):
                new_args = []
                for arg in record.args:
                    arg_str = str(arg)
                    redacted = arg_str
                    for token in self.tokens_to_redact:
                        if token and token in redacted:
                            redacted = redacted.replace(token, "REDACTED")
                    # If redacted value is different, use it as str; else preserve original type
                    if redacted != arg_str:
                        new_args.append(redacted)
                    else:
                        new_args.append(arg)
                record.args = tuple(new_args)

            # Sanitize record.msg itself (rare case where it’s a full string)
            if isinstance(record.msg, str):
                for token in self.tokens_to_redact:
                    if token and token in record.msg:
                        record.msg = record.msg.replace(token, "REDACTED")

            return True

    tokens_to_redact = [config.API_KEY]
    redact_filter = RedactFilter(tokens_to_redact)

    for logger_name in ["root", "httpx", "LiteLLM", "smolagents"]:
        log = logging.getLogger(logger_name)
        log.addFilter(redact_filter)
        log.setLevel(logging.INFO)
        log.propagate = True

    # Log each config parameter, excluding sensitive ones
    for key, value in sorted(config_dict.items()):
        if key in list(logger.sensitive_keys.keys()):
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
