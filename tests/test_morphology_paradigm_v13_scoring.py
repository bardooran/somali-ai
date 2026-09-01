from __future__ import annotations

from src.morphology_paradigm_v13 import report


def test_v13_scorer_preserves_frozen_dimensions() -> None:
    result = report()
    combined = result["combined"]

    assert combined["positive_row_count"] == 2
    assert combined["positive_unique_surface_count"] == 2
    assert combined["deep_feature_row_count"] == 2
    assert combined["unknown_count"] == 8


def test_v13_scorer_reports_pre_answer_authorization_separately() -> None:
    result = report()
    preauthorization = result["preauthorization"]

    assert preauthorization["activation_predates_answer_lookup"] is True
    assert preauthorization["class_authorization_predates_answer_lookup"] is True
    assert set(preauthorization["targets"]) == {"abhi", "afceli"}

    for details in preauthorization["targets"].values():
        assert details["reviewed_class_entry_present"] is True
        assert details["expected_class_preauthorized"] is True
        assert details["generation_enabled_in_class_entry"] is False
        assert details["target_in_activation_cohort"] is True


def test_v13_measurement_preserves_unknown_safety_and_evaluation_boundary() -> None:
    result = report()

    assert result["combined"]["unknown_rejected_count"] == 8
    assert result["combined"]["unknown_safety_rate"] == 1.0
    assert result["master"]["unknown_rejected_count"] == 8
    assert result["master"]["unknown_safety_rate"] == 1.0
    assert result["holdout_integrity"]["benchmark_answers_are_evaluation_only"] is True
    assert result["holdout_integrity"]["runtime_rules_changed_in_measurement_step"] is False
    assert result["holdout_integrity"]["runtime_rule_learning_from_v13_allowed"] is False
    assert result["holdout_integrity"]["answer_sources_may_not_authorize_special_case_runtime_forms"] is True


def test_v13_scorer_does_not_claim_mood_or_full_paradigm_evaluation() -> None:
    interpretation = report()["interpretation"]

    assert interpretation["mood_is_scored"] is False
    assert interpretation["full_paradigm_benchmark"] is False
    assert interpretation["global_morphology_winner_declared"] is False
