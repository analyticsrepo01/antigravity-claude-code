"""
Antigravity subprocess executor with Gemini BYOK injection and diff tracking.
"""

import asyncio
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import List, Optional, Tuple

from antigravity_claude.config import settings
from antigravity_claude.models import (
    CommandRecord,
    ConsultResult,
    FileDiff,
    ReviewResult,
    TaskResult,
)
from antigravity_claude.security import sanitize_text, validate_safe_path


class AntigravityExecutor:
    """Executes Antigravity operations with Gemini API Key injection."""

    def __init__(self, binary_path: Optional[str] = None):
        self.binary_path = binary_path or settings.agy_binary_path
        resolved = shutil.which(self.binary_path)
        if resolved:
            self.binary_path = resolved

    def _get_git_diff(self, working_dir: Path) -> List[FileDiff]:
        """Inspects git changes in working directory before and after execution."""
        diffs = []
        try:
            # Check modified / added tracked files
            result = subprocess.run(
                ["git", "diff", "--stat", "--patch", "HEAD"],
                cwd=str(working_dir),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout:
                # Basic parsing
                diffs.append(
                    FileDiff(
                        file_path="workspace",
                        diff=result.stdout[:15000],  # cap length
                        action="modified",
                    )
                )

            # Check untracked files
            untracked = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                cwd=str(working_dir),
                capture_output=True,
                text=True,
                timeout=5,
            )
            if untracked.returncode == 0 and untracked.stdout.strip():
                for f in untracked.stdout.strip().split("\n")[:10]:
                    diffs.append(FileDiff(file_path=f, diff="", action="created"))
        except Exception:
            pass
        return diffs

    async def execute_task(
        self,
        task_prompt: str,
        working_dir: Optional[str] = None,
        model: Optional[str] = None,
        effort: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> TaskResult:
        """Runs an autonomous coding turn in working_dir."""
        target_dir = validate_safe_path(working_dir or os.getcwd())
        chosen_model = model or settings.default_model
        chosen_effort = effort or settings.default_effort
        api_key = gemini_api_key or settings.gemini_api_key
        time_limit = timeout or settings.task_timeout_seconds

        start_time = time.time()

        env = os.environ.copy()
        if api_key:
            env["GEMINI_API_KEY"] = api_key
            env["modelProvider"] = "gemini"

        cmd = [
            self.binary_path,
            "--print", task_prompt,
            "--model", chosen_model,
            "--effort", chosen_effort,
            "--output-format", "json",
            "--dangerously-skip-permissions",
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(target_dir),
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(),
                timeout=float(time_limit),
            )
            raw_stdout = stdout_bytes.decode(errors="replace")
            raw_stderr = stderr_bytes.decode(errors="replace")
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except Exception:
                pass
            return TaskResult(
                success=False,
                summary="Execution timed out",
                model=chosen_model,
                effort=chosen_effort,
                elapsed_seconds=round(time.time() - start_time, 2),
                error=f"Task exceeded timeout of {time_limit}s",
            )
        except FileNotFoundError:
            return TaskResult(
                success=False,
                summary="Antigravity binary not found",
                model=chosen_model,
                effort=chosen_effort,
                elapsed_seconds=round(time.time() - start_time, 2),
                error=f"Executable '{self.binary_path}' not found. Ensure agy is installed.",
            )

        elapsed = round(time.time() - start_time, 2)
        clean_stdout = sanitize_text(raw_stdout)
        clean_stderr = sanitize_text(raw_stderr)

        if proc.returncode != 0:
            error_msg = clean_stderr or clean_stdout or f"Process exited with code {proc.returncode}"
            return TaskResult(
                success=False,
                summary="Antigravity execution failed",
                model=chosen_model,
                effort=chosen_effort,
                elapsed_seconds=elapsed,
                error=error_msg,
            )

        summary = clean_stdout.strip()
        files_changed = self._get_git_diff(target_dir)
        commands_executed: List[CommandRecord] = []

        try:
            parsed = json.loads(clean_stdout)
            if isinstance(parsed, dict):
                summary = parsed.get("summary") or parsed.get("response") or clean_stdout
                if "files" in parsed and isinstance(parsed["files"], list):
                    for f in parsed["files"]:
                        files_changed.append(FileDiff(file_path=str(f), diff="", action="modified"))
                if "commands" in parsed and isinstance(parsed["commands"], list):
                    for c in parsed["commands"]:
                        commands_executed.append(CommandRecord(command=str(c)))
        except Exception:
            pass

        return TaskResult(
            success=True,
            summary=summary,
            model=chosen_model,
            effort=chosen_effort,
            elapsed_seconds=elapsed,
            files_changed=files_changed,
            commands_executed=commands_executed,
        )

    async def consult(
        self,
        question: str,
        context_files: Optional[List[str]] = None,
        working_dir: Optional[str] = None,
        model: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
    ) -> ConsultResult:
        """Consults Antigravity/Gemini for reasoning or second opinion without editing files."""
        target_dir = validate_safe_path(working_dir or os.getcwd())
        chosen_model = model or settings.default_model
        api_key = gemini_api_key or settings.gemini_api_key
        start_time = time.time()

        consult_prompt = (
            f"You are acting as an expert architectural consultant and second opinion reviewer.\n"
            f"DO NOT modify any files or execute shell commands.\n\n"
            f"Question / Query:\n{question}\n"
        )

        if context_files:
            file_snippets = []
            for cf in context_files[:5]:
                p = (target_dir / cf).resolve()
                if p.exists() and p.is_file():
                    try:
                        content = p.read_text(errors="replace")[:4000]
                        file_snippets.append(f"--- File: {cf} ---\n{content}\n")
                    except Exception:
                        pass
            if file_snippets:
                consult_prompt += "\nRelevant File Context:\n" + "\n".join(file_snippets)

        env = os.environ.copy()
        if api_key:
            env["GEMINI_API_KEY"] = api_key
            env["modelProvider"] = "gemini"

        cmd = [
            self.binary_path,
            "--print", consult_prompt,
            "--model", chosen_model,
            "--effort", "high",
            "--output-format", "text",
            "--mode", "plan",
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(target_dir),
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(),
                timeout=float(settings.consult_timeout_seconds),
            )
            raw_stdout = stdout_bytes.decode(errors="replace")
            clean_stdout = sanitize_text(raw_stdout)
            elapsed = round(time.time() - start_time, 2)

            return ConsultResult(
                success=(proc.returncode == 0),
                question=question,
                advice=clean_stdout.strip(),
                model=chosen_model,
                elapsed_seconds=elapsed,
            )
        except Exception as e:
            return ConsultResult(
                success=False,
                question=question,
                advice="",
                model=chosen_model,
                elapsed_seconds=round(time.time() - start_time, 2),
                error=sanitize_text(str(e)),
            )

    async def review_diff(
        self,
        diff_text: Optional[str] = None,
        working_dir: Optional[str] = None,
        focus: str = "all",
        model: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
    ) -> ReviewResult:
        """Performs a multi-perspective code and security review on diffs."""
        target_dir = validate_safe_path(working_dir or os.getcwd())
        start_time = time.time()
        chosen_model = model or settings.default_model

        if not diff_text:
            try:
                res = subprocess.run(
                    ["git", "diff", "HEAD"],
                    cwd=str(target_dir),
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                diff_text = res.stdout if res.returncode == 0 else ""
            except Exception:
                diff_text = ""

        if not diff_text or not diff_text.strip():
            return ReviewResult(
                success=True,
                summary="No active git diff found in the current workspace to review.",
                model=chosen_model,
                elapsed_seconds=0.1,
            )

        review_prompt = (
            f"You are a Principal Software Engineer conducting a thorough code review.\n"
            f"Focus Area: {focus}\n"
            f"Evaluate the following code changes for:\n"
            f"1. Functional correctness & logic bugs\n"
            f"2. Security vulnerabilities (OWASP, injections, leaks)\n"
            f"3. Performance regressions & edge cases\n\n"
            f"```diff\n{diff_text[:12000]}\n```\n\n"
            f"Provide a structured review with: Summary, Critical Issues, and Suggested Improvements."
        )

        res = await self.consult(
            question=review_prompt,
            working_dir=str(target_dir),
            model=chosen_model,
            gemini_api_key=gemini_api_key,
        )

        critical: List[str] = []
        improvements: List[str] = []
        security: List[str] = []

        if res.advice:
            lines = res.advice.split("\n")
            for line in lines:
                lower = line.lower()
                if "critical" in lower or "bug" in lower or "error" in lower:
                    if len(critical) < 5 and line.strip().startswith(("-", "*", "1", "2", "3")):
                        critical.append(line.strip())
                elif "security" in lower or "leak" in lower or "vuln" in lower:
                    if len(security) < 5 and line.strip().startswith(("-", "*", "1", "2", "3")):
                        security.append(line.strip())
                elif "suggest" in lower or "improve" in lower:
                    if len(improvements) < 5 and line.strip().startswith(("-", "*", "1", "2", "3")):
                        improvements.append(line.strip())

        return ReviewResult(
            success=res.success,
            summary=res.advice or "Review completed.",
            critical_issues=critical,
            improvements=improvements,
            security_concerns=security,
            model=chosen_model,
            elapsed_seconds=round(time.time() - start_time, 2),
            error=res.error,
        )
