"""Input sanitizer for Finance Tracker AI endpoints."""
import re
import logging
from dataclasses import dataclass

logger = logging.getLogger("app.ai.security.input_sanitizer")


@dataclass
class SanitizationResult:
    """Result of input sanitization.

    Attributes:
        is_safe        : True if input passed all checks.
        sanitized_input: Cleaned version of the input.
        risk_level     : none, low, medium, high.
        reason         : Why the input was flagged if not safe.
    """
    is_safe         : bool
    sanitized_input : str
    risk_level      : str  = "none"
    reason          : str  = ""


class InputSanitizer:
    """Sanitizes user input before passing to LLM.

    Defends against:
        - Prompt injection patterns
        - Excessive length inputs
        - Special character abuse
        - Encoding attacks

    Usage:
        sanitizer = InputSanitizer()
        result    = sanitizer.sanitize("user input here")
        if result.is_safe:
            chain.invoke({"transaction": result.sanitized_input})
    """

    MAX_INPUT_LENGTH = 500

    INJECTION_PATTERNS = [
        # instruction override attempts
        r"ignore\s+(previous|all|above|prior|the\s+)?\s*(previous|all|above|prior)?\s*instructions?",
        r"forget\s+(everything|all|previous|your\s+instructions?)",
        r"disregard\s+(previous|all|above|prior)\s+instructions?",
        r"you\s+are\s+now\s+a?\s*(different|new|another)",
        r"pretend\s+(you|to\s+be|that)",
        r"act\s+as\s+(if|a|an|though)",
        r"(new|different|updated|revised)\s+(instructions?|prompt|system)",

        # data extraction attempts
        r"(repeat|show|reveal|print|display|output|return)\s+(the\s+)?(system|your|all|previous)\s+(prompt|instructions?|context|data|messages?)",
        r"what\s+(are|were|is)\s+(your|the)\s+(instructions?|system\s+prompt|context)",

        # jailbreak attempts
        r"(no\s+restrictions?|without\s+restrictions?|ignore\s+restrictions?)",
        r"(bypass|override|disable)\s+(your\s+)?(safety|filter|restriction|limit)",
        r"do\s+(anything|everything|whatever)",
        r"(developer|debug|test|admin|root|sudo)\s+mode",

        # role hijacking
        r"you\s+are\s+(an?\s+)?(evil|malicious|unrestricted|unfiltered|jailbroken)",
        r"(dan|dna|jailbreak|unrestricted\s+ai|evil\s+ai)",
    ]

    def __init__(self):
        self._compiled_patterns = [
            re.compile(p, re.IGNORECASE)
            for p in self.INJECTION_PATTERNS
        ]
        self.logger = logging.getLogger(
            "app.ai.security.InputSanitizer"
        )

    def sanitize(self, user_input: str) -> SanitizationResult:
        """Sanitize user input.

        Args:
            user_input: Raw input from the user.

        Returns:
            SanitizationResult with safety assessment.
        """
        if not user_input or not user_input.strip():
            return SanitizationResult(
                is_safe         = False,
                sanitized_input = "",
                risk_level      = "low",
                reason          = "Input is empty"
            )

        # Step 1 - length check
        if len(user_input) > self.MAX_INPUT_LENGTH:
            self.logger.warning(
                f"Input exceeds max length: {len(user_input)} chars"
            )
            return SanitizationResult(
                is_safe         = False,
                sanitized_input = user_input[:self.MAX_INPUT_LENGTH],
                risk_level      = "medium",
                reason          = f"Input exceeds maximum length of {self.MAX_INPUT_LENGTH} characters"
            )

        # Step 2 - injection pattern check
        for pattern in self._compiled_patterns:
            if pattern.search(user_input):
                self.logger.warning(
                    f"Injection pattern detected: {pattern.pattern}"
                )
                return SanitizationResult(
                    is_safe         = False,
                    sanitized_input = "",
                    risk_level      = "high",
                    reason          = "Potential prompt injection detected"
                )

        # Step 3 - clean the input
        sanitized = self._clean(user_input)

        return SanitizationResult(
            is_safe         = True,
            sanitized_input = sanitized,
            risk_level      = "none",
            reason          = ""
        )

    def _clean(self, text: str) -> str:
        """Clean input of potentially dangerous characters.

        Args:
            text: Input text to clean.

        Returns:
            Cleaned text string.
        """
        # remove null bytes
        text = text.replace("\x00", "")

        # normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

        # remove control characters except newlines and tabs
        text = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

        return text