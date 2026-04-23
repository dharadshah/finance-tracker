"""Prompt guard for wrapping prompts with security context."""
import logging
from app.ai.security.input_sanitizer import InputSanitizer, SanitizationResult
from app.exceptions.app_exceptions import ValidationError

logger = logging.getLogger("app.ai.security.prompt_guard")


class PromptGuard:
    """Guards the prompt pipeline with security checks.

    Wraps input sanitization and provides secure invoke pattern.

    Usage:
        guard  = PromptGuard()
        safe   = guard.check_input("user input")
        result = chain.invoke({"transaction": safe})
    """

    def __init__(self):
        self.sanitizer = InputSanitizer()
        self.logger    = logging.getLogger(
            "app.ai.security.PromptGuard"
        )

    def check_input(self, user_input: str) -> str:
        """Check and sanitize user input before LLM call.

        Args:
            user_input: Raw input from the user.

        Returns:
            Sanitized safe input string.

        Raises:
            ValidationError: If input is unsafe.
        """
        result = self.sanitizer.sanitize(user_input)

        if not result.is_safe:
            self.logger.warning(
                f"Unsafe input blocked: "
                f"risk={result.risk_level} "
                f"reason={result.reason}"
            )
            raise ValidationError(
                f"Input validation failed: {result.reason}"
            )

        if result.sanitized_input != user_input:
            self.logger.info("Input was sanitized before processing")

        return result.sanitized_input

    def check_and_log(self, user_input: str, context: str = "") -> SanitizationResult:
        """Check input and return full result without raising.

        Useful for logging and monitoring without blocking.

        Args:
            user_input: Raw input from the user.
            context   : Optional context for logging.

        Returns:
            SanitizationResult with full details.
        """
        result = self.sanitizer.sanitize(user_input)
        if not result.is_safe:
            self.logger.warning(
                f"Unsafe input detected"
                f"{' in ' + context if context else ''}: "
                f"risk={result.risk_level} "
                f"reason={result.reason}"
            )
        return result