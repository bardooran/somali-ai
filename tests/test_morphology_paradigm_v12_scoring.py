from __future__ import annotations

from src.morphology_paradigm_v12 import report


def test_v12_scorer_preserves_frozen_dimensions() -> None:
    result = report()
    combined = result["combined"]

    assert combined["positive_row_count"] == 2
    assert combined["positive_unique_surface_count"] == 2
    assert combined["deep_feature_row_count"] == 2
    assert combined["unknown_count"] == 8


def test_v12_scorer_reports_preexisting_class_authorization_separately() -> None:
    result = report()
    preauthorization = result["preauthorization"]

    assert preauthorization["class_authorization_predates_answer_search"] is True
    assert preauthorization["class_authorization_predates_answer_freeze"] is True
    assert set(preauthorization["targets"]) == {"aaddi", "aammusi"}

    for details in preauthorization["targets"].values():
        assert details["reviewed_class_entry_present"] is True
        assert details["expected_class_preauthorized"] is True
        assert details["generation_enabled_in_class_entry"] is False
        assert isinstance(details["target_in_activation_cohort"], bool)


def test_v12_measurement_preserves_unknown_safety_and_evaluation_boundary() -> None:
    result = report()

    assert result["combined"]["unknown_rejected_count"] == 8
    assert result["combined"]["unknown_safety_rate"] == 1.0
    assert result["master"]["unknown_rejected_count"] == 8
    assert result["master"]["unknown_safety_rate"] == 1.0
    assert result["holdout_integrity"]["benchmark_answers_are_evaluation_only"] is True
    assert result["holdout_integrity"]["runtime_rules_changed_in_measurement_step"] is False
    assert result["holdout_integrity"]["runtime_rule_learning_from_v12_allowed"] is False
