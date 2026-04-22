"""LLM Client Factory — creates and caches LLM client instances."""
import logging
from typing import Optional
from app.ai.llm.base_client import BaseLLMClient, LLMConfig
from app.ai.llm.groq_client import GroqLLMClient
from app.ai.llm.ollama_client import OllamaLLMClient
from app.constants.app_constants import GROQ_CHAT_MODEL
from app.config.settings import settings

logger = logging.getLogger("app.ai.llm.factory")


class LLMClientFactory:
    """Factory for creating and caching LLM client instances.

    Supports multiple providers:
        groq   -> Groq API (fast, free tier, requires API key)
        ollama -> Local Ollama (private, no API key, requires install)

    Provider selection via settings.llm_provider.

    Usage:
        factory = LLMClientFactory()
        client  = factory.get_client()          # uses default provider
        client  = factory.get_groq_client()     # explicit Groq
        client  = factory.get_ollama_client()   # explicit Ollama
    """

    _instances: dict[str, BaseLLMClient] = {}

    def __init__(self):
        self.logger = logging.getLogger("app.ai.llm.factory")

    def get_client(self) -> BaseLLMClient:
        """Get LLM client based on configured provider.

        Falls back to Groq if configured provider is unavailable.

        Returns:
            Configured LLM client instance.
        """
        provider = getattr(settings, "llm_provider", "groq").lower()

        self.logger.info(f"Getting LLM client for provider: {provider}")

        if provider == "ollama":
            client = self.get_ollama_client()
            if client.health_check():
                return client
            self.logger.warning(
                "Ollama unavailable, falling back to Groq"
            )
            return self.get_groq_client()

        return self.get_groq_client()

    def get_groq_client(
        self,
        model_name  : Optional[str]   = None,
        temperature : Optional[float] = None,
        max_tokens  : Optional[int]   = None
    ) -> GroqLLMClient:
        """Get or create a Groq LLM client.

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
            self.logger.info(f"Creating Groq client: {config.model_name}")
            self._instances[cache_key] = GroqLLMClient(config)
        else:
            self.logger.debug(f"Returning cached Groq client: {config.model_name}")

        return self._instances[cache_key]

    def get_ollama_client(
        self,
        model_name  : Optional[str]   = None,
        temperature : Optional[float] = None
    ) -> OllamaLLMClient:
        """Get or create an Ollama LLM client.

        Args:
            model_name  : Override default model name.
            temperature : Override default temperature.

        Returns:
            Configured OllamaLLMClient instance.
        """
        config = LLMConfig(
            model_name  = model_name  or "llama3.2",
            temperature = temperature or 0.0,
            max_tokens  = 1024,
            timeout     = 60
        )

        cache_key = f"ollama_{config.model_name}_{config.temperature}"

        if cache_key not in self._instances:
            self.logger.info(f"Creating Ollama client: {config.model_name}")
            self._instances[cache_key] = OllamaLLMClient(config)
        else:
            self.logger.debug(
                f"Returning cached Ollama client: {config.model_name}"
            )

        return self._instances[cache_key]

    def clear_cache(self):
        """Clear all cached client instances."""
        self._instances.clear()
        self.logger.info("LLM client cache cleared")

    def list_providers(self) -> list:
        """List all supported providers.

        Returns:
            List of supported provider name strings.
        """
        return ["groq", "ollama"]


# module level factory instance
llm_factory = LLMClientFactory()