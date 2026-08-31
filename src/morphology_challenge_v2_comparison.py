"""Build a side-by-side report for the frozen morphology challenge v2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .morphology_challenge_v2 import MANIFEST_PATH

META_PATH = MANIFEST_PATH.with_suffix(".meta.json")
PRIMARY_METRICS = (
    "positive_recognition_rate",
    "expected_type_coverage",
    "type_precision",
    "exact_type_case_rate",
    "unknown_safety_rate",
)


def _read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("score"), dict):
        raise ValueError(f"invalid challenge report: {path}")
    return value


def _leader(left: float, right: float) -> str:
    if left > right:
        return "somali_ai"
    if right > left:
        return "giellalt"
    return "tie"


def compare(somali_ai_path: Path, giellalt_path: Path) -> dict:
    somali = _read(somali_ai_path)
    giella = _read(giellalt_path)
    somali_score = somali["score"]
    giella_score = giella["score"]

    if somali_score.get("benchmark_version") != "v2":
        raise ValueError("Somali AI report is not challenge v2")
    if giella_score.get("benchmark_version") != "v2":
        raise ValueError("GiellaLT report is not challenge v2")
    for key in ("case_count", "positive_case_count", "expected_type_count", "unknown_case_count"):
        if somali_score.get(key) != giella_score.get(key):
            raise ValueError(f"reports do not describe the same benchmark: {key}")

    metadata = json.loads(META_PATH.read_text(encoding="utf-8"))
    metrics = {}
    for metric in PRIMARY_METRICS:
        left = float(somali_score[metric])
        right = float(giella_score[metric])
        metrics[metric] = {
            "somali_ai": left,
            "giellalt": right,
            "leader": _leader(left, right),
        }

    return {
        "benchmark": {
            "version": "v2",
            "manifest_sha256": metadata["manifest_sha256"],
            "case_count": metadata["case_count"],
            "positive_case_count": metadata["positive_case_count"],
            "unknown_probe_count": metadata["unknown_probe_count"],
            "selection_is_analyzer_blind": metadata["selection_is_analyzer_blind"],
            "source_commit": metadata["source_commit"],
        },
        "systems": {
            "somali_ai": somali_score,
            "giellalt": giella_score,
        },
        "primary_metrics": metrics,
        "interpretation": {
            "same_frozen_manifest": True,
            "metric_leaders_are_descriptive": True,
            "overall_winner_declared": False,
            "reason_no_single_winner": "v2 has no arbitrary weighted composite score",
            "scope": "lexical recognition, coarse POS agreement, and unknown safety",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--somali-ai", required=True, type=Path)
    parser.add_argument("--giellalt", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(args.somali_ai, args.giellalt), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
