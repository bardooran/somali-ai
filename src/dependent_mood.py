"""Conservative analyzer for reviewed Somali ``habka dhimman`` pairs.

The source tables present dependent subject markers in parentheses together with
finite verb forms, e.g. ``(uu) cuno`` / ``(ay) cunto`` and ``(uu) yimaaddo`` /
``(ay) timaaddo``. This module treats the marker and verb as one contextual
agreement pair. It does not reinterpret these as ordinary main-clause
``wuu/way`` constructions and never derives unseen forms from suffixes.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

PAIR_PATHS = (
    Path("data/morphology/qaamuus_2012_reviewed_dependent_pairs.jsonl"),
    Path("data/morphology/qaamuus_2012_reviewed_imow_dependent_pairs.jsonl"),
    Path("data/morphology/qaamuus_2012_reviewed_aqaan_dependent_pairs.jsonl"),
    Path("data/morphology/qaamuus_2012_reviewed_ahaw_dependent_pairs.jsonl"),
)
TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)


@dataclass(frozen=True)
class DependentMoodAnalysis:
    recognized: bool
    marker: str | None = None
    verb: str | None = None
    lemma: str | None = None
    mood: str | None = None
    polarity: str | None = None
    persons: tuple[str, ...] = ()
    tense_aspects: tuple[str, ...] = ()
    marker_persons: tuple[str, ...] = ()
    marker_polarities: tuple[str, ...] = ()
    verb_persons: tuple[str, ...] = ()
    verb_polarities: tuple[str, ...] = ()
    person_neutralized: bool = False
    agrees: bool | None = None
    rule_id: str = "GRAM-DEP-001"
    note: str = ""


def _records() -> list[dict]:
    records: list[dict] = []
    for path in PAIR_PATHS:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    records.append(json.loads(stripped))
    return records


def _unique(values) -> tuple[str, ...]:
    result: list[str] = []
    for value in values:
        if isinstance(value, str) and value and value not in result:
            result.append(value)
    return tuple(result)


def _record_persons(record: dict) -> tuple[str, ...]:
    persons = record.get("persons", [])
    if not isinstance(persons, list):
        return ()
    return tuple(str(person) for person in persons)


def _record_tense_aspects(record: dict) -> tuple[str, ...]:
    values = record.get("tense_aspects", [])
    if not isinstance(values, list):
        return ()
    return tuple(str(value) for value in values)


def _aggregate_persons(records: list[dict]) -> tuple[str, ...]:
    values: list[str] = []
    for record in records:
        for person in _record_persons(record):
            if person not in values:
                values.append(person)
    return tuple(values)


def _aggregate_tense_aspects(records: list[dict]) -> tuple[str, ...]:
    values: list[str] = []
    for record in records:
        for tense_aspect in _record_tense_aspects(record):
            if tense_aspect not in values:
                values.append(tense_aspect)
    return tuple(values)


def analyze_dependent_mood(sentence: str) -> DependentMoodAnalysis:
    """Analyze the first reviewed adjacent ``marker + verb`` dependent pair.

    Exact reviewed pairs are accepted. If both the marker and verb are known in
    the reviewed dependent tables but the exact pairing is absent, the result is
    a review-only conflict. A known marker followed by an unseen verb remains
    unjudged rather than being guessed.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 2:
        return DependentMoodAnalysis(recognized=False)

    records = _records()
    for index in range(len(tokens) - 1):
        marker = tokens[index]
        verb = tokens[index + 1]
        marker_key = marker.casefold()
        verb_key = verb.casefold()

        marker_records = [
            record for record in records if str(record.get("marker", "")).casefold() == marker_key
        ]
        if not marker_records:
            continue

        exact = [
            record
            for record in marker_records
            if str(record.get("verb", "")).casefold() == verb_key
        ]
        marker_persons = _aggregate_persons(marker_records)
        marker_polarities = _unique(record.get("polarity") for record in marker_records)

        if exact:
            return DependentMoodAnalysis(
                recognized=True,
                marker=marker,
                verb=verb,
                lemma=exact[0].get("lemma"),
                mood="habka_dhimman",
                polarity=exact[0].get("polarity"),
                persons=_aggregate_persons(exact),
                tense_aspects=_aggregate_tense_aspects(exact),
                marker_persons=marker_persons,
                marker_polarities=marker_polarities,
                verb_persons=_aggregate_persons(exact),
                verb_polarities=_unique(record.get("polarity") for record in exact),
                person_neutralized=any(bool(record.get("person_neutralized")) for record in exact),
                agrees=True,
                note=(
                    "Exact reviewed habka dhimman marker+verb pair found. The marker and verb are "
                    "interpreted together; no main-clause or suffix-only rule is substituted."
                ),
            )

        verb_records = [
            record for record in records if str(record.get("verb", "")).casefold() == verb_key
        ]
        if verb_records:
            verb_persons = _aggregate_persons(verb_records)
            verb_polarities = _unique(record.get("polarity") for record in verb_records)
            return DependentMoodAnalysis(
                recognized=True,
                marker=marker,
                verb=verb,
                lemma=verb_records[0].get("lemma"),
                mood="habka_dhimman",
                marker_persons=marker_persons,
                marker_polarities=marker_polarities,
                verb_persons=verb_persons,
                verb_polarities=verb_polarities,
                tense_aspects=_aggregate_tense_aspects(verb_records),
                person_neutralized=any(bool(record.get("person_neutralized")) for record in verb_records),
                agrees=False,
                note=(
                    "The marker and verb are both reviewed in habka dhimman, but this exact pair is "
                    "not licensed by the cited paradigms. This may be a person or polarity conflict; "
                    "review required and no automatic rewrite is made."
                ),
            )

        return DependentMoodAnalysis(
            recognized=True,
            marker=marker,
            verb=verb,
            mood="habka_dhimman",
            marker_persons=marker_persons,
            marker_polarities=marker_polarities,
            agrees=None,
            note=(
                "A reviewed dependent marker was found, but the following verb is absent from the "
                "reviewed dependent tables. The form is left unjudged; no suffix inference is used."
            ),
        )

    return DependentMoodAnalysis(recognized=False)
