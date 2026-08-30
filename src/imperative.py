"""Conservative analyzer for reviewed Somali imperative forms.

Imperatives are recognized only from exact reviewed morphology. The current
clause-level scope is intentionally narrow: the imperative surface must be the
first lexical token in the supplied clause/sentence. This prevents the highly
syncretic ``cunin`` surface from being reinterpreted as an imperative when it
follows dependent, jussive, or ordinary negation markers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.morphology_candidates import MorphologyCandidate, analyze_surface_form

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)


@dataclass(frozen=True)
class ImperativeAnalysis:
    recognized: bool
    surface: str | None = None
    lemma: str | None = None
    person: str | None = None
    polarity: str | None = None
    mood: str | None = None
    context_required: bool = False
    record_ids: tuple[str, ...] = ()
    rule_id: str = "GRAM-IMP-001"
    note: str = ""


def _imperative_candidate(candidate: MorphologyCandidate) -> tuple[str, str] | None:
    """Return ``(person, polarity)`` for an exact reviewed imperative reading."""
    features = candidate.features
    if candidate.analysis_type == "imperative" and features.get("mood") == "imperative":
        person = features.get("person")
        polarity = features.get("polarity")
        if isinstance(person, str) and isinstance(polarity, str):
            return person, polarity

    # The source-backed surface ``cunin`` is deliberately stored as a
    # multi-function form because it also occurs in other negative paradigms.
    possible_functions = features.get("possible_functions")
    if (
        candidate.analysis_type == "negative_or_negative_imperative_form"
        and isinstance(possible_functions, list)
        and "negative_imperative_2sg" in possible_functions
    ):
        return "2sg", "negative"

    return None


def analyze_imperative(text: str) -> ImperativeAnalysis:
    """Return an exact reviewed imperative reading for a clause-initial form.

    Unknown forms remain unrecognized. ``cunin`` is accepted as a supported
    negative 2sg imperative reading only when clause-initial, and is marked
    context-required because the same surface is licensed in other moods.
    """
    tokens = TOKEN_RE.findall(text)
    if not tokens:
        return ImperativeAnalysis(recognized=False)

    surface = tokens[0]
    readings: list[tuple[MorphologyCandidate, str, str]] = []
    for candidate in analyze_surface_form(surface):
        reading = _imperative_candidate(candidate)
        if reading is not None:
            readings.append((candidate, reading[0], reading[1]))

    if not readings:
        return ImperativeAnalysis(
            recognized=False,
            surface=surface,
            note="No exact reviewed clause-initial imperative analysis found; no suffix inference used.",
        )

    # Current reviewed data should resolve one imperative person/polarity per
    # surface. If future sources introduce genuine imperative ambiguity, leave
    # it context-required rather than silently selecting one analysis.
    persons = {person for _, person, _ in readings}
    polarities = {polarity for _, _, polarity in readings}
    if len(persons) != 1 or len(polarities) != 1:
        return ImperativeAnalysis(
            recognized=True,
            surface=surface,
            lemma=readings[0][0].lemma,
            mood="imperative",
            context_required=True,
            record_ids=tuple(candidate.record_id for candidate, _, _ in readings),
            note="Multiple exact reviewed imperative readings exist; context is required.",
        )

    person = next(iter(persons))
    polarity = next(iter(polarities))
    syncretic = any(
        candidate.analysis_type == "negative_or_negative_imperative_form"
        for candidate, _, _ in readings
    )
    return ImperativeAnalysis(
        recognized=True,
        surface=surface,
        lemma=readings[0][0].lemma,
        person=person,
        polarity=polarity,
        mood="imperative",
        context_required=syncretic,
        record_ids=tuple(candidate.record_id for candidate, _, _ in readings),
        note=(
            "Exact reviewed clause-initial imperative reading found. "
            + (
                "This surface is syncretic outside imperative context, so surrounding clause structure remains relevant."
                if syncretic
                else "No unseen imperative ending or person form is generated."
            )
        ),
    )
