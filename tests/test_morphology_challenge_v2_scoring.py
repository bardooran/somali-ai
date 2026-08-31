import json
from pathlib import Path

from src.morphology_challenge_v2 import load_cases, score_system


def _write_cases(path: Path) -> None:
    cases = [
        {
            "id": "T-1",
            "benchmark_version": "v2",
            "split": "challenge",
            "surface": "foo",
            "expected_unknown": False,
            "expected_analyses": [
                {"lemma": "foo", "features": {"part_of_speech": "noun"}}
            ],
        },
        {
            "id": "T-2",
            "benchmark_version": "v2",
            "split": "challenge",
            "surface": "bar",
            "expected_unknown": False,
            "expected_analyses": [
                {"lemma": "bar", "features": {"part_of_speech": "verb"}},
                {"lemma": "bar", "features": {"part_of_speech": "adjective"}},
            ],
        },
        {
            "id": "T-U1",
            "benchmark_version": "v2",
            "split": "unknown",
            "surface": "pvzfake",
            "expected_unknown": True,
            "expected_analyses": [],
        },
    ]
    path.write_text(
        "".join(json.dumps(case) + "\n" for case in cases),
        encoding="utf-8",
    )


def test_score_system_uses_same_recognition_and_type_metrics(tmp_path):
    path = tmp_path / "challenge.jsonl"
    _write_cases(path)
    score = score_system(
        system="fake",
        recognized_surfaces={"foo", "bar", "pvzfake"},
        types_by_surface={
            "foo": {"noun", "verb"},
            "bar": {"verb"},
            "pvzfake": set(),
        },
        path=path,
    )

    assert score.case_count == 3
    assert score.positive_case_count == 2
    assert score.recognized_positive_case_count == 2
    assert score.positive_recognition_rate == 1.0
    assert score.expected_type_count == 3
    assert score.matched_expected_type_count == 2
    assert score.expected_type_coverage == 2 / 3
    assert score.returned_type_count == 3
    assert score.unexpected_type_count == 1
    assert score.type_precision == 2 / 3
    assert score.fully_typed_case_count == 1
    assert score.exact_type_case_count == 0
    assert score.unknown_case_count == 1
    assert score.unknown_accepted_count == 1
    assert score.unknown_rejected_count == 0
    assert score.unknown_safety_rate == 0.0
    assert score.runtime_winner_declared is False


def test_frozen_v2_loader_sees_committed_challenge():
    cases = load_cases()
    assert len(cases) == 136
    assert sum(case["split"] == "challenge" for case in cases) == 120
    assert sum(case["split"] == "unknown" for case in cases) == 16
