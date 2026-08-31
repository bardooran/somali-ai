from __future__ import annotations

from src.morphology_challenge_v3 import load_cases, report


def test_v3_manifest_shape_is_frozen() -> None:
    cases = load_cases()
    positives = [case for case in cases if case["split"] == "challenge"]
    unknowns = [case for case in cases if case["split"] == "unknown"]
    assert len(cases) == 126
    assert len(positives) == 110
    assert len(unknowns) == 16
    assert all(case["benchmark_version"] == "v3" for case in cases)


def test_v3_master_runtime_does_not_change_benchmark_contract() -> None:
    value = report()
    reviewed = value["reviewed"]["score"]
    master = value["master"]["score"]
    assert reviewed["benchmark_version"] == "v3"
    assert master["benchmark_version"] == "v3"
    for key in ("case_count", "positive_case_count", "expected_type_count", "unknown_case_count"):
        assert reviewed[key] == master[key]
    assert value["interpretation"]["benchmark_was_frozen_before_master_runtime_evaluation"] is True
    assert value["interpretation"]["master_recognition_does_not_authorize_correction"] is True
    assert 0.0 <= master["positive_recognition_rate"] <= 1.0
    assert 0.0 <= master["type_precision"] <= 1.0
    assert 0.0 <= master["unknown_safety_rate"] <= 1.0
