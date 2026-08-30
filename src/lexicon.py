"""Small, source-backed Somali word lookup prototype.

Default lookup combines multiple reviewed Qaamuus lexical datasets, reviewed
regional-variant metadata, and a conservative morphology-candidate layer.
Homographs are preserved as multiple analyses.

Inflected forms are only linked to lemmas when the exact surface form is stored
in the reviewed morphology dataset. The module does not perform open-ended
suffix stripping or guess unseen lemmas.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from src.morphology_candidates import MorphologyCandidate, analyze_surface_form
from src.regional_variants import RegionalVariantAnalysis, analyze_regional_form

LEXICON_PATH = Path("data/lexical/qaamuus_2012_grammar_lexicon_seed.jsonl")
EVERYDAY_LEXICON_PATH = Path("data/lexical/qaamuus_2012_everyday_lexicon_seed.jsonl")
DEFAULT_LEXICON_PATHS = (LEXICON_PATH, EVERYDAY_LEXICON_PATH)


@dataclass(frozen=True)
class LexiconEntry:
    lemma: str
    homograph_index: int | None
    source_pos: str | None
    domain: str | None
    somali_definition_summary: str | None
    related_lemmas: tuple[str, ...]
    status: str
    source: str
    raw: dict


@dataclass(frozen=True)
class WordLookup:
    query: str
    exact_entries: tuple[LexiconEntry, ...]
    morphology_candidates: tuple[MorphologyCandidate, ...]
    regional_analyses: tuple[RegionalVariantAnalysis, ...]
    known: bool
    note: str


def _load_jsonl(path: str | Path) -> list[dict]:
    records: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def _to_entry(record: dict) -> LexiconEntry:
    related = record.get("related_lemmas", [])
    return LexiconEntry(
        lemma=record["lemma"],
        homograph_index=record.get("homograph_index"),
        source_pos=record.get("source_pos"),
        domain=record.get("domain"),
        somali_definition_summary=record.get("somali_definition_summary"),
        related_lemmas=tuple(related),
        status=record.get("status", ""),
        source=record.get("source", ""),
        raw=record,
    )


def _default_records() -> list[dict]:
    records: list[dict] = []
    for path in DEFAULT_LEXICON_PATHS:
        records.extend(_load_jsonl(path))
    return records


def lookup_word(
    form: str,
    lexicon_path: str | Path | None = None,
) -> WordLookup:
    """Look up a Somali surface form across reviewed evidence layers.

    Exact dictionary headwords, exact reviewed morphology mappings, and
    regional-variant metadata are returned independently. Multiple analyses are
    deliberately retained so callers can resolve them using sentence context.

    ``lexicon_path`` can restrict only the dictionary dataset for tests or
    specialized callers; reviewed morphology and regional evidence still use
    their normal project datasets.
    """
    query = form.strip()
    folded = query.casefold()
    records = _load_jsonl(lexicon_path) if lexicon_path is not None else _default_records()
    entries = tuple(
        _to_entry(record)
        for record in records
        if record.get("lemma", "").casefold() == folded
    )
    morphology = analyze_surface_form(query)
    regional = analyze_regional_form(query)
    known = bool(entries or morphology or regional)

    if entries and len(entries) > 1:
        note = "Exact headword has multiple dictionary analyses; context is required to choose among them."
    elif entries and morphology:
        note = "Exact source-backed headword and reviewed morphology evidence found."
    elif entries:
        note = "Exact source-backed headword found."
    elif morphology and len(morphology) > 1:
        note = "Reviewed surface form has multiple morphology candidates; context is required to choose a lemma."
    elif morphology:
        note = "Reviewed morphology mapping found; lemma is linked from stored evidence rather than guessed by suffix stripping."
    elif regional:
        note = "No exact seed-dictionary or morphology entry yet, but reviewed regional-variant evidence exists."
    else:
        note = "Word is outside the current reviewed lexical and morphology datasets; no analysis is guessed."

    return WordLookup(
        query=query,
        exact_entries=entries,
        morphology_candidates=morphology,
        regional_analyses=regional,
        known=known,
        note=note,
    )
