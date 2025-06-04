import json
import os
from typing import Dict, List, Optional

from langfuse.openai import openai

from .config import DEFAULT_MODEL, OPENAI_API_KEY, OPENROUTER_BASE_URL


class LLMClient:
    """Centralized LLM client for OpenRouter API with Langfuse tracing.

    This client provides a unified interface for making LLM API calls through
    OpenRouter with integrated Langfuse tracing for monitoring and analytics.
    """

    def __init__(self):
        """Initialize the LLM client with API configuration and Langfuse setup."""
        self.api_key = self._get_api_key()
        self.default_model = DEFAULT_MODEL

        self._setup_langfuse()

        self.client = openai.OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=self.api_key,
        )

    def _setup_langfuse(self):
        """Setup Langfuse configuration from environment or config file.

        Attempts to load Langfuse credentials from environment variables first,
        then falls back to config.json file. Prints warning if credentials
        are not found.
        """
        if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
            try:
                with open("config.json") as f:
                    config = json.load(f)

                if "langfuse_public_key" in config:
                    os.environ["LANGFUSE_PUBLIC_KEY"] = config["langfuse_public_key"]
                if "langfuse_secret_key" in config:
                    os.environ["LANGFUSE_SECRET_KEY"] = config["langfuse_secret_key"]
                if "langfuse_host" in config:
                    os.environ["LANGFUSE_HOST"] = config["langfuse_host"]
            except (FileNotFoundError, KeyError):
                print("Warning: Langfuse keys not found. Tracing disabled.")

    def _get_api_key(self) -> str:
        """Get API key from environment or config file.

        Returns:
            str: The OpenAI API key for authentication.

        Raises:
            ValueError: If API key is not found in environment or config.json.
        """
        api_key = OPENAI_API_KEY

        if not api_key:
            try:
                with open("config.json") as f:
                    config = json.load(f)
                api_key = config.get("openai_api_key")
            except FileNotFoundError:
                pass

        if not api_key:
            raise ValueError("OpenAI API key not found in environment or config.json")

        return api_key

    def create_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        model: Optional[str] = None,
        trace_name: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Create a chat completion and return the response content.

        Args:
            messages (List[Dict[str, str]]): List of message dictionaries with
                'role' and 'content' keys.
            temperature (float, optional): Sampling temperature between 0 and 1.
                Defaults to 0.7.
            model (Optional[str], optional): Model to use for completion.
                Defaults to DEFAULT_MODEL if None.
            trace_name (Optional[str], optional): Name for Langfuse trace tracking.
                Defaults to None.
            **kwargs: Additional parameters passed to the OpenAI API.

        Returns:
            str: The response content from the LLM.

        Raises:
            Exception: If the API call fails or returns an error.
        """
        if model is None:
            model = self.default_model

        try:
            if trace_name:
                kwargs["name"] = trace_name

            response = self.client.chat.completions.create(
                model=model, messages=messages, temperature=temperature, **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error creating completion: {e}")
            raise
