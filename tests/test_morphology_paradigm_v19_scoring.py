from __future__ import annotations

from src.morphology_paradigm_v19 import report


def test_v19_scorer_preserves_frozen_dimensions() -> None:
    result = report()
    combined = result["combined"]

    assert combined["positive_row_count"] == 2
    assert combined["positive_unique_surface_count"] == 2
    assert combined["deep_feature_row_count"] == 2
    assert combined["unknown_count"] == 8


def test_v19_scorer_keeps_preselected_targets_separate_from_runtime_authority() -> None:
    result = report()
    preauthorization = result["preauthorization"]

    assert preauthorization["target_selection_predates_answer_lookup"] is True
    assert preauthorization["generic_3sg_feminine_past_authorized_at_freeze"] is False
    assert preauthorization["scored_target_lemmas"] == ["caafi", "bushi"]
    assert preauthorization["unresolved_target_lemmas"] == []
    assert set(preauthorization["selected_targets"]) == {"caafi", "bushi"}

    for details in preauthorization["selected_targets"].values():
        assert details["reviewed_class_entry_present"] is True
        assert details["expected_class_preauthorized"] is True
        assert details["generation_enabled_in_class_entry"] is False
        assert details["target_in_class_past_activation_cohort"] is True


def test_v19_measurement_preserves_unknown_safety_and_evaluation_boundary() -> None:
    result = report()

    assert result["combined"]["unknown_rejected_count"] == 8
    assert result["combined"]["unknown_safety_rate"] == 1.0
    assert result["master"]["unknown_rejected_count"] == 8
    assert result["master"]["unknown_safety_rate"] == 1.0
    integrity = result["holdout_integrity"]
    assert integrity["benchmark_answers_are_evaluation_only"] is True
    assert integrity["runtime_rules_changed_in_measurement_step"] is False
    assert integrity["runtime_rule_learning_from_v19_allowed"] is False
    assert integrity["answer_sources_may_not_authorize_special_case_runtime_forms"] is True
    assert integrity["unresolved_targets_may_not_be_guessed"] is True


def test_v19_metadata_locks_untouched_historical_baseline() -> None:
    benchmark = report()["benchmark"]
    measured = benchmark["measured_result"]

    assert benchmark["measurement_status"] == "measured"
    assert measured["pull_request"] == 60
    assert measured["tested_head_commit"] == "0d002a2076bb27f6d7eef12f5c437f75df65067a"
    assert measured["workflow_run_id"] == 33500358318
    assert measured["workflow_job_id"] == 99832016710
    assert measured["workflow_conclusion"] == "success"
    assert measured["somali_ai_combined_positive_surface_recognition"] == "2/2"
    assert measured["somali_ai_combined_lemma_matches"] == "2/2"
    assert measured["somali_ai_combined_pos_matches"] == "2/2"
    assert measured["somali_ai_combined_conjugation_2a_matches"] == "2/2"
    assert measured["somali_ai_combined_past_tense_matches"] == "2/2"
    assert measured["somali_ai_combined_3sg_f_person_matches"] == "0/2"
    assert measured["somali_ai_combined_deep_feature_rows"] == "0/2"
    assert measured["somali_ai_existing_2sg_analysis"] == "2/2"
    assert measured["somali_ai_2sg_3sg_f_syncretism_preserved"] == "0/2"
    assert measured["somali_ai_reviewed_exact_positive_surface_recognition"] == "0/2"
    assert measured["somali_ai_reviewed_rule_derived_positive_surface_recognition"] == "2/2"
    assert measured["somali_ai_master_positive_surface_recognition"] == "0/2"
    assert measured["unknown_safety"] == "8/8 for combined runtime and master exact"
    assert "3sg_f person and deep-feature resolution remained 0/2" in benchmark["notes"]


def test_v19_scorer_exposes_syncretism_without_forcing_unique_person() -> None:
    diagnostics = report()["combined"]["syncretism_diagnostics"]

    assert diagnostics["expected_persons"] == ["2sg", "3sg_f"]
    assert diagnostics["syncretic_surface_count"] == 2
    assert set(diagnostics["observed_persons_by_surface"]) == {"caafisay", "bushisay"}


def test_v19_scorer_does_not_claim_full_paradigm_or_global_win() -> None:
    interpretation = report()["interpretation"]

    assert interpretation["v19_tests_preselected_c2a_3sg_feminine_past"] is True
    assert interpretation["surface_recognition_is_not_person_resolution"] is True
    assert interpretation["syncretism_with_2sg_is_expected"] is True
    assert interpretation["mood_is_scored"] is False
    assert interpretation["full_paradigm_benchmark"] is False
    assert interpretation["global_morphology_winner_declared"] is False
