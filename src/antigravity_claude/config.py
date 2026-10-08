"""
Configuration settings for Antigravity Claude Code plugin.
"""

import os
import shutil
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Gemini API Key (BYOK)
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

    # Path to Google Antigravity binary (`agy`)
    agy_binary_path: str = (
        os.getenv("AGY_BINARY_PATH")
        or shutil.which("agy")
        or str(Path.home() / ".local" / "bin" / "agy")
        or str(Path.home() / ".gemini" / "antigravity-cli" / "bin" / "agy")
        or "agy"
    )

    # Default model and reasoning effort
    default_model: str = os.getenv("ANTIGRAVITY_MODEL", "gemini-3.8-flash-high")
    default_effort: str = os.getenv("ANTIGRAVITY_EFFORT", "high")

    # Timeouts (in seconds)
    task_timeout_seconds: int = int(os.getenv("ANTIGRAVITY_TIMEOUT", "600"))
    consult_timeout_seconds: int = int(os.getenv("ANTIGRAVITY_CONSULT_TIMEOUT", "180"))

    # Security
    redact_sensitive_keys: bool = True


settings = Settings()
