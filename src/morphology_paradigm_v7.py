"""Score the frozen independent morphology paradigm benchmark v7.

The v7 answers remain evaluation-only. This module measures the already-existing
runtime against the frozen holdout and does not create or modify morphology rules.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from .master_recognition import recognize_form
from .morphology_analysis import analyze_morphology
from .morphology_paradigm_v6 import combined_candidate_matches_row

BENCHMARK_PATH = Path("data/qa/morphology_paradigm_benchmark_v7.jsonl")
METADATA_PATH = Path("data/qa/morphology_paradigm_benchmark_v7.meta.json")


def _rows() -> tuple[dict, ...]:
    return tuple(
        json.loads(line)
        for line in BENCHMARK_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


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
    combined_feature_rows: list[str] = []
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
        if any(candidate.lemma.casefold() == "joogso" for candidate in candidates):
            combined_lemma.add(surface)
        if any(candidate.part_of_speech.casefold() == "verb" for candidate in candidates):
            combined_pos.add(surface)
        for row in expected_rows:
            if any(combined_candidate_matches_row(candidate, row) for candidate in candidates):
                combined_feature_rows.append(str(row["id"]))

    master_recognized: set[str] = set()
    master_lemma: set[str] = set()
    master_pos: set[str] = set()
    for surface in grouped:
        recognitions = recognize_form(surface)
        if recognitions:
            master_recognized.add(surface)
        if any(item.lemma.casefold() == "joogso" for item in recognitions):
            master_lemma.add(surface)
        if any((item.part_of_speech or "").casefold() == "verb" for item in recognitions):
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

    syncretic_surfaces = {
        surface
        for surface, expected_rows in grouped.items()
        if len({str(row.get("person", "")) for row in expected_rows}) > 1
    }
    syncretic_preserved: list[str] = []
    for surface in syncretic_surfaces:
        expected_people = {str(row["person"]).casefold() for row in grouped[surface]}
        actual_people: set[str] = set()
        for candidate in analyze_morphology(surface):
            person = candidate.features.get("person")
            if isinstance(person, str):
                actual_people.add(person.casefold())
            possible = candidate.features.get("possible_persons")
            if isinstance(possible, list):
                actual_people.update(str(value).casefold() for value in possible)
        if expected_people <= actual_people:
            syncretic_preserved.append(surface)

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
            "lemma_matched_unique_surface_count": len(combined_lemma),
            "pos_matched_unique_surface_count": len(combined_pos),
            "deep_feature_matched_row_count": len(combined_feature_rows),
            "deep_feature_recall": len(combined_feature_rows) / total_rows,
            "syncretic_surface_count": len(syncretic_surfaces),
            "syncretic_surface_preserved_count": len(syncretic_preserved),
            "unknown_count": total_unknowns,
            "unknown_rejected_count": total_unknowns - len(combined_unknown_hits),
            "unknown_safety_rate": (total_unknowns - len(combined_unknown_hits)) / total_unknowns,
            "recognized_surfaces": sorted(combined_recognized),
            "feature_matched_row_ids": sorted(combined_feature_rows),
            "unknown_surfaces_with_analysis": combined_unknown_hits,
            "authority_diagnostics": {
                "reviewed_exact_surfaces": sorted(exact_surfaces),
                "reviewed_rule_derived_surfaces": sorted(generated_surfaces),
            },
        },
        "master": {
            "positive_unique_surface_count": total_surfaces,
            "recognized_unique_surface_count": len(master_recognized),
            "lemma_matched_unique_surface_count": len(master_lemma),
            "pos_matched_unique_surface_count": len(master_pos),
            "unknown_count": total_unknowns,
            "unknown_rejected_count": total_unknowns - len(master_unknown_hits),
            "unknown_safety_rate": (total_unknowns - len(master_unknown_hits)) / total_unknowns,
            "recognized_surfaces": sorted(master_recognized),
            "unknown_surfaces_with_analysis": master_unknown_hits,
        },
        "holdout_integrity": {
            "benchmark_answers_are_evaluation_only": True,
            "runtime_rules_changed_in_measurement_step": False,
            "runtime_rule_learning_from_v7_allowed": False,
        },
    }


def main() -> int:
    print(json.dumps(report(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
