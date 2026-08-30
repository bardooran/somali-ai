"""Small, source-backed Somali word lookup prototype.

The current lexicon intentionally supports exact headword lookup only. It does
not guess lemmas from inflected surface forms yet. Homographs are preserved as
multiple entries and regional-variant metadata is attached separately.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from src.regional_variants import RegionalVariantAnalysis, analyze_regional_form

LEXICON_PATH = Path("data/lexical/qaamuus_2012_grammar_lexicon_seed.jsonl")


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


def lookup_word(
    form: str,
    lexicon_path: str | Path = LEXICON_PATH,
) -> WordLookup:
    """Look up an exact Somali headword and reviewed regional metadata.

    This first-stage API deliberately does not stem or normalize inflected
    words. For example, a query such as ``gabadha`` is not silently reduced to
    ``gabadh`` until a tested morphology layer is connected.
    """
    query = form.strip()
    folded = query.casefold()
    entries = tuple(
        _to_entry(record)
        for record in _load_jsonl(lexicon_path)
        if record.get("lemma", "").casefold() == folded
    )
    regional = analyze_regional_form(query)
    known = bool(entries or regional)

    if entries and len(entries) > 1:
        note = "Exact headword has multiple dictionary analyses; context is required to choose among them."
    elif entries:
        note = "Exact source-backed headword found."
    elif regional:
        note = "No exact seed-dictionary entry yet, but reviewed regional-variant evidence exists."
    else:
        note = "Word is outside the current reviewed lexical seed; no analysis is guessed."

    return WordLookup(
        query=query,
        exact_entries=entries,
        regional_analyses=regional,
        known=known,
        note=note,
    )
