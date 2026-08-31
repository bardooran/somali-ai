"""Machine-readable comparison of Somali AI and compiled GiellaLT morphology v1.

This module intentionally does not declare a global winner. Benchmark v1 is
asymmetric: Somali AI development cases are reviewed project cases, while its
holdout cases are frozen and excluded from runtime. The comparison therefore
reports aligned metrics and their differences, plus the fairness limitation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


METRICS = (
    "positive_recognition_rate",
    "holdout_recognition_rate",
    "expected_type_coverage",
    "unknown_safety_rate",
)


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"benchmark JSON must be an object: {path}")
    return value


def compare_payloads(somali_ai_payload: dict, giellalt_payload: dict) -> dict:
    somali = somali_ai_payload.get("runtime_comparable")
    giella = giellalt_payload.get("score")
    if not isinstance(somali, dict):
        raise ValueError("Somali AI payload is missing runtime_comparable metrics")
    if not isinstance(giella, dict):
        raise ValueError("GiellaLT payload is missing score metrics")
    if not giella.get("compiled_fst_evaluated"):
        raise ValueError("GiellaLT comparison requires an actually compiled FST result")

    if somali.get("case_count") != giella.get("case_count"):
        raise ValueError("systems were not evaluated on the same number of benchmark cases")
    if somali.get("unknown_case_count") != giella.get("unknown_case_count"):
        raise ValueError("systems were not evaluated on the same unknown probe count")
    if somali.get("expected_type_count") != giella.get("expected_type_count"):
        raise ValueError("systems were not evaluated against the same expected coarse types")

    metrics: dict[str, dict] = {}
    for metric in METRICS:
        somali_value = float(somali[metric])
        giella_value = float(giella[metric])
        if somali_value > giella_value:
            leader = "somali_ai"
        elif giella_value > somali_value:
            leader = "giellalt"
        else:
            leader = "tie"
        metrics[metric] = {
            "somali_ai": somali_value,
            "giellalt": giella_value,
            "difference_somali_ai_minus_giellalt": somali_value - giella_value,
            "metric_leader": leader,
        }

    return {
        "benchmark_version": "v1",
        "case_count": somali["case_count"],
        "metrics": metrics,
        "counts": {
            "somali_ai": {
                "recognized_positive_case_count": somali["recognized_positive_case_count"],
                "recognized_holdout_case_count": somali["recognized_holdout_case_count"],
                "matched_expected_type_count": somali["matched_expected_type_count"],
                "unknown_accepted_count": somali["unknown_accepted_count"],
            },
            "giellalt": {
                "recognized_positive_case_count": giella["recognized_positive_case_count"],
                "recognized_holdout_case_count": giella["recognized_holdout_case_count"],
                "matched_expected_type_count": giella["matched_expected_type_count"],
                "unknown_accepted_count": giella["unknown_accepted_count"],
            },
        },
        "fairness": {
            "v1_is_asymmetric": True,
            "somali_ai_development_cases_are_reviewed": True,
            "somali_ai_holdouts_are_intentionally_excluded": True,
            "compiled_giellalt_fst_used": True,
            "metric_leaders_are_not_a_global_winner": True,
            "global_winner_declared": False,
            "next_required_step": (
                "freeze and run a source-independent v2 challenge before using "
                "benchmark results for an overall superiority claim"
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--somali-ai", required=True, type=Path)
    parser.add_argument("--giellalt", required=True, type=Path)
    args = parser.parse_args()
    comparison = compare_payloads(_load(args.somali_ai), _load(args.giellalt))
    print(json.dumps(comparison, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
