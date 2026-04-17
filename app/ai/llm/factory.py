"""LLM Client Factory — creates and caches LLM client instances."""
import logging
from typing import Optional
from app.ai.llm.base_client import BaseLLMClient, LLMConfig
from app.ai.llm.groq_client import GroqLLMClient
from app.constants.app_constants import GROQ_CHAT_MODEL

logger = logging.getLogger("app.ai.llm.factory")


class LLMClientFactory:
    """Factory for creating and caching LLM client instances.

    Supports multiple providers. Currently implements Groq.
    Adding a new provider requires:
        1. Create a new client class inheriting BaseLLMClient
        2. Add a new method to this factory
        3. Register in get_client() if needed

    Usage:
        factory = LLMClientFactory()
        client  = factory.get_groq_client()
        model   = client.get_model()
    """

    _instances: dict[str, BaseLLMClient] = {}

    def get_groq_client(
        self,
        model_name  : Optional[str]   = None,
        temperature : Optional[float] = None,
        max_tokens  : Optional[int]   = None
    ) -> GroqLLMClient:
        """Get or create a Groq LLM client.

        Uses constants from app_constants as defaults.
        Caches the instance — same config returns same client.

        Args:
            model_name  : Override default model name.
            temperature : Override default temperature.
            max_tokens  : Override default max tokens.

        Returns:
            Configured GroqLLMClient instance.
        """
        config = LLMConfig(
            model_name  = model_name  or GROQ_CHAT_MODEL.MODEL_NAME.value,
            temperature = temperature or GROQ_CHAT_MODEL.TEMPERATURE.value,
            max_tokens  = max_tokens  or 1024
        )

        cache_key = f"groq_{config.model_name}_{config.temperature}"

        if cache_key not in self._instances:
            self.logger.info(
                f"Creating new Groq client: {config.model_name}"
            )
            self._instances[cache_key] = GroqLLMClient(config)
        else:
            self.logger.debug(
                f"Returning cached Groq client: {config.model_name}"
            )

        return self._instances[cache_key]

    def clear_cache(self):
        """Clear all cached client instances.

        Useful for testing or forcing reconnection.
        """
        self._instances.clear()
        self.logger.info("LLM client cache cleared")

    def __init__(self):
        self.logger = logging.getLogger("app.ai.llm.factory")


# module level factory instance
llm_factory = LLMClientFactory()