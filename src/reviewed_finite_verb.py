"""Exact reviewed finite-verb paradigm analysis.

This module is the shared bridge between reviewed Somali morphology and grammar
agreement layers. It exposes lemma, person, and tense/aspect only for exact
reviewed finite verb surfaces. It deliberately does not derive unseen forms from
suffixes, and it excludes imperatives, masdar/infinitive forms, and other
non-finite records from finite agreement decisions.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.morphology_candidates import MorphologyCandidate, analyze_surface_form

FINITE_ANALYSIS_TYPES = {
    "finite_verb",
    "native_reviewed_finite_verb_surface",
    "fal_sifo_finite",
}


@dataclass(frozen=True)
class ReviewedFiniteVerbAnalysis:
    recognized: bool
    surface: str
    lemmas: tuple[str, ...] = ()
    persons: tuple[str, ...] = ()
    tense_aspects: tuple[str, ...] = ()
    conjugation_classes: tuple[str, ...] = ()
    record_ids: tuple[str, ...] = ()
    note: str = ""


def _candidate_persons(candidate: MorphologyCandidate) -> tuple[str, ...]:
    person = candidate.features.get("person")
    if isinstance(person, str):
        return (person,)

    possible = candidate.features.get("possible_persons")
    if isinstance(possible, list):
        return tuple(str(item) for item in possible)
    return ()


def _is_reviewed_finite(candidate: MorphologyCandidate) -> bool:
    return (
        candidate.features.get("part_of_speech") == "verb"
        and candidate.analysis_type in FINITE_ANALYSIS_TYPES
    )


def _append_unique(items: list[str], value: object) -> None:
    if isinstance(value, str) and value and value not in items:
        items.append(value)


def analyze_reviewed_finite_verb(form: str) -> ReviewedFiniteVerbAnalysis:
    """Return exact reviewed finite-verb features for ``form``.

    Multiple source records may support one surface, so values are accumulated
    without overwriting ambiguity. If the surface is absent, or is reviewed only
    as a non-finite form, ``recognized`` is False.
    """
    finite_candidates = tuple(
        candidate
        for candidate in analyze_surface_form(form)
        if _is_reviewed_finite(candidate)
    )
    if not finite_candidates:
        return ReviewedFiniteVerbAnalysis(
            recognized=False,
            surface=form,
            note=(
                "No exact reviewed finite-verb analysis found. The form may be unknown "
                "or reviewed only as a non-finite/other verb form; no suffix inference used."
            ),
        )

    lemmas: list[str] = []
    persons: list[str] = []
    tense_aspects: list[str] = []
    conjugation_classes: list[str] = []
    record_ids: list[str] = []

    for candidate in finite_candidates:
        _append_unique(lemmas, candidate.lemma)
        for person in _candidate_persons(candidate):
            _append_unique(persons, person)
        _append_unique(tense_aspects, candidate.features.get("tense_aspect"))
        _append_unique(conjugation_classes, candidate.features.get("conjugation_class"))
        _append_unique(record_ids, candidate.record_id)

    return ReviewedFiniteVerbAnalysis(
        recognized=True,
        surface=form,
        lemmas=tuple(lemmas),
        persons=tuple(persons),
        tense_aspects=tuple(tense_aspects),
        conjugation_classes=tuple(conjugation_classes),
        record_ids=tuple(record_ids),
        note=(
            "Features come only from exact reviewed finite morphology records. "
            "No productive suffix rule or invented conjugation is used."
        ),
    )
