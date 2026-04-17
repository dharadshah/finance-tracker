"""Groq LLM client implementation."""
import logging
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel
from app.ai.llm.base_client import BaseLLMClient, LLMConfig
from app.config.settings import settings
logger = logging.getLogger("app.ai.llm.groq_client")


class GroqLLMClient(BaseLLMClient):
    """LLM client for Groq API using LangChain ChatGroq.

    Uses llama-3.3-70b-versatile by default.
    Temperature 0.0 for deterministic, consistent outputs.
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize Groq client with optional config.

        Args:
            config: LLMConfig instance. Uses defaults if not provided.
        """
        if config is None:
            config = LLMConfig(
                model_name  = "llama-3.3-70b-versatile",
                temperature = 0.0,
                max_tokens  = 1024,
                timeout     = 30
            )
        super().__init__(config)
        self._model : Optional[BaseChatModel] = None

    def get_model(self) -> BaseChatModel:
        """Return a configured ChatGroq instance.

        Lazily initializes and caches the model on first call.

        Returns:
            ChatGroq instance ready for use in LangChain chains.
        """
        if self._model is None:
            self.logger.info(
                f"Initializing Groq model: {self.config.model_name}"
            )
            self._model = ChatGroq(
                api_key     = settings.groq_api_key,
                model       = self.config.model_name,
                temperature = self.config.temperature,
                max_tokens  = self.config.max_tokens,
                timeout     = self.config.timeout
            )
        return self._model

    def health_check(self) -> bool:
        """Verify Groq API is reachable with a minimal request.

        Returns:
            True if healthy, False if unreachable.
        """
        try:
            model    = self.get_model()
            response = model.invoke("ping")
            self.logger.info("Groq health check passed")
            return True
        except Exception as e:
            self.logger.error(f"Groq health check failed: {e}")
            return False