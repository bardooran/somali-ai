"""Conservative lookup for reviewed Somali regional variants.

This module does not rewrite text. It exposes project preference metadata so
callers can distinguish preferred Jigjiga/Hargeisa-compatible forms,
co-preferred forms, recognized regional variants, and unverified candidates.
Sense-sensitive pairs remain explicitly marked as requiring context.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

REGIONAL_VARIANTS_PATH = Path("rules/variants/regional_preferences.jsonl")


@dataclass(frozen=True)
class RegionalVariantAnalysis:
    form: str
    record_id: str
    category: str
    concept: str | None
    preference: str
    preferred_forms: tuple[str, ...]
    recognized_forms: tuple[str, ...]
    status: str
    sense_sensitive: bool
    note: str


def _load_jsonl(path: str | Path) -> list[dict]:
    records: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def _casefold_set(values: list[str] | tuple[str, ...]) -> set[str]:
    return {value.casefold() for value in values}


def _concept(record: dict) -> str | None:
    return record.get("concept") or record.get("lemma_family") or record.get("lemma")


def _analysis_for_record(form: str, record: dict) -> RegionalVariantAnalysis | None:
    folded = form.casefold()
    category = record.get("category", "")
    preferred_forms: list[str] = []
    recognized_forms: list[str] = []
    preference: str | None = None

    if category in {"regional_lexical_morphological_variant", "lexical_variant_preference"}:
        preferred = record.get("preferred")
        if isinstance(preferred, str):
            preferred_forms.append(preferred)
        recognized_forms.extend(record.get("accepted_variants", []))
        candidate = record.get("candidate_native_variant")

        if preferred and folded == preferred.casefold():
            preference = "preferred"
        elif folded in _casefold_set(recognized_forms):
            preference = "recognized_variant"
        elif isinstance(candidate, str) and folded == candidate.casefold():
            recognized_forms.append(candidate)
            preference = "candidate_unverified"

    elif category in {"co_preferred_lexical_variants", "co_preferred_phrase_variants"}:
        forms = list(record.get("forms", []))
        if folded in _casefold_set(forms):
            preferred_forms.extend(forms)
            preference = "co_preferred"

    elif category == "regional_verb_paradigm_preference":
        examples = record.get("examples", {})
        preferred_forms.extend(examples.get("preferred", []))
        recognized_forms.extend(examples.get("recognized_variants", []))
        if folded in _casefold_set(preferred_forms):
            preference = "preferred"
        elif folded in _casefold_set(recognized_forms):
            preference = "recognized_variant"

    if preference is None:
        return None

    return RegionalVariantAnalysis(
        form=form,
        record_id=record.get("id", ""),
        category=category,
        concept=_concept(record),
        preference=preference,
        preferred_forms=tuple(preferred_forms),
        recognized_forms=tuple(recognized_forms),
        status=record.get("status", ""),
        sense_sensitive=bool(record.get("sense_sensitive", False)),
        note=record.get("note", ""),
    )


def analyze_regional_form(
    form: str,
    path: str | Path = REGIONAL_VARIANTS_PATH,
) -> tuple[RegionalVariantAnalysis, ...]:
    """Return all reviewed regional analyses for an exact surface form.

    Multiple analyses are intentionally retained. The function never proposes
    a correction and never treats a recognized regional form as an error.
    """
    analyses: list[RegionalVariantAnalysis] = []
    for record in _load_jsonl(path):
        analysis = _analysis_for_record(form.strip(), record)
        if analysis is not None:
            analyses.append(analysis)
    return tuple(analyses)


def preferred_forms_for_concept(
    concept: str,
    path: str | Path = REGIONAL_VARIANTS_PATH,
) -> tuple[str, ...]:
    """Return reviewed preferred forms for an exact project concept key."""
    target = concept.casefold()
    forms: list[str] = []
    for record in _load_jsonl(path):
        if (record.get("concept") or "").casefold() != target:
            continue
        category = record.get("category")
        if category in {"co_preferred_lexical_variants", "co_preferred_phrase_variants"}:
            forms.extend(record.get("forms", []))
        elif isinstance(record.get("preferred"), str):
            forms.append(record["preferred"])
    return tuple(dict.fromkeys(forms))
