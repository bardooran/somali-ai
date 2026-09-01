from __future__ import annotations

from src.morphology_paradigm_v20 import report


def test_v20_scorer_preserves_frozen_dimensions() -> None:
    result = report()
    combined = result["combined"]

    assert combined["positive_row_count"] == 5
    assert combined["positive_unique_surface_count"] == 5
    assert combined["deep_feature_row_count"] == 5
    assert combined["imperative_row_count"] == 2
    assert combined["infinitive_row_count"] == 3
    assert combined["unknown_count"] == 8


def test_v20_scorer_keeps_unresolved_cells_out_of_score() -> None:
    result = report()
    unresolved = result["preauthorization"]["unresolved_cells"]

    assert len(unresolved) == 4
    assert {(row["lemma"], row["mood"], row["person"]) for row in unresolved} == {
        ("butaaci", "imperative", "2sg"),
        ("butaaci", "imperative", "2pl"),
        ("caajisi", "imperative", "2sg"),
        ("caajisi", "imperative", "2pl"),
    }


def test_v20_measurement_preserves_holdout_boundary() -> None:
    result = report()
    integrity = result["holdout_integrity"]

    assert integrity["benchmark_answers_are_evaluation_only"] is True
    assert integrity["runtime_rule_learning_from_v20_allowed"] is False
    assert integrity["unresolved_cells_may_not_be_guessed"] is True
    assert integrity["target_specific_special_cases_allowed"] is False


def test_v20_measurement_preserves_freeze_authorization_state() -> None:
    result = report()
    preauthorization = result["preauthorization"]

    assert preauthorization["generic_c2a_imperative_authorized_at_freeze"] is False
    assert preauthorization["generic_c2a_infinitive_authorized_at_freeze"] is False
    assert set(preauthorization["selected_targets"]) == {"aaddi", "butaaci", "caajisi"}

    for details in preauthorization["selected_targets"].values():
        assert details["reviewed_class_entry_present"] is True
        assert details["class_entry_generation_enabled"] is False
        assert details["class_entry_correction_allowed"] is False


def test_v20_unknown_probes_remain_safe_at_measurement() -> None:
    result = report()

    assert result["combined"]["unknown_rejected_count"] == 8
    assert result["master"]["unknown_rejected_count"] == 8


def test_v20_does_not_claim_full_registry_or_global_win() -> None:
    interpretation = report()["interpretation"]

    assert interpretation["v20_tests_c2a_imperative_and_infinitive"] is True
    assert interpretation["full_nine_cell_registry_scored"] is False
    assert interpretation["only_independently_defensible_rows_scored"] is True
    assert interpretation["global_morphology_winner_declared"] is False
