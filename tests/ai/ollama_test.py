"""Tests for Ollama LLM client."""
import pytest
from unittest.mock import MagicMock, patch
from app.ai.llm.base_client import LLMConfig
from app.ai.llm.ollama_client import OllamaLLMClient
from app.ai.llm.factory import LLMClientFactory


class TestOllamaLLMClient:
    """Tests for OllamaLLMClient."""

    def test_default_config_is_applied(self):
        """Should use default config when none provided."""
        client = OllamaLLMClient()
        assert client.config.model_name  == "llama3.2"
        assert client.config.temperature == 0.0

    def test_custom_config_is_applied(self):
        """Should use provided config."""
        config = LLMConfig(
            model_name  = "mistral",
            temperature = 0.3
        )
        client = OllamaLLMClient(config)
        assert client.config.model_name  == "mistral"
        assert client.config.temperature == 0.3

    def test_repr_contains_model_name(self):
        """Repr should contain model name."""
        client = OllamaLLMClient()
        assert "llama3.2" in repr(client)

    def test_model_is_none_before_first_call(self):
        """Model should be lazily initialized."""
        client = OllamaLLMClient()
        assert client._model is None

    @patch("app.ai.llm.ollama_client.ChatOllama")
    def test_get_model_initializes_chat_ollama(self, mock_chat_ollama):
        """Should initialize ChatOllama on first call."""
        client = OllamaLLMClient()
        client.get_model()
        mock_chat_ollama.assert_called_once()

    @patch("app.ai.llm.ollama_client.ChatOllama")
    def test_get_model_caches_instance(self, mock_chat_ollama):
        """Should return same instance on subsequent calls."""
        client  = OllamaLLMClient()
        model_1 = client.get_model()
        model_2 = client.get_model()
        assert model_1 is model_2
        mock_chat_ollama.assert_called_once()

    @patch("app.ai.llm.ollama_client.ChatOllama")
    def test_health_check_returns_true_on_success(self, mock_chat_ollama):
        """Should return True when Ollama is running."""
        mock_model             = MagicMock()
        mock_chat_ollama.return_value = mock_model
        mock_model.invoke.return_value = MagicMock(content="pong")

        client = OllamaLLMClient()
        assert client.health_check() is True

    @patch("app.ai.llm.ollama_client.ChatOllama")
    def test_health_check_returns_false_when_ollama_not_running(
        self, mock_chat_ollama
    ):
        """Should return False when Ollama is not running."""
        mock_model             = MagicMock()
        mock_chat_ollama.return_value = mock_model
        mock_model.invoke.side_effect = Exception("Connection refused")

        client = OllamaLLMClient()
        assert client.health_check() is False


class TestLLMClientFactoryWithProviders:
    """Tests for LLMClientFactory provider selection."""

    def setup_method(self):
        self.factory = LLMClientFactory()
        self.factory.clear_cache()

    def test_list_providers_returns_all(self):
        """Should list all supported providers."""
        providers = self.factory.list_providers()
        assert "groq"   in providers
        assert "ollama" in providers

    def test_get_ollama_client_returns_ollama_instance(self):
        """Should return OllamaLLMClient instance."""
        client = self.factory.get_ollama_client()
        assert isinstance(client, OllamaLLMClient)

    def test_get_ollama_client_caches_instance(self):
        """Should return same instance for same config."""
        client_1 = self.factory.get_ollama_client()
        client_2 = self.factory.get_ollama_client()
        assert client_1 is client_2

    def test_get_ollama_client_custom_model(self):
        """Should apply custom model name."""
        client = self.factory.get_ollama_client(model_name="mistral")
        assert client.config.model_name == "mistral"

    @patch("app.ai.llm.factory.settings")
    def test_get_client_uses_groq_by_default(self, mock_settings):
        """Should use Groq when provider is groq."""
        mock_settings.llm_provider = "groq"
        from app.ai.llm.groq_client import GroqLLMClient
        client = self.factory.get_client()
        assert isinstance(client, GroqLLMClient)

    @patch("app.ai.llm.factory.settings")
    @patch.object(OllamaLLMClient, "health_check", return_value=True)
    def test_get_client_uses_ollama_when_configured(
        self, mock_health, mock_settings
    ):
        """Should use Ollama when provider is ollama and it is healthy."""
        mock_settings.llm_provider = "ollama"
        client = self.factory.get_client()
        assert isinstance(client, OllamaLLMClient)

    @patch("app.ai.llm.factory.settings")
    @patch.object(OllamaLLMClient, "health_check", return_value=False)
    def test_get_client_falls_back_to_groq_when_ollama_unavailable(
        self, mock_health, mock_settings
    ):
        """Should fall back to Groq when Ollama is unavailable."""
        mock_settings.llm_provider = "ollama"
        from app.ai.llm.groq_client import GroqLLMClient
        client = self.factory.get_client()
        assert isinstance(client, GroqLLMClient)