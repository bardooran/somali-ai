"""Narrow reviewed class-level Conjugation-2A past generation.

This module intentionally lives beside the mature present activation rather than
silently widening it. Only independently supported past cells listed by the
separate policy are authorized. After the v19 baseline the reviewed 11-lemma
allowlist has all seven staged person cells: 1SG, 1PL, 2SG, 2PL, 3SG masculine,
3SG feminine and 3PL. The syncretic 1SG/3SG-masculine cells reuse the reviewed
``i + vowel -> iyV`` glide; the syncretic 2SG/3SG-feminine cells reuse reviewed
``i+t -> is`` assibilation; and the 1PL cell reuses the reviewed weak-causative
``i+n -> inn`` process. Generation is forward-only, allowlist-only, and never
grants correction authority.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from .morphology_class_lexicon import (
    ReviewedMorphologyClassEntry,
    reviewed_class_entries,
    reviewed_class_entry,
)
from .morphology_generator import GeneratedMorphology
from .morphophonology_generator import (
    CONJ2_RULE_PATH,
    _apply_conj2_processes,
    _load_rule,
)

CONJ2_CLASS_PAST_ACTIVATION_PATH = Path(
    "rules/morphology/reviewed_conjugation_2_class_past_activation.json"
)


def _eligible_entry(lemma: str) -> ReviewedMorphologyClassEntry | None:
    activation = _load_rule(CONJ2_CLASS_PAST_ACTIVATION_PATH)
    if not activation.get("activation_enabled"):
        return None

    entry = reviewed_class_entry(lemma)
    if entry is None:
        return None

    activated_lemmas = {
        str(value).casefold() for value in activation.get("activated_lemmas", [])
    }
    if entry.lemma.casefold() not in activated_lemmas:
        return None

    if entry.part_of_speech.casefold() != str(activation["part_of_speech"]).casefold():
        return None
    if entry.conjugation_class.casefold() != str(activation["conjugation_class"]).casefold():
        return None
    if entry.status != str(activation["required_class_entry_status"]):
        return None

    required_suffix = str(activation.get("required_lemma_suffix", ""))
    if required_suffix and not entry.lemma.casefold().endswith(required_suffix.casefold()):
        return None

    # Explicit development profiles retain their narrower profile authority path.
    profile_rule = _load_rule(CONJ2_RULE_PATH)
    if entry.lemma in profile_rule.get("profiles", {}):
        return None
    return entry


def _evidence_summary(
    entry: ReviewedMorphologyClassEntry,
    activation: dict,
) -> tuple[str, ...]:
    evidence = activation.get("development_evidence", {})
    result = [
        (
            f"Reviewed class authorization for {entry.lemma}: "
            f"{entry.source_label}, Zorc 2019 Somali-English Dictionary"
            + (f", p. {entry.source_page}." if entry.source_page is not None else ".")
        )
    ]
    if isinstance(evidence, dict):
        for key in (
            "primary",
            "independent_corroboration",
            "first_plural_independent",
            "first_singular_independent",
            "third_singular_feminine_independent",
        ):
            record = evidence.get(key)
            if not isinstance(record, dict):
                continue
            citation = record.get("citation")
            detail = record.get("evidence")
            if citation and detail:
                result.append(f"{citation} {detail}")
            elif citation:
                result.append(str(citation))
    return tuple(result)


def generate_class_authorized_conj2_past(
    lemma: str,
    person: str,
) -> GeneratedMorphology | None:
    """Generate one reviewed class-authorized C2A past candidate.

    Only persons explicitly listed by the separate past activation policy are
    eligible. After the v19 baseline all seven staged person cells are authorized
    for the reviewed 11-lemma allowlist. Syncretic cells remain separate analysis
    candidates rather than being collapsed into one person label.
    """
    entry = _eligible_entry(lemma)
    if entry is None:
        return None

    activation = _load_rule(CONJ2_CLASS_PAST_ACTIVATION_PATH)
    authorized = {str(value) for value in activation.get("authorized_persons", [])}
    if person not in authorized:
        return None

    morphology = activation.get("past_morphology", {}).get(person)
    if not isinstance(morphology, dict):
        return None

    agreement = str(morphology.get("agreement", ""))
    tam = str(morphology.get("tam", ""))
    processes = {str(value) for value in activation.get("required_processes", [])}
    surface, process = _apply_conj2_processes(entry.lemma, agreement, tam, processes)

    return GeneratedMorphology(
        surface=surface,
        lemma=entry.lemma,
        part_of_speech=entry.part_of_speech,
        conjugation_class=entry.conjugation_class,
        tense_aspect=str(activation["tense_aspect"]),
        mood=str(activation["mood"]),
        person=person,
        form=None,
        status=str(activation["status"]),
        rule_id=f"{activation['id']}:{process}",
        evidence_summary=_evidence_summary(entry, activation),
        correction_allowed=False,
    )


@lru_cache(maxsize=1)
def _surface_index() -> dict[str, tuple[GeneratedMorphology, ...]]:
    activation = _load_rule(CONJ2_CLASS_PAST_ACTIVATION_PATH)
    index: dict[str, list[GeneratedMorphology]] = {}
    for entry in reviewed_class_entries():
        if _eligible_entry(entry.lemma) is None:
            continue
        for person in activation.get("authorized_persons", []):
            candidate = generate_class_authorized_conj2_past(entry.lemma, str(person))
            if candidate is None:
                continue
            index.setdefault(candidate.surface.casefold(), []).append(candidate)
    return {key: tuple(values) for key, values in index.items()}


def analyze_conj2_class_past_surface(form: str) -> tuple[GeneratedMorphology, ...]:
    """Return exact forward-generated C2A class-past candidates for ``form``."""
    return _surface_index().get(form.strip().casefold(), ())


def eligible_conj2_class_past_activation_lemmas() -> tuple[str, ...]:
    """Return C2A class lemmas admitted by the narrow past activation policy."""
    return tuple(
        sorted(
            entry.lemma
            for entry in reviewed_class_entries()
            if _eligible_entry(entry.lemma) is not None
        )
    )
