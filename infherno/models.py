""" Choose which LLM engine to use!"""
from smolagents import HfApiModel, LiteLLMModel, TransformersModel


def load_model(model_class, model_id, context_length, max_new_tokens, device_map, api_key):
    if model_class == "HfApiModel":
        model = HfApiModel(
            model_id=model_id,
            max_tokens=max_new_tokens,
        )
        # e.g., "meta-llama/Llama-3.2-2B-Instruct"

    elif model_class == "LiteLLMModel":
        if "ollama" in api_key:
            import os
            model = LiteLLMModel(
                # model_id="ollama/gemma3:12b",
                # model_id="ollama/llama3.3:70b-instruct-q4_K_M",
                model_id=model_id,
                num_ctx=context_length,
                api_key=api_key,
                api_base=os.environ.get("OLLAMA_ENDPOINT", "http://localhost:11434"),
            )
        elif "anthropic/" in model_id or "deepseek/" in model_id:
            model = LiteLLMModel(
                # model_id="anthropic/claude-3-5-sonnet-20240620",
                model_id=model_id,
                api_key=api_key,
            )
        else:
            model = LiteLLMModel(
                # model_id="gpt-4o",
                model_id=model_id,
                num_ctx=context_length,
                api_key=api_key,
            )

    elif model_class == "TransformersModel":
        model = TransformersModel(
            model_id=model_id,
            #model_id="meta-llama/Llama-3.1-8B-Instruct",
            #model_id="Qwen/Qwen2.5-7B-Instruct",
            #model_id="Qwen/Qwen2.5-14B-Instruct",
            #model_id="google/gemma-3-12b-it",
            #model_id="meta-llama/Llama-4-Maverick-17B-128E-Instruct",
            #model_id="bartowski/Llama-3.3-70B-Instruct-GGUF",
            max_new_tokens=32000,
            device_map=device_map,
        )

    else:
        raise ValueError(f"Unknown model class {model_class}")

    return model
