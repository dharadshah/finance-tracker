"""Abstract base class for all LangChain chains."""
import logging
from abc import ABC, abstractmethod
from typing import Any
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser
from app.ai.llm.base_client import BaseLLMClient
from app.prompts.base_prompt import BasePrompt

logger = logging.getLogger("app.ai.chains.base_chain")


class BaseChain(ABC):
    """Abstract base class for all Finance Tracker chains.

    Each chain combines:
        - A prompt    : structures the input
        - An LLM      : generates the response
        - A parser    : formats the output

    Subclasses must implement:
        prompt   -> the BasePrompt to use
        parse    -> how to parse the LLM response

    Usage:
        chain  = ClassifyChain(llm_client)
        result = chain.invoke({"transaction": "Salary"})
    """

    def __init__(self, llm_client: BaseLLMClient):
        """Initialize with an LLM client.

        Args:
            llm_client: BaseLLMClient instance providing the model.
        """
        self.llm_client = llm_client
        self.logger     = logging.getLogger(
            f"app.ai.chains.{self.__class__.__name__}"
        )

    @property
    @abstractmethod
    def prompt(self) -> BasePrompt:
        """Return the prompt for this chain."""
        pass

    @abstractmethod
    def build(self) -> Runnable:
        """Build and return the LCEL chain.

        Returns:
            Runnable chain ready for invocation.
        """
        pass

    def invoke(self, inputs: dict) -> Any:
        """Invoke the chain with inputs.

        Args:
            inputs: Dict of input variables matching prompt requirements.

        Returns:
            Parsed chain output.

        Raises:
            ValueError : If required inputs are missing.
            Exception  : If LLM call fails.
        """
        self.logger.info(
            f"Invoking {self.__class__.__name__} "
            f"with inputs: {list(inputs.keys())}"
        )
        chain  = self.build()
        result = chain.invoke(inputs)
        self.logger.info(f"{self.__class__.__name__} completed successfully")
        return result

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"model={self.llm_client.config.model_name})"
        )