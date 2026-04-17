"""Abstract base class for LLM clients."""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel

logger = logging.getLogger("app.ai.llm.base_client")


@dataclass
class LLMConfig:
    """Configuration for an LLM client.

    Attributes:
        model_name  : Name of the model to use.
        temperature : Sampling temperature (0.0 = deterministic).
        max_tokens  : Maximum tokens in response.
        timeout     : Request timeout in seconds.
    """
    model_name  : str
    temperature : float = 0.0
    max_tokens  : int   = 1024
    timeout     : int   = 30


class BaseLLMClient(ABC):
    """Abstract base class for all LLM clients.

    All LLM clients must implement:
        get_model() -> returns a LangChain chat model instance

    Usage:
        client = GroqLLMClient(config)
        model  = client.get_model()
        chain  = prompt | model | parser
    """

    def __init__(self, config: LLMConfig):
        """Initialize with LLM configuration.

        Args:
            config: LLMConfig instance with model settings.
        """
        self.config = config
        self.logger = logging.getLogger(
            f"app.ai.llm.{self.__class__.__name__}"
        )

    @abstractmethod
    def get_model(self) -> BaseChatModel:
        """Return a configured LangChain chat model.

        Returns:
            LangChain BaseChatModel instance ready for use in chains.
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verify the LLM client is reachable.

        Returns:
            True if healthy, False otherwise.
        """
        pass

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"model={self.config.model_name}, "
            f"temperature={self.config.temperature})"
        )