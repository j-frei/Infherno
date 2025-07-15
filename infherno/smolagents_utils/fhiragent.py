import hashlib
import httpx
import json
import litellm
import os
import time
import types
import yaml
from collections import defaultdict
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from smolagents import AgentLogger
from smolagents.agents import (
    MultiStepAgent,
    Tool,
    ChatMessage,
    BASE_BUILTIN_MODULES,
    PythonExecutor,
    LocalPythonExecutor,
    E2BExecutor,
    populate_template,
    DockerExecutor,
    ActionStep,
    TaskStep,
    LogLevel,
    AgentParsingError,
    ToolCall,
    fix_final_answer_code,
    parse_code_blobs,
    truncate_content,
    YELLOW_HEX,
    Group,
    Text,
)
from smolagents.local_python_executor import BASE_PYTHON_TOOLS
from typing import List, Callable, Dict, Optional, Any, Union

from infherno.smolagents_utils.smolcodesearch import search_for_code_or_coding
from infherno.tools.fhircodes.terminology_bindings import loadTerminologyBindings


class FHIRAgentLogger(AgentLogger):
    def __init__(self, root_logger, **kwargs):
        super().__init__(**kwargs)
        self.root_logger = root_logger

    def _expand_args(self, args):
        expanded = []
        for arg in args:
            if isinstance(arg, types.GeneratorType):
                expanded.append(list(arg))  # Materialize generator
            else:
                expanded.append(arg)
        return expanded

    def _format_log_entry(self, *args, **kwargs) -> str:
        """Formats rich printable objects into a plain text string."""
        safe_args = self._expand_args(args)

        # Capture the rich renderable as plain text and send to logger
        with self.console.capture() as capture:
            try:
                self.console.print(*safe_args, **kwargs)
            except AttributeError:
                print(*safe_args)
        text_output = capture.get()

        # Heuristic: add newline before "block-like" renderables
        if args and isinstance(args[0], (Panel, Rule, Group)):
            text_output = "\n" + text_output
        return text_output.strip()

    def log(self, *args, level: str | LogLevel = LogLevel.INFO, **kwargs) -> str:
        """Logs a message to the file and returns the formatted string for streaming."""
        if isinstance(level, str):
            level = LogLevel[level.upper()]

        text_output = self._format_log_entry(*args, **kwargs)

        # Log the rendered string to the file
        if self.level <= level:
            log_method = getattr(self.root_logger, level.name.lower(), self.root_logger.info)
            # Split the formatted output by newlines and log each line
            for line in text_output.split('\n'):
                log_method(line)

        # Return the formatted string so it can be yielded
        return text_output

    def log_code(self, content: str, title: str = "Code", level: LogLevel = LogLevel.INFO) -> str:
        """Logs a code block and returns the formatted string."""
        from rich.syntax import Syntax
        syntax = Syntax(content, "python", theme="github-dark", line_numbers=True)
        panel = Panel(syntax, title=title, expand=False)
        return self.log(panel, level=level)

    def log_markdown(self, content: str, title: str = "Markdown", level: LogLevel = LogLevel.INFO) -> str:
        """Logs a markdown block and returns the formatted string."""
        md = Markdown(content)
        panel = Panel(md, title=title, expand=False)
        return self.log(panel, level=level)


class FixedLocalPythonExecutor(LocalPythonExecutor):
    """
    This class inherits from LocalPythonExecutor and overrides the send_tools
    method to correctly handle cases where BASE_PYTHON_TOOLS is a list.
    """

    def send_tools(self, custom_tools_dict: dict[str, Tool]):
        merged_tools = {}

        # Safely add the base tools, whether they are a dict or a list
        if isinstance(BASE_PYTHON_TOOLS, dict):
            merged_tools.update(BASE_PYTHON_TOOLS)
        elif isinstance(BASE_PYTHON_TOOLS, list):
            for tool in BASE_PYTHON_TOOLS:
                if hasattr(tool, 'name'):
                    merged_tools[tool.name] = tool

        # Safely add your custom tools, which are already a dict
        if isinstance(custom_tools_dict, dict):
            merged_tools.update(custom_tools_dict)

        self.static_tools = merged_tools


