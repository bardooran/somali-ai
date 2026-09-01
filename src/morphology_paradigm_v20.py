"""Score frozen C2A imperative + infinitive benchmark v20.

v20 follows the completed seven-person C2A present/past block.  It freezes only
independently defensible imperative/nonfinite rows and keeps unresolved cells
out of the score.  Benchmark answers are evaluation-only.
"""

from __future__ import annotations

import json
from pathlib import Path

from .master_recognition import recognize_form
from .morphology_analysis import MorphologyAnalysis, analyze_morphology
from .morphology_class_lexicon import reviewed_class_entry
from .morphophonology_conj2_class_past import eligible_conj2_class_past_activation_lemmas
from .morphophonology_generator import eligible_conj2_class_activation_lemmas

BENCHMARK_PATH = Path("data/qa/morphology_paradigm_benchmark_v20.jsonl")
METADATA_PATH = Path("data/qa/morphology_paradigm_benchmark_v20.meta.json")
SELECTED_TARGETS = ("aaddi", "butaaci", "caajisi")


def _rows() -> tuple[dict, ...]:
    return tuple(
        json.loads(line)
        for line in BENCHMARK_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def _norm(value: object) -> str:
    return str(value).casefold().replace("-", "_").replace(" ", "_").strip()


def _conjugation(candidate: MorphologyAnalysis) -> str:
    value = candidate.features.get("conjugation_class")
    if value is None:
        value = candidate.features.get("verb_class")
    return _norm(value) if value is not None else ""


def _persons(candidate: MorphologyAnalysis) -> set[str]:
    result: set[str] = set()
    value = candidate.features.get("person")
    if isinstance(value, str) and value:
        result.add(_norm(value))
    possible = candidate.features.get("possible_persons")
    if isinstance(possible, list):
        result.update(_norm(item) for item in possible)
    return result


def _feature_ok(candidate: MorphologyAnalysis, row: dict, feature: str) -> bool:
    if feature == "lemma":
        return candidate.lemma.casefold() == str(row["lemma"]).casefold()
    if feature == "part_of_speech":
        return candidate.part_of_speech.casefold() == str(row["part_of_speech"]).casefold()
    if feature == "conjugation":
        return _conjugation(candidate) == _norm(row["conjugation"])
    if feature == "mood":
        return _norm(candidate.features.get("mood", "")) == _norm(row["mood"])
    if feature == "person":
        return _norm(row["person"]) in _persons(candidate)
    if feature == "form":
        return _norm(candidate.features.get("form", "")) == _norm(row["form"])
    raise KeyError(feature)


def _matches(candidate: MorphologyAnalysis, row: dict) -> bool:
    return all(_feature_ok(candidate, row, feature) for feature in row["feature_scope"])


def report() -> dict:
    rows = _rows()
    positives = tuple(row for row in rows if row["benchmark_role"] == "positive")
    unknowns = tuple(row for row in rows if row["benchmark_role"] == "unknown")

    recognized: set[str] = set()
    exact_surfaces: set[str] = set()
    generated_surfaces: set[str] = set()
    deep_rows: list[str] = []
    imperative_rows: list[str] = []
    infinitive_rows: list[str] = []
    lemma_rows: list[str] = []
    pos_rows: list[str] = []
    conjugation_rows: list[str] = []
    mood_rows: list[str] = []
    person_rows: list[str] = []
    form_rows: list[str] = []
    analyses_by_surface: dict[str, list[dict]] = {}

    master_recognized: set[str] = set()
    master_lemma_rows: list[str] = []
    master_pos_rows: list[str] = []

    for row in positives:
        surface = str(row["surface"]).casefold()
        candidates = analyze_morphology(surface)
        if candidates:
            recognized.add(surface)
        if any(item.authority == "reviewed_exact" for item in candidates):
            exact_surfaces.add(surface)
        if any(item.authority == "reviewed_rule_derived" for item in candidates):
            generated_surfaces.add(surface)

        analyses_by_surface[surface] = [
            {
                "lemma": item.lemma,
                "authority": item.authority,
                "features": item.features,
                "correction_allowed": item.correction_allowed,
            }
            for item in candidates
        ]

        row_id = str(row["id"])
        if any(_feature_ok(item, row, "lemma") for item in candidates):
            lemma_rows.append(row_id)
        if any(_feature_ok(item, row, "part_of_speech") for item in candidates):
            pos_rows.append(row_id)
        if any(_feature_ok(item, row, "conjugation") for item in candidates):
            conjugation_rows.append(row_id)
        if "mood" in row and any(_feature_ok(item, row, "mood") for item in candidates):
            mood_rows.append(row_id)
        if "person" in row and any(_feature_ok(item, row, "person") for item in candidates):
            person_rows.append(row_id)
        if "form" in row and any(_feature_ok(item, row, "form") for item in candidates):
            form_rows.append(row_id)
        if any(_matches(item, row) for item in candidates):
            deep_rows.append(row_id)
            if row.get("mood") == "imperative":
                imperative_rows.append(row_id)
            if row.get("form") == "infinitive":
                infinitive_rows.append(row_id)

        master = recognize_form(surface)
        if master:
            master_recognized.add(surface)
        if any(item.lemma.casefold() == str(row["lemma"]).casefold() for item in master):
            master_lemma_rows.append(row_id)
        if any((item.part_of_speech or "").casefold() == str(row["part_of_speech"]).casefold() for item in master):
            master_pos_rows.append(row_id)

    combined_unknown_hits = [
        str(row["surface"]) for row in unknowns if analyze_morphology(str(row["surface"]))
    ]
    master_unknown_hits = [
        str(row["surface"]) for row in unknowns if recognize_form(str(row["surface"]))
    ]

    present_cohort = set(eligible_conj2_class_activation_lemmas())
    past_cohort = set(eligible_conj2_class_past_activation_lemmas())
    selected_state: dict[str, dict] = {}
    for lemma in SELECTED_TARGETS:
        entry = reviewed_class_entry(lemma)
        selected_state[lemma] = {
            "reviewed_class_entry_present": entry is not None,
            "present_class_activation_member": lemma in present_cohort,
            "past_class_activation_member": lemma in past_cohort,
            "class_entry_generation_enabled": entry.generation_enabled if entry else None,
            "class_entry_correction_allowed": entry.correction_allowed if entry else None,
        }

    total_rows = len(positives)
    unique_surfaces = {str(row["surface"]).casefold() for row in positives}
    imperative_total = sum(1 for row in positives if row.get("mood") == "imperative")
    infinitive_total = sum(1 for row in positives if row.get("form") == "infinitive")
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

    return {
        "benchmark": metadata,
        "preauthorization": {
            "selected_targets": selected_state,
            "generic_c2a_imperative_authorized_at_freeze": False,
            "generic_c2a_infinitive_authorized_at_freeze": False,
            "unresolved_cells": metadata["unresolved_cells"],
        },
        "combined": {
            "positive_row_count": total_rows,
            "positive_unique_surface_count": len(unique_surfaces),
            "recognized_unique_surface_count": len(recognized),
            "lemma_matched_row_count": len(lemma_rows),
            "pos_matched_row_count": len(pos_rows),
            "conjugation_matched_row_count": len(conjugation_rows),
            "mood_matched_row_count": len(mood_rows),
            "person_matched_row_count": len(person_rows),
            "form_matched_row_count": len(form_rows),
            "deep_feature_row_count": total_rows,
            "deep_feature_matched_row_count": len(deep_rows),
            "imperative_row_count": imperative_total,
            "imperative_deep_matched_row_count": len(imperative_rows),
            "infinitive_row_count": infinitive_total,
            "infinitive_deep_matched_row_count": len(infinitive_rows),
            "unknown_count": len(unknowns),
            "unknown_rejected_count": len(unknowns) - len(combined_unknown_hits),
            "recognized_surfaces": sorted(recognized),
            "feature_matched_row_ids": sorted(deep_rows),
            "unknown_surfaces_with_analysis": combined_unknown_hits,
            "authority_diagnostics": {
                "reviewed_exact_surfaces": sorted(exact_surfaces),
                "reviewed_rule_derived_surfaces": sorted(generated_surfaces),
                "analyses_by_surface": analyses_by_surface,
            },
        },
        "master": {
            "positive_unique_surface_count": len(unique_surfaces),
            "recognized_unique_surface_count": len(master_recognized),
            "lemma_matched_row_count": len(master_lemma_rows),
            "pos_matched_row_count": len(master_pos_rows),
            "unknown_count": len(unknowns),
            "unknown_rejected_count": len(unknowns) - len(master_unknown_hits),
            "recognized_surfaces": sorted(master_recognized),
            "unknown_surfaces_with_analysis": master_unknown_hits,
        },
        "holdout_integrity": {
            "benchmark_answers_are_evaluation_only": True,
            "runtime_rule_learning_from_v20_allowed": False,
            "unresolved_cells_may_not_be_guessed": True,
            "target_specific_special_cases_allowed": False,
        },
        "interpretation": {
            "v20_tests_c2a_imperative_and_infinitive": True,
            "full_nine_cell_registry_scored": False,
            "only_independently_defensible_rows_scored": True,
            "global_morphology_winner_declared": False,
        },
    }


def main() -> int:
    print(json.dumps(report(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
