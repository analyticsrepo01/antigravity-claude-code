"""
Unit tests for Antigravity Claude Code plugin.
"""

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest

# Ensure repo root and src are on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from antigravity_claude.config import Settings
from antigravity_claude.executor import AntigravityExecutor
from antigravity_claude.security import sanitize_text, validate_safe_path
from servers.antigravity_mcp import antigravity_status, mcp


def test_security_sanitization():
    """Tests API key and secret redaction."""
    gemini_sample = "Error with key AIzaSyD3x91abcdefghijklmnopqrstuvwxyz123 occurred"
    sanitized = sanitize_text(gemini_sample)
    assert "[REDACTED_GEMINI_KEY]" in sanitized
    assert "AIzaSy" not in sanitized

    openai_sample = "Using sk-abcdefghijklmnopqrstuvwxyz1234567890123"
    sanitized = sanitize_text(openai_sample)
    assert "[REDACTED_OPENAI_KEY]" in sanitized

    bearer_sample = "Authorization: Bearer mySecretToken1234567890"
    sanitized = sanitize_text(bearer_sample)
    assert "[REDACTED_TOKEN]" in sanitized


def test_path_traversal_prevention(tmp_path):
    """Ensures paths escaping the base directory are rejected."""
    base_dir = tmp_path / "workspace"
    base_dir.mkdir()

    safe_file = base_dir / "app.py"
    safe_file.touch()
    assert validate_safe_path(str(safe_file), str(base_dir)) == safe_file.resolve()

    escaping_path = tmp_path / "other" / "secrets.txt"
    with pytest.raises(PermissionError):
        validate_safe_path(str(escaping_path), str(base_dir))


def test_antigravity_status_tool():
    """Tests the antigravity_status tool."""
    status_msg = asyncio.run(antigravity_status())
    assert "Antigravity Plugin Status for Claude Code:" in status_msg
    assert "Antigravity Binary:" in status_msg
    assert "Default Model:" in status_msg


def test_executor_task_success(tmp_path):
    """Tests simulated task execution through the executor."""
    executor = AntigravityExecutor()

    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = (
        b'{"summary": "Created sample.py and ran tests", "files": ["sample.py"], "commands": ["pytest"]}',
        b"",
    )

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        result = asyncio.run(
            executor.execute_task(
                task_prompt="Create sample script",
                working_dir=str(tmp_path),
                model="gemini-3.8-flash-high",
                gemini_api_key="AIzaSyMockKeyForTestingOnly123456789",
            )
        )

        assert result.success is True
        assert "Created sample.py" in result.summary
        assert any(f.file_path == "sample.py" for f in result.files_changed)


def test_executor_error_handling(tmp_path):
    """Tests error propagation when agy exits with non-zero code."""
    executor = AntigravityExecutor()

    mock_proc = AsyncMock()
    mock_proc.returncode = 1
    mock_proc.communicate.return_value = (
        b"",
        b"RESOURCE_EXHAUSTED: Rate limit exceeded for key AIzaSyD3x91abcdefghijklmnopqrstuvwxyz123",
    )

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        result = asyncio.run(
            executor.execute_task(
                task_prompt="Run heavy task",
                working_dir=str(tmp_path),
            )
        )

        assert result.success is False
        assert "[REDACTED_GEMINI_KEY]" in result.error
        assert "AIzaSy" not in result.error
