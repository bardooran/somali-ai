from __future__ import annotations

from src.morphology_paradigm_v14 import report


def test_v14_scorer_preserves_frozen_dimensions() -> None:
    result = report()
    combined = result["combined"]

    assert combined["positive_row_count"] == 1
    assert combined["positive_unique_surface_count"] == 1
    assert combined["deep_feature_row_count"] == 1
    assert combined["unknown_count"] == 8


def test_v14_scorer_keeps_scored_and_unresolved_targets_separate() -> None:
    result = report()
    preauthorization = result["preauthorization"]

    assert preauthorization["target_selection_predates_answer_lookup"] is True
    assert preauthorization["generic_2pl_past_authorized_at_freeze"] is False
    assert preauthorization["scored_target_lemmas"] == ["buufi"]
    assert preauthorization["unresolved_target_lemmas"] == ["caafi"]
    assert set(preauthorization["selected_targets"]) == {"buufi", "caafi"}

    for details in preauthorization["selected_targets"].values():
        assert details["reviewed_class_entry_present"] is True
        assert details["expected_class_preauthorized"] is True
        assert details["generation_enabled_in_class_entry"] is False
        assert details["target_in_class_past_activation_cohort"] is True


def test_v14_measurement_preserves_unknown_safety_and_evaluation_boundary() -> None:
    result = report()

    assert result["combined"]["unknown_rejected_count"] == 8
    assert result["combined"]["unknown_safety_rate"] == 1.0
    assert result["master"]["unknown_rejected_count"] == 8
    assert result["master"]["unknown_safety_rate"] == 1.0
    integrity = result["holdout_integrity"]
    assert integrity["benchmark_answers_are_evaluation_only"] is True
    assert integrity["runtime_rules_changed_in_measurement_step"] is False
    assert integrity["runtime_rule_learning_from_v14_allowed"] is False
    assert integrity["answer_sources_may_not_authorize_special_case_runtime_forms"] is True
    assert integrity["unresolved_targets_may_not_be_guessed"] is True


def test_v14_scorer_does_not_claim_mood_full_paradigm_or_global_win() -> None:
    interpretation = report()["interpretation"]

    assert interpretation["v14_tests_preselected_c2a_2pl_past"] is True
    assert interpretation["mood_is_scored"] is False
    assert interpretation["full_paradigm_benchmark"] is False
    assert interpretation["partial_answer_set_is_intentional"] is True
    assert interpretation["global_morphology_winner_declared"] is False
