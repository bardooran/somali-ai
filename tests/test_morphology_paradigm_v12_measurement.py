from __future__ import annotations

from src.morphology_paradigm_v12 import report


def test_v12_measurement_reports_two_preauthorized_unactivated_targets() -> None:
    result = report()
    assert set(result["preauthorization"]) == {"aaddi", "aammusi"}
    for values in result["preauthorization"].values():
        assert values["reviewed_class_entry_present"] is True
        assert values["expected_class_preauthorized"] is True
        assert values["generation_enabled_in_class_entry"] is False
        assert values["in_class_activation_cohort"] is False
        assert values["class_authorization_predates_answer_search"] is True


def test_v12_measurement_has_expected_denominators_and_safety_shape() -> None:
    result = report()
    combined = result["combined"]
    master = result["master"]

    assert combined["positive_row_count"] == 2
    assert combined["positive_unique_surface_count"] == 2
    assert combined["deep_feature_row_count"] == 2
    assert combined["unknown_count"] == 8
    assert master["positive_unique_surface_count"] == 2
    assert master["unknown_count"] == 8

    assert 0 <= combined["recognized_unique_surface_count"] <= 2
    assert 0 <= combined["deep_feature_matched_row_count"] <= 2
    assert 0 <= combined["unknown_rejected_count"] <= 8
    assert 0 <= master["recognized_unique_surface_count"] <= 2
    assert 0 <= master["unknown_rejected_count"] <= 8


def test_v12_measurement_preserves_holdout_policy() -> None:
    integrity = report()["holdout_integrity"]
    assert integrity["benchmark_answers_are_evaluation_only"] is True
    assert integrity["runtime_rules_changed_in_measurement_step"] is False
    assert integrity["runtime_rule_learning_from_v12_allowed"] is False
    assert integrity["class_authorization_predates_answer_search"] is True
    assert integrity["targets_unactivated_at_measurement"] is True
