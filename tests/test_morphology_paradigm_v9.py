from __future__ import annotations

from src.morphology_paradigm_v9 import report


def test_v9_report_shape_and_holdout_integrity() -> None:
    result = report()
    assert result["benchmark"]["benchmark_version"] == "v9"
    assert result["combined"]["positive_unique_surface_count"] == 7
    assert result["combined"]["comparable_feature_row_count"] == 7
    assert result["combined"]["unknown_count"] == 8
    assert result["master"]["positive_unique_surface_count"] == 7
    assert result["master"]["unknown_count"] == 8
    assert result["holdout_integrity"] == {
        "benchmark_answers_are_evaluation_only": True,
        "runtime_rules_changed_in_measurement_step": False,
        "runtime_rule_learning_from_v9_allowed": False,
    }


def test_v9_measurement_does_not_require_person_or_tense() -> None:
    result = report()
    assert result["interpretation"]["v9_tests_nonfinite_conjugation2_morphology"] is True
    assert result["interpretation"]["person_or_tense_features_required"] is False


def test_v9_unknown_safety_metrics_are_bounded() -> None:
    result = report()
    for system in ("combined", "master"):
        score = result[system]
        assert 0 <= score["unknown_rejected_count"] <= 8
        assert 0.0 <= score["unknown_safety_rate"] <= 1.0


def test_v9_authority_diagnostics_are_explicit() -> None:
    result = report()
    diagnostics = result["combined"]["authority_diagnostics"]
    assert set(diagnostics) == {
        "reviewed_exact_surfaces",
        "reviewed_rule_derived_surfaces",
    }


def test_v9_historical_baseline_is_recorded_as_clean_zero_overlap() -> None:
    result = report()
    measured = result["benchmark"]["measured_result"]

    assert result["benchmark"]["freeze_commit"] == "f84bd99fab4162ded31d7469989b3200333df7da"
    assert result["benchmark"]["manifest_git_blob_sha"] == "a3ed1aa4e9c44a42daee23c37ca585160cb6adda"
    assert result["benchmark"]["pre_freeze_overlap_status"] == "measured"
    assert measured["somali_ai_combined_positive_surface_recognition"] == "0/7"
    assert measured["somali_ai_master_positive_surface_recognition"] == "0/7"
    assert measured["somali_ai_combined_comparable_feature_rows"] == "0/7"
    assert measured["somali_ai_reviewed_exact_positive_surface_recognition"] == "0/7"
    assert measured["somali_ai_reviewed_rule_derived_positive_surface_recognition"] == "0/7"
    assert measured["unknown_safety"] == "8/8 for combined runtime and master exact"
    assert measured["workflow_run_id"] == 33448961752

    # These are the live values at the measurement commit. Keeping the exact
    # assertions here prevents the baseline-recording PR from silently changing
    # the state it claims to have measured.
    assert result["combined"]["recognized_unique_surface_count"] == 0
    assert result["combined"]["comparable_feature_matched_row_count"] == 0
    assert result["combined"]["authority_diagnostics"]["reviewed_exact_surfaces"] == []
    assert result["combined"]["authority_diagnostics"]["reviewed_rule_derived_surfaces"] == []
    assert result["combined"]["unknown_rejected_count"] == 8
    assert result["master"]["recognized_unique_surface_count"] == 0
    assert result["master"]["unknown_rejected_count"] == 8
