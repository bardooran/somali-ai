from __future__ import annotations

from src.morphology_paradigm_v17 import report


def test_v17_scorer_preserves_frozen_dimensions() -> None:
    result = report()
    combined = result["combined"]

    assert combined["positive_row_count"] == 2
    assert combined["positive_unique_surface_count"] == 2
    assert combined["deep_feature_row_count"] == 2
    assert combined["unknown_count"] == 8


def test_v17_scorer_keeps_scored_and_unresolved_targets_separate() -> None:
    result = report()
    preauthorization = result["preauthorization"]

    assert preauthorization["target_selection_predates_answer_lookup"] is True
    assert preauthorization["generic_1sg_past_authorized_at_freeze"] is False
    assert preauthorization["scored_target_lemmas"] == ["aaddi", "buufi"]
    assert preauthorization["unresolved_target_lemmas"] == ["afceli"]
    assert set(preauthorization["selected_targets"]) == {"aaddi", "afceli", "buufi"}

    for details in preauthorization["selected_targets"].values():
        assert details["reviewed_class_entry_present"] is True
        assert details["expected_class_preauthorized"] is True
        assert details["generation_enabled_in_class_entry"] is False
        assert details["target_in_class_past_activation_cohort"] is True


def test_v17_measurement_preserves_unknown_safety_and_evaluation_boundary() -> None:
    result = report()

    assert result["combined"]["unknown_rejected_count"] == 8
    assert result["combined"]["unknown_safety_rate"] == 1.0
    assert result["master"]["unknown_rejected_count"] == 8
    assert result["master"]["unknown_safety_rate"] == 1.0
    integrity = result["holdout_integrity"]
    assert integrity["benchmark_answers_are_evaluation_only"] is True
    assert integrity["runtime_rules_changed_in_measurement_step"] is False
    assert integrity["runtime_rule_learning_from_v17_allowed"] is False
    assert integrity["answer_sources_may_not_authorize_special_case_runtime_forms"] is True
    assert integrity["unresolved_targets_may_not_be_guessed"] is True


def test_v17_metadata_locks_untouched_historical_baseline() -> None:
    benchmark = report()["benchmark"]
    measured = benchmark["measured_result"]

    assert benchmark["measurement_status"] == "measured"
    assert measured["full_test_suite"] == "1180/1180 passed"
    assert measured["pull_request"] == 52
    assert measured["tested_head_commit"] == "b5e8615382cbf4387288f563993655a426b4e707"
    assert measured["workflow_run_id"] == 33493694140
    assert measured["workflow_job_id"] == 99810866856
    assert measured["somali_ai_combined_positive_surface_recognition"] == "0/2"
    assert measured["somali_ai_combined_lemma_matches"] == "0/2"
    assert measured["somali_ai_combined_pos_matches"] == "0/2"
    assert measured["somali_ai_combined_conjugation_2a_matches"] == "0/2"
    assert measured["somali_ai_combined_past_tense_matches"] == "0/2"
    assert measured["somali_ai_combined_person_matches"] == "0/2"
    assert measured["somali_ai_combined_deep_feature_rows"] == "0/2"
    assert measured["somali_ai_master_positive_surface_recognition"] == "0/2"
    assert measured["somali_ai_reviewed_exact_positive_surface_recognition"] == "0/2"
    assert measured["somali_ai_reviewed_rule_derived_positive_surface_recognition"] == "0/2"
    assert measured["unknown_safety"] == "8/8 for combined runtime and master exact"
    assert "0/2" in measured["historical_interpretation"]
    assert "afceli remained unresolved" in measured["historical_interpretation"]
    assert "1180/1180" in benchmark["notes"]


def test_v17_scorer_does_not_claim_mood_full_paradigm_or_global_win() -> None:
    interpretation = report()["interpretation"]

    assert interpretation["v17_tests_preselected_c2a_1sg_past"] is True
    assert interpretation["mood_is_scored"] is False
    assert interpretation["full_paradigm_benchmark"] is False
    assert interpretation["partial_answer_set_is_intentional"] is True
    assert interpretation["global_morphology_winner_declared"] is False
