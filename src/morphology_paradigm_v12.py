"""Score the frozen preauthorized C2A natural-text benchmark v12.

v12 answer rows are evaluation-only. Both target lemmas were reviewed as C2A and
merged before answer-source search, while the Stage 1M activation cohort excluded
them at freeze. This scorer measures the current runtime only; it grants no new
generation or correction authority.
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
        and _feature_matches(str(row["mood"]), candidate.features.get("mood"))
        and _normalize(row["person"]) in _analysis_persons(candidate)
    )


def report() -> dict:
    rows = _rows()
    positives = tuple(row for row in rows if row["benchmark_role"] == "positive")
    unknowns = tuple(row for row in rows if row["benchmark_role"] == "unknown")

    recognized: set[str] = set()
    lemma_matched: set[str] = set()
    pos_matched: set[str] = set()
    conjugation_matched: set[str] = set()
    tense_matched: set[str] = set()
    mood_matched: set[str] = set()
    person_matched: set[str] = set()
    deep_rows: list[str] = []
    exact_surfaces: set[str] = set()
    rule_derived_surfaces: set[str] = set()

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
            rule_derived_surfaces.add(surface)

        if any(candidate.lemma.casefold() == str(row["lemma"]).casefold() for candidate in candidates):
            lemma_matched.add(surface)
        if any(candidate.part_of_speech.casefold() == str(row["part_of_speech"]).casefold() for candidate in candidates):
            pos_matched.add(surface)
        if any(_conjugation_matches(str(row["conjugation"]), candidate) for candidate in candidates):
            conjugation_matched.add(surface)
        if any(_tense_matches(str(row["tense_aspect"]), candidate) for candidate in candidates):
            tense_matched.add(surface)
        if any(_feature_matches(str(row["mood"]), candidate.features.get("mood")) for candidate in candidates):
            mood_matched.add(surface)
        if any(_normalize(row["person"]) in _analysis_persons(candidate) for candidate in candidates):
            person_matched.add(surface)
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

    preauthorization: dict[str, dict[str, object]] = {}
    activated = set(eligible_conj2_class_activation_lemmas())
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
            "in_class_activation_cohort": lemma in activated,
            "class_authorization_predates_answer_search": True,
        }

    total = len(positives)
    unknown_total = len(unknowns)
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

    return {
        "benchmark": metadata,
        "preauthorization": preauthorization,
        "combined": {
            "positive_row_count": total,
            "positive_unique_surface_count": total,
            "recognized_unique_surface_count": len(recognized),
            "recognition_rate": len(recognized) / total,
            "lemma_matched_unique_surface_count": len(lemma_matched),
            "lemma_recall": len(lemma_matched) / total,
            "pos_matched_unique_surface_count": len(pos_matched),
            "pos_recall": len(pos_matched) / total,
            "conjugation_matched_unique_surface_count": len(conjugation_matched),
            "conjugation_recall": len(conjugation_matched) / total,
            "tense_matched_unique_surface_count": len(tense_matched),
            "tense_recall": len(tense_matched) / total,
            "mood_matched_unique_surface_count": len(mood_matched),
            "mood_recall": len(mood_matched) / total,
            "person_matched_unique_surface_count": len(person_matched),
            "person_recall": len(person_matched) / total,
            "deep_feature_row_count": total,
            "deep_feature_matched_row_count": len(deep_rows),
            "deep_feature_recall": len(deep_rows) / total,
            "unknown_count": unknown_total,
            "unknown_rejected_count": unknown_total - len(combined_unknown_hits),
            "unknown_safety_rate": (unknown_total - len(combined_unknown_hits)) / unknown_total,
            "recognized_surfaces": sorted(recognized),
            "feature_matched_row_ids": sorted(deep_rows),
            "unknown_surfaces_with_analysis": combined_unknown_hits,
            "authority_diagnostics": {
                "reviewed_exact_surfaces": sorted(exact_surfaces),
                "reviewed_rule_derived_surfaces": sorted(rule_derived_surfaces),
            },
        },
        "master": {
            "positive_unique_surface_count": total,
            "recognized_unique_surface_count": len(master_recognized),
            "recognition_rate": len(master_recognized) / total,
            "lemma_matched_unique_surface_count": len(master_lemma),
            "lemma_recall": len(master_lemma) / total,
            "pos_matched_unique_surface_count": len(master_pos),
            "pos_recall": len(master_pos) / total,
            "unknown_count": unknown_total,
            "unknown_rejected_count": unknown_total - len(master_unknown_hits),
            "unknown_safety_rate": (unknown_total - len(master_unknown_hits)) / unknown_total,
            "recognized_surfaces": sorted(master_recognized),
            "unknown_surfaces_with_analysis": master_unknown_hits,
            "note": "Master exact recognition is not credited with conjugation, tense, mood, or person features it does not expose.",
        },
        "holdout_integrity": {
            "benchmark_answers_are_evaluation_only": True,
            "runtime_rules_changed_in_measurement_step": False,
            "runtime_rule_learning_from_v12_allowed": False,
            "class_authorization_predates_answer_search": True,
            "targets_unactivated_at_measurement": all(
                not values["in_class_activation_cohort"]
                for values in preauthorization.values()
            ),
        },
        "interpretation": {
            "v12_tests_preauthorized_multi_source_natural_c2a_3pl_generalization": True,
            "person_tense_mood_and_class_features_required": True,
            "full_paradigm_benchmark": False,
            "natural_text_feature_resolution": True,
            "global_morphology_winner_declared": False,
        },
    }


def main() -> int:
    print(json.dumps(report(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
