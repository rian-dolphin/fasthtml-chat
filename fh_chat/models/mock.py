"""Mock model provider for testing without using API tokens."""

import asyncio
from typing import AsyncGenerator, Dict, List, Optional

from .base import ModelProvider


class MockProvider(ModelProvider):
    """Mock model provider that generates simple text streams for testing."""

    def __init__(
        self,
        delay: float = 0.05,
        **kwargs,
    ):
        """
        Initialize the Mock provider.

        Args:
            delay: Delay between text chunks (seconds)
            **kwargs: Additional arguments (ignored)
        """
        self.delay = delay

    async def generate_stream(
        self,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response with a repeating test sentence."""
        # Simple repeating sentence
        message = "This is a mock response."
        chunks = message.split(" ")

        # Stream each character with a small delay
        for _ in range(15):  # Repeat the message a few times
            for chunk in chunks:
                yield " " + chunk
                await asyncio.sleep(self.delay)

    def get_available_models(self) -> List[str]:
        """Return a list of available mock models."""
        return [
            "mock-default",
        ]
