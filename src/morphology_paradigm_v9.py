"""Score the frozen independent Conjugation-2 infinitive benchmark v9.

Fayruus v9 answers are evaluation-only. This module measures the existing
runtime against the already-frozen holdout and never creates or modifies
morphology rules, lexica, or generation profiles.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from .master_recognition import recognize_form
from .morphology_analysis import MorphologyAnalysis, analyze_morphology

BENCHMARK_PATH = Path("data/qa/morphology_paradigm_benchmark_v9.jsonl")
METADATA_PATH = Path("data/qa/morphology_paradigm_benchmark_v9.meta.json")


def _rows() -> tuple[dict, ...]:
    return tuple(
        json.loads(line)
        for line in BENCHMARK_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def _normalize(value: object) -> str:
    return str(value).casefold().replace("-", "_").replace(" ", "_").strip()


def _conjugation_matches(expected: str, candidate: MorphologyAnalysis) -> bool:
    actual = candidate.features.get("conjugation_class")
    if actual is None:
        actual = candidate.features.get("verb_class")
    return actual is not None and _normalize(actual) == _normalize(expected)


def _form_matches(expected: str, candidate: MorphologyAnalysis) -> bool:
    actual = candidate.features.get("form")
    if actual is not None and _normalize(actual) == _normalize(expected):
        return True
    # Some exact-reviewed records encode non-finite type separately.
    non_finite = candidate.features.get("non_finite")
    return non_finite is not None and _normalize(non_finite) == _normalize(expected)


def _candidate_matches_row(candidate: MorphologyAnalysis, row: dict) -> bool:
    if candidate.lemma.casefold() != str(row["lemma"]).casefold():
        return False
    if candidate.part_of_speech.casefold() != str(row["part_of_speech"]).casefold():
        return False
    if not _conjugation_matches(str(row["conjugation"]), candidate):
        return False
    if not _form_matches(str(row["form"]), candidate):
        return False
    return True


def report() -> dict:
    rows = _rows()
    positives = tuple(row for row in rows if row["benchmark_role"] == "positive")
    unknowns = tuple(row for row in rows if row["benchmark_role"] == "unknown")
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in positives:
        grouped[str(row["surface"]).casefold()].append(row)

    combined_recognized: set[str] = set()
    combined_lemma: set[str] = set()
    combined_pos: set[str] = set()
    combined_conjugation: set[str] = set()
    combined_form: set[str] = set()
    comparable_feature_rows: list[str] = []
    exact_surfaces: set[str] = set()
    generated_surfaces: set[str] = set()

    for surface, expected_rows in grouped.items():
        candidates = analyze_morphology(surface)
        if candidates:
            combined_recognized.add(surface)
        if any(candidate.authority == "reviewed_exact" for candidate in candidates):
            exact_surfaces.add(surface)
        if any(candidate.authority == "reviewed_rule_derived" for candidate in candidates):
            generated_surfaces.add(surface)

        expected_lemmas = {str(row["lemma"]).casefold() for row in expected_rows}
        if any(candidate.lemma.casefold() in expected_lemmas for candidate in candidates):
            combined_lemma.add(surface)
        expected_pos = {str(row["part_of_speech"]).casefold() for row in expected_rows}
        if any(candidate.part_of_speech.casefold() in expected_pos for candidate in candidates):
            combined_pos.add(surface)
        if any(
            any(_conjugation_matches(str(row["conjugation"]), candidate) for row in expected_rows)
            for candidate in candidates
        ):
            combined_conjugation.add(surface)
        if any(
            any(_form_matches(str(row["form"]), candidate) for row in expected_rows)
            for candidate in candidates
        ):
            combined_form.add(surface)
        for row in expected_rows:
            if any(_candidate_matches_row(candidate, row) for candidate in candidates):
                comparable_feature_rows.append(str(row["id"]))

    master_recognized: set[str] = set()
    master_lemma: set[str] = set()
    master_pos: set[str] = set()
    for surface, expected_rows in grouped.items():
        recognitions = recognize_form(surface)
        if recognitions:
            master_recognized.add(surface)
        expected_lemmas = {str(row["lemma"]).casefold() for row in expected_rows}
        if any(item.lemma.casefold() in expected_lemmas for item in recognitions):
            master_lemma.add(surface)
        expected_pos = {str(row["part_of_speech"]).casefold() for row in expected_rows}
        if any((item.part_of_speech or "").casefold() in expected_pos for item in recognitions):
            master_pos.add(surface)

    combined_unknown_hits = [
        str(row["surface"])
        for row in unknowns
        if analyze_morphology(str(row["surface"]))
    ]
    master_unknown_hits = [
        str(row["surface"])
        for row in unknowns
        if recognize_form(str(row["surface"]))
    ]

    total_surfaces = len(grouped)
    total_rows = len(positives)
    total_unknowns = len(unknowns)
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

    return {
        "benchmark": metadata,
        "combined": {
            "positive_row_count": total_rows,
            "positive_unique_surface_count": total_surfaces,
            "recognized_unique_surface_count": len(combined_recognized),
            "recognition_rate": len(combined_recognized) / total_surfaces,
            "lemma_matched_unique_surface_count": len(combined_lemma),
            "lemma_recall": len(combined_lemma) / total_surfaces,
            "pos_matched_unique_surface_count": len(combined_pos),
            "pos_recall": len(combined_pos) / total_surfaces,
            "conjugation_matched_unique_surface_count": len(combined_conjugation),
            "conjugation_recall": len(combined_conjugation) / total_surfaces,
            "form_matched_unique_surface_count": len(combined_form),
            "form_recall": len(combined_form) / total_surfaces,
            "comparable_feature_row_count": total_rows,
            "comparable_feature_matched_row_count": len(comparable_feature_rows),
            "comparable_feature_recall": len(comparable_feature_rows) / total_rows,
            "unknown_count": total_unknowns,
            "unknown_rejected_count": total_unknowns - len(combined_unknown_hits),
            "unknown_safety_rate": (total_unknowns - len(combined_unknown_hits)) / total_unknowns,
            "recognized_surfaces": sorted(combined_recognized),
            "feature_matched_row_ids": sorted(comparable_feature_rows),
            "unknown_surfaces_with_analysis": combined_unknown_hits,
            "authority_diagnostics": {
                "reviewed_exact_surfaces": sorted(exact_surfaces),
                "reviewed_rule_derived_surfaces": sorted(generated_surfaces),
            },
        },
        "master": {
            "positive_unique_surface_count": total_surfaces,
            "recognized_unique_surface_count": len(master_recognized),
            "recognition_rate": len(master_recognized) / total_surfaces,
            "lemma_matched_unique_surface_count": len(master_lemma),
            "lemma_recall": len(master_lemma) / total_surfaces,
            "pos_matched_unique_surface_count": len(master_pos),
            "pos_recall": len(master_pos) / total_surfaces,
            "unknown_count": total_unknowns,
            "unknown_rejected_count": total_unknowns - len(master_unknown_hits),
            "unknown_safety_rate": (total_unknowns - len(master_unknown_hits)) / total_unknowns,
            "recognized_surfaces": sorted(master_recognized),
            "unknown_surfaces_with_analysis": master_unknown_hits,
            "note": "Master exact recognition is not credited with conjugation or infinitive-form features it does not expose.",
        },
        "holdout_integrity": {
            "benchmark_answers_are_evaluation_only": True,
            "runtime_rules_changed_in_measurement_step": False,
            "runtime_rule_learning_from_v9_allowed": False,
        },
        "interpretation": {
            "v9_tests_nonfinite_conjugation2_morphology": True,
            "person_or_tense_features_required": False,
            "global_morphology_winner_declared": False,
        },
    }


def main() -> int:
    print(json.dumps(report(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
