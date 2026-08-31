from __future__ import annotations

from src.morphology_paradigm_v8 import report


def test_v8_runtime_score_shape() -> None:
    value = report()
    combined = value["combined"]
    master = value["master"]

    assert combined["positive_row_count"] == 7
    assert combined["positive_unique_surface_count"] == 7
    assert master["positive_unique_surface_count"] == 7
    assert combined["unknown_count"] == 8
    assert master["unknown_count"] == 8
    assert combined["syncretic_surface_count"] == 0


def test_v8_unknown_safety_is_preserved() -> None:
    value = report()

    assert value["combined"]["unknown_rejected_count"] == 8
    assert value["combined"]["unknown_safety_rate"] == 1.0
    assert value["combined"]["unknown_surfaces_with_analysis"] == []
    assert value["master"]["unknown_rejected_count"] == 8
    assert value["master"]["unknown_safety_rate"] == 1.0
    assert value["master"]["unknown_surfaces_with_analysis"] == []


def test_v8_measurement_does_not_change_runtime_or_learn_answers() -> None:
    value = report()
    integrity = value["holdout_integrity"]

    assert integrity["benchmark_answers_are_evaluation_only"] is True
    assert integrity["runtime_rules_changed_in_measurement_step"] is False
    assert integrity["runtime_rule_learning_from_v8_allowed"] is False
    assert value["combined"]["authority_diagnostics"]["reviewed_exact_surfaces"] == []
    assert value["combined"]["authority_diagnostics"]["reviewed_rule_derived_surfaces"] == []
