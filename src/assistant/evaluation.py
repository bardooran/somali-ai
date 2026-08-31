"""Capability evaluation harness for the Somali-first assistant.

The harness records real model outputs and performs only objective structural
checks automatically. Semantic quality remains explicitly reviewable; it is not
faked with brittle keyword scoring.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from .pipeline import ConversationSession, SomaliAssistant


DEFAULT_CASES_PATH = Path("data/qa/somali_assistant_capabilities.jsonl")


@dataclass(frozen=True)
class CapabilityCase:
    id: str
    category: str
    turns: tuple[str, ...]
    minimum_final_words: int
    criteria: tuple[str, ...]
    expected_language: str = "so"


@dataclass(frozen=True)
class CapabilityRun:
    id: str
    category: str
    turns: tuple[str, ...]
    responses: tuple[str, ...]
    final_word_count: int
    structural_pass: bool
    criteria: tuple[str, ...]
    expected_language: str
    review_required: bool
    model: str
    knowledge_paths: tuple[str, ...]


def _case_from_dict(item: dict) -> CapabilityCase:
    turns = item.get("turns")
    if not isinstance(turns, list) or not turns or not all(isinstance(x, str) and x.strip() for x in turns):
        raise ValueError("capability case requires non-empty string turns")
    criteria = item.get("criteria", [])
    if not isinstance(criteria, list) or not all(isinstance(x, str) for x in criteria):
        raise ValueError("criteria must be a list of strings")
    return CapabilityCase(
        id=str(item["id"]),
        category=str(item["category"]),
        turns=tuple(x.strip() for x in turns),
        minimum_final_words=int(item.get("minimum_final_words", 1)),
        criteria=tuple(criteria),
        expected_language=str(item.get("expected_language", "so")),
    )


def load_capability_cases(path: str | Path = DEFAULT_CASES_PATH) -> tuple[CapabilityCase, ...]:
    cases: list[CapabilityCase] = []
    seen: set[str] = set()
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                case = _case_from_dict(json.loads(stripped))
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise ValueError(f"invalid capability case on line {line_number}: {exc}") from exc
            if case.id in seen:
                raise ValueError(f"duplicate capability case id: {case.id}")
            if case.minimum_final_words < 1:
                raise ValueError(f"minimum_final_words must be positive: {case.id}")
            seen.add(case.id)
            cases.append(case)
    return tuple(cases)


def run_capability_case(assistant: SomaliAssistant, case: CapabilityCase) -> CapabilityRun:
    session = ConversationSession(assistant)
    responses: list[str] = []
    paths: set[str] = set()
    model = assistant.model.model_name
    for turn in case.turns:
        result = session.ask(turn)
        responses.append(result.text)
        paths.update(result.knowledge_paths)
        model = result.model

    final = responses[-1] if responses else ""
    word_count = len(final.split())
    structural_pass = bool(final.strip()) and word_count >= case.minimum_final_words
    return CapabilityRun(
        id=case.id,
        category=case.category,
        turns=case.turns,
        responses=tuple(responses),
        final_word_count=word_count,
        structural_pass=structural_pass,
        criteria=case.criteria,
        expected_language=case.expected_language,
        review_required=True,
        model=model,
        knowledge_paths=tuple(sorted(paths)),
    )


def run_capability_suite(
    assistant: SomaliAssistant,
    cases: Iterable[CapabilityCase],
) -> tuple[CapabilityRun, ...]:
    return tuple(run_capability_case(assistant, case) for case in cases)


def write_capability_runs(runs: Iterable[CapabilityRun], path: str | Path) -> int:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output.open("w", encoding="utf-8") as handle:
        for run in runs:
            handle.write(json.dumps(asdict(run), ensure_ascii=False, sort_keys=True))
            handle.write("\n")
            count += 1
    return count
