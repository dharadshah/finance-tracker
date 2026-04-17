"""Tests for LLM Client Factory.

Note: These tests do NOT make real API calls.
They test configuration, caching, and structure only.
"""
import pytest
from unittest.mock import MagicMock, patch
from app.ai.llm.base_client import LLMConfig
from app.ai.llm.groq_client import GroqLLMClient
from app.ai.llm.factory import LLMClientFactory


# ============================================================
# LLMConfig
# ============================================================

class TestLLMConfig:
    """Tests for LLMConfig dataclass."""

    def test_config_stores_model_name(self):
        """Should store model name correctly."""
        config = LLMConfig(model_name="llama-3.3-70b-versatile")
        assert config.model_name == "llama-3.3-70b-versatile"

    def test_config_default_temperature(self):
        """Should default temperature to 0.0."""
        config = LLMConfig(model_name="test-model")
        assert config.temperature == 0.0

    def test_config_default_max_tokens(self):
        """Should default max_tokens to 1024."""
        config = LLMConfig(model_name="test-model")
        assert config.max_tokens == 1024

    def test_config_default_timeout(self):
        """Should default timeout to 30."""
        config = LLMConfig(model_name="test-model")
        assert config.timeout == 30

    def test_config_custom_values(self):
        """Should store all custom values correctly."""
        config = LLMConfig(
            model_name  = "custom-model",
            temperature = 0.5,
            max_tokens  = 2048,
            timeout     = 60
        )
        assert config.model_name  == "custom-model"
        assert config.temperature == 0.5
        assert config.max_tokens  == 2048
        assert config.timeout     == 60


# ============================================================
# GroqLLMClient
# ============================================================

class TestGroqLLMClient:
    """Tests for GroqLLMClient."""

    def test_default_config_is_applied(self):
        """Should use default config when none provided."""
        client = GroqLLMClient()
        assert client.config.model_name  == "llama-3.3-70b-versatile"
        assert client.config.temperature == 0.0

    def test_custom_config_is_applied(self):
        """Should use provided config."""
        config = LLMConfig(
            model_name  = "custom-model",
            temperature = 0.5
        )
        client = GroqLLMClient(config)
        assert client.config.model_name  == "custom-model"
        assert client.config.temperature == 0.5

    def test_repr_contains_model_name(self):
        """Repr should contain model name."""
        client = GroqLLMClient()
        assert "llama-3.3-70b-versatile" in repr(client)

    def test_repr_contains_temperature(self):
        """Repr should contain temperature."""
        client = GroqLLMClient()
        assert "0.0" in repr(client)

    def test_model_is_none_before_first_call(self):
        """Model should be lazily initialized."""
        client = GroqLLMClient()
        assert client._model is None

    @patch("app.ai.llm.groq_client.ChatGroq")
    def test_get_model_initializes_chat_groq(self, mock_chat_groq):
        """Should initialize ChatGroq on first call."""
        client = GroqLLMClient()
        client.get_model()
        mock_chat_groq.assert_called_once()

    @patch("app.ai.llm.groq_client.ChatGroq")
    def test_get_model_caches_instance(self, mock_chat_groq):
        """Should return same instance on subsequent calls."""
        client  = GroqLLMClient()
        model_1 = client.get_model()
        model_2 = client.get_model()
        assert model_1 is model_2
        mock_chat_groq.assert_called_once()

    @patch("app.ai.llm.groq_client.ChatGroq")
    def test_get_model_uses_correct_config(self, mock_chat_groq):
        """Should pass correct config to ChatGroq."""
        config = LLMConfig(
            model_name  = "test-model",
            temperature = 0.5,
            max_tokens  = 512,
            timeout     = 10
        )
        client = GroqLLMClient(config)
        client.get_model()

        _, kwargs = mock_chat_groq.call_args
        assert kwargs["model"]       == "test-model"
        assert kwargs["temperature"] == 0.5
        assert kwargs["max_tokens"]  == 512
        assert kwargs["timeout"]     == 10
        assert "api_key" in kwargs

    @patch("app.ai.llm.groq_client.ChatGroq")
    def test_health_check_returns_true_on_success(self, mock_chat_groq):
        """Should return True when API is reachable."""
        mock_model          = MagicMock()
        mock_chat_groq.return_value = mock_model
        mock_model.invoke.return_value = MagicMock(content="pong")

        client = GroqLLMClient()
        assert client.health_check() is True

    @patch("app.ai.llm.groq_client.ChatGroq")
    def test_health_check_returns_false_on_failure(self, mock_chat_groq):
        """Should return False when API is unreachable."""
        mock_model          = MagicMock()
        mock_chat_groq.return_value = mock_model
        mock_model.invoke.side_effect = Exception("Connection error")

        client = GroqLLMClient()
        assert client.health_check() is False


# ============================================================
# LLMClientFactory
# ============================================================

class TestLLMClientFactory:
    """Tests for LLMClientFactory."""

    def setup_method(self):
        """Clear cache before each test."""
        self.factory = LLMClientFactory()
        self.factory.clear_cache()

    def test_get_groq_client_returns_groq_instance(self):
        """Should return GroqLLMClient instance."""
        client = self.factory.get_groq_client()
        assert isinstance(client, GroqLLMClient)

    def test_get_groq_client_uses_default_model(self):
        """Should use default model from app_constants."""
        from app.constants.app_constants import GROQ_CHAT_MODEL
        client = self.factory.get_groq_client()
        assert client.config.model_name == GROQ_CHAT_MODEL.MODEL_NAME.value

    def test_get_groq_client_caches_instance(self):
        """Should return same instance for same config."""
        client_1 = self.factory.get_groq_client()
        client_2 = self.factory.get_groq_client()
        assert client_1 is client_2

    def test_get_groq_client_different_models_different_instances(self):
        """Should return different instances for different models."""
        client_1 = self.factory.get_groq_client(model_name="model-a")
        client_2 = self.factory.get_groq_client(model_name="model-b")
        assert client_1 is not client_2

    def test_get_groq_client_custom_temperature(self):
        """Should apply custom temperature."""
        client = self.factory.get_groq_client(temperature=0.7)
        assert client.config.temperature == 0.7

    def test_get_groq_client_custom_max_tokens(self):
        """Should apply custom max tokens."""
        client = self.factory.get_groq_client(max_tokens=2048)
        assert client.config.max_tokens == 2048

    def test_clear_cache_removes_instances(self):
        """Should clear all cached instances."""
        self.factory.get_groq_client()
        self.factory.clear_cache()
        assert len(self.factory._instances) == 0

    def test_after_clear_cache_new_instance_created(self):
        """Should create new instance after cache is cleared."""
        client_1 = self.factory.get_groq_client()
        self.factory.clear_cache()
        client_2 = self.factory.get_groq_client()
        assert client_1 is not client_2

    def test_module_level_factory_is_correct_type(self):
        """Module level llm_factory should be LLMClientFactory instance."""
        from app.ai.llm.factory import llm_factory
        assert isinstance(llm_factory, LLMClientFactory)