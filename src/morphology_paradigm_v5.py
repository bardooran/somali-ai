"""Score the frozen independent morphology paradigm benchmark v5.

v5 is intentionally separate from the Qaamuus-derived lexical challenges.  It
measures pre-existing exact surface recognition, lemma/POS recovery, reviewed
feature analysis, ambiguity preservation, and unknown safety.  The benchmark is
evaluation-only and must not become a source of runtime morphology.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

from .master_recognition import recognize_form
from .morphology_candidates import MorphologyCandidate, analyze_surface_form

BENCHMARK_PATH = Path("data/qa/morphology_paradigm_benchmark_v5.jsonl")
METADATA_PATH = Path("data/qa/morphology_paradigm_benchmark_v5.meta.json")

CORE_FEATURES = ("conjugation", "tense_aspect", "mood", "person", "polarity")
CONJUGATION_ALIASES = {
    "1": {"1", "i", "class i", "class_1", "class-i"},
    "2": {"2", "ii", "class ii", "class_2", "class-ii"},
    "3": {"3", "iii", "class iii", "class_3", "class-iii"},
}


@dataclass(frozen=True)
class V5RuntimeScore:
    system: str
    positive_row_count: int
    positive_unique_surface_count: int
    recognized_unique_surface_count: int
    recognition_rate: float
    lemma_matched_unique_surface_count: int
    lemma_recall: float
    pos_matched_unique_surface_count: int
    pos_recall: float
    deep_feature_row_count: int
    deep_feature_matched_row_count: int
    deep_feature_recall: float
    syncretic_surface_count: int
    syncretic_surface_preserved_count: int
    ambiguity_preservation_rate: float
    unknown_count: int
    unknown_rejected_count: int
    unknown_safety_rate: float
    deep_features_available: bool


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 1.0


def load_rows(path: Path = BENCHMARK_PATH) -> tuple[dict, ...]:
    return tuple(
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def positive_rows(path: Path = BENCHMARK_PATH) -> tuple[dict, ...]:
    return tuple(row for row in load_rows(path) if row["benchmark_role"] == "positive")


def unknown_rows(path: Path = BENCHMARK_PATH) -> tuple[dict, ...]:
    return tuple(row for row in load_rows(path) if row["benchmark_role"] == "unknown")


def expected_by_surface(path: Path = BENCHMARK_PATH) -> dict[str, tuple[dict, ...]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in positive_rows(path):
        grouped[str(row["surface"]).casefold()].append(row)
    return {key: tuple(values) for key, values in grouped.items()}


def _candidate_pos(candidate: MorphologyCandidate) -> str:
    value = str(candidate.features.get("part_of_speech", "")).casefold().strip()
    if value:
        return value
    analysis_type = candidate.analysis_type.casefold()
    return "verb" if "verb" in analysis_type else ""


def _candidate_persons(candidate: MorphologyCandidate) -> set[str]:
    result: set[str] = set()
    person = candidate.features.get("person")
    if isinstance(person, str) and person:
        result.add(person.casefold())
    possible = candidate.features.get("possible_persons")
    if isinstance(possible, list):
        result.update(str(value).casefold() for value in possible)
    return result


def _text_feature_matches(expected: str, actual: object) -> bool:
    if not isinstance(actual, str):
        return False
    e = expected.casefold().replace("-", "_").strip()
    a = actual.casefold().replace("-", "_").strip()
    if e == a:
        return True
    # Reviewed datasets use labels such as simple_present/simple_past.
    if e in {"present", "past"} and e in a.split("_"):
        return True
    return False


def _conjugation_matches(expected: str, candidate: MorphologyCandidate) -> bool:
    actual = candidate.features.get("conjugation_class")
    if actual is None:
        actual = candidate.features.get("verb_class")
    if actual is None:
        return False
    normalized = str(actual).casefold().replace("_", " ").replace("-", " ").strip()
    aliases = {value.replace("_", " ").replace("-", " ") for value in CONJUGATION_ALIASES.get(expected, {expected})}
    return normalized in aliases


def reviewed_candidate_matches_row(candidate: MorphologyCandidate, row: dict) -> bool:
    if candidate.lemma.casefold() != str(row["lemma"]).casefold():
        return False
    if _candidate_pos(candidate) != str(row["part_of_speech"]).casefold():
        return False
    if "conjugation" in row and not _conjugation_matches(str(row["conjugation"]), candidate):
        return False
    if "tense_aspect" in row and not _text_feature_matches(str(row["tense_aspect"]), candidate.features.get("tense_aspect")):
        return False
    if "mood" in row and not _text_feature_matches(str(row["mood"]), candidate.features.get("mood")):
        return False
    if "person" in row and str(row["person"]).casefold() not in _candidate_persons(candidate):
        return False
    if "polarity" in row and not _text_feature_matches(str(row["polarity"]), candidate.features.get("polarity")):
        return False
    return True


def _syncretic_surfaces(path: Path = BENCHMARK_PATH) -> set[str]:
    grouped = expected_by_surface(path)
    return {
        surface
        for surface, rows in grouped.items()
        if len({str(row.get("person", "")) for row in rows if row.get("person")}) > 1
    }


def reviewed_report(path: Path = BENCHMARK_PATH) -> dict:
    positives = positive_rows(path)
    unknowns = unknown_rows(path)
    grouped = expected_by_surface(path)
    recognized: set[str] = set()
    lemma_matched: set[str] = set()
    pos_matched: set[str] = set()
    feature_matches = 0
    candidates_by_surface: dict[str, tuple[MorphologyCandidate, ...]] = {}

    for surface, rows in grouped.items():
        candidates = analyze_surface_form(surface)
        candidates_by_surface[surface] = candidates
        if candidates:
            recognized.add(surface)
        expected_lemmas = {str(row["lemma"]).casefold() for row in rows}
        if any(candidate.lemma.casefold() in expected_lemmas for candidate in candidates):
            lemma_matched.add(surface)
        expected_pos = {str(row["part_of_speech"]).casefold() for row in rows}
        if any(_candidate_pos(candidate) in expected_pos for candidate in candidates):
            pos_matched.add(surface)
        for row in rows:
            if any(reviewed_candidate_matches_row(candidate, row) for candidate in candidates):
                feature_matches += 1

    syncretic = _syncretic_surfaces(path)
    syncretic_preserved = 0
    for surface in syncretic:
        expected_persons = {
            str(row["person"]).casefold()
            for row in grouped[surface]
            if row.get("person")
        }
        actual_persons: set[str] = set()
        for candidate in candidates_by_surface.get(surface, ()):
            actual_persons.update(_candidate_persons(candidate))
        if expected_persons <= actual_persons:
            syncretic_preserved += 1

    unknown_hits = [row["surface"] for row in unknowns if analyze_surface_form(str(row["surface"]))]
    score = V5RuntimeScore(
        system="somali_ai_reviewed",
        positive_row_count=len(positives),
        positive_unique_surface_count=len(grouped),
        recognized_unique_surface_count=len(recognized),
        recognition_rate=_ratio(len(recognized), len(grouped)),
        lemma_matched_unique_surface_count=len(lemma_matched),
        lemma_recall=_ratio(len(lemma_matched), len(grouped)),
        pos_matched_unique_surface_count=len(pos_matched),
        pos_recall=_ratio(len(pos_matched), len(grouped)),
        deep_feature_row_count=len(positives),
        deep_feature_matched_row_count=feature_matches,
        deep_feature_recall=_ratio(feature_matches, len(positives)),
        syncretic_surface_count=len(syncretic),
        syncretic_surface_preserved_count=syncretic_preserved,
        ambiguity_preservation_rate=_ratio(syncretic_preserved, len(syncretic)),
        unknown_count=len(unknowns),
        unknown_rejected_count=len(unknowns) - len(unknown_hits),
        unknown_safety_rate=_ratio(len(unknowns) - len(unknown_hits), len(unknowns)),
        deep_features_available=True,
    )
    return {
        "score": asdict(score),
        "recognized_surfaces": sorted(recognized),
        "unrecognized_surfaces": sorted(set(grouped) - recognized),
        "unknown_surfaces_with_analysis": unknown_hits,
    }


def master_report(path: Path = BENCHMARK_PATH) -> dict:
    positives = positive_rows(path)
    unknowns = unknown_rows(path)
    grouped = expected_by_surface(path)
    recognized: set[str] = set()
    lemma_matched: set[str] = set()
    pos_matched: set[str] = set()

    for surface, rows in grouped.items():
        recognitions = recognize_form(surface)
        if recognitions:
            recognized.add(surface)
        expected_lemmas = {str(row["lemma"]).casefold() for row in rows}
        if any(item.lemma.casefold() in expected_lemmas for item in recognitions):
            lemma_matched.add(surface)
        expected_pos = {str(row["part_of_speech"]).casefold() for row in rows}
        if any((item.part_of_speech or "").casefold() in expected_pos for item in recognitions):
            pos_matched.add(surface)

    unknown_hits = [row["surface"] for row in unknowns if recognize_form(str(row["surface"]))]
    syncretic = _syncretic_surfaces(path)
    score = V5RuntimeScore(
        system="somali_ai_master_exact",
        positive_row_count=len(positives),
        positive_unique_surface_count=len(grouped),
        recognized_unique_surface_count=len(recognized),
        recognition_rate=_ratio(len(recognized), len(grouped)),
        lemma_matched_unique_surface_count=len(lemma_matched),
        lemma_recall=_ratio(len(lemma_matched), len(grouped)),
        pos_matched_unique_surface_count=len(pos_matched),
        pos_recall=_ratio(len(pos_matched), len(grouped)),
        deep_feature_row_count=len(positives),
        deep_feature_matched_row_count=0,
        deep_feature_recall=0.0,
        syncretic_surface_count=len(syncretic),
        syncretic_surface_preserved_count=0,
        ambiguity_preservation_rate=0.0,
        unknown_count=len(unknowns),
        unknown_rejected_count=len(unknowns) - len(unknown_hits),
        unknown_safety_rate=_ratio(len(unknowns) - len(unknown_hits), len(unknowns)),
        deep_features_available=False,
    )
    return {
        "score": asdict(score),
        "recognized_surfaces": sorted(recognized),
        "unrecognized_surfaces": sorted(set(grouped) - recognized),
        "unknown_surfaces_with_analysis": unknown_hits,
        "note": "Master recognition carries lemma/POS/confidence but is not credited with person/tense/mood features it does not expose.",
    }


def report(path: Path = BENCHMARK_PATH) -> dict:
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    reviewed = reviewed_report(path)
    master = master_report(path)
    grouped = expected_by_surface(path)
    reviewed_preexisting = set(reviewed["recognized_surfaces"])
    master_preexisting = set(master["recognized_surfaces"])
    return {
        "benchmark": metadata,
        "reviewed": reviewed,
        "master": master,
        "pre_freeze_overlap": {
            "positive_unique_surface_count": len(grouped),
            "reviewed_recognized_surface_count": len(reviewed_preexisting),
            "master_recognized_surface_count": len(master_preexisting),
            "master_unseen_surface_count": len(grouped) - len(master_preexisting),
            "master_unseen_surfaces": sorted(set(grouped) - master_preexisting),
            "runtime_identity_frozen_before_v5_harness": True,
        },
        "interpretation": {
            "source_family_independent_of_v2_v4": True,
            "benchmark_answers_are_evaluation_only": True,
            "surface_recognition_and_deep_feature_analysis_are_separate": True,
            "global_morphology_winner_declared": False,
        },
    }


def main() -> int:
    print(json.dumps(report(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
