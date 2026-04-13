"""Logging configuration for Personal Finance Tracker."""
import json
import logging
import os
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """Custom formatter that outputs log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a JSON string.

        Args:
            record: The log record to format.

        Returns:
            JSON-encoded string representation of the log entry.
        """
        log_entry = {
            "timestamp" : datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level"     : record.levelname,
            "logger"    : record.name,
            "message"   : record.getMessage(),
            "module"    : record.module,
            "function"  : record.funcName,
            "line"      : record.lineno,
            "env"       : os.getenv("ENVIRONMENT", "dev")
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        if record.stack_info:
            log_entry["stack"] = self.formatStack(record.stack_info)

        return json.dumps(log_entry, ensure_ascii=True)


def setup_logging():
    """Configure application-wide logging."""
    environment = os.getenv("ENVIRONMENT", "dev")
    log_level   = logging.DEBUG if environment == "dev" else logging.INFO

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    logging.basicConfig(
        level    = log_level,
        handlers = [handler]
    )

    # Suppress noisy third-party loggers
    noisy_loggers = [
        "httpx",
        "httpcore",
        "uvicorn.access",
        "sqlalchemy.engine",
        "langchain.agents.agent_iterator",
        "urllib3.connectionpool",
        "sentence_transformers",
        "transformers",
        "tokenizers",
        "filelock",
        "groq",
        "openai",
        "openai._base_client"
    ]

    for name in noisy_loggers:
        logging.getLogger(name).setLevel(logging.WARNING)


# module level logger
logger = logging.getLogger("app")