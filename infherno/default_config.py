# === MODEL ===

MODEL_ID = "gemini/gemini-1.5-pro"
MODEL_CLASS = "LiteLLMModel"
CONTEXT_LENGTH = 131072
MAX_NEW_TOKENS = 32000
API_KEY = "ollama"

# for local models
DEVICE_MAP = "cuda:0"


# === DATA ===
TARGET_DATA = "dummy"
FHIR_VALUESETS = [   # TODO: Currently unused
    "Patient",
    "Condition",
    "MedicationStatement",
]
RANDOMIZE_DATA = False


# === TESTS / EVALUATION ===  # TODO: Currently unused
APPLIED_TESTS = None


# === OVERRIDES ===
try:
    from local_config import *
    print("Successfully imported local config.")
except ImportError:
    print("No local config imported.")
    pass
