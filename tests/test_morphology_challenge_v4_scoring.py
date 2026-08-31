from __future__ import annotations

import hashlib
import json
from pathlib import Path

from src.morphology_challenge_v4 import MANIFEST_PATH, MANIFEST_SHA256, load_cases, report

META_PATH = Path("data/qa/morphology_challenge_v4.meta.json")


def test_v4_manifest_identity_is_frozen() -> None:
    assert hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest() == MANIFEST_SHA256
    metadata = json.loads(META_PATH.read_text(encoding="utf-8"))
    assert metadata["manifest_sha256"] == MANIFEST_SHA256
    assert metadata["selection_is_analyzer_blind"] is True
    assert metadata["definitions_copied"] is False
    assert metadata["prior_positive_overlap_count"] == 0
    assert metadata["excluded_benchmarks"] == ["v2", "v3"]


def test_v4_manifest_shape_is_frozen() -> None:
    cases = load_cases()
    positives = [case for case in cases if case["split"] == "challenge"]
    unknowns = [case for case in cases if case["split"] == "unknown"]
    assert len(cases) == 160
    assert len(positives) == 144
    assert len(unknowns) == 16
    assert all(case["benchmark_version"] == "v4" for case in cases)
    counts = {pos: 0 for pos in ("noun", "verb", "numeral")}
    for case in positives:
        for expected in case["expected_analyses"]:
            counts[expected["features"]["part_of_speech"]] += 1
    assert counts == {"noun": 64, "verb": 64, "numeral": 16}


def test_v4_master_runtime_keeps_benchmark_contract() -> None:
    value = report()
    reviewed = value["reviewed"]["score"]
    master = value["master"]["score"]
    assert reviewed["benchmark_version"] == "v4"
    assert master["benchmark_version"] == "v4"
    for key in ("case_count", "positive_case_count", "expected_type_count", "unknown_case_count"):
        assert reviewed[key] == master[key]
    assert value["interpretation"]["benchmark_was_frozen_before_next_breadth_pass"] is True
    assert value["interpretation"]["master_recognition_does_not_authorize_correction"] is True
    assert value["interpretation"]["benchmark_manifest_sha256"] == MANIFEST_SHA256
    assert 0.0 <= master["positive_recognition_rate"] <= 1.0
    assert 0.0 <= master["type_precision"] <= 1.0
    assert 0.0 <= master["unknown_safety_rate"] <= 1.0
