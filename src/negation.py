"""Conservative Somali verb-negation analysis.

This module only reasons over explicitly documented affirmative/negative
pairs. It does not attempt unrestricted tense/aspect parsing and never rewrites
text automatically.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

NEGATION_PATH = Path("rules/grammar/negation_patterns.jsonl")


@dataclass(frozen=True)
class NegationResult:
    input_form: str
    known: bool
    polarity: str | None
    lemma: str | None
    paradigm: str | None
    paired_form: str | None
    agrees_with_documented_pair: bool | None
    note: str


def _load_pairs(path: str | Path = NEGATION_PATH) -> list[dict]:
    records: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if record.get("category") == "verb_negation" and record.get("affirmative") and record.get("negative"):
                records.append(record)
    return records


def analyze_negation_form(form: str, path: str | Path = NEGATION_PATH) -> NegationResult:
    normalized = " ".join(form.casefold().split())
    for record in _load_pairs(path):
        affirmative = " ".join(record["affirmative"].casefold().split())
        negative = " ".join(record["negative"].casefold().split())
        if normalized == affirmative:
            return NegationResult(form, True, "affirmative", record.get("lemma"), record.get("paradigm"), record["negative"], True, "Form matches a documented affirmative member of a negation pair.")
        if normalized == negative:
            return NegationResult(form, True, "negative", record.get("lemma"), record.get("paradigm"), record["affirmative"], True, "Form matches a documented negative member of a negation pair.")
    return NegationResult(form, False, None, None, None, None, None, "Form is outside the currently documented executable negation pairs.")


def analyze_ma_plus_verb(text: str, path: str | Path = NEGATION_PATH) -> NegationResult:
    """Review an exact ``ma + verb`` form against documented negative pairs.

    Unknown forms remain unjudged. If the input is ``ma`` plus a documented
    affirmative form (for example ``ma cunaa``), the analyzer can safely say
    it conflicts with the documented pair, but it still does not autocorrect.
    """
    normalized = " ".join(text.casefold().split())
    result = analyze_negation_form(normalized, path)
    if result.known:
        return result
    if not normalized.startswith("ma "):
        return result
    following = normalized[3:]
    for record in _load_pairs(path):
        affirmative = " ".join(record["affirmative"].casefold().split())
        if following == affirmative:
            return NegationResult(
                text,
                True,
                "negative_attempt",
                record.get("lemma"),
                record.get("paradigm"),
                record["negative"],
                False,
                "The input uses ma before a documented affirmative form; the cited paradigm uses a different negative form. Review required; no automatic rewrite.",
            )
    return NegationResult(text, False, None, None, None, None, None, "Negative construction is outside the currently documented executable pairs.")
