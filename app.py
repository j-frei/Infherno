import gradio as gr
import os
import re
import time
import traceback
from datetime import datetime
from queue import Queue
from threading import Thread

from infherno import default_config as config
from infherno.data_utils import load_dummy, load_dummy_en
from infherno.defaults import determine_snowstorm_branch
from infherno.models import load_model
from infherno.smolagents_utils.fhiragent import FHIRAgent, FHIRAgentLogger
from infherno.tools.fhircodes.instance import GenericSnomedInstance
from infherno.utils import setup_logging


def replay_log_chat(message, history, log_file_name, speedup=1.0):
    if not log_file_name:
        yield "⚠️ Please select a log file to replay."
        return

    if not os.path.isfile(log_file_name):
        yield f"❌ Error: The path '{os.path.basename(log_file_name)}' is not a valid file."
        return

    messages = []
    try:
        with open(log_file_name, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        yield f"❌ Error reading log file: {e}"
        return

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
            if line.startswith("Out - "):
                is_final_output = True
                current_msg.append("```json\n{\n")
            elif is_final_output and len(lines) - 1 == i:
                current_msg.append(line + "\n" + "```")
            else:
                current_msg.append(line)
    if current_time and current_msg:
        messages.append((current_time, ''.join(current_msg).rstrip()))

    if not messages:
        yield "ℹ️ Log file appears to be empty or in an unrecognized format."
        return

    full_response = ""
    for i, (timestamp, log_message) in enumerate(messages):
        entry_markdown = f"\n`{timestamp.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]}`\n```\n{log_message}\n```\n---\n"
        full_response += entry_markdown

        if i > 0:
            delay = (timestamp - messages[i - 1][0]).total_seconds() / speedup
            if delay > 0:
                time.sleep(min(delay, 2.0))

                # Yield the accumulated string response
        yield full_response


def list_log_files(directory="./gemini_logs"):
    files = [
        os.path.join(directory, f) for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f)) and f.endswith(".log")
    ]
    return sorted(files, key=os.path.getmtime)


log_files = list_log_files()


def agent_chat_fn(message, history, model_class, model_id, api_key, snowstorm_url):
    """
    Generator function to stream agent's intermediate steps to the Gradio chat interface.
    """
    if not message or not message.strip():
        return

    # 1. Create a queue to hold the messages from the agent
    output_queue = Queue()

    # 2. Define the callback function that the agent will call
    def stream_callback(log_message: str):
        output_queue.put(log_message)

    def agent_worker():
        try:
            # The agent setup remains the same
            SNOMED_INSTANCE = GenericSnomedInstance(snowstorm_url, branch=determine_snowstorm_branch())
            config.INSTANCE_ID = 1
            logger, log_file = setup_logging(config)
            agent_logger = FHIRAgentLogger(logger, level=2)

            from infherno.smolagents_utils.fhiragent import SnomedTool
            snomed_tool = SnomedTool()
            #snomed_tool.name = "search_for_code_or_coding"

            agent = FHIRAgent(
                tools=[snomed_tool],
                model=load_model(
                    model_class=model_class,
                    model_id=model_id,
                    context_length=config.CONTEXT_LENGTH,
                    max_new_tokens=config.MAX_NEW_TOKENS,
                    device_map=config.DEVICE_MAP,
                    api_key=api_key,
                ), logger=agent_logger,
                fhir_config=config,
            )
            # Run the agent with the callback. This is a blocking call.
            final_result = agent.run(
                f"The input text is as follows:\n```\n{message}\n```",
                max_steps=config.MAX_STEPS,
                callback=stream_callback
            )
            # Put the final result in the queue as a tuple to distinguish it
            output_queue.put(("final_answer", final_result))

        except Exception as e:
            print("--- AGENT WORKER THREAD ERROR ---")
            traceback.print_exc()
            print("---------------------------------")
            output_queue.put(("error", e))
        finally:
            output_queue.put(None)

    # Start the worker thread
    thread = Thread(target=agent_worker)
    thread.start()

    full_response = ""
    while True:
        item = output_queue.get()
        if item is None:
            break

        if isinstance(item, tuple):
            event_type, data = item
            if event_type == "final_answer":
                if data is not None:
                    pass
                    """
                    if isinstance(data, types.GeneratorType):
                        data = list(data)
                    final_content = json.dumps(data, indent=2, ensure_ascii=False)
                    full_response += f"**✨ Final Answer:**\n```json\n{final_content}\n```"
                    """
                else:
                    full_response += "\n🏁 Agent finished without a final answer."
            elif event_type == "error":
                full_response += f"❌ **Error:**\n\n```\n{str(data)}\n```"
        else:
            log_message = item
            full_response += f"```\n{log_message}\n```\n---\n"

        yield full_response


with gr.Blocks() as demo:
    gr.Markdown("# 🔥Infherno")
    with gr.Tabs():
        with gr.Tab("Agent Chat"):
            with gr.Row():
                model_class = gr.Dropdown(
                    choices=[
                        "TransformersModel",
                        "HfApiModel",
                        "LiteLLMModel",
                        # "AcademicCloudModel"
                    ],
                    value = "TransformersModel", label = "Model Class")
                model_id = gr.Dropdown(
                    choices=["HuggingFaceTB/SmolLM2-360M-Instruct",
                             "HuggingFaceTB/SmolLM3-3B",
                             "google/medgemma-4b-it",
                             "gemini/gemini-2.5-pro"],
                    value="HuggingFaceTB/SmolLM2-360M-Instruct",
                    label="Model ID",
                    allow_custom_value=True)
                api_key = gr.Textbox(
                    label="API Key (if required)",
                    type="password"
                )
                snowstorm_url = gr.Textbox(
                    label="SNOMED CT Server URL",
                    value="https://browser.ihtsdotools.org/snowstorm/snomed-ct",
                )

            chatbot1 = gr.Chatbot(
                label="FHIR Agent",
                height=600,
                render_markdown=True,
                show_copy_button=True
            )

            gr.ChatInterface(
                fn=agent_chat_fn,
                chatbot=chatbot1,
                additional_inputs=[
                    model_class,
                    model_id,
                    api_key,
                    snowstorm_url
                ],
                examples=[
                    [load_dummy()["text"], None, None, None, None],
                    [load_dummy_en()["text"], None, None, None, None],
                ],
                title="Agent Chat",
                description="Chat with the agent. Returns a FHIR resource.",
                fill_height=True
            )

        with gr.Tab("Log Replay"):
            chatbot2 = gr.Chatbot(
                label="Log Replay",
                height=600,
                render_markdown=True
            )
            with gr.Row():
                log_dropdown = gr.Dropdown(choices=log_files, label="Choose a log file to replay")
            speed_slider = gr.Slider(0.1, 10, value=1.0, label="Speedup (higher is faster)")

            gr.ChatInterface(
                fn=replay_log_chat,
                chatbot=chatbot2,
                additional_inputs=[log_dropdown, speed_slider],
                title="Log Replay",
                description="Select a log file and press Enter to start the replay.",
                fill_height=True
            )

if __name__ == "__main__":
    demo.launch()
