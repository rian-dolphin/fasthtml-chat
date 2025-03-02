"""Base class for model providers in FastHTMLChat."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, List, Optional


class ModelProvider(ABC):
    """Base interface for AI model providers."""

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "You are a helpful assistant.",
        model_name: Optional[str] = None,
        max_tokens: int = 1000,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from the model.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: System instructions for the model
            model_name: Specific model to use (provider-dependent)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            An async generator yielding response chunks
        """
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Return a list of available models for this provider."""
        pass
