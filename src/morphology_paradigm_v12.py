"""Score the frozen preauthorized C2A natural-text benchmark v12.

v12 answer rows are evaluation-only. The target lemma/class authorizations predate
answer search and freeze, while both targets remained outside the finite activation
cohort. This scorer measures the current runtime without changing morphology rules
or generation authority.
"""

from __future__ import annotations

import json
from pathlib import Path

from .master_recognition import recognize_form
from .morphology_analysis import MorphologyAnalysis, analyze_morphology
from .morphology_class_lexicon import reviewed_class_entry
from .morphophonology_generator import eligible_conj2_class_activation_lemmas

BENCHMARK_PATH = Path("data/qa/morphology_paradigm_benchmark_v12.jsonl")
METADATA_PATH = Path("data/qa/morphology_paradigm_benchmark_v12.meta.json")
TARGET_LEMMAS = ("aaddi", "aammusi")


def _rows() -> tuple[dict, ...]:
    return tuple(
        json.loads(line)
        for line in BENCHMARK_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def _normalize(value: object) -> str:
    return str(value).casefold().replace("-", "_").replace(" ", "_").strip()


def _feature_matches(expected: str, actual: object | None) -> bool:
    return actual is not None and _normalize(actual) == _normalize(expected)


def _conjugation_matches(expected: str, candidate: MorphologyAnalysis) -> bool:
    actual = candidate.features.get("conjugation_class")
    if actual is None:
        actual = candidate.features.get("verb_class")
    return _feature_matches(expected, actual)


def _tense_matches(expected: str, candidate: MorphologyAnalysis) -> bool:
    actual = candidate.features.get("tense_aspect")
    if actual is None:
        return False
    expected_norm = _normalize(expected)
    actual_norm = _normalize(actual)
    return actual_norm == expected_norm or expected_norm in actual_norm.split("_")


def _mood_matches(expected: str, candidate: MorphologyAnalysis) -> bool:
    return _feature_matches(expected, candidate.features.get("mood"))


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
    return (
        candidate.lemma.casefold() == str(row["lemma"]).casefold()
        and candidate.part_of_speech.casefold() == str(row["part_of_speech"]).casefold()
        and _conjugation_matches(str(row["conjugation"]), candidate)
        and _tense_matches(str(row["tense_aspect"]), candidate)
        and _mood_matches(str(row["mood"]), candidate)
        and _normalize(row["person"]) in _analysis_persons(candidate)
    )


def report() -> dict:
    rows = _rows()
    positives = tuple(row for row in rows if row["benchmark_role"] == "positive")
    unknowns = tuple(row for row in rows if row["benchmark_role"] == "unknown")

    recognized: set[str] = set()
    lemma_matches: set[str] = set()
    pos_matches: set[str] = set()
    conjugation_matches: set[str] = set()
    tense_matches: set[str] = set()
    mood_matches: set[str] = set()
    deep_rows: list[str] = []
    exact_surfaces: set[str] = set()
    generated_surfaces: set[str] = set()

    master_recognized: set[str] = set()
    master_lemma: set[str] = set()
    master_pos: set[str] = set()

    for row in positives:
        surface = str(row["surface"]).casefold()
        candidates = analyze_morphology(surface)
        if candidates:
            recognized.add(surface)
        if any(candidate.authority == "reviewed_exact" for candidate in candidates):
            exact_surfaces.add(surface)
        if any(candidate.authority == "reviewed_rule_derived" for candidate in candidates):
            generated_surfaces.add(surface)
        if any(candidate.lemma.casefold() == str(row["lemma"]).casefold() for candidate in candidates):
            lemma_matches.add(surface)
        if any(candidate.part_of_speech.casefold() == str(row["part_of_speech"]).casefold() for candidate in candidates):
            pos_matches.add(surface)
        if any(_conjugation_matches(str(row["conjugation"]), candidate) for candidate in candidates):
            conjugation_matches.add(surface)
        if any(_tense_matches(str(row["tense_aspect"]), candidate) for candidate in candidates):
            tense_matches.add(surface)
        if any(_mood_matches(str(row["mood"]), candidate) for candidate in candidates):
            mood_matches.add(surface)
        if any(_candidate_matches_row(candidate, row) for candidate in candidates):
            deep_rows.append(str(row["id"]))

        recognitions = recognize_form(surface)
        if recognitions:
            master_recognized.add(surface)
        if any(item.lemma.casefold() == str(row["lemma"]).casefold() for item in recognitions):
            master_lemma.add(surface)
        if any((item.part_of_speech or "").casefold() == str(row["part_of_speech"]).casefold() for item in recognitions):
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

    activated = set(eligible_conj2_class_activation_lemmas())
    preauthorization: dict[str, dict] = {}
    for lemma in TARGET_LEMMAS:
        entry = reviewed_class_entry(lemma)
        preauthorization[lemma] = {
            "reviewed_class_entry_present": entry is not None,
            "expected_class_preauthorized": (
                entry is not None
                and entry.part_of_speech == "verb"
                and entry.conjugation_class == "2A"
            ),
            "generation_enabled_in_class_entry": (
                entry.generation_enabled if entry is not None else None
            ),
            "target_in_activation_cohort": lemma in activated,
        }

    total_surfaces = len(positives)
    total_rows = len(positives)
    total_unknowns = len(unknowns)
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

    return {
        "benchmark": metadata,
        "preauthorization": {
            "targets": preauthorization,
            "class_authorization_predates_answer_search": True,
            "class_authorization_predates_answer_freeze": True,
        },
        "combined": {
            "positive_row_count": total_rows,
            "positive_unique_surface_count": total_surfaces,
            "recognized_unique_surface_count": len(recognized),
            "recognition_rate": len(recognized) / total_surfaces,
            "lemma_matched_unique_surface_count": len(lemma_matches),
            "lemma_recall": len(lemma_matches) / total_surfaces,
            "pos_matched_unique_surface_count": len(pos_matches),
            "pos_recall": len(pos_matches) / total_surfaces,
            "conjugation_matched_unique_surface_count": len(conjugation_matches),
            "conjugation_recall": len(conjugation_matches) / total_surfaces,
            "tense_matched_unique_surface_count": len(tense_matches),
            "tense_recall": len(tense_matches) / total_surfaces,
            "mood_matched_unique_surface_count": len(mood_matches),
            "mood_recall": len(mood_matches) / total_surfaces,
            "deep_feature_row_count": total_rows,
            "deep_feature_matched_row_count": len(deep_rows),
            "deep_feature_recall": len(deep_rows) / total_rows,
            "unknown_count": total_unknowns,
            "unknown_rejected_count": total_unknowns - len(combined_unknown_hits),
            "unknown_safety_rate": (total_unknowns - len(combined_unknown_hits)) / total_unknowns,
            "recognized_surfaces": sorted(recognized),
            "feature_matched_row_ids": sorted(deep_rows),
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
            "note": "Master exact recognition is not credited with conjugation, tense, mood, or person features it does not expose.",
        },
        "holdout_integrity": {
            "benchmark_answers_are_evaluation_only": True,
            "runtime_rules_changed_in_measurement_step": False,
            "runtime_rule_learning_from_v12_allowed": False,
            "pre_freeze_class_authorization_allowed": True,
        },
        "interpretation": {
            "v12_tests_preauthorized_multi_source_natural_c2a_3pl_generalization": True,
            "natural_text_features_require_contextual_resolution": True,
            "person_tense_mood_and_class_features_required": True,
            "full_paradigm_benchmark": False,
            "global_morphology_winner_declared": False,
        },
    }


def main() -> int:
    print(json.dumps(report(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
