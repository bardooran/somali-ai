from __future__ import annotations

import json
from pathlib import Path

from src.morphology_class_lexicon import reviewed_class_entry
from src.morphology_paradigm_v20 import report

BENCHMARK = Path("data/qa/morphology_paradigm_benchmark_v20.jsonl")
META = Path("data/qa/morphology_paradigm_benchmark_v20.meta.json")


def _rows() -> list[dict]:
    return [json.loads(line) for line in BENCHMARK.read_text(encoding="utf-8").splitlines() if line.strip()]


def _meta() -> dict:
    return json.loads(META.read_text(encoding="utf-8"))


def test_v20_manifest_is_frozen_after_registry_merge() -> None:
    meta = _meta()
    rows = _rows()
    positives = [row for row in rows if row["benchmark_role"] == "positive"]
    unknowns = [row for row in rows if row["benchmark_role"] == "unknown"]

    assert meta["status"] == "historical_baseline_locked"
    assert meta["registry_merge_commit"] == "2130e2bf53d29e5b4b015778009dac44b53639f3"
    assert meta["benchmark_blob_sha"] == "08a3f58a73fdc2bbfb5c9381932fed295403dcf8"
    assert len(positives) == 5
    assert len(unknowns) == 8
    assert {row["id"] for row in positives} == {
        "V20-AADDI-IMP-2SG",
        "V20-AADDI-IMP-2PL",
        "V20-AADDI-INF",
        "V20-BUTAACI-INF",
        "V20-CAAJISI-INF",
    }


def test_v20_only_scores_supported_rows_and_keeps_four_imperatives_unresolved() -> None:
    meta = _meta()
    assert meta["positive_row_count"] == 5
    assert meta["unknown_probe_count"] == 8
    assert meta["unresolved_cells"] == [
        {"lemma": "butaaci", "mood": "imperative", "person": "2sg"},
        {"lemma": "butaaci", "mood": "imperative", "person": "2pl"},
        {"lemma": "caajisi", "mood": "imperative", "person": "2sg"},
        {"lemma": "caajisi", "mood": "imperative", "person": "2pl"},
    ]
    assert meta["isolation"]["unresolved_cells_may_not_be_guessed"] is True
    assert meta["isolation"]["v20_answers_may_not_authorize_runtime_rule"] is True


def test_v20_targets_were_class_known_before_nonfinite_experiment() -> None:
    for lemma in ("aaddi", "butaaci", "caajisi"):
        entry = reviewed_class_entry(lemma)
        assert entry is not None
        assert entry.part_of_speech == "verb"
        assert entry.conjugation_class == "2A"
        assert entry.status == "reviewed_class_only"
        assert entry.correction_allowed is False


def test_v20_freeze_records_pre_activation_state_without_pinning_future_live_runtime() -> None:
    meta = _meta()
    state = meta["pre_freeze_runtime_state"]
    assert state["c2a_present_all_seven_persons"] is True
    assert state["c2a_past_all_seven_persons"] is True
    assert state["generic_c2a_imperative_authorized"] is False
    assert state["generic_c2a_infinitive_authorized"] is False
    assert state["open_class_generation"] is False
    assert state["reverse_suffix_stripping"] is False
    assert state["correction_authority"] is False


def test_v20_scorer_preserves_holdout_boundary() -> None:
    result = report()
    assert result["combined"]["positive_row_count"] == 5
    assert result["combined"]["imperative_row_count"] == 2
    assert result["combined"]["infinitive_row_count"] == 3
    assert result["combined"]["unknown_count"] == 8
    assert result["holdout_integrity"]["benchmark_answers_are_evaluation_only"] is True
    assert result["holdout_integrity"]["runtime_rule_learning_from_v20_allowed"] is False
    assert result["holdout_integrity"]["unresolved_cells_may_not_be_guessed"] is True
