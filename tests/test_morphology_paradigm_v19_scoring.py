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


def test_v19_untouched_runtime_has_only_the_preexisting_2sg_side_of_syncretism() -> None:
    result = report()
    combined = result["combined"]
    diagnostics = combined["syncretism_diagnostics"]

    assert combined["recognized_unique_surface_count"] == 2
    assert combined["lemma_matched_unique_surface_count"] == 2
    assert combined["pos_matched_unique_surface_count"] == 2
    assert combined["conjugation_matched_unique_surface_count"] == 2
    assert combined["tense_matched_unique_surface_count"] == 2
    assert combined["person_matched_unique_surface_count"] == 0
    assert combined["deep_feature_matched_row_count"] == 0
    assert combined["authority_diagnostics"]["reviewed_exact_surfaces"] == []
    assert combined["authority_diagnostics"]["reviewed_rule_derived_surfaces"] == [
        "bushisay",
        "caafisay",
    ]
    assert diagnostics["surface_has_2sg_analysis_count"] == 2
    assert diagnostics["surface_has_3sg_f_analysis_count"] == 0
    assert diagnostics["syncretic_surface_preserved_count"] == 0
    assert result["master"]["recognized_unique_surface_count"] == 0


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
