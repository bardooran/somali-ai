from __future__ import annotations

from src.morphology_paradigm_v10 import report


def test_v10_measurement_reports_frozen_dimensions_without_runtime_learning() -> None:
    result = report()
    combined = result["combined"]
    master = result["master"]
    integrity = result["holdout_integrity"]

    assert result["benchmark"]["benchmark_version"] == "v10"
    assert combined["positive_row_count"] == 14
    assert combined["positive_unique_surface_count"] == 10
    assert combined["deep_feature_row_count"] == 14
    assert combined["syncretic_surface_count"] == 4
    assert combined["unknown_count"] == 8
    assert master["positive_unique_surface_count"] == 10
    assert master["unknown_count"] == 8
    assert integrity["benchmark_answers_are_evaluation_only"] is True
    assert integrity["runtime_rules_changed_in_measurement_step"] is False
    assert integrity["runtime_rule_learning_from_v10_allowed"] is False


def test_v10_measurement_counts_are_in_valid_ranges() -> None:
    result = report()
    combined = result["combined"]
    master = result["master"]

    assert 0 <= combined["recognized_unique_surface_count"] <= 10
    assert 0 <= combined["lemma_matched_unique_surface_count"] <= 10
    assert 0 <= combined["pos_matched_unique_surface_count"] <= 10
    assert 0 <= combined["conjugation_matched_unique_surface_count"] <= 10
    assert 0 <= combined["tense_matched_unique_surface_count"] <= 10
    assert 0 <= combined["deep_feature_matched_row_count"] <= 14
    assert 0 <= combined["syncretic_surface_preserved_count"] <= 4
    assert 0 <= combined["unknown_rejected_count"] <= 8
    assert 0 <= master["recognized_unique_surface_count"] <= 10
    assert 0 <= master["unknown_rejected_count"] <= 8


def test_v10_measurement_does_not_claim_a_global_winner() -> None:
    result = report()
    interpretation = result["interpretation"]

    assert interpretation["v10_tests_finite_conjugation2a_present_morphology"] is True
    assert interpretation["person_and_tense_features_required"] is True
    assert interpretation["syncretism_is_scored"] is True
    assert interpretation["global_morphology_winner_declared"] is False
