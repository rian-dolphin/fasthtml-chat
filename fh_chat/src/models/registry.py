"""Model provider registry for managing different AI providers."""

from typing import Dict, Type

from .anthropic import AnthropicProvider
from .base import ModelProvider

# from .openai import OpenAIProvider

# Registry of available providers
_PROVIDERS: Dict[str, Type[ModelProvider]] = {
    "anthropic": AnthropicProvider,
    # "openai": OpenAIProvider,
}


def get_model_provider(provider_name: str, **kwargs) -> ModelProvider:
    """
    Get a model provider instance by name.

    Args:
        provider_name: Name of the provider ("anthropic", "openai")
        **kwargs: Additional arguments to pass to the provider constructor

    Returns:
        A ModelProvider instance
    """
    provider_cls = _PROVIDERS.get(provider_name.lower())
    if not provider_cls:
        raise ValueError(
            f"Unknown provider: {provider_name}. Available providers: {list(_PROVIDERS.keys())}"
        )

    return provider_cls(**kwargs)


__all__ = ["ModelProvider", "get_model_provider"]
