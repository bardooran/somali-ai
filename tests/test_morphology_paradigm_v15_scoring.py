from __future__ import annotations

from src.morphology_paradigm_v15 import report


def test_v15_scorer_preserves_frozen_dimensions() -> None:
    result = report()
    combined = result["combined"]

    assert combined["positive_row_count"] == 1
    assert combined["positive_unique_surface_count"] == 1
    assert combined["deep_feature_row_count"] == 1
    assert combined["unknown_count"] == 8


def test_v15_scorer_keeps_scored_and_unresolved_targets_separate() -> None:
    result = report()
    preauthorization = result["preauthorization"]

    assert preauthorization["target_selection_predates_answer_lookup"] is True
    assert preauthorization["generic_2sg_past_authorized_at_freeze"] is False
    assert preauthorization["scored_target_lemmas"] == ["buuxi"]
    assert preauthorization["unresolved_target_lemmas"] == ["caajisi"]
    assert set(preauthorization["selected_targets"]) == {"buuxi", "caajisi"}

    for details in preauthorization["selected_targets"].values():
        assert details["reviewed_class_entry_present"] is True
        assert details["expected_class_preauthorized"] is True
        assert details["generation_enabled_in_class_entry"] is False
        assert details["target_in_class_past_activation_cohort"] is True


def test_v15_measurement_preserves_unknown_safety_and_evaluation_boundary() -> None:
    result = report()

    assert result["combined"]["unknown_rejected_count"] == 8
    assert result["combined"]["unknown_safety_rate"] == 1.0
    assert result["master"]["unknown_rejected_count"] == 8
    assert result["master"]["unknown_safety_rate"] == 1.0
    integrity = result["holdout_integrity"]
    assert integrity["benchmark_answers_are_evaluation_only"] is True
    assert integrity["runtime_rules_changed_in_measurement_step"] is False
    assert integrity["runtime_rule_learning_from_v15_allowed"] is False
    assert integrity["answer_sources_may_not_authorize_special_case_runtime_forms"] is True
    assert integrity["unresolved_targets_may_not_be_guessed"] is True


def test_v15_scorer_does_not_claim_mood_full_paradigm_or_global_win() -> None:
    interpretation = report()["interpretation"]

    assert interpretation["v15_tests_preselected_c2a_2sg_past"] is True
    assert interpretation["mood_is_scored"] is False
    assert interpretation["full_paradigm_benchmark"] is False
    assert interpretation["partial_answer_set_is_intentional"] is True
    assert interpretation["global_morphology_winner_declared"] is False


def test_v15_freeze_identity_is_locked_before_measurement() -> None:
    benchmark = report()["benchmark"]

    assert benchmark["freeze_commit"] == "6e05780305802610870dfd94c5d64936e768b178"
    assert benchmark["freeze_status"] == "frozen"
    assert benchmark["freeze_validation"]["pull_request"] == 43
    assert benchmark["freeze_validation"]["tested_head_commit"] == (
        "a8ce9917c53a2b3a3edd1a62d61712497bcc05ba"
    )
    assert benchmark["freeze_validation"]["workflow_run_id"] == 33463736584
    assert benchmark["freeze_validation"]["workflow_job_id"] == 99719176772
    assert benchmark["freeze_validation"]["full_test_suite"] == "1142/1142 passed"


def test_v15_historical_untouched_baseline_is_locked_in_metadata() -> None:
    measured = report()["benchmark"]["measured_result"]

    assert measured["pull_request"] == 44
    assert measured["tested_head_commit"] == "cf9fe4cab77072fbeca28aa9ba5e58aea3a6c8fa"
    assert measured["workflow_run_id"] == 33464111141
    assert measured["workflow_job_id"] == 99720281376
    assert measured["full_test_suite"] == "1147/1147 passed"
    assert measured["somali_ai_combined_positive_surface_recognition"] == "0/1"
    assert measured["somali_ai_combined_lemma_matches"] == "0/1"
    assert measured["somali_ai_combined_pos_matches"] == "0/1"
    assert measured["somali_ai_combined_conjugation_2a_matches"] == "0/1"
    assert measured["somali_ai_combined_past_tense_matches"] == "0/1"
    assert measured["somali_ai_combined_person_matches"] == "0/1"
    assert measured["somali_ai_combined_deep_feature_rows"] == "0/1"
    assert measured["somali_ai_reviewed_exact_positive_surface_recognition"] == "0/1"
    assert measured["somali_ai_reviewed_rule_derived_positive_surface_recognition"] == "0/1"
    assert measured["somali_ai_master_positive_surface_recognition"] == "0/1"
    assert measured["unknown_safety"] == "8/8 for combined runtime and master exact"
