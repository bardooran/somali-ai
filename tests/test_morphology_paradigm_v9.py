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
