"""End-to-end Somali assistant orchestration."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from datetime import datetime
from pathlib import Path

from src.checker import Rule, apply_safe_fixes, check_text, load_rules

from .model import ModelAdapter
from .prompts import build_instructions
from .retrieval import KnowledgeIndex
from .types import AssistantResult, ChatMessage


DEFAULT_RESPONSE_RULE_DIRS = (
    Path("rules/orthography"),
    Path("rules/variants"),
)
DEFAULT_HISTORY_MESSAGES = 60


def load_response_rules(
    paths: Iterable[str | Path] = DEFAULT_RESPONSE_RULE_DIRS,
) -> tuple[Rule, ...]:
    rules: list[Rule] = []
    for path_value in paths:
        path = Path(path_value)
        if path.exists():
            rules.extend(load_rules(path))
    return tuple(rules)


def _local_now() -> datetime:
    return datetime.now().astimezone()


class SomaliAssistant:
    """A Somali-first reasoning model wrapped with project retrieval and checking."""

    def __init__(
        self,
        model: ModelAdapter,
        *,
        knowledge: KnowledgeIndex | None = None,
        response_rules: Sequence[Rule] | None = None,
        evidence_limit: int = 8,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.model = model
        self.knowledge = knowledge if knowledge is not None else KnowledgeIndex.build()
        self.response_rules = (
            tuple(response_rules) if response_rules is not None else load_response_rules()
        )
        self.evidence_limit = evidence_limit
        self.clock = clock or _local_now

    def ask(
        self,
        user_text: str,
        *,
        history: Sequence[ChatMessage] = (),
    ) -> AssistantResult:
        stripped = user_text.strip()
        if not stripped:
            raise ValueError("user_text must not be empty")

        hits = self.knowledge.search(stripped, limit=self.evidence_limit)
        instructions = build_instructions(hits, current_time=self.clock())
        messages = [*history, ChatMessage(role="user", content=stripped)]
        draft = self.model.generate(messages, instructions).strip()
        if not draft:
            raise RuntimeError("Model returned an empty response.")

        findings = tuple(check_text(draft, self.response_rules))
        final_text = apply_safe_fixes(draft, findings)

        return AssistantResult(
            text=final_text,
            draft_text=draft,
            findings=findings,
            knowledge_paths=tuple(hit.path for hit in hits),
            model=self.model.model_name,
        )


class ConversationSession:
    """In-process conversation history for CLI/API callers.

    History is kept as complete user/assistant pairs. The default keeps thirty
    turns, which is substantially deeper than the first MVP while remaining
    bounded for predictable request size.
    """

    def __init__(
        self,
        assistant: SomaliAssistant,
        max_messages: int = DEFAULT_HISTORY_MESSAGES,
    ) -> None:
        if max_messages < 2:
            raise ValueError("max_messages must be at least 2")
        if max_messages % 2:
            raise ValueError("max_messages must be even so conversation turns stay paired")
        self.assistant = assistant
        self.max_messages = max_messages
        self._history: list[ChatMessage] = []

    @property
    def history(self) -> tuple[ChatMessage, ...]:
        return tuple(self._history)

    def clear(self) -> None:
        self._history.clear()

    def ask(self, user_text: str) -> AssistantResult:
        result = self.assistant.ask(user_text, history=self.history)
        self._history.append(ChatMessage(role="user", content=user_text.strip()))
        self._history.append(ChatMessage(role="assistant", content=result.text))
        if len(self._history) > self.max_messages:
            self._history = self._history[-self.max_messages :]
        return result
