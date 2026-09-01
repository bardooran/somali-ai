from __future__ import annotations

import json
from pathlib import Path

from src.morphology_class_lexicon import reviewed_class_entry
from src.morphophonology_generator import eligible_conj2_profile_lemmas

MANIFEST = Path("data/qa/morphology_paradigm_benchmark_v12.jsonl")
META = Path("data/qa/morphology_paradigm_benchmark_v12.meta.json")

TARGETS = {
    "aaddi": "aaddiyaan",
    "aammusi": "aammusiyaan",
}
RESERVE_STAGE1N = {"abhi", "afceli"}
STAGE1N = set(TARGETS) | RESERVE_STAGE1N


def _rows() -> list[dict]:
    return [
        json.loads(line)
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_v12_manifest_is_two_lemma_natural_3pl_challenge() -> None:
    rows = _rows()
    positives = [row for row in rows if row.get("benchmark_role") == "positive"]
    unknowns = [row for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(rows) == 10
    assert len(positives) == 2
    assert len(unknowns) == 8
    assert {row["lemma"]: row["surface"] for row in positives} == TARGETS
    assert all(row.get("part_of_speech") == "verb" for row in positives)
    assert all(row.get("conjugation") == "2A" for row in positives)
    assert all(row.get("tense_aspect") == "present" for row in positives)
    assert all(row.get("mood") == "indicative" for row in positives)
    assert all(row.get("person") == "3pl" for row in positives)


def test_v12_uses_two_distinct_post_class_authorization_answer_sources() -> None:
    positives = [row for row in _rows() if row.get("benchmark_role") == "positive"]
    families = {row.get("source_family") for row in positives}
    assert families == {
        "Dalka Journal 2023 Somali natural text",
        "Kapchits 2005 Sentence particles in the Somali language",
    }
    assert {row.get("surface") for row in positives} == {"aaddiyaan", "aammusiyaan"}


def test_v12_policy_pre_freeze_identity_and_historical_baseline_are_locked() -> None:
    meta = json.loads(META.read_text(encoding="utf-8"))
    assert meta["benchmark_version"] == "v12"
    assert meta["manifest_git_blob_sha"] == "6ddfc6e97245911569e833472a2c4c71af76e17d"
    assert meta["freeze_commit"] == "83c7a7d06a3a988b07a43835847e180b9b0d1fc3"
    assert meta["pre_freeze_class_authorization_commit"] == (
        "0ab8f13d2e5bc932048b413ebb3a82b445193b6a"
    )
    assert meta["pre_freeze_runtime_commit"] == (
        "0ab8f13d2e5bc932048b413ebb3a82b445193b6a"
    )
    assert meta["pre_freeze_blob_identities"] == {
        "rules/morphology/reviewed_conjugation_2_class_lexicon.json": (
            "2c4cbf5e2736cb6bd4fee7614c5495258a44c3b3"
        ),
        "rules/morphology/reviewed_conjugation_2_class_activation.json": (
            "2ff0e40c4d85784fe2d7e0d94ab8f96c2287aeea"
        ),
        "src/morphophonology_generator.py": (
            "43a62617d4f6ad9c0fad0a446afcbd9724dc703b"
        ),
    }
    assert meta["positive_case_count"] == 2
    assert meta["positive_unique_surface_count"] == 2
    assert meta["target_lemma_count"] == 2
    assert meta["unknown_case_count"] == 8
    assert set(meta["stage1n_reserve_class_only_lemmas"]) == RESERVE_STAGE1N
    assert meta["measurement_status"] == "measured"

    measured = meta["measured_result"]
    assert measured["full_test_suite"] == "1096/1096 passed"
    assert measured["somali_ai_combined_positive_surface_recognition"] == "0/2"
    assert measured["somali_ai_combined_lemma_matches"] == "0/2"
    assert measured["somali_ai_combined_pos_matches"] == "0/2"
    assert measured["somali_ai_combined_conjugation_2a_matches"] == "0/2"
    assert measured["somali_ai_combined_present_tense_matches"] == "0/2"
    assert measured["somali_ai_combined_indicative_mood_matches"] == "0/2"
    assert measured["somali_ai_combined_deep_feature_rows"] == "0/2"
    assert measured["somali_ai_reviewed_exact_positive_surface_recognition"] == "0/2"
    assert measured["somali_ai_reviewed_rule_derived_positive_surface_recognition"] == "0/2"
    assert measured["somali_ai_master_positive_surface_recognition"] == "0/2"
    assert measured["target_activation_at_baseline"] == "0/2 targets activated"
    assert measured["unknown_safety"] == "8/8 for combined runtime and master exact"
    assert measured["tested_head_commit"] == (
        "a4eb6e365b338856dc8667a2437235d553a8a9e1"
    )
    assert measured["tested_pull_request_merge_commit"] == (
        "1879179fcb4d9c536894adb1a161819527dbfa3d"
    )
    assert measured["workflow_run_id"] == 33456661445

    policy = meta["benchmark_policy"]
    assert policy["answers_are_evaluation_only"] is True
    assert policy["runtime_rule_learning_from_v12_allowed"] is False
    assert policy["explicit_source_surfaces_only"] is True
    assert policy["inferred_unattested_surfaces_included"] is False
    assert policy["pre_freeze_class_authorization_allowed"] is True
    assert policy["pre_freeze_surface_generation_for_targets_enabled"] is False
    assert policy["post_freeze_uniform_activation_of_stage1n_cohort_allowed"] is True
    assert policy["v12_answer_rows_may_authorize_special_case_runtime_forms"] is False

    design = meta["experimental_design"]
    assert design["class_authorization_predates_answer_search"] is True
    assert design["class_authorization_predates_answer_freeze"] is True
    assert design["targets_were_not_in_activation_cohort_before_freeze"] is True


def test_v12_stage1n_lemmas_remain_class_only_and_never_target_profiles() -> None:
    explicit_profiles = set(eligible_conj2_profile_lemmas())

    for lemma in STAGE1N:
        entry = reviewed_class_entry(lemma)
        assert entry is not None
        assert entry.part_of_speech == "verb"
        assert entry.conjugation_class == "2A"
        assert entry.status == "reviewed_class_only"
        assert entry.generation_enabled is False
        assert entry.correction_allowed is False
        assert lemma not in explicit_profiles


def test_v12_unknowns_are_distinct_synthetic_safety_strings() -> None:
    rows = _rows()
    positives = {row["surface"] for row in rows if row.get("benchmark_role") == "positive"}
    unknowns = [row["surface"] for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(unknowns) == len(set(unknowns)) == 8
    assert positives.isdisjoint(unknowns)
    assert all("z" in surface or "q" in surface or "v" in surface for surface in unknowns)
