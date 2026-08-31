"""Exact recognition over the compact somali-ai-data runtime index.

This layer is deliberately separate from the trusted morphology analyzer.
Recognizing a surface as supported/provisional does not authorize grammatical
correction, generation, or correctness claims.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

DEFAULT_MASTER_INDEX_PATH = Path("data/master/recognition_index.jsonl")
CONFIDENCE_RANK = {"trusted": 0, "supported": 1, "provisional": 2}


@dataclass(frozen=True)
class MasterRecognition:
    surface: str
    lemma: str
    part_of_speech: str | None
    record_type: str | None
    confidence_tier: str
    status: str | None
    correction_authority: bool
    promotion_allowed: bool
    regions: tuple[str, ...]
    master_record_id: str | None
    master_data_commit: str | None
    master_data_path: str | None
    sources: tuple[dict, ...]
    raw: dict


def _to_recognition(row: dict) -> MasterRecognition:
    return MasterRecognition(
        surface=str(row["surface"]),
        lemma=str(row.get("lemma") or row["surface"]),
        part_of_speech=row.get("part_of_speech"),
        record_type=row.get("record_type"),
        confidence_tier=str(row.get("confidence_tier") or "provisional"),
        status=row.get("status"),
        correction_authority=bool(row.get("correction_authority", False)),
        promotion_allowed=bool(row.get("promotion_allowed", False)),
        regions=tuple(str(item) for item in row.get("regions", []) if isinstance(item, str)),
        master_record_id=row.get("master_record_id"),
        master_data_commit=row.get("master_data_commit"),
        master_data_path=row.get("master_data_path"),
        sources=tuple(source for source in row.get("sources", []) if isinstance(source, dict)),
        raw=row,
    )


@lru_cache(maxsize=8)
def _load_index(path_text: str) -> dict[str, tuple[MasterRecognition, ...]]:
    path = Path(path_text)
    if not path.is_file():
        return {}
    grouped: dict[str, list[MasterRecognition]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            row = json.loads(text)
            if not isinstance(row, dict) or not isinstance(row.get("surface"), str):
                continue
            recognition = _to_recognition(row)
            grouped.setdefault(recognition.surface.casefold(), []).append(recognition)
    result: dict[str, tuple[MasterRecognition, ...]] = {}
    for key, values in grouped.items():
        values.sort(
            key=lambda item: (
                CONFIDENCE_RANK.get(item.confidence_tier, 99),
                item.part_of_speech or "",
                item.lemma.casefold(),
                item.master_record_id or "",
            )
        )
        result[key] = tuple(values)
    return result


def clear_master_recognition_cache() -> None:
    _load_index.cache_clear()


def recognize_form(
    form: str,
    *,
    path: str | Path = DEFAULT_MASTER_INDEX_PATH,
    minimum_confidence: str | None = None,
) -> tuple[MasterRecognition, ...]:
    """Return exact master-store recognitions for ``form``.

    Matching is case-insensitive but otherwise exact. No stemming, suffix
    stripping, spelling repair, or morphology generation happens here.

    ``minimum_confidence`` can be ``trusted``, ``supported``, or ``provisional``.
    For example, ``supported`` returns trusted + supported rows and excludes
    provisional candidates.
    """

    query = form.strip().casefold()
    if not query:
        return ()
    values = _load_index(str(Path(path))).get(query, ())
    if minimum_confidence is None:
        return values
    if minimum_confidence not in CONFIDENCE_RANK:
        raise ValueError(f"unknown confidence tier: {minimum_confidence}")
    ceiling = CONFIDENCE_RANK[minimum_confidence]
    return tuple(
        value
        for value in values
        if CONFIDENCE_RANK.get(value.confidence_tier, 99) <= ceiling
    )


def is_recognized(form: str, *, path: str | Path = DEFAULT_MASTER_INDEX_PATH) -> bool:
    return bool(recognize_form(form, path=path))
