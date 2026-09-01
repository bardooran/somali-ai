from __future__ import annotations

import json
from pathlib import Path

from src.morphology_analysis import analyze_morphology
from src.morphology_class_lexicon import reviewed_class_entry
from src.morphophonology_generator import eligible_conj2_profile_lemmas

MANIFEST = Path("data/qa/morphology_paradigm_benchmark_v16.jsonl")
META = Path("data/qa/morphology_paradigm_benchmark_v16.meta.json")
REGISTRY = Path("data/qa/morphology_paradigm_v16_target_registry.json")
TARGETS = ("bushi", "butaaci", "buubi")


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


def test_v16_manifest_scores_only_explicitly_attested_buubi_surface() -> None:
    rows = _rows()
    positives = [row for row in rows if row.get("benchmark_role") == "positive"]
    unknowns = [row for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(rows) == 9
    assert len(positives) == 1
    assert len(unknowns) == 8
    positive = positives[0]
    assert positive["id"] == "V16-BUUBI-PST-1PL"
    assert positive["surface"] == "buubinnay"
    assert positive["lemma"] == "buubi"
    assert positive["part_of_speech"] == "verb"
    assert positive["conjugation"] == "2A"
    assert positive["tense_aspect"] == "past"
    assert positive["person"] == "1pl"
    assert positive["feature_scope"] == [
        "lemma",
        "part_of_speech",
        "conjugation",
        "tense_aspect",
        "person",
    ]
    assert positive["source_family"] == "Green 2021 Somali Grammar"
    assert positive["source_table"] == "50"


def test_v16_target_registry_proves_selection_predated_answer_lookup() -> None:
    registry = _registry()

    assert registry["status"] == "pre_answer_target_registry"
    assert tuple(registry["target_lemmas"]) == TARGETS
    assert registry["target_tense_aspect"] == "past"
    assert registry["target_person"] == "1pl"
    assert registry["answer_surfaces_recorded"] is False
    assert registry["answer_source_search_started"] is False
    assert registry["selection_commit_base"] == (
        "301600a65409724d366895d75d5a74144930bcda"
    )
    assert registry["pre_answer_state"]["generic_1pl_past_activation_exists"] is False
    assert registry["benchmark_policy"]["inferred_unattested_forms_allowed"] is False


def test_v16_metadata_records_partial_attestation_without_guessing_unresolved_targets() -> None:
    meta = _meta()

    assert meta["benchmark_version"] == "v16"
    assert meta["manifest_git_blob_sha"] == "17f92a5d64aaa933a860c125e7fccb12f1b9ccf8"
    assert meta["pre_answer_target_registry_merge_commit"] == (
        "ab04068f4ab7a2b563020f2375f22201f1d732c1"
    )
    assert meta["selected_target_lemmas"] == list(TARGETS)
    assert meta["scored_target_lemmas"] == ["buubi"]
    assert meta["unresolved_target_lemmas"] == ["bushi", "butaaci"]
    assert meta["positive_case_count"] == 1
    assert meta["unknown_case_count"] == 8

    unresolved = meta["unresolved_targets"]
    assert [item["lemma"] for item in unresolved] == ["bushi", "butaaci"]
    assert all(item["status"] == "unresolved_not_scored" for item in unresolved)
    assert all("No surface is inferred" in item["reason"] for item in unresolved)

    source = meta["answer_sources"][0]
    assert source["target_lemma"] == "buubi"
    assert source["surface"] == "buubinnay"
    assert source["source_family"] == "Green 2021 Somali Grammar"
    assert source["source_table"] == "50"
    assert source["evidence_type"] == "explicit_scholarly_paradigm_table"


def test_v16_freeze_pins_historical_three_cell_class_past_scope_and_1pl_gap() -> None:
    meta = _meta()
    state = meta["pre_freeze_runtime_state"]

    assert state["authorized_class_past_persons"] == ["2sg", "2pl", "3pl"]
    assert state["generic_1pl_past_authorized"] is False
    assert state["bushi_1pl_past_available"] is False
    assert state["butaaci_1pl_past_available"] is False
    assert state["buubi_1pl_past_available"] is False
    assert state["target_specific_profiles_allowed"] is False
    assert meta["pre_freeze_runtime_blob_identities"][
        "rules/morphology/reviewed_conjugation_2_class_past_activation.json"
    ] == "4ca74d7d73483214dd2744134d8140160d4632a6"
    assert meta["benchmark_policy"][
        "future_generic_1pl_past_improvement_allowed_from_independent_development_evidence"
    ] is True


def test_v16_targets_remain_class_entries_not_target_specific_profiles() -> None:
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


def test_v16_policy_keeps_answer_evidence_out_of_runtime_authority() -> None:
    policy = _meta()["benchmark_policy"]

    assert policy["answers_are_evaluation_only"] is True
    assert policy["runtime_rule_learning_from_v16_allowed"] is False
    assert policy["answer_sources_may_not_authorize_special_case_runtime_forms"] is True
    assert policy["explicit_source_surfaces_only"] is True
    assert policy["inferred_unattested_surfaces_included"] is False
    assert policy["unresolved_targets_may_not_be_guessed"] is True
    assert policy[
        "future_generic_1pl_past_improvement_allowed_from_independent_development_evidence"
    ] is True
    assert policy[
        "development_rule_authority_must_be_independent_of_v16_answer_sources"
    ] is True


def test_v16_unknowns_are_synthetic_distinct_and_remain_safe() -> None:
    rows = _rows()
    positives = {row["surface"] for row in rows if row.get("benchmark_role") == "positive"}
    unknowns = [row["surface"] for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(unknowns) == len(set(unknowns)) == 8
    assert positives.isdisjoint(unknowns)
    assert all("q" in surface or "v" in surface or "z" in surface for surface in unknowns)
    for surface in unknowns:
        assert analyze_morphology(surface) == ()
