#!/usr/bin/env python3
"""
Antigravity Model Context Protocol (MCP) Server for Claude Code.
Exposes autonomous coding, consultation, and code review tools powered by Gemini (BYOK).
"""

import asyncio
import os
import sys
from typing import List, Optional

# Add package src to path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from mcp.server.fastmcp import FastMCP
from antigravity_claude.config import settings
from antigravity_claude.executor import AntigravityExecutor

# Initialize FastMCP application
mcp = FastMCP(
    name="antigravity",
    instructions=(
        "Antigravity MCP server for Claude Code. Enables autonomous software engineering, "
        "architectural consultation, and code review powered by Google Gemini (BYOK)."
    ),
)

executor = AntigravityExecutor()


@mcp.tool(
    name="antigravity_task",
    description=(
        "Executes an autonomous software engineering turn using Google Antigravity (agy). "
        "Performs codebase edits, refactoring, bash commands, and test verification in the target directory."
    ),
)
async def antigravity_task(
    task: str,
    working_dir: Optional[str] = None,
    model: str = "gemini-3.8-flash-high",
    effort: str = "high",
    gemini_api_key: Optional[str] = None,
) -> str:
    """Executes a coding task using Antigravity and returns results."""
    target_dir = working_dir or os.getcwd()
    result = await executor.execute_task(
        task_prompt=task,
        working_dir=target_dir,
        model=model,
        effort=effort,
        gemini_api_key=gemini_api_key,
    )

    if not result.success:
        return f"❌ Antigravity Task Failed ({result.elapsed_seconds}s):\n{result.error or result.summary}"

    output_lines = [
        f"✅ Antigravity Task Completed ({result.elapsed_seconds}s | Model: {result.model} | Effort: {result.effort})",
        "",
        "### Summary:",
        result.summary,
    ]

    if result.files_changed:
        output_lines.append("\n### Modified / Created Files:")
        for f in result.files_changed:
            output_lines.append(f"- `{f.file_path}` ({f.action})")

    if result.commands_executed:
        output_lines.append("\n### Commands Executed:")
        for c in result.commands_executed:
            output_lines.append(f"- `{c.command}` (exit {c.exit_code})")

    return "\n".join(output_lines)


@mcp.tool(
    name="antigravity_consult",
    description=(
        "Queries Antigravity and Gemini for an architectural second opinion, algorithm design, "
        "or deep reasoning without modifying any files on disk."
    ),
)
async def antigravity_consult(
    question: str,
    context_files: Optional[List[str]] = None,
    working_dir: Optional[str] = None,
    model: str = "gemini-3.8-flash-high",
    gemini_api_key: Optional[str] = None,
) -> str:
    """Consults Gemini via Antigravity without editing files."""
    target_dir = working_dir or os.getcwd()
    result = await executor.consult(
        question=question,
        context_files=context_files,
        working_dir=target_dir,
        model=model,
        gemini_api_key=gemini_api_key,
    )

    if not result.success:
        return f"❌ Antigravity Consultation Failed ({result.elapsed_seconds}s):\n{result.error}"

    return (
        f"💡 Antigravity Consultation ({result.elapsed_seconds}s | Model: {result.model}):\n\n"
        f"{result.advice}"
    )


@mcp.tool(
    name="antigravity_review",
    description=(
        "Conducts a comprehensive code review on the active git diff or provided code patch, "
        "checking for logic bugs, security vulnerabilities (OWASP), and performance regressions."
    ),
)
async def antigravity_review(
    diff: Optional[str] = None,
    focus: str = "all",
    working_dir: Optional[str] = None,
    model: str = "gemini-3.8-flash-high",
    gemini_api_key: Optional[str] = None,
) -> str:
    """Runs a multi-perspective code review using Antigravity."""
    target_dir = working_dir or os.getcwd()
    result = await executor.review_diff(
        diff_text=diff,
        working_dir=target_dir,
        focus=focus,
        model=model,
        gemini_api_key=gemini_api_key,
    )

    if not result.success:
        return f"❌ Code Review Failed:\n{result.error or result.summary}"

    output_lines = [
        f"🔍 Antigravity Code Review ({result.elapsed_seconds}s | Model: {result.model} | Focus: {focus})",
        "",
        result.summary,
    ]

    return "\n".join(output_lines)


@mcp.tool(
    name="antigravity_status",
    description="Checks the health and configuration of the Antigravity CLI and Gemini BYOK environment.",
)
async def antigravity_status() -> str:
    """Returns local environment diagnosis for Antigravity."""
    import shutil

    binary = executor.binary_path
    resolved = shutil.which(binary)
    has_key = bool(settings.gemini_api_key)

    lines = [
        "Antigravity Plugin Status for Claude Code:",
        f"- Antigravity Binary: `{binary}` ({'Found' if resolved else 'Missing'})",
        f"- Gemini BYOK API Key: {'Configured in Environment' if has_key else 'Not detected (pass via tool or GEMINI_API_KEY env)'}",
        f"- Default Model: `{settings.default_model}`",
        f"- Default Effort: `{settings.default_effort}`",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
