"""Conservative analyzer for explicitly reviewed Somali question constructions.

The analyzer recognizes only whole question patterns that have project evidence.
It returns grammatical roles and confidence metadata but never rewrites text.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

QUESTION_PATH = Path("rules/grammar/question_patterns.jsonl")


@dataclass(frozen=True)
class QuestionAnalysis:
    text: str
    recognized: bool
    rule_id: str | None
    status: str | None
    subject_person: int | None
    subject_number: str | None
    subject_gender: str | None
    object_clitic: str | None
    object_person: int | None
    object_number: str | None
    aspect: str | None
    marker: str | None
    executable: bool
    note: str


def _normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def _load(path: str | Path = QUESTION_PATH) -> list[dict]:
    records: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def analyze_question(text: str, path: str | Path = QUESTION_PATH) -> QuestionAnalysis:
    normalized = _normalize(text)
    for record in _load(path):
        if _normalize(record["surface"]) != normalized:
            continue
        status = record.get("status")
        marker = record.get("question_marker_surface") or record.get("question_marker") or record.get("surface_fusion")
        subject_gender = record.get("subject_gender") or record.get("understood_subject_gender")
        return QuestionAnalysis(
            text=text,
            recognized=True,
            rule_id=record.get("id"),
            status=status,
            subject_person=record.get("subject_person"),
            subject_number=record.get("subject_number"),
            subject_gender=subject_gender,
            object_clitic=record.get("object_clitic"),
            object_person=record.get("object_person"),
            object_number=record.get("object_number"),
            aspect=record.get("aspect"),
            marker=marker,
            executable=status != "context_required",
            note=(
                "Question matches a reviewed construction. Roles may be used for analysis, not autocorrection."
                if status != "context_required"
                else "Question is recorded as native evidence, but its exact grammatical analysis remains context-required."
            ),
        )
    return QuestionAnalysis(text, False, None, None, None, None, None, None, None, None, None, None, False, "Question is outside the currently reviewed question patterns.")
