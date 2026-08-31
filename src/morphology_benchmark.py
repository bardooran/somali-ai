"""Held-out morphology benchmark for Somali AI.

Benchmark v1 deliberately separates:
- development cases already represented in reviewed project morphology,
- frozen Qaamuus holdouts that must not be directly promoted just to raise the score,
- synthetic unknown probes that should remain unjudged.

GiellaLT numbers in this module measure the imported lexical candidate inventory only.
They are not results from the compiled GiellaLT FST and must not be presented as
a runtime model-vs-model win.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator

from .morphology_candidates import MorphologyCandidate, analyze_surface_form
from .morphology_competition import GIELLALT_CANDIDATES_PATH, giellalt_candidate_records

BENCHMARK_PATH = Path("data/qa/morphology_benchmark_v1.jsonl")
VALID_SPLITS = {"development", "holdout", "unknown"}
COARSE_PARTS_OF_SPEECH = {"noun", "verb", "adjective", "numeral"}


@dataclass(frozen=True)
class SplitScore:
    case_count: int
    positive_case_count: int
    covered_case_count: int
    exact_case_count: int
    expected_analysis_count: int
    matched_expected_analysis_count: int
    returned_analysis_count: int
    false_analysis_count: int
    case_coverage: float
    analysis_recall: float
    analysis_precision: float


@dataclass(frozen=True)
class MorphologyBenchmarkScore:
    benchmark_version: str
    case_count: int
    development: SplitScore
    holdout: SplitScore
    unknown_case_count: int
    unknown_safe_count: int
    unknown_unsafe_count: int
    unknown_safety_rate: float
    ambiguous_case_count: int
    ambiguity_preserved_count: int
    ambiguity_preservation_rate: float
    giellalt_candidate_expected_type_count: int
    giellalt_candidate_matched_type_count: int
    giellalt_candidate_type_coverage: float
    giellalt_compiled_fst_evaluated: bool
    runtime_winner_declared: bool


@dataclass(frozen=True)
class RuntimeComparableScore:
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


def _read_jsonl(path: Path) -> Iterator[dict]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                value = json.loads(stripped)
                if isinstance(value, dict):
                    yield value


def load_cases(path: Path = BENCHMARK_PATH) -> tuple[dict, ...]:
    cases = tuple(_read_jsonl(path))
    seen_ids: set[str] = set()
    for case in cases:
        case_id = str(case.get("id", ""))
        split = str(case.get("split", ""))
        surface = str(case.get("surface", ""))
        expected = case.get("expected_analyses")
        if not case_id or case_id in seen_ids:
            raise ValueError(f"invalid or duplicate benchmark id: {case_id!r}")
        if split not in VALID_SPLITS:
            raise ValueError(f"invalid benchmark split for {case_id}: {split!r}")
        if not surface:
            raise ValueError(f"missing benchmark surface for {case_id}")
        if not isinstance(expected, list):
            raise ValueError(f"expected_analyses must be a list for {case_id}")
        if split == "unknown" and expected:
            raise ValueError(f"unknown benchmark case has positive analyses: {case_id}")
        if bool(case.get("expected_unknown")) != (split == "unknown"):
            raise ValueError(f"expected_unknown disagrees with split for {case_id}")
        seen_ids.add(case_id)
    return cases


def _same_value(actual: object, expected: object) -> bool:
    if isinstance(expected, list):
        if not isinstance(actual, (list, tuple, set)):
            return False
        return {str(value) for value in actual} == {str(value) for value in expected}
    if isinstance(expected, str) and isinstance(actual, str):
        return actual.casefold() == expected.casefold()
    return actual == expected


def _candidate_matches(candidate: MorphologyCandidate, expected: dict) -> bool:
    expected_lemma = expected.get("lemma")
    if isinstance(expected_lemma, str) and candidate.lemma.casefold() != expected_lemma.casefold():
        return False

    expected_type = expected.get("analysis_type")
    if isinstance(expected_type, str) and candidate.analysis_type != expected_type:
        return False

    expected_features = expected.get("features", {})
    if not isinstance(expected_features, dict):
        return False
    for key, value in expected_features.items():
        if not _same_value(candidate.features.get(key), value):
            return False

    expected_homograph = expected.get("homograph_index")
    if expected_homograph is not None and candidate.raw.get("homograph_index") != expected_homograph:
        return False
    return True


def evaluate_case(case: dict) -> dict:
    analyses = analyze_surface_form(str(case["surface"]))
    expected = tuple(case.get("expected_analyses", ()))

    matched_expected = sum(
        any(_candidate_matches(candidate, signature) for candidate in analyses)
        for signature in expected
    )
    false_analyses = sum(
        not any(_candidate_matches(candidate, signature) for signature in expected)
        for candidate in analyses
    )
    positive = bool(expected)
    covered = positive and matched_expected == len(expected)
    exact = covered and false_analyses == 0

    return {
        "id": case["id"],
        "split": case["split"],
        "surface": case["surface"],
        "positive": positive,
        "expected_analysis_count": len(expected),
        "matched_expected_analysis_count": matched_expected,
        "returned_analysis_count": len(analyses),
        "false_analysis_count": false_analyses,
        "covered": covered,
        "exact": exact,
        "ambiguity_required": bool(case.get("ambiguity_required")),
        "ambiguity_preserved": (
            bool(case.get("ambiguity_required")) and matched_expected == len(expected)
        ),
    }


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 1.0


def _score_split(results: tuple[dict, ...]) -> SplitScore:
    positives = tuple(result for result in results if result["positive"])
    expected_count = sum(result["expected_analysis_count"] for result in positives)
    matched_count = sum(result["matched_expected_analysis_count"] for result in positives)
    returned_count = sum(result["returned_analysis_count"] for result in positives)
    false_count = sum(result["false_analysis_count"] for result in positives)
    true_returned = max(returned_count - false_count, 0)
    return SplitScore(
        case_count=len(results),
        positive_case_count=len(positives),
        covered_case_count=sum(result["covered"] for result in positives),
        exact_case_count=sum(result["exact"] for result in positives),
        expected_analysis_count=expected_count,
        matched_expected_analysis_count=matched_count,
        returned_analysis_count=returned_count,
        false_analysis_count=false_count,
        case_coverage=_ratio(sum(result["covered"] for result in positives), len(positives)),
        analysis_recall=_ratio(matched_count, expected_count),
        analysis_precision=_ratio(true_returned, returned_count),
    )


def _expected_types(case: dict) -> set[str]:
    result: set[str] = set()
    for expected in case.get("expected_analyses", ()):
        features = expected.get("features", {})
        if not isinstance(features, dict):
            continue
        part_of_speech = str(features.get("part_of_speech", "")).casefold().strip()
        if part_of_speech in COARSE_PARTS_OF_SPEECH:
            result.add(part_of_speech)
    return result


def runtime_comparable_score(path: Path = BENCHMARK_PATH) -> RuntimeComparableScore:
    """Return metrics aligned with the compiled-GiellaLT runtime comparator.

    This intentionally measures recognition and coarse POS coverage, not the richer
    exact project analyses used by ``build_score``. That makes the quantities
    comparable while retaining the richer project-native benchmark separately.
    """
    cases = load_cases(path)
    positives = tuple(case for case in cases if case["split"] != "unknown")
    holdouts = tuple(case for case in cases if case["split"] == "holdout")
    unknowns = tuple(case for case in cases if case["split"] == "unknown")

    analyses_by_id = {
        str(case["id"]): analyze_surface_form(str(case["surface"])) for case in cases
    }

    recognized_positive = sum(bool(analyses_by_id[str(case["id"])]) for case in positives)
    recognized_holdout = sum(bool(analyses_by_id[str(case["id"])]) for case in holdouts)
    unknown_accepted = sum(bool(analyses_by_id[str(case["id"])]) for case in unknowns)

    expected_type_count = 0
    matched_type_count = 0
    for case in positives:
        expected_types = _expected_types(case)
        if not expected_types:
            continue
        actual_types = {
            str(candidate.features.get("part_of_speech", "")).casefold().strip()
            for candidate in analyses_by_id[str(case["id"])]
            if str(candidate.features.get("part_of_speech", "")).casefold().strip()
            in COARSE_PARTS_OF_SPEECH
        }
        expected_type_count += len(expected_types)
        matched_type_count += len(expected_types & actual_types)

    return RuntimeComparableScore(
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
    )


def _giellalt_types_by_lemma(path: Path = GIELLALT_CANDIDATES_PATH) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for record in giellalt_candidate_records(path):
        lemma = str(record.get("lemma", "")).casefold().strip()
        record_type = str(record.get("record_type", "")).casefold().strip()
        if lemma and record_type:
            result.setdefault(lemma, set()).add(record_type)
    return result


def _expected_coarse_pairs(cases: tuple[dict, ...]) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for case in cases:
        if case["split"] == "unknown":
            continue
        for expected in case.get("expected_analyses", ()):
            lemma = str(expected.get("lemma", "")).casefold().strip()
            features = expected.get("features", {})
            if not isinstance(features, dict):
                continue
            part_of_speech = str(features.get("part_of_speech", "")).casefold().strip()
            if lemma and part_of_speech in COARSE_PARTS_OF_SPEECH:
                pairs.add((lemma, part_of_speech))
    return pairs


def build_score(path: Path = BENCHMARK_PATH) -> MorphologyBenchmarkScore:
    cases = load_cases(path)
    results = tuple(evaluate_case(case) for case in cases)

    development_results = tuple(
        result for result in results if result["split"] == "development"
    )
    holdout_results = tuple(result for result in results if result["split"] == "holdout")
    unknown_results = tuple(result for result in results if result["split"] == "unknown")

    unknown_unsafe = sum(result["returned_analysis_count"] > 0 for result in unknown_results)
    ambiguous = tuple(result for result in results if result["ambiguity_required"])

    expected_pairs = _expected_coarse_pairs(cases)
    giellalt_types = _giellalt_types_by_lemma()
    matched_pairs = {
        pair for pair in expected_pairs if pair[1] in giellalt_types.get(pair[0], set())
    }

    return MorphologyBenchmarkScore(
        benchmark_version="v1",
        case_count=len(cases),
        development=_score_split(development_results),
        holdout=_score_split(holdout_results),
        unknown_case_count=len(unknown_results),
        unknown_safe_count=len(unknown_results) - unknown_unsafe,
        unknown_unsafe_count=unknown_unsafe,
        unknown_safety_rate=_ratio(len(unknown_results) - unknown_unsafe, len(unknown_results)),
        ambiguous_case_count=len(ambiguous),
        ambiguity_preserved_count=sum(result["ambiguity_preserved"] for result in ambiguous),
        ambiguity_preservation_rate=_ratio(
            sum(result["ambiguity_preserved"] for result in ambiguous), len(ambiguous)
        ),
        giellalt_candidate_expected_type_count=len(expected_pairs),
        giellalt_candidate_matched_type_count=len(matched_pairs),
        giellalt_candidate_type_coverage=_ratio(len(matched_pairs), len(expected_pairs)),
        giellalt_compiled_fst_evaluated=False,
        runtime_winner_declared=False,
    )


def report(path: Path = BENCHMARK_PATH) -> dict:
    cases = load_cases(path)
    results = tuple(evaluate_case(case) for case in cases)
    score = build_score(path)
    return {
        "score": asdict(score),
        "runtime_comparable": asdict(runtime_comparable_score(path)),
        "misses": [
            result
            for result in results
            if result["positive"] and not result["covered"]
        ],
        "false_analysis_cases": [
            result for result in results if result["false_analysis_count"]
        ],
        "interpretation": {
            "holdout_is_frozen": True,
            "unknown_means_unjudged_not_ungrammatical": True,
            "giellalt_candidate_inventory_is_not_compiled_fst": True,
            "runtime_model_vs_model_claim_allowed": False,
            "v1_is_asymmetric": True,
            "reason_v1_is_asymmetric": (
                "development cases were already reviewed by Somali AI, while holdouts are "
                "explicitly excluded from Somali AI runtime"
            ),
            "next_comparison": "freeze a source-independent v2 challenge before further promotion",
        },
    }


def main() -> int:
    print(json.dumps(report(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
