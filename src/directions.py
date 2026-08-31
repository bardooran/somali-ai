"""Exact reviewed Somali direction/location vocabulary lookup."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DIRECTION_TERMS_PATH = Path("data/vocabulary/somali_direction_terms.jsonl")


@dataclass(frozen=True)
class DirectionAnalysis:
    expression: str
    recognized: bool
    meaning: str | None
    status: str
    note: str


def _load_records(path: str | Path = DIRECTION_TERMS_PATH) -> list[dict]:
    records: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def analyze_direction_term(expression: str, path: str | Path = DIRECTION_TERMS_PATH) -> DirectionAnalysis:
    query = expression.strip()
    folded = query.casefold()
    for record in _load_records(path):
        if record.get("lemma", "").casefold() != folded:
            continue
        status = record.get("status", "reviewed")
        return DirectionAnalysis(
            expression=query,
            recognized=True,
            meaning=record.get("meaning"),
            status=status,
            note=(
                "Reviewed direction/location term; sentence meaning may still require context."
                if "context_sensitive" in status
                else "Reviewed direction/location term."
            ),
        )
    return DirectionAnalysis(
        expression=query,
        recognized=False,
        meaning=None,
        status="unknown_unjudged",
        note="Direction/location term is outside the reviewed dataset; no meaning is guessed.",
    )
