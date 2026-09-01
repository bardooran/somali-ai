from __future__ import annotations

import json
from pathlib import Path

from src.morphology_class_lexicon import reviewed_class_entry
from src.morphophonology_conj2_class_past import generate_class_authorized_conj2_past
from src.morphophonology_generator import (
    eligible_conj2_class_activation_lemmas,
    eligible_conj2_profile_lemmas,
)

REGISTRY = Path("data/qa/morphology_paradigm_v14_target_registry.json")
TARGETS = ("buufi", "caafi")


def test_v14_targets_are_registered_before_answer_lookup() -> None:
    record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    assert record["status"] == "pre_answer_target_registry"
    assert tuple(record["target_lemmas"]) == TARGETS
    assert record["target_part_of_speech"] == "verb"
    assert record["target_conjugation_class"] == "2A"
    assert record["target_tense_aspect"] == "past"
    assert record["target_person"] == "2pl"
    assert record["answer_surfaces_recorded"] is False
    assert record["answer_source_search_started"] is False
    assert record["selection_commit_base"] == (
        "4765d8812eb8a5c167e7d576458010493fcded84"
    )

    policy = record["benchmark_policy"]
    assert policy["external_answer_lookup_allowed_only_after_registry_merge"] is True
    assert policy["answers_will_be_evaluation_only"] is True
    assert policy["target_specific_runtime_special_cases_allowed"] is False
    assert policy["inferred_unattested_forms_allowed"] is False
    assert policy["unknown_safety_probes_required"] is True
    assert policy[
        "development_rule_authority_must_be_independent_of_v14_answer_sources"
    ] is True


def test_v14_targets_are_class_known_but_have_no_generic_2pl_past_authority() -> None:
    activated = set(eligible_conj2_class_activation_lemmas())
    profiles = set(eligible_conj2_profile_lemmas())

    for lemma in TARGETS:
        entry = reviewed_class_entry(lemma)
        assert entry is not None
        assert entry.part_of_speech == "verb"
        assert entry.conjugation_class == "2A"
        assert entry.status == "reviewed_class_only"
        assert entry.generation_enabled is False
        assert entry.correction_allowed is False
        assert lemma in activated
        assert lemma not in profiles
        assert generate_class_authorized_conj2_past(lemma, "2pl") is None


def test_v14_target_registry_contains_no_answer_surfaces() -> None:
    raw = REGISTRY.read_text(encoding="utf-8")
    record = json.loads(raw)

    assert "answer_surfaces" not in record
    assert "expected_surfaces" not in record
    assert record["pre_answer_state"]["generic_2pl_past_activation_exists"] is False
    assert record["pre_answer_state"]["target_specific_profiles_exist"] is False
    assert record["pre_answer_state"]["v14_answers_used_as_runtime_evidence"] is False
