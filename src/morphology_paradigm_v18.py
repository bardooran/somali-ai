"""Score the frozen preselected C2A 3sg-masculine-past benchmark v18.

The two target surfaces are lemma-specific dictionary attestations. Because C2A
1SG and 3SG masculine are documented as syncretic, v18 deliberately separates
surface recognition from 3SG-masculine person resolution and reports whether
both person analyses are preserved after any future generic activation.
Benchmark answers remain evaluation-only.
"""

from __future__ import annotations

import json
from pathlib import Path

from .master_recognition import recognize_form
from .morphology_analysis import MorphologyAnalysis, analyze_morphology
from .morphology_class_lexicon import reviewed_class_entry
from .morphophonology_conj2_class_past import eligible_conj2_class_past_activation_lemmas

BENCHMARK_PATH = Path("data/qa/morphology_paradigm_benchmark_v18.jsonl")
METADATA_PATH = Path("data/qa/morphology_paradigm_benchmark_v18.meta.json")
SELECTED_TARGETS = ("aammusi", "abhi")
EXPECTED_SYNCRETIC_PERSONS = {"1sg", "3sg_m"}


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
    checks = {
        "lemma": candidate.lemma.casefold() == str(row["lemma"]).casefold(),
        "part_of_speech": candidate.part_of_speech.casefold() == str(row["part_of_speech"]).casefold(),
        "conjugation": _conjugation_matches(str(row["conjugation"]), candidate),
        "tense_aspect": _tense_matches(str(row["tense_aspect"]), candidate),
        "person": _normalize(row["person"]) in _analysis_persons(candidate),
    }
    return all(checks[feature] for feature in row["feature_scope"])


def _relevant_persons(candidates: tuple[MorphologyAnalysis, ...], row: dict) -> set[str]:
    persons: set[str] = set()
    for candidate in candidates:
        if candidate.lemma.casefold() != str(row["lemma"]).casefold():
            continue
        if candidate.part_of_speech.casefold() != str(row["part_of_speech"]).casefold():
            continue
        if not _conjugation_matches(str(row["conjugation"]), candidate):
            continue
        if not _tense_matches(str(row["tense_aspect"]), candidate):
            continue
        persons.update(_analysis_persons(candidate))
    return persons


def report() -> dict:
    rows = _rows()
    positives = tuple(row for row in rows if row["benchmark_role"] == "positive")
    unknowns = tuple(row for row in rows if row["benchmark_role"] == "unknown")

    recognized: set[str] = set()
    lemma_matches: set[str] = set()
    pos_matches: set[str] = set()
    conjugation_matches: set[str] = set()
    tense_matches: set[str] = set()
    person_matches: set[str] = set()
    deep_rows: list[str] = []
    exact_surfaces: set[str] = set()
    generated_surfaces: set[str] = set()
    observed_persons: dict[str, list[str]] = {}
    has_1sg: set[str] = set()
    has_3sg_m: set[str] = set()
    syncretism_preserved: set[str] = set()

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
        if any(_normalize(row["person"]) in _analysis_persons(candidate) for candidate in candidates):
            person_matches.add(surface)
        if any(_candidate_matches_row(candidate, row) for candidate in candidates):
            deep_rows.append(str(row["id"]))

        persons = _relevant_persons(candidates, row)
        observed_persons[surface] = sorted(persons)
        if "1sg" in persons:
            has_1sg.add(surface)
        if "3sg_m" in persons:
            has_3sg_m.add(surface)
        if EXPECTED_SYNCRETIC_PERSONS.issubset(persons):
            syncretism_preserved.add(surface)

        recognitions = recognize_form(surface)
        if recognitions:
            master_recognized.add(surface)
        if any(item.lemma.casefold() == str(row["lemma"]).casefold() for item in recognitions):
            master_lemma.add(surface)
        if any((item.part_of_speech or "").casefold() == str(row["part_of_speech"]).casefold() for item in recognitions):
            master_pos.add(surface)

    combined_unknown_hits = [str(row["surface"]) for row in unknowns if analyze_morphology(str(row["surface"]))]
    master_unknown_hits = [str(row["surface"]) for row in unknowns if recognize_form(str(row["surface"]))]

    past_activated = set(eligible_conj2_class_past_activation_lemmas())
    selected_state: dict[str, dict] = {}
    for lemma in SELECTED_TARGETS:
        entry = reviewed_class_entry(lemma)
        selected_state[lemma] = {
            "reviewed_class_entry_present": entry is not None,
            "expected_class_preauthorized": (
                entry is not None
                and entry.part_of_speech == "verb"
                and entry.conjugation_class == "2A"
            ),
            "generation_enabled_in_class_entry": entry.generation_enabled if entry is not None else None,
            "target_in_class_past_activation_cohort": lemma in past_activated,
        }

    total_surfaces = len({str(row["surface"]).casefold() for row in positives})
    total_rows = len(positives)
    total_unknowns = len(unknowns)
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

    return {
        "benchmark": metadata,
        "preauthorization": {
            "selected_targets": selected_state,
            "target_selection_predates_answer_lookup": True,
            "generic_3sg_masculine_past_authorized_at_freeze": False,
            "scored_target_lemmas": metadata["scored_target_lemmas"],
            "unresolved_target_lemmas": metadata["unresolved_target_lemmas"],
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
            "person_matched_unique_surface_count": len(person_matches),
            "person_recall": len(person_matches) / total_surfaces,
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
            "syncretism_diagnostics": {
                "expected_persons": sorted(EXPECTED_SYNCRETIC_PERSONS),
                "observed_persons_by_surface": observed_persons,
                "surface_has_1sg_analysis_count": len(has_1sg),
                "surface_has_3sg_m_analysis_count": len(has_3sg_m),
                "syncretic_surface_count": total_surfaces,
                "syncretic_surface_preserved_count": len(syncretism_preserved),
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
            "runtime_rule_learning_from_v18_allowed": False,
            "answer_sources_may_not_authorize_special_case_runtime_forms": True,
            "unresolved_targets_may_not_be_guessed": True,
        },
        "interpretation": {
            "v18_tests_preselected_c2a_3sg_masculine_past": True,
            "surface_recognition_is_not_person_resolution": True,
            "syncretism_with_1sg_is_expected": True,
            "mood_is_scored": False,
            "full_paradigm_benchmark": False,
            "global_morphology_winner_declared": False,
        },
    }


def main() -> int:
    print(json.dumps(report(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
