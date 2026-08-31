"""Conservative productive Somali morphology from reviewed class rules.

This module is deliberately *not* a suffix stripper.  It starts from lemmas
explicitly authorized by a reviewed morphology rule, generates that finite
paradigm, and can then match a surface against those generated candidates.
Unknown lemmas therefore remain unknown rather than being reverse-engineered
from an apparent ending.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

RULE_PATH = Path("rules/morphology/reviewed_class_i_productive.json")


@dataclass(frozen=True)
class GeneratedMorphology:
    surface: str
    lemma: str
    part_of_speech: str
    conjugation_class: str
    tense_aspect: str | None
    mood: str | None
    person: str | None
    form: str | None
    status: str
    rule_id: str
    evidence_summary: tuple[str, ...]
    correction_allowed: bool


@lru_cache(maxsize=1)
def _rule() -> dict:
    return json.loads(RULE_PATH.read_text(encoding="utf-8"))


def eligible_lemmas() -> tuple[str, ...]:
    return tuple(str(value) for value in _rule()["eligible_lemmas"])


def _render(template: str, lemma: str) -> str:
    return template.format(lemma=lemma)


def _candidate(
    *,
    lemma: str,
    surface: str,
    tense_aspect: str | None = None,
    mood: str | None = None,
    person: str | None = None,
    form: str | None = None,
) -> GeneratedMorphology:
    rule = _rule()
    evidence = tuple(str(item["detail"]) for item in rule.get("evidence", ()))
    return GeneratedMorphology(
        surface=surface,
        lemma=lemma,
        part_of_speech=str(rule["part_of_speech"]),
        conjugation_class=str(rule["conjugation_class"]),
        tense_aspect=tense_aspect,
        mood=mood,
        person=person,
        form=form,
        status=str(rule["status"]),
        rule_id=str(rule["id"]),
        evidence_summary=evidence,
        correction_allowed=bool(rule.get("safety", {}).get("correction_authority", False)),
    )


def generate_verb(
    lemma: str,
    *,
    tense_aspect: str | None = None,
    mood: str | None = None,
    person: str | None = None,
    form: str | None = None,
) -> tuple[GeneratedMorphology, ...]:
    """Generate reviewed-rule-derived forms for one authorized Class-I lemma.

    Exactly one of ``tense_aspect``, ``mood`` or ``form`` must select a rule
    family.  ``person`` is required for finite/imperative forms.  Unsupported
    lemmas or feature bundles return an empty tuple.
    """

    lemma_key = lemma.strip().casefold()
    if lemma_key not in {value.casefold() for value in eligible_lemmas()}:
        return ()

    rule = _rule()
    forms = rule["forms"]

    if tense_aspect in {"present", "past"} and person:
        template = forms.get(tense_aspect, {}).get(person)
        if not template:
            return ()
        return (
            _candidate(
                lemma=lemma_key,
                surface=_render(str(template), lemma_key),
                tense_aspect=tense_aspect,
                mood="indicative",
                person=person,
            ),
        )

    if mood == "imperative" and person:
        template = forms.get("imperative", {}).get(person)
        if not template:
            return ()
        return (
            _candidate(
                lemma=lemma_key,
                surface=_render(str(template), lemma_key),
                mood="imperative",
                person=person,
            ),
        )

    if form == "infinitive":
        template = forms.get("infinitive", {}).get("nonfinite")
        if not template:
            return ()
        return (
            _candidate(
                lemma=lemma_key,
                surface=_render(str(template), lemma_key),
                form="infinitive",
            ),
        )

    return ()


def paradigm_for_lemma(lemma: str) -> tuple[GeneratedMorphology, ...]:
    result: list[GeneratedMorphology] = []
    for tense in ("present", "past"):
        for person in ("1sg", "2sg", "3sg_m", "3sg_f", "1pl", "2pl", "3pl"):
            result.extend(generate_verb(lemma, tense_aspect=tense, person=person))
    for person in ("2sg", "2pl"):
        result.extend(generate_verb(lemma, mood="imperative", person=person))
    result.extend(generate_verb(lemma, form="infinitive"))
    return tuple(result)


@lru_cache(maxsize=1)
def _surface_index() -> dict[str, tuple[GeneratedMorphology, ...]]:
    grouped: dict[str, list[GeneratedMorphology]] = {}
    for lemma in eligible_lemmas():
        for candidate in paradigm_for_lemma(lemma):
            grouped.setdefault(candidate.surface.casefold(), []).append(candidate)
    return {key: tuple(values) for key, values in grouped.items()}


def analyze_generated_surface(surface: str) -> tuple[GeneratedMorphology, ...]:
    """Match a surface only against finite paradigms generated from reviewed lemmas."""
    return _surface_index().get(surface.strip().casefold(), ())


def clear_generator_cache() -> None:
    _rule.cache_clear()
    _surface_index.cache_clear()
