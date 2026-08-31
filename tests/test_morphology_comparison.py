from src.morphology_benchmark import runtime_comparable_score
from src.morphology_comparison import compare_payloads


def test_somali_ai_runtime_comparable_metrics_share_v1_denominators():
    score = runtime_comparable_score()
    assert score.case_count == 41
    assert score.positive_case_count == 35
    assert score.holdout_case_count == 10
    assert score.expected_type_count == 34
    assert score.unknown_case_count == 6
    assert score.recognized_positive_case_count == 25
    assert score.recognized_holdout_case_count == 0
    assert score.unknown_accepted_count == 0
    assert score.unknown_safety_rate == 1.0


def test_comparison_reports_aligned_metrics_without_global_winner():
    somali = {
        "runtime_comparable": {
            "case_count": 41,
            "recognized_positive_case_count": 25,
            "positive_recognition_rate": 25 / 35,
            "recognized_holdout_case_count": 0,
            "holdout_recognition_rate": 0.0,
            "expected_type_count": 34,
            "matched_expected_type_count": 22,
            "expected_type_coverage": 22 / 34,
            "unknown_case_count": 6,
            "unknown_accepted_count": 0,
            "unknown_safety_rate": 1.0,
        }
    }
    giella = {
        "score": {
            "compiled_fst_evaluated": True,
            "case_count": 41,
            "recognized_positive_case_count": 18,
            "positive_recognition_rate": 18 / 35,
            "recognized_holdout_case_count": 6,
            "holdout_recognition_rate": 0.6,
            "expected_type_count": 34,
            "matched_expected_type_count": 9,
            "expected_type_coverage": 9 / 34,
            "unknown_case_count": 6,
            "unknown_accepted_count": 0,
            "unknown_safety_rate": 1.0,
        }
    }
    result = compare_payloads(somali, giella)
    assert result["metrics"]["positive_recognition_rate"]["metric_leader"] == "somali_ai"
    assert result["metrics"]["holdout_recognition_rate"]["metric_leader"] == "giellalt"
    assert result["metrics"]["unknown_safety_rate"]["metric_leader"] == "tie"
    assert result["fairness"]["global_winner_declared"] is False
    assert result["fairness"]["v1_is_asymmetric"] is True


def test_comparison_rejects_candidate_only_giellalt_payload():
    somali = {
        "runtime_comparable": {
            "case_count": 1,
            "expected_type_count": 1,
            "unknown_case_count": 0,
        }
    }
    giella = {"score": {"compiled_fst_evaluated": False}}
    try:
        compare_payloads(somali, giella)
    except ValueError as error:
        assert "compiled FST" in str(error)
    else:
        raise AssertionError("candidate-only GiellaLT payload must not compare as runtime")
