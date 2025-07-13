import gradio as gr
import json
import os
import re
import time
from datasets import Dataset
from datetime import datetime


"""
from Infherno.infherno import default_config as config
from Infherno.infherno.data_utils import load_dummy, load_dummy_en
from Infherno.infherno.defaults import determine_snowstorm_url, determine_snowstorm_branch
from Infherno.infherno.models import load_model
from Infherno.infherno.smolagents_utils.fhiragent import FHIRAgent, FHIRAgentLogger
from Infherno.infherno.smolagents_utils.smolcodesearch import search_for_code_or_coding
from Infherno.infherno.tools.fhircodes.instance import GenericSnomedInstance
from Infherno.infherno.utils import setup_logging
"""


def replay_log_chat(message, history, log_file_name, speedup=1.0):
    messages = []
    try:
        with open(log_file_name, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except TypeError:
        with open(log_files[0], "r", encoding="utf-8") as f:
            lines = f.readlines()
    log_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - .*? - (.*)", re.DOTALL)
    current_time = None
    is_final_output = False
    current_msg = []
    for i, line in enumerate(lines):
        match = log_pattern.match(line)
        if match:
            if current_time and current_msg:
                messages.append((current_time, ''.join(current_msg).rstrip()))
            current_time = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S,%f")
            current_msg = [match.group(2) + "\n"]
        else:
            if line.startswith("Out - Final answer:"):
                is_final_output = True
                current_msg.append("```json\n{\n")
            elif is_final_output and len(lines) - 1 == i:
                current_msg.append(line + "\n" + "```")
            else:
                current_msg.append(line)
    if current_time and current_msg:
        messages.append((current_time, ''.join(current_msg).rstrip()))

    full_response = ""
    for i, (timestamp, log_message) in enumerate(messages):
        # Format each log entry as a distinct, readable block in Markdown
        # We add the timestamp as a header for clarity
        entry_markdown = f"\n`{timestamp.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]}`\n```\n{log_message}\n```\n---\n"
        full_response += entry_markdown

        if i > 0:
            delay = (timestamp - messages[i - 1][0]).total_seconds() / speedup
            # Prevent excessively long sleeps
            if delay > 0:
                time.sleep(min(delay, 2.0))  # Sleep for a max of 2s between entries

        yield full_response


def load_dummy() -> Dataset:
    dummy_str = ("Magenbeschwerden seit 2 Tagen, Übelkeit, Erbrechen, kein Durchfall.\n"
                 "Patient hat eine Allergie gegen Penicillin, keine weiteren Allergien bekannt.\n"
                 "Verschrieben wurde deshalb Pantoprazol 20mg 1-0-1.")
    dataset = Dataset.from_dict({"text": [dummy_str]})
    return dataset


def load_dummy_en() -> Dataset:
    dummy_str = ("Patient presents with headache and dizziness lasting 3 days, no fever.\n"
                 "History of hypertension, currently on Lisinopril, no known drug allergies.\n"
                 "Prescribed Ibuprofen 400mg as needed for pain, advised hydration and rest.")
    dataset = Dataset.from_dict({"text": [dummy_str]})
    return dataset


def list_log_files(directory="./gemini_logs"):
    files = [
        os.path.join(directory, f) for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f)) and f.endswith(".log")
    ]
    return files

log_files = list_log_files()


def dummy_agent_chat_fn(message, history):
    return "Agent Chat function will be available shortly."


def agent_chat_fn(message, history):
    SNOMED_INSTANCE = GenericSnomedInstance(determine_snowstorm_url(), branch=determine_snowstorm_branch())
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
        final_content = ""
        if isinstance(result, (dict, list)):
            # If the agent returns a Python object, dump it to a formatted string.
            final_content = json.dumps(result, indent=2, ensure_ascii=False)
        else:
            # If the agent returns anything else (like a pre-formatted string),
            # use it directly. We convert to string just in case.
            final_content = str(result)
            # Defensive check: if it's a string that looks like JSON,
            # we can try to parse and re-format it to ensure it's pretty.
            try:
                parsed_json = json.loads(final_content)
                final_content = json.dumps(parsed_json, indent=2, ensure_ascii=False)
            except (json.JSONDecodeError, TypeError):
                # If it fails, it wasn't a JSON string, so we just use the original.
                pass

        # Return the final content wrapped in Markdown for proper rendering.
        return f"```json\n{final_content}\n```"
    except Exception as e:
        chat = history[:] if history else []
        chat.append(f"❌ Error: {str(e)}")
        return chat

with gr.Blocks() as demo:
    gr.Markdown("# 🔥Infherno")
    with gr.Tabs():
        with gr.Tab("Agent Chat"):
            chatbot1 = gr.Chatbot(
                label="FHIR Agent",
                bubble_full_width=True,
                height=600,
                render_markdown=True,
                show_copy_button=True
            )
            agent_chat = gr.ChatInterface(
                fn=dummy_agent_chat_fn,
                chatbot=chatbot1,
                examples=[
                    load_dummy()["text"],
                    load_dummy_en()["text"],
                ],
                title="Agent Chat",
                description="Chat with the agent. Returns a FHIR resource.",
                fill_height=True
            )
        with gr.Tab("Log Replay"):
            chatbot2 = gr.Chatbot()
            with gr.Row():
                log_dropdown = gr.Dropdown(choices=log_files, label="Choose a log file")
                speed_slider = gr.Slider(0.1, 10, value=1.0, label="Speedup (higher is faster)")

            log_chat = gr.ChatInterface(
                fn=replay_log_chat,
                chatbot=chatbot2,
                additional_inputs=[log_dropdown, speed_slider],
                title="Log Replay",
                description="Select a log file to replay as chat. Press enter to start replay.",
                fill_height=True
            )

if __name__ == "__main__":
    demo.launch()
