"""Unified conservative morphology analysis.

The exact-reviewed lookup remains the highest-authority source.  This module adds
reviewed-rule-derived candidates generated only from explicitly authorized
lemmas/classes.  It never performs suffix stripping and never upgrades generated
candidates to correction authority.
"""

from __future__ import annotations

from dataclasses import dataclass

from .morphology_candidates import MorphologyCandidate, analyze_surface_form
from .morphology_generator import GeneratedMorphology, analyze_generated_surface
from .morphophonology_conj2_class_past import analyze_conj2_class_past_surface
from .morphophonology_generator import analyze_morphophonological_surface


@dataclass(frozen=True)
class MorphologyAnalysis:
    surface: str
    lemma: str
    part_of_speech: str
    analysis_type: str
    features: dict[str, object]
    authority: str
    status: str
    evidence_id: str
    correction_allowed: bool
    note: str


def _exact_features(candidate: MorphologyCandidate) -> dict[str, object]:
    return dict(candidate.features)


def _generated_features(candidate: GeneratedMorphology) -> dict[str, object]:
    result: dict[str, object] = {
        "part_of_speech": candidate.part_of_speech,
        "conjugation_class": candidate.conjugation_class,
    }
    if candidate.tense_aspect:
        result["tense_aspect"] = candidate.tense_aspect
    if candidate.mood:
        result["mood"] = candidate.mood
    if candidate.person:
        result["person"] = candidate.person
    if candidate.form:
        result["form"] = candidate.form
    return result


def _from_exact(candidate: MorphologyCandidate) -> MorphologyAnalysis:
    return MorphologyAnalysis(
        surface=candidate.surface,
        lemma=candidate.lemma,
        part_of_speech=str(candidate.features.get("part_of_speech", "")),
        analysis_type=candidate.analysis_type,
        features=_exact_features(candidate),
        authority="reviewed_exact",
        status=candidate.status,
        evidence_id=candidate.record_id,
        correction_allowed=bool(candidate.executable),
        note=(
            "Exact reviewed morphology record. Its existing executable flag is "
            "preserved; this combined analyzer does not increase correction authority."
        ),
    )


def _from_generated(candidate: GeneratedMorphology) -> MorphologyAnalysis:
    return MorphologyAnalysis(
        surface=candidate.surface,
        lemma=candidate.lemma,
        part_of_speech=candidate.part_of_speech,
        analysis_type="reviewed_rule_derived",
        features=_generated_features(candidate),
        authority="reviewed_rule_derived",
        status=candidate.status,
        evidence_id=candidate.rule_id,
        correction_allowed=False,
        note=(
            "Generated from a finite reviewed class rule and an explicitly authorized "
            "lemma. Recognition/analysis only; never automatic correction authority."
        ),
    )


def _person_set(features: dict[str, object]) -> tuple[str, ...]:
    person = features.get("person")
    if isinstance(person, str) and person:
        return (person,)
    possible = features.get("possible_persons")
    if isinstance(possible, list):
        return tuple(str(value) for value in possible)
    return ()


def _signature(item: MorphologyAnalysis) -> tuple[object, ...]:
    """Semantic signature used only to suppress generated duplicates of exact facts."""
    return (
        item.surface.casefold(),
        item.lemma.casefold(),
        item.part_of_speech.casefold(),
        str(item.features.get("tense_aspect", "")).casefold(),
        str(item.features.get("mood", "")).casefold(),
        tuple(sorted(value.casefold() for value in _person_set(item.features))),
        str(item.features.get("form", "")).casefold(),
    )


def analyze_morphology(form: str) -> tuple[MorphologyAnalysis, ...]:
    """Return exact-reviewed plus safely generated analyses for ``form``.

    Exact reviewed records are returned first.  A generated candidate with the
    same semantic signature is suppressed, because generated evidence must not
    obscure or duplicate a stronger exact record.  Unknown forms return an empty
    tuple; no reverse suffix inference is attempted.
    """
    exact = tuple(_from_exact(candidate) for candidate in analyze_surface_form(form))
    seen = {_signature(item) for item in exact}
    generated: list[MorphologyAnalysis] = []
    candidates = (
        analyze_generated_surface(form)
        + analyze_morphophonological_surface(form)
        + analyze_conj2_class_past_surface(form)
    )
    for candidate in candidates:
        item = _from_generated(candidate)
        signature = _signature(item)
        if signature in seen:
            continue
        seen.add(signature)
        generated.append(item)
    return exact + tuple(generated)


def analyze_finite_verb_morphology(form: str) -> tuple[MorphologyAnalysis, ...]:
    """Return finite verb analyses from the combined conservative morphology layer."""
    result: list[MorphologyAnalysis] = []
    for item in analyze_morphology(form):
        if item.part_of_speech != "verb":
            continue
        if item.features.get("person") or item.features.get("possible_persons"):
            if item.features.get("tense_aspect"):
                result.append(item)
    return tuple(result)
