import hashlib
import json
import os
import types
import yaml
from collections import defaultdict
from rich.console import Group
from rich.panel import Panel
from rich.rule import Rule
from smolagents import AgentLogger
from smolagents.agents import (
    MultiStepAgent,
    Tool,
    ChatMessage,
    PromptTemplates,
    BASE_BUILTIN_MODULES,
    PythonExecutor,
    LocalPythonExecutor,
    E2BExecutor,
    populate_template,
    DockerExecutor,
    ActionStep,
    AgentGenerationError,
    LogLevel,
    AgentExecutionError,
    AgentParsingError,
    ToolCall,
    fix_final_answer_code,
    parse_code_blobs,
    truncate_content,
    YELLOW_HEX,
    Group,
    Text,
)
from typing import List, Callable, Dict, Optional, Any, Union
from infherno.tools.fhircodes.terminology_bindings import getTerminologyBindings

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

    def log(self, *args, level: str | LogLevel = LogLevel.INFO, **kwargs) -> None:
        """Logs a message to the console.

        Args:
            level (LogLevel, optional): Defaults to LogLevel.INFO.
        """
        if isinstance(level, str):
            level = LogLevel[level.upper()]

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

        # Log the rendered string
        if level == LogLevel.DEBUG:
            self.root_logger.debug(text_output)
        elif level == LogLevel.INFO:
            self.root_logger.info(text_output)
        elif level == LogLevel.ERROR:
            self.root_logger.error(text_output)


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
        #prompt_templates: Optional[PromptTemplates] = None,
        grammar: Optional[Dict[str, str]] = None,
        #additional_authorized_imports: Optional[List[str]] = None,
        planning_interval: Optional[int] = None,
        executor_type: str | None = "local",
        executor_kwargs: Optional[Dict[str, Any]] = None,
        max_print_outputs_length: Optional[int] = None,
        logger: FHIRAgentLogger = None,
        fhir_config = None,
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
        if "*" in self.additional_authorized_imports:
            self.logger.log(
                "Caution: you set an authorization for all imports, meaning your agent can decide to import "
                "any package it deems necessary. This might raise issues if the package is not installed in your "
                "environment.",
                0,
            )
        self.executor_type = executor_type or "local"
        self.executor_kwargs = executor_kwargs or {}
        self.python_executor = self.create_python_executor()
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
                return LocalPythonExecutor(
                    self.additional_authorized_imports,
                    max_print_outputs_length=self.max_print_outputs_length,
                )
            case _:  # if applicable
                raise ValueError(f"Unsupported executor type: {self.executor_type}")

    def initialize_system_prompt(self) -> str:
        # Get the FHIR valuesets from the fhir_config, or use default ones
        fhir_valuesets = getattr(self.fhir_config, "FHIR_VALUESETS", ["Patient", "Condition", "MedicationStatement"]),

        system_prompt = populate_template(
            self.prompt_templates["system_prompt"],
            variables={
                "tools": self.tools,
                "managed_agents": self.managed_agents,
                "authorized_imports": (
                    "You can import from any package you want."
                    if "*" in self.authorized_imports
                    else str(self.authorized_imports)
                ),

                "fhir_config": {
                    "FHIR_VALUESETS": fhir_valuesets,
                    "SUPPORTED_QUERY_PATHS": [
                        fhir_attribute_path
                        for fhir_attribute_path in getTerminologyBindings("R4").keys()
                        # Only accept paths that start with "Patient.XYZ", "Condition.XYZ", or "MedicationStatement.XYZ"
                        if any(
                            fhir_attribute_path.startswith(fhir_resource + ".")
                            for fhir_resource in fhir_valuesets
                        )
                    ]
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

    def step(self, memory_step: ActionStep) -> Union[None, Any]:
        """
        Perform one step in the ReAct framework: the agent thinks, acts, and observes the result.
        Returns None if the step is not final.
        """
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
                self.logger.log(panel)

        # Add new step in logs
        memory_step.model_input_messages = memory_messages.copy()
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
        except Exception as e:
            raise AgentGenerationError(f"Error in generating model output:\n{e}", self.logger) from e

        self.logger.log_markdown(
            content=model_output,
            title="Output message of the LLM:",
            level=LogLevel.DEBUG,
        )

        # Parse
        try:
            code_action = fix_final_answer_code(parse_code_blobs(model_output))
        except Exception as e:
            error_msg = f"Error in code parsing:\n{e}\nMake sure to provide correct code blobs."
            raise AgentParsingError(error_msg, self.logger)

        memory_step.tool_calls = [
            ToolCall(
                name="python_interpreter",
                arguments=code_action,
                id=f"call_{len(self.memory.steps)}",
            )
        ]

        # Execute
        self.logger.log_code(title="Executing parsed code:", content=code_action, level=LogLevel.INFO)
        is_final_answer = False
        try:
            output, execution_logs, is_final_answer = self.python_executor(code_action)
            execution_outputs_console = []
            if len(execution_logs) > 0:
                execution_outputs_console += [
                    Text("Execution logs:", style="bold"),
                    Text(execution_logs),
                ]
            observation = "Execution logs:\n" + execution_logs
        except Exception as e:
            if hasattr(self.python_executor, "state") and "_print_outputs" in self.python_executor.state:
                execution_logs = str(self.python_executor.state["_print_outputs"])
                if len(execution_logs) > 0:
                    execution_outputs_console = [
                        Text("Execution logs:", style="bold"),
                        Text(execution_logs),
                    ]
                    memory_step.observations = "Execution logs:\n" + execution_logs
                    self.logger.log(Group(*execution_outputs_console), level=LogLevel.INFO)
            error_msg = str(e)
            if "Import of " in error_msg and " is not allowed" in error_msg:
                self.logger.log(
                    "[bold red]Warning to user: Code execution failed due to an unauthorized import - "
                    "Consider passing said import under `additional_authorized_imports` "
                    "when initializing your CodeAgent.",
                    level=LogLevel.INFO,
                )
            raise AgentExecutionError(error_msg, self.logger)

        truncated_output = truncate_content(str(output))
        observation += "Last output from code snippet:\n" + truncated_output
        memory_step.observations = observation

        execution_outputs_console += [
            Text(
                f"{('Out - Final answer' if is_final_answer else 'Out')}: {truncated_output}",
                style=(f"bold {YELLOW_HEX}" if is_final_answer else ""),
            ),
        ]
        self.logger.log(Group(*execution_outputs_console), level=LogLevel.INFO)
        memory_step.action_output = output
        return output if is_final_answer else None

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
