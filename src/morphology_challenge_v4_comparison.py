"""Three-way comparison for frozen morphology challenge v4."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .morphology_challenge_v4 import MANIFEST_PATH, TARGET_TYPES

META_PATH = MANIFEST_PATH.with_suffix(".meta.json")
PRIMARY_METRICS = (
    "positive_recognition_rate",
    "expected_type_coverage",
    "type_precision",
    "exact_type_case_rate",
    "unknown_safety_rate",
)
PER_POS_METRICS = (
    "recognition_rate",
    "expected_type_coverage",
    "type_precision",
    "exact_type_case_rate",
)


def _read_somali(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"invalid Somali AI v4 report: {path}")
    for key in ("reviewed", "master"):
        if not isinstance(value.get(key), dict) or not isinstance(value[key].get("score"), dict):
            raise ValueError(f"missing {key} score in {path}")
        if not isinstance(value[key].get("per_pos"), dict):
            raise ValueError(f"missing {key} per-POS diagnostics in {path}")
    return value


def _read_giellalt(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("score"), dict):
        raise ValueError(f"invalid GiellaLT v4 report: {path}")
    if not isinstance(value.get("per_pos"), dict):
        raise ValueError(f"missing GiellaLT v4 per-POS diagnostics in {path}")
    return value


def _leaders(values: dict[str, float]) -> list[str]:
    best = max(values.values())
    return sorted(name for name, value in values.items() if value == best)


def compare(somali_ai_path: Path, giellalt_path: Path) -> dict:
    somali = _read_somali(somali_ai_path)
    giella = _read_giellalt(giellalt_path)
    scores = {
        "somali_ai_reviewed": somali["reviewed"]["score"],
        "somali_ai_master": somali["master"]["score"],
        "giellalt": giella["score"],
    }
    per_pos = {
        "somali_ai_reviewed": somali["reviewed"]["per_pos"],
        "somali_ai_master": somali["master"]["per_pos"],
        "giellalt": giella["per_pos"],
    }
    for name, score in scores.items():
        if score.get("benchmark_version") != "v4":
            raise ValueError(f"{name} report is not challenge v4")
    baseline = scores["somali_ai_reviewed"]
    for name, score in scores.items():
        for key in ("case_count", "positive_case_count", "expected_type_count", "unknown_case_count"):
            if score.get(key) != baseline.get(key):
                raise ValueError(f"{name} does not describe the same benchmark: {key}")

    metadata = json.loads(META_PATH.read_text(encoding="utf-8"))
    metrics: dict[str, dict] = {}
    for metric in PRIMARY_METRICS:
        values = {name: float(score[metric]) for name, score in scores.items()}
        metrics[metric] = {**values, "leaders": _leaders(values)}

    category_metrics: dict[str, dict] = {}
    for pos in sorted(TARGET_TYPES):
        counts = {
            name: int(system_breakdown[pos]["positive_case_count"])
            for name, system_breakdown in per_pos.items()
        }
        if len(set(counts.values())) != 1:
            raise ValueError(f"per-POS case counts disagree for {pos}")
        values_by_metric: dict[str, dict] = {}
        for metric in PER_POS_METRICS:
            values = {
                name: float(system_breakdown[pos][metric])
                for name, system_breakdown in per_pos.items()
            }
            values_by_metric[metric] = {**values, "leaders": _leaders(values)}
        category_metrics[pos] = {
            "positive_case_count": next(iter(counts.values())),
            "metrics": values_by_metric,
            "systems": {name: breakdown[pos] for name, breakdown in per_pos.items()},
        }

    return {
        "benchmark": {
            "version": "v4",
            "manifest_sha256": metadata["manifest_sha256"],
            "case_count": metadata["case_count"],
            "positive_case_count": metadata["positive_case_count"],
            "unknown_probe_count": metadata["unknown_probe_count"],
            "selection_is_analyzer_blind": metadata["selection_is_analyzer_blind"],
            "source_commit": metadata["source_commit"],
            "prior_positive_overlap_count": metadata["prior_positive_overlap_count"],
        },
        "systems": scores,
        "primary_metrics": metrics,
        "per_pos": category_metrics,
        "master_runtime_note": {
            "recognition_only": True,
            "provisional_records_do_not_gain_correction_authority": True,
        },
        "interpretation": {
            "same_frozen_manifest": True,
            "metric_leaders_are_descriptive": True,
            "per_pos_labels_are_evaluation_only": True,
            "overall_winner_declared": False,
            "reason_no_single_winner": "v4 has no arbitrary weighted composite score",
            "scope": "fresh lexical recognition, coarse POS agreement, and unknown safety",
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
