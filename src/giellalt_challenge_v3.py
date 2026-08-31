"""Run frozen morphology challenge v3 against a compiled GiellaLT analyzer."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .giellalt_runtime_benchmark import coarse_types, run_hfst_lookup
from .morphology_challenge_v3 import MANIFEST_PATH, expected_types, load_cases, score_system


def giellalt_report(analyzer: Path, giellalt_commit: str, path: Path = MANIFEST_PATH) -> dict:
    cases = load_cases(path)
    surfaces = tuple(str(case["surface"]) for case in cases)
    analyses = run_hfst_lookup(analyzer, surfaces)

    recognized = {
        surface.casefold()
        for surface in surfaces
        if analyses.get(surface.casefold(), ())
    }
    types_by_surface: dict[str, set[str]] = {}
    for surface in surfaces:
        key = surface.casefold()
        actual: set[str] = set()
        for analysis in analyses.get(key, ()):
            actual.update(coarse_types(analysis))
        types_by_surface[key] = actual

    score = score_system(
        system="giellalt_compiled_hfst",
        recognized_surfaces=recognized,
        types_by_surface=types_by_surface,
        path=path,
    )

    misses: list[str] = []
    type_misses: list[dict] = []
    unknown_hits: list[str] = []
    for case in cases:
        surface = str(case["surface"])
        key = surface.casefold()
        if case["split"] == "unknown":
            if key in recognized:
                unknown_hits.append(surface)
            continue
        expected = expected_types(case)
        actual = types_by_surface.get(key, set())
        if key not in recognized:
            misses.append(surface)
        if not expected <= actual:
            type_misses.append(
                {
                    "surface": surface,
                    "expected_types": sorted(expected),
                    "actual_types": sorted(actual),
                }
            )

    return {
        "score": {
            **asdict(score),
            "giellalt_commit": giellalt_commit,
            "analyzer_path": str(analyzer),
            "compiled_fst_evaluated": True,
        },
        "unrecognized_positive_surfaces": misses,
        "type_misses": type_misses,
        "unknown_surfaces_with_analysis": unknown_hits,
        "interpretation": {
            "selection_was_frozen_before_runtime_evaluation": True,
            "benchmark_manifest_sha256": "7222ef7a4e4f0c9b960b5feece50aaba11737dc7f3265040cfdac6a3e99ffd6c",
            "compiled_giellalt_fst_evaluated": True,
            "coarse_pos_challenge_only": True,
            "recognition_is_not_full_morphological_correctness": True,
            "runtime_winner_declared": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyzer", required=True, type=Path)
    parser.add_argument("--giellalt-commit", required=True)
    parser.add_argument("--benchmark", type=Path, default=MANIFEST_PATH)
    args = parser.parse_args()
    print(
        json.dumps(
            giellalt_report(args.analyzer, args.giellalt_commit, args.benchmark),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
