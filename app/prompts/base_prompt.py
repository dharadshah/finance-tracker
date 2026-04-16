"""Abstract base class for all Finance Tracker prompts."""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger("app.prompts.base_prompt")


@dataclass
class PromptMetadata:
    """Metadata for a prompt.

    Attributes:
        name       : Unique prompt identifier.
        version    : Semantic version string.
        description: What this prompt does.
        author     : Who created this prompt.
        input_vars : List of required input variable names.
    """
    name        : str
    version     : str
    description : str
    author      : str           = "Finance Tracker"
    input_vars  : list[str]     = field(default_factory=list)


class BasePrompt(ABC):
    """Abstract base class for all prompts.

    All prompts must define:
        metadata   : PromptMetadata describing the prompt.
        system     : The system message template.
        human      : The human message template.

    Usage:
        prompt   = MyPrompt()
        template = prompt.build()
        result   = template.format_messages(var1="value1")
    """

    @property
    @abstractmethod
    def metadata(self) -> PromptMetadata:
        """Return prompt metadata."""
        pass

    @property
    @abstractmethod
    def system(self) -> str:
        """Return the system message template."""
        pass

    @property
    @abstractmethod
    def human(self) -> str:
        """Return the human message template."""
        pass

    def build(self) -> ChatPromptTemplate:
        """Build and return a LangChain ChatPromptTemplate.

        Returns:
            ChatPromptTemplate ready for use in a chain.
        """
        self._validate()
        logger.debug(
            f"Building prompt: {self.metadata.name} "
            f"v{self.metadata.version}"
        )
        return ChatPromptTemplate.from_messages([
            ("system", self.system),
            ("human",  self.human)
        ])

    def _validate(self):
        """Validate that metadata is complete.

        Raises:
            ValueError: If required metadata fields are missing.
        """
        if not self.metadata.name:
            raise ValueError("Prompt metadata must have a name")
        if not self.metadata.version:
            raise ValueError("Prompt metadata must have a version")
        if not self.system:
            raise ValueError(f"Prompt {self.metadata.name} must have a system message")
        if not self.human:
            raise ValueError(f"Prompt {self.metadata.name} must have a human message")

    def format(self, **kwargs) -> list:
        """Build and format the prompt with provided variables.

        Args:
            **kwargs: Variables to inject into the prompt template.

        Returns:
            List of formatted messages ready for LLM.

        Raises:
            ValueError: If required input variables are missing.
        """
        missing = [v for v in self.metadata.input_vars if v not in kwargs]
        if missing:
            raise ValueError(
                f"Prompt '{self.metadata.name}' missing required "
                f"variables: {missing}"
            )
        return self.build().format_messages(**kwargs)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.metadata.name}, "
            f"version={self.metadata.version})"
        )