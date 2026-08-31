"""Score the frozen analyzer-blind morphology challenge v2.

The challenge measures only what its independent source reliably labels:
lexical recognition, coarse noun/verb/adjective/numeral agreement, and explicit
unknown-probe safety. It does not treat recognition as proof of full morphology.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .morphology_candidates import analyze_surface_form

MANIFEST_PATH = Path("data/qa/morphology_challenge_v2.jsonl")
TARGET_TYPES = {"noun", "verb", "adjective", "numeral"}


@dataclass(frozen=True)
class ChallengeV2Score:
    system: str
    benchmark_version: str
    case_count: int
    positive_case_count: int
    recognized_positive_case_count: int
    positive_recognition_rate: float
    expected_type_count: int
    matched_expected_type_count: int
    expected_type_coverage: float
    returned_type_count: int
    unexpected_type_count: int
    type_precision: float
    fully_typed_case_count: int
    fully_typed_case_rate: float
    exact_type_case_count: int
    exact_type_case_rate: float
    unknown_case_count: int
    unknown_rejected_count: int
    unknown_accepted_count: int
    unknown_safety_rate: float
    runtime_winner_declared: bool


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 1.0


def load_cases(path: Path = MANIFEST_PATH) -> tuple[dict, ...]:
    cases: list[dict] = []
    seen_ids: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            case = json.loads(stripped)
            if not isinstance(case, dict):
                raise ValueError("v2 benchmark row must be an object")
            case_id = str(case.get("id", ""))
            split = str(case.get("split", ""))
            expected = case.get("expected_analyses")
            if not case_id or case_id in seen_ids:
                raise ValueError(f"invalid or duplicate v2 id: {case_id!r}")
            if case.get("benchmark_version") != "v2":
                raise ValueError(f"wrong benchmark version for {case_id}")
            if split not in {"challenge", "unknown"}:
                raise ValueError(f"invalid v2 split for {case_id}: {split!r}")
            if not isinstance(expected, list):
                raise ValueError(f"expected_analyses must be a list for {case_id}")
            if bool(case.get("expected_unknown")) != (split == "unknown"):
                raise ValueError(f"expected_unknown disagrees with split for {case_id}")
            if split == "unknown" and expected:
                raise ValueError(f"unknown v2 case has positive analyses: {case_id}")
            seen_ids.add(case_id)
            cases.append(case)
    return tuple(cases)


def expected_types(case: dict) -> set[str]:
    result: set[str] = set()
    for expected in case.get("expected_analyses", ()):
        features = expected.get("features", {})
        if not isinstance(features, dict):
            continue
        pos = str(features.get("part_of_speech", "")).casefold().strip()
        if pos in TARGET_TYPES:
            result.add(pos)
    return result


def score_system(
    *,
    system: str,
    recognized_surfaces: set[str],
    types_by_surface: dict[str, set[str]],
    path: Path = MANIFEST_PATH,
) -> ChallengeV2Score:
    cases = load_cases(path)
    positives = tuple(case for case in cases if case["split"] == "challenge")
    unknowns = tuple(case for case in cases if case["split"] == "unknown")

    recognized = {surface.casefold() for surface in recognized_surfaces}
    normalized_types = {
        surface.casefold(): {value.casefold() for value in values if value.casefold() in TARGET_TYPES}
        for surface, values in types_by_surface.items()
    }

    recognized_positive = 0
    expected_type_count = 0
    matched_type_count = 0
    returned_type_count = 0
    unexpected_type_count = 0
    fully_typed_cases = 0
    exact_type_cases = 0

    for case in positives:
        surface = str(case["surface"]).casefold()
        expected = expected_types(case)
        actual = normalized_types.get(surface, set())
        if surface in recognized:
            recognized_positive += 1
        expected_type_count += len(expected)
        matched = expected & actual
        unexpected = actual - expected
        matched_type_count += len(matched)
        returned_type_count += len(actual)
        unexpected_type_count += len(unexpected)
        if expected <= actual:
            fully_typed_cases += 1
        if expected == actual:
            exact_type_cases += 1

    unknown_accepted = sum(
        str(case["surface"]).casefold() in recognized for case in unknowns
    )

    return ChallengeV2Score(
        system=system,
        benchmark_version="v2",
        case_count=len(cases),
        positive_case_count=len(positives),
        recognized_positive_case_count=recognized_positive,
        positive_recognition_rate=_ratio(recognized_positive, len(positives)),
        expected_type_count=expected_type_count,
        matched_expected_type_count=matched_type_count,
        expected_type_coverage=_ratio(matched_type_count, expected_type_count),
        returned_type_count=returned_type_count,
        unexpected_type_count=unexpected_type_count,
        type_precision=_ratio(matched_type_count, returned_type_count),
        fully_typed_case_count=fully_typed_cases,
        fully_typed_case_rate=_ratio(fully_typed_cases, len(positives)),
        exact_type_case_count=exact_type_cases,
        exact_type_case_rate=_ratio(exact_type_cases, len(positives)),
        unknown_case_count=len(unknowns),
        unknown_rejected_count=len(unknowns) - unknown_accepted,
        unknown_accepted_count=unknown_accepted,
        unknown_safety_rate=_ratio(len(unknowns) - unknown_accepted, len(unknowns)),
        runtime_winner_declared=False,
    )


def somali_ai_observations(path: Path = MANIFEST_PATH) -> tuple[set[str], dict[str, set[str]]]:
    recognized: set[str] = set()
    types: dict[str, set[str]] = {}
    for case in load_cases(path):
        surface = str(case["surface"])
        candidates = analyze_surface_form(surface)
        key = surface.casefold()
        if candidates:
            recognized.add(key)
        coarse: set[str] = set()
        for candidate in candidates:
            pos = str(candidate.features.get("part_of_speech", "")).casefold().strip()
            if pos in TARGET_TYPES:
                coarse.add(pos)
        types[key] = coarse
    return recognized, types


def somali_ai_report(path: Path = MANIFEST_PATH) -> dict:
    cases = load_cases(path)
    recognized, types = somali_ai_observations(path)
    score = score_system(
        system="somali_ai_reviewed_runtime",
        recognized_surfaces=recognized,
        types_by_surface=types,
        path=path,
    )
    misses = []
    type_misses = []
    unknown_hits = []
    for case in cases:
        surface = str(case["surface"])
        key = surface.casefold()
        if case["split"] == "unknown":
            if key in recognized:
                unknown_hits.append(surface)
            continue
        expected = expected_types(case)
        actual = types.get(key, set())
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
        "score": asdict(score),
        "unrecognized_positive_surfaces": misses,
        "type_misses": type_misses,
        "unknown_surfaces_with_analysis": unknown_hits,
        "interpretation": {
            "selection_was_frozen_before_runtime_evaluation": True,
            "coarse_pos_challenge_only": True,
            "recognition_is_not_full_morphological_correctness": True,
            "runtime_winner_declared": False,
        },
    }


def main() -> int:
    print(json.dumps(somali_ai_report(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
