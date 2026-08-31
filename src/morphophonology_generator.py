"""Finite reviewed morphophonology generation for explicitly authorized profiles.

This module is deliberately separate from the broader concatenative morphology
generator. It handles only reviewed, non-concatenative development profiles and
builds finite forward indexes. It never performs reverse suffix stripping and
never grants correction authority.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from .morphology_generator import GeneratedMorphology

CLASS_I_RULE_PATH = Path("rules/morphology/reviewed_class_i_morphophonology.json")
CONJ2_RULE_PATH = Path("rules/morphology/reviewed_conjugation_2_morphophonology.json")


def _load_rule(path: Path = CLASS_I_RULE_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _apply_processes(
    lemma: str,
    agreement: str,
    tam: str,
    processes: set[str],
) -> tuple[str, str]:
    """Return one reviewed Class-I surface plus a short process label."""
    if agreement == "t" and lemma.endswith("l") and "l_t_assibilation" in processes:
        return lemma[:-1] + "sh" + tam, "l_t_assibilation"
    if agreement == "n" and lemma.endswith("l") and "l_n_assimilation" in processes:
        return lemma + "l" + tam, "l_n_assimilation"
    if agreement == "n" and lemma.endswith("r") and "r_n_assimilation" in processes:
        return lemma + "r" + tam, "r_n_assimilation"
    if agreement == "t" and lemma.endswith("dh") and "dh_t_assimilation" in processes:
        return lemma + "dh" + tam, "dh_t_assimilation"
    return lemma + agreement + tam, "concatenative_elsewhere"


def _apply_conj2_processes(
    lemma: str,
    agreement: str,
    tam: str,
    processes: set[str],
) -> tuple[str, str]:
    """Return one reviewed Conjugation-2 surface plus a process label."""
    if agreement == "t" and lemma.endswith("i") and "i_t_assibilation" in processes:
        return lemma + "s" + tam, "i_t_assibilation"
    return lemma + agreement + tam, "concatenative_elsewhere"


def _evidence_summary(rule: dict, profile: dict, process: str) -> tuple[str, ...]:
    result: list[str] = []
    class_evidence = profile.get("class_evidence")
    if class_evidence:
        result.append(str(class_evidence))
    development_evidence = profile.get("development_evidence")
    if development_evidence:
        result.append(str(development_evidence))
    process_record = rule.get("processes", {}).get(process)
    if isinstance(process_record, dict) and process_record.get("source"):
        result.append(str(process_record["source"]))
    return tuple(result)


def generate_profile_past(lemma: str, person: str) -> GeneratedMorphology | None:
    rule = _load_rule(CLASS_I_RULE_PATH)
    profile = rule.get("profiles", {}).get(lemma)
    if not isinstance(profile, dict):
        return None
    authorized = {str(value) for value in profile.get("authorized_persons", [])}
    if person not in authorized:
        return None
    morphology = rule.get("past_morphology", {}).get(person)
    if not isinstance(morphology, dict):
        return None
    agreement = str(morphology.get("agreement", ""))
    tam = str(morphology.get("tam", ""))
    processes = {str(value) for value in profile.get("processes", [])}
    surface, process = _apply_processes(lemma, agreement, tam, processes)
    return GeneratedMorphology(
        surface=surface,
        lemma=lemma,
        part_of_speech=str(rule["part_of_speech"]),
        conjugation_class=str(rule["conjugation_class"]),
        tense_aspect="past",
        mood="indicative",
        person=person,
        form=None,
        status=str(rule["status"]),
        rule_id=f"{rule['id']}:{process}",
        evidence_summary=_evidence_summary(rule, profile, process),
        correction_allowed=False,
    )


def _generate_conj2_finite(
    lemma: str,
    person: str,
    tense_aspect: str,
) -> GeneratedMorphology | None:
    """Generate one explicitly authorized finite Conjugation-2 candidate."""
    rule = _load_rule(CONJ2_RULE_PATH)
    profile = rule.get("profiles", {}).get(lemma)
    if not isinstance(profile, dict):
        return None

    authorized_key = f"authorized_{tense_aspect}_persons"
    authorized = {str(value) for value in profile.get(authorized_key, [])}
    if person not in authorized:
        return None

    morphology_table = rule.get(f"{tense_aspect}_morphology", {})
    morphology = morphology_table.get(person) if isinstance(morphology_table, dict) else None
    if not isinstance(morphology, dict):
        return None

    agreement = str(morphology.get("agreement", ""))
    tam = str(morphology.get("tam", ""))
    processes = {str(value) for value in profile.get("processes", [])}
    surface, process = _apply_conj2_processes(lemma, agreement, tam, processes)
    return GeneratedMorphology(
        surface=surface,
        lemma=lemma,
        part_of_speech=str(rule["part_of_speech"]),
        conjugation_class=str(rule["conjugation_class"]),
        tense_aspect=tense_aspect,
        mood="indicative",
        person=person,
        form=None,
        status=str(rule["status"]),
        rule_id=f"{rule['id']}:{process}",
        evidence_summary=_evidence_summary(rule, profile, process),
        correction_allowed=False,
    )


def generate_conj2_present(lemma: str, person: str) -> GeneratedMorphology | None:
    """Generate one finite reviewed Conjugation-2 present candidate."""
    return _generate_conj2_finite(lemma, person, "present")


def generate_conj2_past(lemma: str, person: str) -> GeneratedMorphology | None:
    """Generate one finite reviewed Conjugation-2 past candidate."""
    return _generate_conj2_finite(lemma, person, "past")


@lru_cache(maxsize=1)
def _surface_index() -> dict[str, tuple[GeneratedMorphology, ...]]:
    rule = _load_rule(CLASS_I_RULE_PATH)
    index: dict[str, list[GeneratedMorphology]] = {}
    for lemma, profile in rule.get("profiles", {}).items():
        if not isinstance(profile, dict):
            continue
        for person in profile.get("authorized_persons", []):
            candidate = generate_profile_past(str(lemma), str(person))
            if candidate is None:
                continue
            index.setdefault(candidate.surface.casefold(), []).append(candidate)
    return {key: tuple(values) for key, values in index.items()}


@lru_cache(maxsize=1)
def _conj2_surface_index() -> dict[str, tuple[GeneratedMorphology, ...]]:
    rule = _load_rule(CONJ2_RULE_PATH)
    index: dict[str, list[GeneratedMorphology]] = {}
    for lemma, profile in rule.get("profiles", {}).items():
        if not isinstance(profile, dict):
            continue
        for tense_aspect in ("present", "past"):
            authorized_key = f"authorized_{tense_aspect}_persons"
            for person in profile.get(authorized_key, []):
                candidate = _generate_conj2_finite(
                    str(lemma), str(person), tense_aspect
                )
                if candidate is None:
                    continue
                index.setdefault(candidate.surface.casefold(), []).append(candidate)
    return {key: tuple(values) for key, values in index.items()}


def analyze_morphophonological_surface(form: str) -> tuple[GeneratedMorphology, ...]:
    """Return exact forward-generated candidates from finite reviewed profiles."""
    key = form.strip().casefold()
    return _surface_index().get(key, ()) + _conj2_surface_index().get(key, ())


def eligible_profile_lemmas() -> tuple[str, ...]:
    """Return the existing Class-I development-profile lemmas."""
    rule = _load_rule(CLASS_I_RULE_PATH)
    return tuple(sorted(str(value) for value in rule.get("profiles", {})))


def eligible_conj2_profile_lemmas() -> tuple[str, ...]:
    rule = _load_rule(CONJ2_RULE_PATH)
    return tuple(sorted(str(value) for value in rule.get("profiles", {})))
