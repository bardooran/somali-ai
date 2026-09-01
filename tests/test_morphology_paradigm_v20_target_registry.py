from __future__ import annotations

import json
from pathlib import Path

from src.morphology_class_lexicon import reviewed_class_entry
from src.morphophonology_conj2_class_past import eligible_conj2_class_past_activation_lemmas
from src.morphophonology_generator import eligible_conj2_class_activation_lemmas, eligible_conj2_profile_lemmas

REGISTRY = Path("data/qa/morphology_paradigm_v20_target_registry.json")
TARGETS = ("aaddi", "butaaci", "caajisi")


def _registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_v20_targets_are_registered_before_answer_lookup() -> None:
    record = _registry()
    assert record["status"] == "pre_answer_target_registry"
    assert tuple(record["target_lemmas"]) == TARGETS
    assert record["target_part_of_speech"] == "verb"
    assert record["target_conjugation_class"] == "2A"
    assert record["maximum_scored_rows"] == 9
    assert record["answer_surfaces_recorded"] is False
    assert record["answer_source_search_started"] is False
    assert record["selection_commit_base"] == "b85279847233697bf19c808391d8898a30e7b69e"
    assert record["target_cells"] == [
        {"mood": "imperative", "person": "2sg"},
        {"mood": "imperative", "person": "2pl"},
        {"form": "infinitive", "finite": False},
    ]


def test_v20_targets_are_already_reviewed_c2a_class_members() -> None:
    present_cohort = set(eligible_conj2_class_activation_lemmas())
    past_cohort = set(eligible_conj2_class_past_activation_lemmas())
    profiles = set(eligible_conj2_profile_lemmas())
    for lemma in TARGETS:
        entry = reviewed_class_entry(lemma)
        assert entry is not None
        assert entry.part_of_speech == "verb"
        assert entry.conjugation_class == "2A"
        assert entry.status == "reviewed_class_only"
        assert entry.correction_allowed is False
        assert lemma in present_cohort
        assert lemma in past_cohort
        assert lemma not in profiles


def test_v20_pins_nonfinite_gap_before_activation() -> None:
    state = _registry()["pre_answer_state"]
    assert state["generic_present_all_seven_persons_predates_v20"] is True
    assert state["generic_past_all_seven_persons_predates_v20"] is True
    assert state["generic_c2a_imperative_activation_exists"] is False
    assert state["generic_c2a_infinitive_activation_exists"] is False
    assert state["target_specific_profiles_exist"] is False
    assert state["v20_answers_used_as_runtime_evidence"] is False
    assert state["correction_authority"] is False
    assert state["open_class_generation"] is False
    assert state["reverse_suffix_stripping"] is False


def test_v20_policy_preserves_answer_isolation() -> None:
    policy = _registry()["benchmark_policy"]
    assert policy["external_answer_lookup_allowed_only_after_registry_merge"] is True
    assert policy["answers_will_be_evaluation_only"] is True
    assert policy["target_specific_runtime_special_cases_allowed"] is False
    assert policy["inferred_unattested_forms_allowed"] is False
    assert policy["unknown_safety_probes_required"] is True
    assert policy["development_rule_authority_must_be_independent_of_v20_answer_sources"] is True
    assert policy["unresolved_cells_must_remain_unscored"] is True
    assert policy["orthographic_variants_must_be_attested_not_assumed"] is True


def test_v20_registry_contains_no_answer_surfaces() -> None:
    record = _registry()
    assert "answer_surfaces" not in record
    assert "expected_surfaces" not in record
    assert "attested_surfaces" not in record
