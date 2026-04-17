"""Tests for LangSmith configuration."""
import pytest
import os
from unittest.mock import patch


class TestSetupLangsmith:
    """Tests for setup_langsmith()."""

    def test_langsmith_disabled_when_tracing_false(self):
        """Should not set env vars when tracing is disabled."""
        os.environ.pop("LANGCHAIN_TRACING_V2", None)

        with patch("app.config.langsmith_config.settings") as mock_settings:
            mock_settings.langchain_tracing_v2 = False
            from app.config.langsmith_config import setup_langsmith
            setup_langsmith()
            assert os.environ.get("LANGCHAIN_TRACING_V2") != "true"

    def test_langsmith_warns_when_api_key_missing(self, caplog):
        """Should log warning when API key is missing."""
        import logging
        with patch("app.config.langsmith_config.settings") as mock_settings:
            mock_settings.langchain_tracing_v2 = True
            mock_settings.langchain_api_key    = ""
            from app.config.langsmith_config import setup_langsmith
            with caplog.at_level(logging.WARNING):
                setup_langsmith()
            assert any("missing" in r.message.lower() for r in caplog.records)

    def test_langsmith_sets_env_vars_when_enabled(self):
        """Should set all required env vars when properly configured."""
        with patch("app.config.langsmith_config.settings") as mock_settings:
            mock_settings.langchain_tracing_v2 = True
            mock_settings.langchain_api_key    = "test-key"
            mock_settings.langchain_endpoint   = "https://api.smith.langchain.com"
            mock_settings.langchain_project    = "test-project"
            mock_settings.app_name             = "Test App"
            mock_settings.app_version          = "1.0.0"
            mock_settings.environment          = "dev"

            from app.config.langsmith_config import setup_langsmith
            setup_langsmith()

            assert os.environ.get("LANGCHAIN_TRACING_V2") == "true"
            assert os.environ.get("LANGCHAIN_API_KEY")    == "test-key"
            assert os.environ.get("LANGCHAIN_PROJECT")    == "test-project"


class TestGetTraceMetadata:
    """Tests for get_trace_metadata()."""

    def test_returns_dict(self):
        """Should return a dict."""
        from app.config.langsmith_config import get_trace_metadata
        result = get_trace_metadata("test_operation")
        assert isinstance(result, dict)

    def test_contains_operation(self):
        """Should contain operation key."""
        from app.config.langsmith_config import get_trace_metadata
        result = get_trace_metadata("classify_transaction")
        assert result["operation"] == "classify_transaction"

    def test_contains_app_name(self):
        """Should contain app name."""
        from app.config.langsmith_config import get_trace_metadata
        result = get_trace_metadata("test")
        assert "app" in result

    def test_contains_environment(self):
        """Should contain environment."""
        from app.config.langsmith_config import get_trace_metadata
        result = get_trace_metadata("test")
        assert "environment" in result

    def test_contains_version(self):
        """Should contain version."""
        from app.config.langsmith_config import get_trace_metadata
        result = get_trace_metadata("test")
        assert "version" in result