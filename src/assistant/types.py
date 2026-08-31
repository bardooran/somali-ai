"""Shared types for the Somali assistant layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from src.checker import Finding


Role = Literal["user", "assistant"]


@dataclass(frozen=True)
class ChatMessage:
    role: Role
    content: str


@dataclass(frozen=True)
class AssistantResult:
    """One assistant turn, including the evidence and checker audit trail."""

    text: str
    draft_text: str
    findings: tuple[Finding, ...]
    knowledge_paths: tuple[str, ...]
    model: str
