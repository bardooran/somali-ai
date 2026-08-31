from __future__ import annotations

from src.morphology_paradigm_v5 import report


def test_v5_baseline_keeps_recognition_and_deep_features_separate() -> None:
    value = report()
    reviewed = value["reviewed"]["score"]
    master = value["master"]["score"]
    overlap = value["pre_freeze_overlap"]

    assert reviewed["positive_row_count"] == 37
    assert master["positive_row_count"] == 37
    assert reviewed["positive_unique_surface_count"] == 33
    assert master["positive_unique_surface_count"] == 33
    assert reviewed["unknown_count"] == 8
    assert master["unknown_count"] == 8
    assert reviewed["unknown_safety_rate"] == 1.0
    assert master["unknown_safety_rate"] == 1.0
    assert reviewed["deep_features_available"] is True
    assert master["deep_features_available"] is False
    assert master["deep_feature_matched_row_count"] == 0
    assert overlap["master_recognized_surface_count"] == master["recognized_unique_surface_count"]
    assert overlap["master_unseen_surface_count"] + overlap["master_recognized_surface_count"] == 33
    assert value["interpretation"]["global_morphology_winner_declared"] is False
