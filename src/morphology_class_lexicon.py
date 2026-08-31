"""Reviewed lemma-to-morphology-class knowledge with no generation authority.

This module intentionally exposes lexical class information separately from finite
surface generation. A class-only entry must not become a generated analysis merely
because its conjugation class is known.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

CLASS_LEXICON_PATH = Path("rules/morphology/reviewed_conjugation_2_class_lexicon.json")


@dataclass(frozen=True)
class ReviewedMorphologyClassEntry:
    lemma: str
    part_of_speech: str
    conjugation_class: str
    status: str
    generation_enabled: bool
    correction_allowed: bool
    source_label: str
    source_page: int | None
    gloss: str | None


@lru_cache(maxsize=1)
def _load_class_lexicon() -> dict:
    return json.loads(CLASS_LEXICON_PATH.read_text(encoding="utf-8"))


def reviewed_class_entries() -> tuple[ReviewedMorphologyClassEntry, ...]:
    data = _load_class_lexicon()
    result: list[ReviewedMorphologyClassEntry] = []
    for lemma, record in data.get("entries", {}).items():
        if not isinstance(record, dict):
            continue
        result.append(
            ReviewedMorphologyClassEntry(
                lemma=str(lemma),
                part_of_speech=str(data["part_of_speech"]),
                conjugation_class=str(data["conjugation_class"]),
                status=str(data["status"]),
                generation_enabled=bool(data.get("generation_enabled", False)),
                correction_allowed=bool(data.get("correction_authority", False)),
                source_label=str(record.get("source_label", "")),
                source_page=(
                    int(record["source_page"])
                    if record.get("source_page") is not None
                    else None
                ),
                gloss=(str(record["gloss"]) if record.get("gloss") else None),
            )
        )
    return tuple(sorted(result, key=lambda item: item.lemma))


def reviewed_class_entry(lemma: str) -> ReviewedMorphologyClassEntry | None:
    key = lemma.strip().casefold()
    return next((item for item in reviewed_class_entries() if item.lemma.casefold() == key), None)


def reviewed_class_lemmas(conjugation_class: str | None = None) -> tuple[str, ...]:
    entries = reviewed_class_entries()
    if conjugation_class is not None:
        entries = tuple(
            item
            for item in entries
            if item.conjugation_class.casefold() == conjugation_class.casefold()
        )
    return tuple(item.lemma for item in entries)
