"""Security Sanitization: User-Provided Text as Data, Not Instructions (EPIC-17-T08).

Prevents prompt injection, jailbreaks, and command escape attacks by treating
all user inputs as data parameters rather than instruction overrides.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

INJECTION_PATTERNS = [
    r"(?i)ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions",
    r"(?i)system\s*:\s*",
    r"(?i)disregard\s+(?:the\s+)?above",
    r"(?i)you\s+are\s+now\s+(?:in\s+)?(?:developer|jailbreak|dan)\s+mode",
    r"(?i)override\s+(?:system\s+)?prompt",
    r"(?i)<\s*/?\s*script",
    r"(?i)drop\s+table",
    r"(?i)union\s+select",
]


@dataclass
class SanitizedInput:
    original_text: str
    cleaned_text: str
    is_suspicious: bool
    detected_threats: list[str]
    safe_data_payload: str


class InputSanitizer:
    """Sanitizes user input for Copilot agent queries."""

    @staticmethod
    def sanitize(text: str) -> SanitizedInput:
        """Inspect and sanitize input, neutralizing prompt injection attacks."""
        if not text:
            return SanitizedInput(
                original_text="",
                cleaned_text="",
                is_suspicious=False,
                detected_threats=[],
                safe_data_payload="",
            )

        detected: list[str] = []
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, text):
                detected.append(pattern)

        # Strip control characters and dangerous delimiters
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

        # Neutralize common markdown/injection backticks and delimiters
        cleaned = cleaned.replace("```", "'''")

        # Wrap in unambiguous data encapsulation
        safe_payload = f"<user_data>\n{html.escape(cleaned.strip())}\n</user_data>"

        return SanitizedInput(
            original_text=text,
            cleaned_text=cleaned.strip(),
            is_suspicious=len(detected) > 0,
            detected_threats=detected,
            safe_data_payload=safe_payload,
        )
