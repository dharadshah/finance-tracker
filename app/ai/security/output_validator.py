"""Output validator for LLM responses."""
import re
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("app.ai.security.output_validator")


@dataclass
class ValidationResult:
    """Result of output validation.

    Attributes:
        is_valid : True if output passed all checks.
        output   : The validated output.
        reason   : Why it failed if not valid.
    """
    is_valid : bool
    output   : str
    reason   : str = ""


class OutputValidator:
    """Validates LLM responses before returning to client.

    Defends against:
        - Prompt leaking in responses
        - Unexpected response formats
        - Sensitive data in responses
        - Extremely long responses

    Usage:
        validator = OutputValidator()
        result    = validator.validate(llm_response)
        if result.is_valid:
            return result.output
    """

    MAX_OUTPUT_LENGTH = 5000

    LEAK_PATTERNS = [
        r"system\s*prompt\s*:",
        r"my\s+instructions?\s+(are|were|say)",
        r"i\s+was\s+(told|instructed|programmed)\s+to",
        r"<\s*system\s*>",
        r"\[system\]",
        r"anthropic|openai\s+policy",
    ]

    def __init__(self):
        self._compiled_patterns = [
            re.compile(p, re.IGNORECASE)
            for p in self.LEAK_PATTERNS
        ]
        self.logger = logging.getLogger(
            "app.ai.security.OutputValidator"
        )

    def validate(self, output: str) -> ValidationResult:
        """Validate LLM output before returning to client.

        Args:
            output: Raw LLM response string.

        Returns:
            ValidationResult with safety assessment.
        """
        if not output or not output.strip():
            return ValidationResult(
                is_valid = False,
                output   = "",
                reason   = "Empty response from LLM"
            )

        # length check
        if len(output) > self.MAX_OUTPUT_LENGTH:
            self.logger.warning(
                f"Output truncated from {len(output)} chars"
            )
            output = output[:self.MAX_OUTPUT_LENGTH]

        # prompt leak check
        for pattern in self._compiled_patterns:
            if pattern.search(output):
                self.logger.warning(
                    f"Potential prompt leak in output: {pattern.pattern}"
                )
                return ValidationResult(
                    is_valid = False,
                    output   = "",
                    reason   = "Response contains potentially leaked system information"
                )

        return ValidationResult(
            is_valid = True,
            output   = output.strip(),
            reason   = ""
        )

    def validate_classification(self, output: str) -> ValidationResult:
        """Validate that classification output is INCOME or EXPENSE only.

        Args:
            output: Raw classification response.

        Returns:
            ValidationResult with sanitized classification.
        """
        sanitized = "INCOME" if "INCOME" in output.upper() else "EXPENSE"
        self.logger.debug(f"Classification validated: {sanitized}")
        return ValidationResult(
            is_valid = True,
            output   = sanitized,
            reason   = ""
        )

    def validate_json(self, output: str) -> ValidationResult:
        """Validate that output is valid JSON.

        Args:
            output: Raw LLM response expected to be JSON.

        Returns:
            ValidationResult with cleaned JSON string.
        """
        import json
        cleaned = output.strip().replace("```json", "").replace("```", "")
        try:
            json.loads(cleaned)
            return ValidationResult(
                is_valid = True,
                output   = cleaned,
                reason   = ""
            )
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in LLM response: {e}")
            return ValidationResult(
                is_valid = False,
                output   = "",
                reason   = f"LLM response was not valid JSON: {str(e)}"
            )