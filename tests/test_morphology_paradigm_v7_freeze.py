from __future__ import annotations

import json
from pathlib import Path

BENCHMARK = Path("data/qa/morphology_paradigm_benchmark_v7.jsonl")
METADATA = Path("data/qa/morphology_paradigm_benchmark_v7.meta.json")


def _rows() -> list[dict]:
    return [
        json.loads(line)
        for line in BENCHMARK.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_v7_frozen_shape_and_source_independence() -> None:
    rows = _rows()
    positive = [row for row in rows if row["benchmark_role"] == "positive"]
    unknown = [row for row in rows if row["benchmark_role"] == "unknown"]
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))

    assert len(rows) == 16
    assert len(positive) == 8
    assert len({row["surface"] for row in positive}) == 6
    assert len(unknown) == 8
    assert {row["source_family"] for row in positive} == {
        "Zorc & Issa 1990 Somali Textbook"
    }
    assert {row["source_page"] for row in positive} == {113}
    assert metadata["positive_case_count"] == 8
    assert metadata["positive_unique_surface_count"] == 6
    assert metadata["unknown_case_count"] == 8
    assert metadata["independence"] == {
        "independent_of_qaamuus_v2_v4": True,
        "independent_of_nilsson_v5": True,
        "independent_of_orwin_v6": True,
    }


def test_v7_unknowns_do_not_overlap_positive_surfaces() -> None:
    rows = _rows()
    positive_surfaces = {
        row["surface"] for row in rows if row["benchmark_role"] == "positive"
    }
    unknown_surfaces = {
        row["surface"] for row in rows if row["benchmark_role"] == "unknown"
    }

    assert positive_surfaces.isdisjoint(unknown_surfaces)


def test_v7_answers_are_locked_evaluation_only() -> None:
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    policy = metadata["benchmark_policy"]
    measured = metadata["measured_result"]

    assert policy["answers_are_evaluation_only"] is True
    assert policy["runtime_rule_learning_from_v7_allowed"] is False
    assert policy["explicit_source_forms_only"] is True
    assert policy["inferred_unattested_forms_included"] is False
    assert metadata["pre_freeze_overlap_status"] == "measured"
    assert measured["somali_ai_combined_positive_surface_recognition"] == "0/6"
    assert measured["somali_ai_combined_comparable_feature_rows"] == "0/8"
    assert measured["unknown_safety"] == "8/8 for combined runtime and master exact"
