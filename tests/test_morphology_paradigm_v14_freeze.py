from __future__ import annotations

import json
from pathlib import Path

from src.morphology_analysis import analyze_morphology
from src.morphology_class_lexicon import reviewed_class_entry
from src.morphophonology_generator import eligible_conj2_profile_lemmas

MANIFEST = Path("data/qa/morphology_paradigm_benchmark_v14.jsonl")
META = Path("data/qa/morphology_paradigm_benchmark_v14.meta.json")
REGISTRY = Path("data/qa/morphology_paradigm_v14_target_registry.json")


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


def test_v14_manifest_scores_only_independently_attested_buufi_surface() -> None:
    rows = _rows()
    positives = [row for row in rows if row.get("benchmark_role") == "positive"]
    unknowns = [row for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(rows) == 9
    assert len(positives) == 1
    assert len(unknowns) == 8
    assert positives[0]["id"] == "V14-BUUFI-PST-2PL"
    assert positives[0]["surface"] == "buufiseen"
    assert positives[0]["lemma"] == "buufi"
    assert positives[0]["part_of_speech"] == "verb"
    assert positives[0]["conjugation"] == "2A"
    assert positives[0]["tense_aspect"] == "past"
    assert positives[0]["person"] == "2pl"
    assert positives[0]["feature_scope"] == [
        "lemma",
        "part_of_speech",
        "conjugation",
        "tense_aspect",
        "person",
    ]


def test_v14_target_registry_proves_selection_predated_answer_lookup() -> None:
    registry = _registry()

    assert registry["status"] == "pre_answer_target_registry"
    assert registry["target_lemmas"] == ["buufi", "caafi"]
    assert registry["target_tense_aspect"] == "past"
    assert registry["target_person"] == "2pl"
    assert registry["answer_surfaces_recorded"] is False
    assert registry["answer_source_search_started"] is False
    assert registry["pre_answer_state"]["generic_2pl_past_activation_exists"] is False
    assert registry["benchmark_policy"]["inferred_unattested_forms_allowed"] is False


def test_v14_metadata_locks_freeze_and_historical_zero_baseline() -> None:
    meta = _meta()

    assert meta["benchmark_version"] == "v14"
    assert meta["manifest_git_blob_sha"] == "67786024c209abed20388bf47a6287b3d99efcd7"
    assert meta["freeze_commit"] == "7d7039565391a7641be3a29ae037f253a3b3f698"
    assert meta["freeze_status"] == "frozen"
    assert meta["measurement_status"] == "measured"
    assert meta["freeze_validation"] == {
        "pull_request": 39,
        "tested_head_commit": "03a4de5fe16244636541699f96dc598a754c6b2f",
        "workflow_run_id": 33461609377,
        "workflow_job_id": 99712712452,
        "full_test_suite": "1125/1125 passed",
    }

    measured = meta["measured_result"]
    assert measured["pull_request"] == 40
    assert measured["tested_head_commit"] == "d0e1d169b469c62d4e838b31d2fc758382d3b901"
    assert measured["workflow_run_id"] == 33462088895
    assert measured["workflow_job_id"] == 99714184959
    assert measured["full_test_suite"] == "1129/1129 passed"
    assert measured["somali_ai_combined_positive_surface_recognition"] == "0/1"
    assert measured["somali_ai_combined_deep_feature_rows"] == "0/1"
    assert measured["somali_ai_reviewed_exact_positive_surface_recognition"] == "0/1"
    assert measured["somali_ai_reviewed_rule_derived_positive_surface_recognition"] == "0/1"
    assert measured["somali_ai_master_positive_surface_recognition"] == "0/1"
    assert measured["unknown_safety"] == "8/8 for combined runtime and master exact"

    state = meta["pre_freeze_runtime_state"]
    assert state["authorized_class_past_persons"] == ["3pl"]
    assert state["generic_2pl_past_authorized"] is False
    assert state["buufi_2pl_past_available"] is False
    assert state["caafi_2pl_past_available"] is False


def test_v14_metadata_records_partial_attestation_without_guessing_caafi() -> None:
    meta = _meta()

    assert meta["pre_answer_target_registry_merge_commit"] == (
        "107b733021e27b8da6ba1470e76946d0b7181a78"
    )
    assert meta["selected_target_lemmas"] == ["buufi", "caafi"]
    assert meta["scored_target_lemmas"] == ["buufi"]
    assert meta["unresolved_target_lemmas"] == ["caafi"]
    assert meta["positive_case_count"] == 1
    assert meta["unknown_case_count"] == 8

    unresolved = meta["unresolved_targets"]
    assert len(unresolved) == 1
    assert unresolved[0]["lemma"] == "caafi"
    assert unresolved[0]["status"] == "unresolved_not_scored"
    assert "No surface is inferred" in unresolved[0]["reason"]

    verification = meta["answer_sources"][0]["verification"]
    assert verification["pdf_text_layer_verified"] is True
    assert verification["web_screenshot_attempted"] is True
    assert verification["web_screenshot_succeeded"] is False
    assert verification["visual_screenshot_claimed"] is False

    policy = meta["benchmark_policy"]
    assert policy["answers_are_evaluation_only"] is True
    assert policy["runtime_rule_learning_from_v14_allowed"] is False
    assert policy["unresolved_targets_may_not_be_guessed"] is True
    assert policy[
        "future_generic_2pl_past_improvement_allowed_from_independent_development_evidence"
    ] is True


def test_v14_targets_remain_class_entries_not_target_specific_profiles() -> None:
    profiles = set(eligible_conj2_profile_lemmas())

    for lemma in ("buufi", "caafi"):
        entry = reviewed_class_entry(lemma)
        assert entry is not None
        assert entry.part_of_speech == "verb"
        assert entry.conjugation_class == "2A"
        assert entry.status == "reviewed_class_only"
        assert entry.generation_enabled is False
        assert entry.correction_allowed is False
        assert lemma not in profiles


def test_v14_unknowns_are_synthetic_distinct_and_remain_safe() -> None:
    rows = _rows()
    positives = {row["surface"] for row in rows if row.get("benchmark_role") == "positive"}
    unknowns = [row["surface"] for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(unknowns) == len(set(unknowns)) == 8
    assert positives.isdisjoint(unknowns)
    assert all("q" in surface or "v" in surface or "z" in surface for surface in unknowns)
    for surface in unknowns:
        assert analyze_morphology(surface) == ()
