from __future__ import annotations

from src.morphology_paradigm_v6 import report


def test_v6_score_shape_and_frozen_counts() -> None:
    value = report()
    combined = value["combined"]["score"]
    master = value["master"]["score"]

    assert combined["positive_row_count"] == 21
    assert master["positive_row_count"] == 21
    assert combined["positive_unique_surface_count"] == 19
    assert master["positive_unique_surface_count"] == 19
    assert combined["unknown_count"] == 8
    assert master["unknown_count"] == 8
    assert combined["deep_features_available"] is True
    assert master["deep_features_available"] is False
    assert master["deep_feature_matched_row_count"] == 0
    assert value["interpretation"]["global_morphology_winner_declared"] is False


def test_v6_unknowns_remain_unknown_in_combined_runtime() -> None:
    value = report()
    combined = value["combined"]["score"]

    assert combined["unknown_rejected_count"] == 8
    assert combined["unknown_safety_rate"] == 1.0
    assert value["combined"]["unknown_surfaces_with_analysis"] == []


def test_v6_does_not_become_productive_rule_training_data() -> None:
    value = report()
    holdout = value["holdout_integrity"]

    assert holdout["benchmark_answers_are_evaluation_only"] is True
    assert holdout["benchmark_frozen_before_productive_rule"] is True
    assert holdout["runtime_rule_learning_from_v6_allowed"] is False
    assert holdout["reviewed_rule_derived_v6_surface_count"] == 0
    assert holdout["reviewed_rule_derived_v6_surfaces"] == []
