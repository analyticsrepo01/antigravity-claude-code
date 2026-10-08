"""
Data models for Antigravity responses and execution tracking.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class CommandRecord(BaseModel):
    command: str
    exit_code: int = 0
    output: Optional[str] = None


class FileDiff(BaseModel):
    file_path: str
    diff: str
    action: str = "modified"  # modified, created, deleted


class TaskResult(BaseModel):
    success: bool = True
    summary: str
    model: str
    effort: str
    elapsed_seconds: float
    files_changed: List[FileDiff] = Field(default_factory=list)
    commands_executed: List[CommandRecord] = Field(default_factory=list)
    error: Optional[str] = None


class ConsultResult(BaseModel):
    success: bool = True
    question: str
    advice: str
    model: str
    elapsed_seconds: float
    error: Optional[str] = None


class ReviewResult(BaseModel):
    success: bool = True
    summary: str
    critical_issues: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    security_concerns: List[str] = Field(default_factory=list)
    model: str
    elapsed_seconds: float
    error: Optional[str] = None
