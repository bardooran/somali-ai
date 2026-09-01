from __future__ import annotations

import json
from pathlib import Path

from src.morphology_analysis import analyze_morphology
from src.morphology_class_lexicon import reviewed_class_lemmas
from src.morphology_paradigm_v11 import report as v11_report
from src.morphophonology_generator import (
    analyze_morphophonological_surface,
    eligible_conj2_class_activation_lemmas,
    eligible_conj2_profile_lemmas,
    generate_class_authorized_conj2_present,
    generate_conj2_past,
)

V10 = Path("data/qa/morphology_paradigm_benchmark_v10.jsonl")
V11 = Path("data/qa/morphology_paradigm_benchmark_v11.jsonl")

EXPECTED_CLASS_LEMMAS = (
    "bushi",
    "butaaci",
    "buubi",
    "buufi",
    "buuxi",
    "caafi",
    "caajisi",
)

PERSON_PROCESS = {
    "1sg": "i_vowel_glide",
    "2sg": "i_t_assibilation",
    "3sg_m": "i_vowel_glide",
    "3sg_f": "i_t_assibilation",
    "1pl": "i_n_weak_causative_manner_alternation",
    "2pl": "i_t_assibilation",
    "3pl": "i_vowel_glide",
}


def _expected_present_surface(lemma: str, person: str) -> str:
    if person in {"1sg", "3sg_m"}:
        return lemma + "yaa"
    if person in {"2sg", "3sg_f"}:
        return lemma + "saa"
    if person == "1pl":
        return lemma + "nnaa"
    if person == "2pl":
        return lemma + "saan"
    if person == "3pl":
        return lemma + "yaan"
    raise AssertionError(person)


def test_activation_uniformly_covers_complete_pre_v11_c2a_registry() -> None:
    assert reviewed_class_lemmas("2A") == EXPECTED_CLASS_LEMMAS
    assert eligible_conj2_class_activation_lemmas() == EXPECTED_CLASS_LEMMAS

    for lemma in EXPECTED_CLASS_LEMMAS:
        for person, process in PERSON_PROCESS.items():
            candidate = generate_class_authorized_conj2_present(lemma, person)
            assert candidate is not None
            assert candidate.surface == _expected_present_surface(lemma, person)
            assert candidate.lemma == lemma
            assert candidate.part_of_speech == "verb"
            assert candidate.conjugation_class == "2A"
            assert candidate.tense_aspect == "present"
            assert candidate.mood == "indicative"
            assert candidate.person == person
            assert candidate.status == "reviewed_rule_derived"
            assert candidate.rule_id == f"MORPH-CONJ-IIA-CLASS-ACT-001:{process}"
            assert candidate.correction_allowed is False


def test_activation_generalizes_on_non_v11_lemmas_and_preserves_syncretism() -> None:
    for lemma in ("buufi", "buuxi", "caajisi"):
        singular_common = _expected_present_surface(lemma, "1sg")
        t_common = _expected_present_surface(lemma, "2sg")

        singular_people = {
            item.person
            for item in analyze_morphophonological_surface(singular_common)
            if item.lemma == lemma
        }
        t_people = {
            item.person
            for item in analyze_morphophonological_surface(t_common)
            if item.lemma == lemma
        }
        assert singular_people == {"1sg", "3sg_m"}
        assert t_people == {"2sg", "3sg_f"}

        analyses = [item for item in analyze_morphology(singular_common) if item.lemma == lemma]
        assert {item.features.get("person") for item in analyses} >= {"1sg", "3sg_m"}
        assert all(item.features.get("conjugation_class") == "2A" for item in analyses)
        assert all(item.features.get("tense_aspect") == "present" for item in analyses)
        assert all(item.features.get("mood") == "indicative" for item in analyses)
        assert all(item.correction_allowed is False for item in analyses)


def test_class_activation_does_not_create_target_specific_profiles_or_past_forms() -> None:
    explicit_profiles = set(eligible_conj2_profile_lemmas())
    assert explicit_profiles == {"joogi", "kari"}
    assert "buubi" not in explicit_profiles

    for lemma in EXPECTED_CLASS_LEMMAS:
        assert generate_conj2_past(lemma, "1sg") is None
        assert generate_conj2_past(lemma, "2sg") is None
        assert generate_conj2_past(lemma, "3pl") is None


def test_activation_never_infers_class_from_i_final_spelling() -> None:
    for unknown_lemma in ("zzabi", "qarqari", "nadiifi", "qurxi", "kari", "joogi"):
        for person in PERSON_PROCESS:
            assert generate_class_authorized_conj2_present(unknown_lemma, person) is None

    for synthetic_surface in (
        "zzabiyaa",
        "zzabisaa",
        "zzabinnaa",
        "qarqariyaan",
        "qarqarisaan",
    ):
        assert not any(
            item.rule_id.startswith("MORPH-CONJ-IIA-CLASS-ACT-001:")
            for item in analyze_morphophonological_surface(synthetic_surface)
        )


def test_frozen_v10_remains_outside_class_activation() -> None:
    for line in V10.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("benchmark_role") != "positive":
            continue
        assert not any(
            item.rule_id.startswith("MORPH-CONJ-IIA-CLASS-ACT-001:")
            for item in analyze_morphophonological_surface(str(row["surface"]))
        )


def test_v11_target_is_reached_only_through_generic_class_activation() -> None:
    positive_surfaces = {
        str(row["surface"])
        for row in (
            json.loads(line)
            for line in V11.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
        if row.get("benchmark_role") == "positive"
    }
    assert len(positive_surfaces) == 5

    for surface in positive_surfaces:
        candidates = [
            item
            for item in analyze_morphophonological_surface(surface)
            if item.lemma == "buubi"
        ]
        assert candidates
        assert all(
            item.rule_id.startswith("MORPH-CONJ-IIA-CLASS-ACT-001:")
            for item in candidates
        )
        assert all(item.correction_allowed is False for item in candidates)


def test_v11_score_demonstrates_post_freeze_cross_lemma_generalization() -> None:
    result = v11_report()
    combined = result["combined"]

    assert combined["recognized_unique_surface_count"] == 5
    assert combined["lemma_matched_unique_surface_count"] == 5
    assert combined["pos_matched_unique_surface_count"] == 5
    assert combined["conjugation_matched_unique_surface_count"] == 5
    assert combined["tense_matched_unique_surface_count"] == 5
    assert combined["mood_matched_unique_surface_count"] == 5
    assert combined["deep_feature_matched_row_count"] == 7
    assert combined["syncretic_surface_preserved_count"] == 2
    assert combined["unknown_rejected_count"] == 8
    assert combined["unknown_safety_rate"] == 1.0
    assert combined["authority_diagnostics"]["reviewed_exact_surfaces"] == []
    assert len(combined["authority_diagnostics"]["reviewed_rule_derived_surfaces"]) == 5
