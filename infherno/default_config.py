# === MODEL ===

# For Ollama, use the following format in your local_config.py definition:
# MODEL_ID = "ollama_chat/gemma3:27b"
MODEL_ID = "gemini/gemini-1.5-pro"
MODEL_CLASS = "LiteLLMModel"
CONTEXT_LENGTH = 131072
MAX_NEW_TOKENS = 32000
API_KEY = "ollama"
MAX_API_RETRIES = 3
API_SLEEP_SECONDS = 60
MAX_STEPS = 20

# for local models
DEVICE_MAP = "auto"


# === DATA ===
DATA_DIRECTORY = "./"
TARGET_DATA = "dummy"
ROOT_FHIR_RESOURCES = [   # TODO: Currently unused
    "Patient",
    "Condition",
    "MedicationStatement",
]
APPLY_PARTITIONING = False
RANDOMIZE_DATA = False
SHORTEST_FIRST = False
TAKE_SUBSAMPLE = True
SUBSAMPLE_SIZE = 10


# === TESTS / EVALUATION ===  # TODO: Currently unused
APPLIED_TESTS = None


# === OVERRIDES ===
try:
    from local_config import *
    print("Successfully imported local config.")
except ImportError:
    print("No local config imported.")
    pass
