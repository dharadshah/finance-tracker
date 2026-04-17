"""LangSmith observability configuration for Finance Tracker."""
import os
import logging
from app.config.settings import settings

logger = logging.getLogger("app.config.langsmith_config")


def setup_langsmith():
    """Configure LangSmith tracing via environment variables.

    LangChain automatically reads these environment variables
    to enable tracing — no code changes needed in chains or agents.

    When enabled:
        Every chain invoke, agent node, and LLM call is traced
        and visible in the LangSmith dashboard at smith.langchain.com
    """
    if not settings.langchain_tracing_v2:
        logger.info("LangSmith tracing disabled")
        return

    if not settings.langchain_api_key:
        logger.warning(
            "LangSmith tracing enabled but LANGCHAIN_API_KEY is missing"
        )
        return

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"]   = settings.langchain_endpoint
    os.environ["LANGCHAIN_API_KEY"]    = settings.langchain_api_key
    os.environ["LANGCHAIN_PROJECT"]    = settings.langchain_project

    logger.info(
        f"LangSmith tracing enabled: "
        f"project={settings.langchain_project}, "
        f"endpoint={settings.langchain_endpoint}"
    )


def get_trace_metadata(operation: str) -> dict:
    """Return metadata dict for tagging LangSmith traces.

    Args:
        operation: Name of the operation being traced.

    Returns:
        Dict of metadata tags for the trace.
    """
    return {
        "app"         : settings.app_name,
        "version"     : settings.app_version,
        "environment" : settings.environment,
        "operation"   : operation
    }