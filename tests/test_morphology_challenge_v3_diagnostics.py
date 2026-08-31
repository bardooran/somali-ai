from __future__ import annotations

from src.morphology_challenge_v3 import report
from src.morphology_challenge_v3_gap_audit import audit


def test_v3_per_pos_breakdown_partitions_frozen_positive_cases() -> None:
    value = report()
    expected_counts = {"noun": 48, "verb": 48, "numeral": 8, "adjective": 6}
    for system in ("reviewed", "master"):
        per_pos = value[system]["per_pos"]
        assert {pos: data["positive_case_count"] for pos, data in per_pos.items()} == expected_counts
        assert sum(data["positive_case_count"] for data in per_pos.values()) == 110
        for data in per_pos.values():
            assert 0.0 <= data["recognition_rate"] <= 1.0
            assert 0.0 <= data["expected_type_coverage"] <= 1.0
            assert 0.0 <= data["type_precision"] <= 1.0
            assert 0.0 <= data["exact_type_case_rate"] <= 1.0


def test_v3_gap_audit_is_diagnostic_only() -> None:
    value = audit()
    assert value["positive_case_count"] == 110
    assert sum(value["diagnostic_state_counts"].values()) == 110
    assert value["safety"] == {
        "diagnostic_only": True,
        "writes_runtime_data": False,
        "automatic_promotion_allowed": False,
        "benchmark_labels_feed_runtime": False,
        "tier_a_occurrence_proves_correctness": False,
        "giellalt_candidate_proves_correctness": False,
    }
    assert len(value["records"]) == 110
    assert all(record["automatic_promotion_allowed"] is False for record in value["records"])
    assert all(record["correctness_inference_from_usage_allowed"] is False for record in value["records"])