class SnomedTool(Tool):
    """A dedicated Tool subclass for the SNOMED code search functionality."""

    def __init__(self):
        super().__init__()  # Call the parent constructor

        # --- Define all required class attributes ---
        self.name = "search_for_code_or_coding"
        self.description = "Use this tool to search for SNOMED CT codes. Input is a string search query."
        self.output_type = "string"  # Define the output type

        # The 'inputs' attribute must be a DICTIONARY, not a list.
        self.inputs = {
            "fhir_attribute_path": {
                "type": "string",
                "description": "The FHIR attribute path for the code search, e.g., 'Condition.code'."
            },
            "search_term": {
                "type": "string",
                "description": "The clinical term to search for, e.g., 'abdominal pain'."
            }
        }

    # Implement the 'forward' method with a signature matching the keys in 'inputs'.
    def forward(self, fhir_attribute_path: str, search_term: str):
        """
        This method is called by the executor and will run your actual function.
        """
        return search_for_code_or_coding(
            fhir_attribute_path=fhir_attribute_path,
            search_term=search_term
        )


'''
Mostly copied from smolagents' codeagent.py with slight modifications
- Fixed prompt template to fhiragent.yaml
- Added fhir.resources to authorized imports
'''

class FHIRAgent(MultiStepAgent):
    """
    In this agent, the tool calls will be formulated by the LLM in code format, then parsed and executed.

    Args:
        tools (`list[Tool]`): [`Tool`]s that the agent can use.
        model (`Callable[[list[dict[str, str]]], ChatMessage]`): Model that will generate the agent's actions.
        prompt_templates ([`~agents.PromptTemplates`], *optional*): Prompt templates.
        grammar (`dict[str, str]`, *optional*): Grammar used to parse the LLM output.
        additional_authorized_imports (`list[str]`, *optional*): Additional authorized imports for the agent.
        planning_interval (`int`, *optional*): Interval at which the agent will run a planning step.
        executor_type (`str`, default `"local"`): Which executor type to use between `"local"`, `"e2b"`, or `"docker"`.
        executor_kwargs (`dict`, *optional*): Additional arguments to pass to initialize the executor.
        max_print_outputs_length (`int`, *optional*): Maximum length of the print outputs.
        **kwargs: Additional keyword arguments.

    """

    def __init__(
            self,
            tools: List[Tool],
            model: Callable[[List[Dict[str, str]]], ChatMessage],
            # prompt_templates: Optional[PromptTemplates] = None,
            grammar: Optional[Dict[str, str]] = None,
            # additional_authorized_imports: Optional[List[str]] = None,
            planning_interval: Optional[int] = None,
            executor_type: str | None = "local",
            executor_kwargs: Optional[Dict[str, Any]] = None,
            max_print_outputs_length: Optional[int] = None,
            logger: FHIRAgentLogger = None,
            fhir_config=None,
            **kwargs,
    ):
        self.additional_authorized_imports = ["fhir.resources", "datetime", "time", "dateutil"]
        self.authorized_imports = sorted(set(BASE_BUILTIN_MODULES) | set(self.additional_authorized_imports))
        self.max_print_outputs_length = max_print_outputs_length
        with open(os.path.join(os.path.dirname(__file__), "fhiragent.yaml")) as f:
            prompt_templates = yaml.safe_load(f)

        self.fhir_config = fhir_config

        super().__init__(
            tools=tools,
            model=model,
            prompt_templates=prompt_templates,
            grammar=grammar,
            planning_interval=planning_interval,
            **kwargs,
        )
        self.executor_type = executor_type or "local"
        self.executor_kwargs = executor_kwargs or {}
        self.python_executor = self.create_python_executor()
        if self.tools:
            self.python_executor.send_tools(self.tools)

        self.logger = logger
        self._seen_message_hashes = set()

    def create_python_executor(self) -> PythonExecutor:
        match self.executor_type:
            case "e2b" | "docker":
                if self.managed_agents:
                    raise Exception("Managed agents are not yet supported with remote code execution.")
                if self.executor_type == "e2b":
                    return E2BExecutor(self.additional_authorized_imports, self.logger, **self.executor_kwargs)
                else:
                    return DockerExecutor(self.additional_authorized_imports, self.logger, **self.executor_kwargs)
            case "local":
                return FixedLocalPythonExecutor(
                    self.additional_authorized_imports,
                    max_print_outputs_length=self.max_print_outputs_length,
                )
            case _:  # if applicable
                raise ValueError(f"Unsupported executor type: {self.executor_type}")

    def initialize_system_prompt(self) -> str:
        # Get the FHIR valuesets from the fhir_config, or use default ones
        root_fhir_resources = getattr(self.fhir_config, "ROOT_FHIR_RESOURCES",
                                      ["Patient", "Condition", "MedicationStatement"])
        terminology_bindings = loadTerminologyBindings(root_fhir_resources, "R4")

        system_prompt = populate_template(
            self.prompt_templates["system_prompt"],
            variables={
                "tools": self.tools,
                "managed_agents": self.managed_agents,
                "authorized_imports": str(self.authorized_imports),
                "fhir_config": {
                    "ROOT_FHIR_RESOURCES": root_fhir_resources,
                    "SUPPORTED_QUERY_PATHS": terminology_bindings.keys()
                }
            },
        )
        return system_prompt

    def _hash_message(self, message):
        # Serialize the full message dict deterministically
        return hashlib.sha256(json.dumps(message, sort_keys=True).encode()).hexdigest()

    def _get_new_memory_messages(self, memory_messages):
        new_messages = []
        for msg in memory_messages:
            h = self._hash_message(msg)
            if h not in self._seen_message_hashes:
                self._seen_message_hashes.add(h)
                new_messages.append(msg)
        return new_messages

    def step(self, memory_step: ActionStep, callback: Optional[Callable[[str], None]] = None) -> Union[None, Any]:
        """
        Perform one step in the ReAct framework: the agent thinks, acts, and observes the result.
        Returns None if the step is not final.
        """

        def _callback_if_exists(log_message: str):
            if callback:
                callback(log_message)

        memory_messages = self.write_memory_to_messages()

        self.input_messages = memory_messages.copy()
        new_messages = self._get_new_memory_messages(memory_messages)

        if new_messages:
            # Group new messages by role
            messages_by_role = defaultdict(list)
            for msg in new_messages:
                role = msg.get("role", "unknown")
                text = msg.get("content", [{}])[0].get("text", "")
                messages_by_role[role].append(text)

            # Create and log one Panel per role
            for role, texts in messages_by_role.items():
                block = "\n".join(texts)
                panel = Panel(block, title=role, expand=False)
                _callback_if_exists(self.logger.log(panel))

        # Add new step in logs
        memory_step.model_input_messages = memory_messages.copy()

        model_output = None
        for attempt in range(1, self.fhir_config.MAX_API_RETRIES + 1):
            try:
                additional_args = {"grammar": self.grammar} if self.grammar is not None else {}
                chat_message: ChatMessage = self.model(
                    self.input_messages,
                    stop_sequences=["<end_code>", "Observation:", "Calling tools:"],
                    **additional_args,
                )
                memory_step.model_output_message = chat_message
                model_output = chat_message.content

                # This adds <end_code> sequence to the history.
                # This will nudge ulterior LLM calls to finish with <end_code>, thus efficiently stopping generation.
                if model_output and model_output.strip().endswith("```"):
                    model_output += "<end_code>"
                    memory_step.model_output_message.content = model_output

                memory_step.model_output = model_output
                break
            except (httpx.ConnectError, litellm.APIConnectionError) as e:
                self.logger.log(f"Attempt {attempt}: Connection error: {e}")
                if attempt < self.fhir_config.MAX_API_RETRIES:
                    self.logger.log(f"Sleeping {self.fhir_config.API_SLEEP_SECONDS} seconds before retry...")
                    time.sleep(self.fhir_config.API_SLEEP_SECONDS)
                else:
                    self.logger.log("Max retries reached. Giving up.")

            except Exception as e:
                err_msg = self.logger.log(f"Error in generating model output:\n{e}", level=LogLevel.ERROR)
                _callback_if_exists(err_msg)

        # Gracefully handle cases where the model returns an empty or None response.
        if not model_output:
            empty_response_msg = "The model returned an empty response. The agent will try again in the next step."
            _callback_if_exists(self.logger.log(empty_response_msg, level=LogLevel.ERROR))
            # Return None to allow the agent's run loop to continue to the next step.
            return None

        _callback_if_exists(self.logger.log_markdown(content=model_output, title="LLM Output", level=LogLevel.DEBUG))

        # Parse
        try:
            code_action = fix_final_answer_code(parse_code_blobs(model_output))
        except Exception as e:
            error_msg = f"Error in code parsing:\n{e}\nMake sure to provide correct code blobs."
            _callback_if_exists(self.logger.log(error_msg, level=LogLevel.ERROR))
            raise AgentParsingError(error_msg, self.logger)

        memory_step.tool_calls = [
            ToolCall(
                name="python_interpreter",
                arguments=code_action,
                id=f"call_{len(self.memory.steps)}",
            )
        ]
        _callback_if_exists(self.logger.log_code(title="Executing Code", content=code_action, level=LogLevel.INFO))

        # Execute
        try:
            output, execution_logs, is_final_answer = self.python_executor(code_action)
            observation = ""
            if execution_logs:
                log_group = Group(Text("Execution Logs:", style="bold"), Text(execution_logs))
                _callback_if_exists(self.logger.log(log_group))
                observation = "Execution logs:\n" + execution_logs
        except Exception as e:
            # Instead of raising an exception, format the error as an observation for the LLM.
            error_message = str(e)
            observation = f"Tool execution failed with an error: {error_message}"

            # Log the error and send it to the UI via callback.
            _callback_if_exists(self.logger.log(observation, level=LogLevel.ERROR))

            # Set the step's observation to the error message so the agent can see its mistake.
            memory_step.observations = observation

            # Return None to allow the agent to continue to the next step.
            return None

        truncated_output = truncate_content(str(output))
        observation += "Last output from code snippet:\n" + truncated_output
        memory_step.observations = observation

        final_output_text = Text(
            f"{('Out - Final answer' if is_final_answer else 'Out')}: {truncated_output}",
            style=(f"bold {YELLOW_HEX}" if is_final_answer else ""),
        )
        _callback_if_exists(self.logger.log(Group(final_output_text), level=LogLevel.INFO))
        memory_step.action_output = output

        return output if is_final_answer else None

    def run(self, task: str, max_steps: int = 20, callback: Optional[Callable[[str], None]] = None) -> Any:
        """
        Override of smolagents default `run` method.
        Runs the agent and yields intermediate steps.
        """
        self.memory.steps.append(TaskStep(task=task))
        if callback:
            callback(self.logger.log(Panel(task, title="Input", expand=False)))

        for i in range(max_steps):
            action_step = ActionStep(step_number=i + 1)
            self.memory.steps.append(action_step)

            final_answer = self.step(self.memory.steps[-1], callback=callback)

            if final_answer is not None:
                return final_answer

        return "Max steps reached"

    def to_dict(self) -> dict[str, Any]:
        """Convert the agent to a dictionary representation.

        Returns:
            `dict`: Dictionary representation of the agent.
        """
        agent_dict = super().to_dict()
        agent_dict["authorized_imports"] = self.authorized_imports
        agent_dict["executor_type"] = self.executor_type
        agent_dict["executor_kwargs"] = self.executor_kwargs
        agent_dict["max_print_outputs_length"] = self.max_print_outputs_length
        return agent_dict
