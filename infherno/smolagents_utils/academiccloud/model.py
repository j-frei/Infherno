from typing import Optional, List, Dict
import sys
import json
from logging import getLogger

from smolagents.tools import Tool
from smolagents.models import (
    ChatMessage,
    MessageRole,
    ApiModel,
    remove_stop_sequences,
)

logger = getLogger(__name__)

class AcademicCloudModel(ApiModel):
    """This model connects to the AcademicCloud API server.

    This API is OpenAI-compatible but uses OpenIDC session cookie for authentication
    and the endpoint is at /chat-ai-backend. It returns plain text responses.

    Parameters:
        model_id (`str`):
            The model identifier to use on the server (e.g. "meta-llama-3.1-8b-instruct").
        base_url (`str`, *optional*):
            The base URL of the API server. Defaults to "https://chat-ai.academiccloud.de".
        openidc_session_cookie (`str`):
            The OpenIDC session cookie to use for authentication.
        custom_role_conversions (`dict[str, str]`, *optional*):
            Custom role conversion mapping to convert message roles.
        temperature (`float`, *optional*):
            Temperature for sampling. Defaults to 0.5.
        top_p (`float`, *optional*):
            Nucleus sampling parameter. Defaults to 0.5.
        **kwargs:
            Additional keyword arguments.
    """

    def __init__(
        self,
        model_id: str,
        base_url: Optional[str] = "https://chat-ai.academiccloud.de",
        openidc_session_cookie: Optional[str] = None,
        custom_role_conversions: dict[str, str] | None = None,
        temperature: float = 0.5,
        top_p: float = 0.5,
        **kwargs,
    ):
        self.base_url = base_url
        if not openidc_session_cookie:
            raise ValueError("The 'openidc_session_cookie' parameter is required for AcademicCloudModel.")
        self.openidc_session_cookie = openidc_session_cookie
        self.temperature = temperature
        self.top_p = top_p

        super().__init__(
            model_id=model_id,
            custom_role_conversions=custom_role_conversions,
            **kwargs,
        )

        # Load the models available on the server
        model_response = self.client.get(
            f"{self.base_url}/models"
        )
        model_response.raise_for_status()
        model_data = model_response.json()
        self.available_models = [ m["id"] for m in model_data.get("data", []) ]

        print(f"Available models: {self.available_models}", file=sys.stderr)

        # Check if the specified model is available
        if model_id not in self.available_models:
            raise ValueError(
                f"Model '{model_id}' is not available on the server. Available models: {self.available_models}"
            )

    def create_client(self):
        """Create the AcademicCloud client."""
        try:
            import requests
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "Please install 'requests' to use AcademicCloudModel: `pip install requests`"
            ) from e

        session = requests.Session()
        session.cookies.set("mod_auth_openidc_session", self.openidc_session_cookie)
        session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"
        })
        return session

    def __call__(
        self,
        messages: List[Dict[str, str]],
        stop_sequences: Optional[List[str]] = None,
        grammar: Optional[str] = None,
        tools_to_call_from: Optional[List[Tool]] = None,
        **kwargs,
    ) -> ChatMessage:
        completion_kwargs = self._prepare_completion_kwargs(
            messages=messages,
            stop_sequences=stop_sequences,
            grammar=grammar,
            tools_to_call_from=tools_to_call_from,
            custom_role_conversions=self.custom_role_conversions,
            **kwargs,
        )

        # Extract prepared messages and convert to expected format
        prepared_messages = []
        for message in completion_kwargs.pop("messages"):
            content = message.get("content", "")

            # If content is a list (multimodal content), extract just the text parts
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                content = " ".join(text_parts)

            prepared_messages.append({
                "role": message["role"],
                "content": content
            })

        # Prepare API payload
        payload = {
            "model": self.model_id,
            "messages": prepared_messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", self.top_p),
        }

        # Add stop sequences if provided and supported by the API
        if stop_sequences:
            payload["stop"] = stop_sequences

        try:
            response = self.client.post(
                f"{self.base_url}/chat-ai-backend",
                json=payload,
            )

            # Handle HTTP errors
            if response.status_code != 200:
                error_msg = f"API request failed with status code {response.status_code}: {response.text}"
                logger.error(error_msg)
                return ChatMessage(
                    role=MessageRole.ASSISTANT,
                    content=f"Error: {error_msg}",
                    raw={"error": error_msg, "status_code": response.status_code},
                )

            # Get the plain text response
            response_text = response.text

            # Apply stop sequences manually if provided
            if stop_sequences:
                response_text = remove_stop_sequences(response_text, stop_sequences)

            # Create the chat message
            chat_message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=response_text,
                raw={"response": response_text, "completion_kwargs": completion_kwargs},
            )

            # Approximate token counts using a simple ratio
            input_text = json.dumps(payload)
            self.last_input_token_count = len(input_text) // 4  # Rough approximation
            self.last_output_token_count = len(response_text) // 4  # Rough approximation

            return chat_message

        except Exception as e:
            error_msg = f"Error calling AcademicCloud API: {str(e)}"
            logger.error(error_msg)
            return ChatMessage(
                role=MessageRole.ASSISTANT,
                content=f"Error: {error_msg}",
                raw={"error": error_msg},
            )

    def get_available_models(self) -> List[str]:
        """Get the list of available models on the server."""
        return self.available_models
