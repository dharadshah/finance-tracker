"""Ollama LLM client for local open source model inference."""
import logging
from typing import Optional
from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel
from app.ai.llm.base_client import BaseLLMClient, LLMConfig

logger = logging.getLogger("app.ai.llm.ollama_client")


class OllamaLLMClient(BaseLLMClient):
    """LLM client for locally running Ollama models.

    Runs models completely locally - no API key required.
    Requires Ollama to be installed and running on localhost.

    Supported models (must be pulled with ollama pull):
        llama3.2        -> Meta LLaMA 3.2 3B (fast, lightweight)
        llama3.1        -> Meta LLaMA 3.1 8B (balanced)
        mistral         -> Mistral 7B (strong reasoning)
        phi3            -> Microsoft Phi-3 (small but capable)
        gemma2          -> Google Gemma 2 9B

    Usage:
        client = OllamaLLMClient()
        model  = client.get_model()
        chain  = prompt | model | parser
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize Ollama client with optional config.

        Args:
            config: LLMConfig instance. Uses defaults if not provided.
        """
        if config is None:
            config = LLMConfig(
                model_name  = "llama3.2",
                temperature = 0.0,
                max_tokens  = 1024,
                timeout     = 60        # local models can be slower
            )
        super().__init__(config)
        self._model : Optional[BaseChatModel] = None

    def get_model(self) -> BaseChatModel:
        """Return a configured ChatOllama instance.

        Lazily initializes and caches the model on first call.

        Returns:
            ChatOllama instance ready for use in LangChain chains.
        """
        if self._model is None:
            self.logger.info(
                f"Initializing Ollama model: {self.config.model_name}"
            )
            self._model = ChatOllama(
                model       = self.config.model_name,
                temperature = self.config.temperature,
                num_predict = self.config.max_tokens
            )
        return self._model

    def health_check(self) -> bool:
        """Verify Ollama is running and model is available.

        Returns:
            True if healthy, False if Ollama not running or model missing.
        """
        try:
            model    = self.get_model()
            response = model.invoke("ping")
            self.logger.info("Ollama health check passed")
            return True
        except Exception as e:
            self.logger.error(
                f"Ollama health check failed: {e}. "
                f"Is Ollama running? Try: ollama serve"
            )
            return False