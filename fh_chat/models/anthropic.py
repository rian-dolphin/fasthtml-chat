"""Anthropic Claude provider implementation."""

import os
from typing import AsyncGenerator, Dict, List, Optional

try:
    from anthropic import Anthropic
except ImportError:
    raise ImportError("Please install the Anthropic Python SDK: uv add anthropic")

from .base import ModelProvider


class AnthropicProvider(ModelProvider):
    """Anthropic Claude model provider."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Anthropic provider.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key is required. Set ANTHROPIC_API_KEY env var or pass it to the constructor."
            )

        self.client = Anthropic(api_key=self.api_key)

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "You are a helpful assistant.",
        model_name: Optional[str] = "claude-3-haiku-20240307",
        max_tokens: int = 1000,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response from Claude."""
        with self.client.messages.stream(
            max_tokens=max_tokens,
            messages=messages,
            model=model_name,
            system=system_prompt,
            **kwargs,
        ) as stream:
            for text in stream.text_stream:
                yield text

    def get_available_models(self) -> List[str]:
        """Return a list of available Claude models."""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20240620",
            "claude-3-7-sonnet-20250219",
        ]
