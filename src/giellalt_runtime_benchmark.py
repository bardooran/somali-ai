"""Run the frozen morphology benchmark against a compiled GiellaLT HFST analyzer."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from .morphology_benchmark import BENCHMARK_PATH, load_cases


@dataclass(frozen=True)
class GiellaLTRuntimeScore:
    giellalt_commit: str
    analyzer_path: str
    case_count: int
    positive_case_count: int
    recognized_positive_case_count: int
    positive_recognition_rate: float
    holdout_case_count: int
    recognized_holdout_case_count: int
    holdout_recognition_rate: float
    expected_type_count: int
    matched_expected_type_count: int
    expected_type_coverage: float
    unknown_case_count: int
    unknown_rejected_count: int
    unknown_accepted_count: int
    unknown_safety_rate: float
    compiled_fst_evaluated: bool
    runtime_winner_declared: bool


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 1.0


def coarse_types(analysis: str) -> set[str]:
    tags = {f"+{part}" for part in analysis.split("+")[1:]}
    result: set[str] = set()
    if "+N" in tags:
        result.add("noun")
    if "+V" in tags:
        result.add("verb")
    if "+A" in tags:
        result.add("adjective")
    if "+Num" in tags:
        result.add("numeral")
    return result


def parse_hfst_lookup_output(text: str) -> dict[str, tuple[str, ...]]:
    analyses: dict[str, list[str]] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or "\t" not in line:
            continue
        fields = line.split("\t")
        if len(fields) < 2:
            continue
        surface = fields[0].strip().casefold()
        analysis = fields[1].strip()
        if not surface or not analysis:
            continue
        if analysis.endswith("+?") or analysis == f"{fields[0].strip()}+?":
            analyses.setdefault(surface, [])
            continue
        analyses.setdefault(surface, []).append(analysis)
    return {
        surface: tuple(dict.fromkeys(values))
        for surface, values in analyses.items()
    }


def run_hfst_lookup(analyzer: Path, surfaces: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    completed = subprocess.run(
        ["hfst-lookup", "-q", str(analyzer)],
        input="\n".join(surfaces) + "\n",
        text=True,
        capture_output=True,
        check=True,
    )
    return parse_hfst_lookup_output(completed.stdout)


def _expected_types(case: dict) -> set[str]:
    result: set[str] = set()
    for expected in case.get("expected_analyses", ()):
        features = expected.get("features", {})
        if not isinstance(features, dict):
            continue
        part_of_speech = str(features.get("part_of_speech", "")).casefold().strip()
        if part_of_speech in {"noun", "verb", "adjective", "numeral"}:
            result.add(part_of_speech)
    return result


def score_runtime(
    *,
    analyzer_path: Path,
    giellalt_commit: str,
    analyses_by_surface: dict[str, tuple[str, ...]],
    benchmark_path: Path = BENCHMARK_PATH,
) -> GiellaLTRuntimeScore:
    cases = load_cases(benchmark_path)
    positives = tuple(case for case in cases if case["split"] != "unknown")
    holdouts = tuple(case for case in cases if case["split"] == "holdout")
    unknowns = tuple(case for case in cases if case["split"] == "unknown")

    def returned(case: dict) -> tuple[str, ...]:
        return analyses_by_surface.get(str(case["surface"]).casefold(), ())

    recognized_positive = sum(bool(returned(case)) for case in positives)
    recognized_holdout = sum(bool(returned(case)) for case in holdouts)
    unknown_accepted = sum(bool(returned(case)) for case in unknowns)

    expected_type_count = 0
    matched_type_count = 0
    for case in positives:
        expected_types = _expected_types(case)
        if not expected_types:
            continue
        actual_types: set[str] = set()
        for analysis in returned(case):
            actual_types.update(coarse_types(analysis))
        expected_type_count += len(expected_types)
        matched_type_count += len(expected_types & actual_types)

    return GiellaLTRuntimeScore(
        giellalt_commit=giellalt_commit,
        analyzer_path=str(analyzer_path),
        case_count=len(cases),
        positive_case_count=len(positives),
        recognized_positive_case_count=recognized_positive,
        positive_recognition_rate=_ratio(recognized_positive, len(positives)),
        holdout_case_count=len(holdouts),
        recognized_holdout_case_count=recognized_holdout,
        holdout_recognition_rate=_ratio(recognized_holdout, len(holdouts)),
        expected_type_count=expected_type_count,
        matched_expected_type_count=matched_type_count,
        expected_type_coverage=_ratio(matched_type_count, expected_type_count),
        unknown_case_count=len(unknowns),
        unknown_rejected_count=len(unknowns) - unknown_accepted,
        unknown_accepted_count=unknown_accepted,
        unknown_safety_rate=_ratio(len(unknowns) - unknown_accepted, len(unknowns)),
        compiled_fst_evaluated=True,
        runtime_winner_declared=False,
    )


def report(analyzer: Path, giellalt_commit: str) -> dict:
    cases = load_cases()
    surfaces = tuple(str(case["surface"]) for case in cases)
    analyses = run_hfst_lookup(analyzer, surfaces)
    score = score_runtime(
        analyzer_path=analyzer,
        giellalt_commit=giellalt_commit,
        analyses_by_surface=analyses,
    )
    return {
        "score": asdict(score),
        "unrecognized_positive_surfaces": [
            case["surface"]
            for case in cases
            if case["split"] != "unknown"
            and not analyses.get(str(case["surface"]).casefold(), ())
        ],
        "unknown_surfaces_with_analysis": [
            case["surface"]
            for case in cases
            if case["split"] == "unknown"
            and analyses.get(str(case["surface"]).casefold(), ())
        ],
        "interpretation": {
            "compiled_giellalt_fst_evaluated": True,
            "benchmark_is_small_v1": True,
            "recognition_is_not_automatically_correctness": True,
            "runtime_winner_declared": False,
            "compare_with_somali_ai_metrics": "src.morphology_benchmark",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyzer", required=True, type=Path)
    parser.add_argument("--giellalt-commit", required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            report(args.analyzer, args.giellalt_commit),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
