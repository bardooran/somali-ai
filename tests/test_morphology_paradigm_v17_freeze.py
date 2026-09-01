from __future__ import annotations

import json
from pathlib import Path

from src.morphology_analysis import analyze_morphology
from src.morphology_class_lexicon import reviewed_class_entry
from src.morphophonology_generator import eligible_conj2_profile_lemmas

MANIFEST = Path("data/qa/morphology_paradigm_benchmark_v17.jsonl")
META = Path("data/qa/morphology_paradigm_benchmark_v17.meta.json")
REGISTRY = Path("data/qa/morphology_paradigm_v17_target_registry.json")
TARGETS = ("aaddi", "afceli", "buufi")


def _rows() -> list[dict]:
    return [
        json.loads(line)
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _meta() -> dict:
    return json.loads(META.read_text(encoding="utf-8"))


def _registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_v17_manifest_scores_only_explicit_person_resolved_surfaces() -> None:
    rows = _rows()
    positives = [row for row in rows if row.get("benchmark_role") == "positive"]
    unknowns = [row for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(rows) == 10
    assert len(positives) == 2
    assert len(unknowns) == 8
    assert [(row["id"], row["surface"], row["lemma"]) for row in positives] == [
        ("V17-AADDI-PST-1SG", "aaddiyay", "aaddi"),
        ("V17-BUUFI-PST-1SG", "buufiyay", "buufi"),
    ]
    for positive in positives:
        assert positive["part_of_speech"] == "verb"
        assert positive["conjugation"] == "2A"
        assert positive["tense_aspect"] == "past"
        assert positive["person"] == "1sg"
        assert positive["feature_scope"] == [
            "lemma",
            "part_of_speech",
            "conjugation",
            "tense_aspect",
            "person",
        ]


def test_v17_target_registry_proves_selection_predated_answer_lookup() -> None:
    registry = _registry()

    assert registry["status"] == "pre_answer_target_registry"
    assert tuple(registry["target_lemmas"]) == TARGETS
    assert registry["target_tense_aspect"] == "past"
    assert registry["target_person"] == "1sg"
    assert registry["answer_surfaces_recorded"] is False
    assert registry["answer_source_search_started"] is False
    assert registry["selection_commit_base"] == (
        "6c66f97d58d8a0d667a9f3cc19539049c9a2803c"
    )
    assert registry["pre_answer_state"]["generic_1sg_past_activation_exists"] is False
    assert registry["benchmark_policy"]["inferred_unattested_forms_allowed"] is False


def test_v17_metadata_records_partial_attestation_without_guessing_afceli() -> None:
    meta = _meta()

    assert meta["benchmark_version"] == "v17"
    assert meta["manifest_git_blob_sha"] == "8f9d1bd4fd9e71a034c105eacaae19d3a05023d4"
    assert meta["pre_answer_target_registry_merge_commit"] == (
        "2d432b6edacb96e18a93ae9fd52cf0af52e6b793"
    )
    assert meta["selected_target_lemmas"] == list(TARGETS)
    assert meta["scored_target_lemmas"] == ["aaddi", "buufi"]
    assert meta["unresolved_target_lemmas"] == ["afceli"]
    assert meta["positive_case_count"] == 2
    assert meta["unknown_case_count"] == 8

    unresolved = meta["unresolved_targets"]
    assert len(unresolved) == 1
    assert unresolved[0]["lemma"] == "afceli"
    assert unresolved[0]["status"] == "unresolved_not_scored"
    assert "No surface is inferred" in unresolved[0]["reason"]

    sources = meta["answer_sources"]
    assert [(item["target_lemma"], item["surface"]) for item in sources] == [
        ("aaddi", "aaddiyay"),
        ("buufi", "buufiyay"),
    ]
    assert sources[0]["source_family"] == "Hadhwanaag 2020 Wax Tegay natural narrative"
    assert sources[1]["source_family"] == "Harvard ELIAS Beginning Somali Lesson 25"


def test_v17_freeze_metadata_is_pending_validation_before_ci_lock() -> None:
    meta = _meta()
    assert meta["freeze_status"] == "pending_validation"
    assert meta["measurement_status"] == "not_measured"
    assert "freeze_commit" not in meta
    assert "freeze_validation" not in meta


def test_v17_freeze_pins_historical_four_cell_scope_and_1sg_gap() -> None:
    meta = _meta()
    state = meta["pre_freeze_runtime_state"]

    assert state["authorized_class_past_persons"] == ["1pl", "2sg", "2pl", "3pl"]
    assert state["generic_1sg_past_authorized"] is False
    assert state["aaddi_1sg_past_available"] is False
    assert state["afceli_1sg_past_available"] is False
    assert state["buufi_1sg_past_available"] is False
    assert state["target_specific_profiles_allowed"] is False
    assert meta["pre_freeze_runtime_blob_identities"] == {
        "rules/morphology/reviewed_conjugation_2_class_past_activation.json": "76460bc7e4f21cf235e908d3f9f1946c1fc296c9",
        "src/morphology_analysis.py": "11b5b04e4c617100d0e05a20775420f5775e33a7",
        "src/morphophonology_conj2_class_past.py": "0c1f3c839902037df490a2722a2e2c458c969d4f",
    }


def test_v17_targets_remain_class_entries_not_target_specific_profiles() -> None:
    profiles = set(eligible_conj2_profile_lemmas())

    for lemma in TARGETS:
        entry = reviewed_class_entry(lemma)
        assert entry is not None
        assert entry.part_of_speech == "verb"
        assert entry.conjugation_class == "2A"
        assert entry.status == "reviewed_class_only"
        assert entry.generation_enabled is False
        assert entry.correction_allowed is False
        assert lemma not in profiles


def test_v17_policy_keeps_answer_evidence_out_of_runtime_authority() -> None:
    policy = _meta()["benchmark_policy"]

    assert policy["answers_are_evaluation_only"] is True
    assert policy["runtime_rule_learning_from_v17_allowed"] is False
    assert policy["answer_sources_may_not_authorize_special_case_runtime_forms"] is True
    assert policy["explicit_source_surfaces_only"] is True
    assert policy["inferred_unattested_surfaces_included"] is False
    assert policy["unresolved_targets_may_not_be_guessed"] is True
    assert policy["syncretic_person_values_require_contextual_resolution"] is True
    assert policy[
        "future_generic_1sg_past_improvement_allowed_from_independent_development_evidence"
    ] is True
    assert policy[
        "development_rule_authority_must_be_independent_of_v17_answer_sources"
    ] is True


def test_v17_unknowns_are_synthetic_distinct_and_remain_safe() -> None:
    rows = _rows()
    positives = {row["surface"] for row in rows if row.get("benchmark_role") == "positive"}
    unknowns = [row["surface"] for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(unknowns) == len(set(unknowns)) == 8
    assert positives.isdisjoint(unknowns)
    assert all("q" in surface or "v" in surface or "z" in surface for surface in unknowns)
    for surface in unknowns:
        assert analyze_morphology(surface) == ()
