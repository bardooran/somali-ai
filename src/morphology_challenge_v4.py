"""Score frozen analyzer-blind morphology challenge v4.

v4 was frozen before the next morphology breadth pass. It measures fresh noun,
verb, and numeral lexical recognition plus deterministic unknown safety. The
frozen labels are evaluation-only and must never be promoted into runtime data.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .master_recognition import recognize_form
from .morphology_candidates import analyze_surface_form

MANIFEST_PATH = Path("data/qa/morphology_challenge_v4.jsonl")
MANIFEST_SHA256 = "6a61900ea57a2c0f77121eb133195c4cae1246a518624b361d37d924e33cb3ce"
TARGET_TYPES = {"noun", "verb", "numeral"}


@dataclass(frozen=True)
class ChallengeV4Score:
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


def _precision(matched: int, returned: int) -> float:
    return matched / returned if returned else 0.0


def load_cases(path: Path = MANIFEST_PATH) -> tuple[dict, ...]:
    cases: list[dict] = []
    seen: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            case = json.loads(text)
            if not isinstance(case, dict):
                raise ValueError("v4 benchmark row must be an object")
            case_id = str(case.get("id", ""))
            split = str(case.get("split", ""))
            expected = case.get("expected_analyses")
            if not case_id or case_id in seen:
                raise ValueError(f"invalid or duplicate v4 id: {case_id!r}")
            if case.get("benchmark_version") != "v4":
                raise ValueError(f"wrong benchmark version for {case_id}")
            if split not in {"challenge", "unknown"}:
                raise ValueError(f"invalid v4 split for {case_id}: {split!r}")
            if not isinstance(expected, list):
                raise ValueError(f"expected_analyses must be a list for {case_id}")
            if bool(case.get("expected_unknown")) != (split == "unknown"):
                raise ValueError(f"expected_unknown disagrees with split for {case_id}")
            if split == "unknown" and expected:
                raise ValueError(f"unknown v4 case has positive analyses: {case_id}")
            seen.add(case_id)
            cases.append(case)
    return tuple(cases)


def expected_types(case: dict) -> set[str]:
    result: set[str] = set()
    for expected in case.get("expected_analyses", ()):
        features = expected.get("features", {})
        if not isinstance(features, dict):
            continue
        value = str(features.get("part_of_speech", "")).casefold().strip()
        if value in TARGET_TYPES:
            result.add(value)
    return result


def _normalize(
    recognized_surfaces: set[str],
    types_by_surface: dict[str, set[str]],
) -> tuple[set[str], dict[str, set[str]]]:
    recognized = {value.casefold() for value in recognized_surfaces}
    types = {
        surface.casefold(): {
            value.casefold() for value in values if value.casefold() in TARGET_TYPES
        }
        for surface, values in types_by_surface.items()
    }
    return recognized, types


def score_system(
    *,
    system: str,
    recognized_surfaces: set[str],
    types_by_surface: dict[str, set[str]],
    path: Path = MANIFEST_PATH,
) -> ChallengeV4Score:
    cases = load_cases(path)
    positives = tuple(case for case in cases if case["split"] == "challenge")
    unknowns = tuple(case for case in cases if case["split"] == "unknown")
    recognized, types = _normalize(recognized_surfaces, types_by_surface)

    recognized_positive = expected_count = matched_count = returned_count = 0
    unexpected_count = fully_typed = exact_typed = 0
    for case in positives:
        surface = str(case["surface"]).casefold()
        expected = expected_types(case)
        actual = types.get(surface, set())
        if surface in recognized:
            recognized_positive += 1
        matched = expected & actual
        expected_count += len(expected)
        matched_count += len(matched)
        returned_count += len(actual)
        unexpected_count += len(actual - expected)
        if expected <= actual:
            fully_typed += 1
        if expected == actual:
            exact_typed += 1

    unknown_accepted = sum(str(case["surface"]).casefold() in recognized for case in unknowns)
    return ChallengeV4Score(
        system=system,
        benchmark_version="v4",
        case_count=len(cases),
        positive_case_count=len(positives),
        recognized_positive_case_count=recognized_positive,
        positive_recognition_rate=_ratio(recognized_positive, len(positives)),
        expected_type_count=expected_count,
        matched_expected_type_count=matched_count,
        expected_type_coverage=_ratio(matched_count, expected_count),
        returned_type_count=returned_count,
        unexpected_type_count=unexpected_count,
        type_precision=_precision(matched_count, returned_count),
        fully_typed_case_count=fully_typed,
        fully_typed_case_rate=_ratio(fully_typed, len(positives)),
        exact_type_case_count=exact_typed,
        exact_type_case_rate=_ratio(exact_typed, len(positives)),
        unknown_case_count=len(unknowns),
        unknown_rejected_count=len(unknowns) - unknown_accepted,
        unknown_accepted_count=unknown_accepted,
        unknown_safety_rate=_ratio(len(unknowns) - unknown_accepted, len(unknowns)),
        runtime_winner_declared=False,
    )


def per_pos_breakdown(
    *,
    recognized_surfaces: set[str],
    types_by_surface: dict[str, set[str]],
    path: Path = MANIFEST_PATH,
) -> dict[str, dict]:
    recognized, types = _normalize(recognized_surfaces, types_by_surface)
    positives = tuple(case for case in load_cases(path) if case["split"] == "challenge")
    result: dict[str, dict] = {}
    for pos in sorted(TARGET_TYPES):
        subset = tuple(case for case in positives if pos in expected_types(case))
        recognized_count = expected_count = matched_count = returned_count = 0
        unexpected_count = fully_typed = exact_typed = 0
        for case in subset:
            surface = str(case["surface"]).casefold()
            expected = expected_types(case)
            actual = types.get(surface, set())
            if surface in recognized:
                recognized_count += 1
            matched = expected & actual
            expected_count += len(expected)
            matched_count += len(matched)
            returned_count += len(actual)
            unexpected_count += len(actual - expected)
            if expected <= actual:
                fully_typed += 1
            if expected == actual:
                exact_typed += 1
        result[pos] = {
            "positive_case_count": len(subset),
            "recognized_case_count": recognized_count,
            "recognition_rate": _ratio(recognized_count, len(subset)),
            "expected_type_count": expected_count,
            "matched_expected_type_count": matched_count,
            "expected_type_coverage": _ratio(matched_count, expected_count),
            "returned_type_count": returned_count,
            "unexpected_type_count": unexpected_count,
            "type_precision": _precision(matched_count, returned_count),
            "fully_typed_case_count": fully_typed,
            "fully_typed_case_rate": _ratio(fully_typed, len(subset)),
            "exact_type_case_count": exact_typed,
            "exact_type_case_rate": _ratio(exact_typed, len(subset)),
        }
    return result


def _details(cases: tuple[dict, ...], recognized: set[str], types: dict[str, set[str]]) -> dict:
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
        actual = types.get(key, set())
        if key not in recognized:
            misses.append(surface)
        if not expected <= actual:
            type_misses.append({
                "surface": surface,
                "expected_types": sorted(expected),
                "actual_types": sorted(actual),
            })
    return {
        "unrecognized_positive_surfaces": misses,
        "type_misses": type_misses,
        "unknown_surfaces_with_analysis": unknown_hits,
    }


def reviewed_observations(path: Path = MANIFEST_PATH) -> tuple[set[str], dict[str, set[str]]]:
    recognized: set[str] = set()
    types: dict[str, set[str]] = {}
    for case in load_cases(path):
        surface = str(case["surface"])
        key = surface.casefold()
        analyses = analyze_surface_form(surface)
        if analyses:
            recognized.add(key)
        types[key] = {
            str(item.features.get("part_of_speech", "")).casefold().strip()
            for item in analyses
        } & TARGET_TYPES
    return recognized, types


def master_observations(path: Path = MANIFEST_PATH) -> tuple[set[str], dict[str, set[str]], dict[str, set[str]]]:
    recognized: set[str] = set()
    types: dict[str, set[str]] = {}
    confidence: dict[str, set[str]] = {}
    for case in load_cases(path):
        surface = str(case["surface"])
        key = surface.casefold()
        analyses = recognize_form(surface)
        if analyses:
            recognized.add(key)
        types[key] = {
            str(item.part_of_speech).casefold().strip()
            for item in analyses
            if item.part_of_speech and str(item.part_of_speech).casefold().strip() in TARGET_TYPES
        }
        confidence[key] = {item.confidence_tier for item in analyses}
    return recognized, types, confidence


def report(path: Path = MANIFEST_PATH) -> dict:
    cases = load_cases(path)
    reviewed_recognized, reviewed_types = reviewed_observations(path)
    master_recognized, master_types, confidence = master_observations(path)
    reviewed_score = score_system(
        system="somali_ai_reviewed_runtime",
        recognized_surfaces=reviewed_recognized,
        types_by_surface=reviewed_types,
        path=path,
    )
    master_score = score_system(
        system="somali_ai_master_exact_recognition",
        recognized_surfaces=master_recognized,
        types_by_surface=master_types,
        path=path,
    )
    confidence_counts = {tier: 0 for tier in ("trusted", "supported", "provisional")}
    for case in cases:
        if case["split"] != "challenge":
            continue
        tiers = confidence.get(str(case["surface"]).casefold(), set())
        for tier in confidence_counts:
            if tier in tiers:
                confidence_counts[tier] += 1
    return {
        "reviewed": {
            "score": asdict(reviewed_score),
            "per_pos": per_pos_breakdown(
                recognized_surfaces=reviewed_recognized,
                types_by_surface=reviewed_types,
                path=path,
            ),
            **_details(cases, reviewed_recognized, reviewed_types),
        },
        "master": {
            "score": asdict(master_score),
            "per_pos": per_pos_breakdown(
                recognized_surfaces=master_recognized,
                types_by_surface=master_types,
                path=path,
            ),
            "recognized_positive_confidence_presence": confidence_counts,
            **_details(cases, master_recognized, master_types),
        },
        "interpretation": {
            "benchmark_was_frozen_before_next_breadth_pass": True,
            "benchmark_manifest_sha256": MANIFEST_SHA256,
            "coarse_pos_challenge_only": True,
            "per_pos_labels_are_evaluation_only": True,
            "master_recognition_does_not_authorize_correction": True,
            "recognition_is_not_full_morphological_correctness": True,
            "runtime_winner_declared": False,
        },
    }


def main() -> int:
    print(json.dumps(report(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
