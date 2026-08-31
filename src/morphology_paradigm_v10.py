"""Score the frozen independent Conjugation-2A finite-present benchmark v10.

Hersi v10 answers are evaluation-only. This module measures the existing
runtime against the already-frozen holdout and never creates or modifies
morphology rules, lexica, or generation profiles.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from .master_recognition import recognize_form
from .morphology_analysis import MorphologyAnalysis, analyze_morphology

BENCHMARK_PATH = Path("data/qa/morphology_paradigm_benchmark_v10.jsonl")
METADATA_PATH = Path("data/qa/morphology_paradigm_benchmark_v10.meta.json")


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


def _tense_matches(expected: str, candidate: MorphologyAnalysis) -> bool:
    actual = candidate.features.get("tense_aspect")
    if actual is None:
        return False
    expected_norm = _normalize(expected)
    actual_norm = _normalize(actual)
    return actual_norm == expected_norm or expected_norm in actual_norm.split("_")


def _analysis_persons(candidate: MorphologyAnalysis) -> set[str]:
    result: set[str] = set()
    person = candidate.features.get("person")
    if isinstance(person, str) and person:
        result.add(_normalize(person))
    possible = candidate.features.get("possible_persons")
    if isinstance(possible, list):
        result.update(_normalize(value) for value in possible)
    return result


def _candidate_matches_row(candidate: MorphologyAnalysis, row: dict) -> bool:
    if candidate.lemma.casefold() != str(row["lemma"]).casefold():
        return False
    if candidate.part_of_speech.casefold() != str(row["part_of_speech"]).casefold():
        return False
    if not _conjugation_matches(str(row["conjugation"]), candidate):
        return False
    if not _tense_matches(str(row["tense_aspect"]), candidate):
        return False
    if _normalize(row["person"]) not in _analysis_persons(candidate):
        return False
    return True


def _expected_people(rows: list[dict]) -> set[str]:
    return {_normalize(row["person"]) for row in rows if row.get("person")}


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
    combined_tense: set[str] = set()
    deep_feature_rows: list[str] = []
    exact_surfaces: set[str] = set()
    generated_surfaces: set[str] = set()
    candidates_by_surface: dict[str, tuple[MorphologyAnalysis, ...]] = {}

    for surface, expected_rows in grouped.items():
        candidates = analyze_morphology(surface)
        candidates_by_surface[surface] = candidates
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
            any(_tense_matches(str(row["tense_aspect"]), candidate) for row in expected_rows)
            for candidate in candidates
        ):
            combined_tense.add(surface)
        for row in expected_rows:
            if any(_candidate_matches_row(candidate, row) for candidate in candidates):
                deep_feature_rows.append(str(row["id"]))

    syncretic_surfaces = {
        surface for surface, expected_rows in grouped.items() if len(_expected_people(expected_rows)) > 1
    }
    syncretic_preserved = {
        surface
        for surface in syncretic_surfaces
        if _expected_people(grouped[surface])
        <= {
            person
            for candidate in candidates_by_surface[surface]
            for person in _analysis_persons(candidate)
        }
    }

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
            "tense_matched_unique_surface_count": len(combined_tense),
            "tense_recall": len(combined_tense) / total_surfaces,
            "deep_feature_row_count": total_rows,
            "deep_feature_matched_row_count": len(deep_feature_rows),
            "deep_feature_recall": len(deep_feature_rows) / total_rows,
            "syncretic_surface_count": len(syncretic_surfaces),
            "syncretic_surface_preserved_count": len(syncretic_preserved),
            "ambiguity_preservation_rate": len(syncretic_preserved) / len(syncretic_surfaces),
            "unknown_count": total_unknowns,
            "unknown_rejected_count": total_unknowns - len(combined_unknown_hits),
            "unknown_safety_rate": (total_unknowns - len(combined_unknown_hits)) / total_unknowns,
            "recognized_surfaces": sorted(combined_recognized),
            "feature_matched_row_ids": sorted(deep_feature_rows),
            "syncretic_surfaces_preserved": sorted(syncretic_preserved),
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
            "note": "Master exact recognition is not credited with conjugation, tense, or person features it does not expose.",
        },
        "holdout_integrity": {
            "benchmark_answers_are_evaluation_only": True,
            "runtime_rules_changed_in_measurement_step": False,
            "runtime_rule_learning_from_v10_allowed": False,
        },
        "interpretation": {
            "v10_tests_finite_conjugation2a_present_morphology": True,
            "person_and_tense_features_required": True,
            "syncretism_is_scored": True,
            "global_morphology_winner_declared": False,
        },
    }


def main() -> int:
    print(json.dumps(report(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
