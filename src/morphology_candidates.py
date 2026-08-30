"""Conservative morphology candidate lookup for reviewed Somali surface forms.

This module intentionally does not perform open-ended suffix stripping. It only
returns analyses for surface forms that are explicitly stored in the reviewed
morphology dataset. That gives the word analyzer a safe bridge from inflected
surface forms to candidate lemmas while broader morphology remains under
validation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

REVIEWED_NOUN_FORMS_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_noun_forms.jsonl"
)


@dataclass(frozen=True)
class MorphologyCandidate:
    surface: str
    lemma: str
    record_id: str
    analysis_type: str
    segmentation: str
    features: dict
    evidence_type: str
    source: str
    status: str
    executable: bool
    note: str
    raw: dict


def _load_jsonl(path: str | Path) -> list[dict]:
    records: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def _to_candidate(record: dict) -> MorphologyCandidate:
    return MorphologyCandidate(
        surface=record["surface"],
        lemma=record["lemma"],
        record_id=record.get("id", ""),
        analysis_type=record.get("analysis_type", ""),
        segmentation=record.get("segmentation", ""),
        features=dict(record.get("features", {})),
        evidence_type=record.get("evidence_type", ""),
        source=record.get("source", ""),
        status=record.get("status", ""),
        executable=bool(record.get("executable", False)),
        note=record.get("note", ""),
        raw=record,
    )


def analyze_surface_form(
    form: str,
    path: str | Path = REVIEWED_NOUN_FORMS_PATH,
) -> tuple[MorphologyCandidate, ...]:
    """Return reviewed morphology candidates for an exact surface form.

    Matching is case-insensitive, but no characters are removed, replaced, or
    normalized beyond Unicode-preserving Python ``casefold`` comparison. If a
    form is absent from the reviewed dataset, the function returns an empty
    tuple rather than guessing a lemma.
    """
    query = form.strip().casefold()
    return tuple(
        _to_candidate(record)
        for record in _load_jsonl(path)
        if record.get("surface", "").casefold() == query
    )
