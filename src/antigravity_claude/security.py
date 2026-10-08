"""
Security and key redaction utilities.
"""

import re
from pathlib import Path
from typing import Optional

# Common API key patterns
KEY_PATTERNS = [
    # Google AI Studio / Gemini Key
    (re.compile(r"AIza[0-9A-Za-z\-_]{35}"), "[REDACTED_GEMINI_KEY]"),
    # OpenAI API Key
    (re.compile(r"sk-[a-zA-Z0-9]{32,}"), "[REDACTED_OPENAI_KEY]"),
    # Anthropic API Key
    (re.compile(r"sk-ant-[a-zA-Z0-9\-_]{32,}"), "[REDACTED_ANTHROPIC_KEY]"),
    # Generic Bearer tokens
    (re.compile(r"(Bearer\s+)[A-Za-z0-9\-\._~+/]+=*", re.IGNORECASE), r"\1[REDACTED_TOKEN]"),
]


def sanitize_text(text: Optional[str]) -> str:
    """Masks secret tokens and API keys from logs and subprocess outputs."""
    if not text:
        return ""
    sanitized = text
    for pattern, replacement in KEY_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


def validate_safe_path(target_path: str, base_directory: Optional[str] = None) -> Path:
    """Ensures target path does not escape allowed workspace base directory."""
    target = Path(target_path).resolve()
    if base_directory:
        base = Path(base_directory).resolve()
        try:
            target.relative_to(base)
        except ValueError:
            raise PermissionError(f"Access denied: path '{target}' escapes workspace root '{base}'.")
    return target
