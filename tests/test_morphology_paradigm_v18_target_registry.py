from __future__ import annotations

import json
from pathlib import Path

from src.morphology_class_lexicon import reviewed_class_entry
from src.morphophonology_conj2_class_past import eligible_conj2_class_past_activation_lemmas
from src.morphophonology_generator import eligible_conj2_profile_lemmas

REGISTRY = Path("data/qa/morphology_paradigm_v18_target_registry.json")
TARGETS = ("aammusi", "abhi")


def _registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_v18_targets_are_registered_before_answer_lookup() -> None:
    record = _registry()

    assert record["status"] == "pre_answer_target_registry"
    assert tuple(record["target_lemmas"]) == TARGETS
    assert record["target_part_of_speech"] == "verb"
    assert record["target_conjugation_class"] == "2A"
    assert record["target_tense_aspect"] == "past"
    assert record["target_person"] == "3sg_masculine"
    assert record["answer_surfaces_recorded"] is False
    assert record["answer_source_search_started"] is False
    assert record["selection_commit_base"] == (
        "219c9c0d892d0c04b59352af5a836af1d879dc4b"
    )

    policy = record["benchmark_policy"]
    assert policy["external_answer_lookup_allowed_only_after_registry_merge"] is True
    assert policy["answers_will_be_evaluation_only"] is True
    assert policy["target_specific_runtime_special_cases_allowed"] is False
    assert policy["inferred_unattested_forms_allowed"] is False
    assert policy["unknown_safety_probes_required"] is True
    assert policy[
        "development_rule_authority_must_be_independent_of_v18_answer_sources"
    ] is True
    assert policy["unresolved_targets_must_remain_unscored"] is True
    assert policy["orthographic_variants_must_be_attested_not_assumed"] is True
    assert policy["syncretic_person_values_must_be_preserved_as_ambiguity"] is True
    assert policy["surface_recognition_must_not_force_unique_person"] is True


def test_v18_targets_are_class_known_and_not_target_specific_profiles() -> None:
    past_cohort = set(eligible_conj2_class_past_activation_lemmas())
    profiles = set(eligible_conj2_profile_lemmas())

    for lemma in TARGETS:
        entry = reviewed_class_entry(lemma)
        assert entry is not None
        assert entry.part_of_speech == "verb"
        assert entry.conjugation_class == "2A"
        assert entry.status == "reviewed_class_only"
        assert entry.generation_enabled is False
        assert entry.correction_allowed is False
        assert lemma in past_cohort
        assert lemma not in profiles


def test_v18_selection_pins_pre_answer_five_cell_class_past_scope() -> None:
    state = _registry()["pre_answer_state"]

    assert state["authorized_class_past_persons"] == [
        "1sg",
        "1pl",
        "2sg",
        "2pl",
        "3pl",
    ]
    assert state["generic_3sg_masculine_past_activation_exists"] is False
    assert state["target_specific_profiles_exist"] is False
    assert state["v18_answers_used_as_runtime_evidence"] is False
    assert state["one_surface_can_have_multiple_person_analyses"] is True
    assert state["documented_1sg_3sg_masculine_syncretism_predates_v18"] is True


def test_v18_registry_contains_no_answer_surface_fields_or_answers() -> None:
    record = _registry()
    raw = REGISTRY.read_text(encoding="utf-8")

    assert "answer_surfaces" not in record
    assert "expected_surfaces" not in record
    assert record["pre_answer_state"]["target_specific_profiles_exist"] is False
    assert record["pre_answer_state"]["v18_answers_used_as_runtime_evidence"] is False
    for lemma in TARGETS:
        assert lemma in raw
