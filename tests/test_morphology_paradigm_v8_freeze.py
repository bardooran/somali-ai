from __future__ import annotations

import json
from pathlib import Path

BENCHMARK = Path("data/qa/morphology_paradigm_benchmark_v8.jsonl")
METADATA = Path("data/qa/morphology_paradigm_benchmark_v8.meta.json")
V6 = Path("data/qa/morphology_paradigm_benchmark_v6.jsonl")
V7 = Path("data/qa/morphology_paradigm_benchmark_v7.jsonl")
STAGE1C_RULE = Path("rules/morphology/reviewed_class_i_morphophonology.json")


def _rows(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _positive_lemmas(path: Path) -> set[str]:
    return {
        str(row["lemma"])
        for row in _rows(path)
        if row.get("benchmark_role") == "positive" and row.get("lemma")
    }


def test_v8_frozen_shape_and_source() -> None:
    rows = _rows(BENCHMARK)
    positive = [row for row in rows if row["benchmark_role"] == "positive"]
    unknown = [row for row in rows if row["benchmark_role"] == "unknown"]
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))

    assert len(rows) == 15
    assert len(positive) == 7
    assert len({row["surface"] for row in positive}) == 7
    assert len(unknown) == 8
    assert {row["source_family"] for row in positive} == {
        "Warner 1985 Somali Grammar Vol. 1"
    }
    assert {row["source_page"] for row in positive} == {"1.10"}
    assert {row["conjugation"] for row in positive} == {"1"}
    assert {row["part_of_speech"] for row in positive} == {"verb"}
    assert metadata["positive_case_count"] == 7
    assert metadata["positive_unique_surface_count"] == 7
    assert metadata["unknown_case_count"] == 8


def test_v8_positive_lemmas_are_isolated_from_development_and_prior_holdouts() -> None:
    v8_lemmas = _positive_lemmas(BENCHMARK)
    v6_lemmas = _positive_lemmas(V6)
    v7_lemmas = _positive_lemmas(V7)
    stage1c = json.loads(STAGE1C_RULE.read_text(encoding="utf-8"))
    stage1c_lemmas = {str(value) for value in stage1c.get("profiles", {})}

    assert v8_lemmas == {"keen", "raac", "rid", "riix", "sheeg"}
    assert v8_lemmas.isdisjoint(v6_lemmas)
    assert v8_lemmas.isdisjoint(v7_lemmas)
    assert v8_lemmas.isdisjoint(stage1c_lemmas)


def test_v8_unknowns_do_not_overlap_positive_surfaces() -> None:
    rows = _rows(BENCHMARK)
    positive_surfaces = {
        row["surface"] for row in rows if row["benchmark_role"] == "positive"
    }
    unknown_surfaces = {
        row["surface"] for row in rows if row["benchmark_role"] == "unknown"
    }

    assert positive_surfaces.isdisjoint(unknown_surfaces)


def test_v8_answers_and_measured_baseline_are_locked() -> None:
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    policy = metadata["benchmark_policy"]
    measured = metadata["measured_result"]

    assert policy["answers_are_evaluation_only"] is True
    assert policy["runtime_rule_learning_from_v8_allowed"] is False
    assert policy["explicit_source_forms_only"] is True
    assert policy["inferred_unattested_forms_included"] is False
    assert policy["synthetic_unknowns_are_claimed_somali_forms"] is False
    assert metadata["pre_freeze_overlap_status"] == "measured"
    assert metadata["pre_freeze_runtime_commit"] == (
        "a48bb5d6e131b07e192f3effaea0d347d83dd46b"
    )
    assert measured == {
        "full_test_suite": "1033/1033 passed",
        "somali_ai_combined_positive_surface_recognition": "0/7",
        "somali_ai_combined_comparable_feature_rows": "0/7",
        "somali_ai_master_positive_surface_recognition": "0/7",
        "somali_ai_reviewed_exact_positive_surface_recognition": "0/7",
        "somali_ai_reviewed_rule_derived_positive_surface_recognition": "0/7",
        "unknown_safety": "8/8 for combined runtime and master exact",
        "tested_head_commit": "89777000483e6c3e652484ce66501f5d8e706918",
        "workflow_run_id": 33446813886,
    }
    assert metadata["independence"] == {
        "independent_of_qaamuus_v2_v4": True,
        "independent_of_nilsson_v5": True,
        "independent_of_orwin_v6": True,
        "independent_of_zorc_issa_v7": True,
        "independent_of_green_morrison_stage1c": True,
        "independent_of_giellalt_as_runtime_evidence": True,
    }
