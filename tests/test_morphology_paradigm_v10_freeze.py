from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from src.morphophonology_generator import (
    eligible_conj2_profile_lemmas,
    eligible_profile_lemmas,
)

MANIFEST = Path("data/qa/morphology_paradigm_benchmark_v10.jsonl")
META = Path("data/qa/morphology_paradigm_benchmark_v10.meta.json")


def _rows() -> list[dict]:
    return [
        json.loads(line)
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_v10_manifest_is_frozen_to_two_full_present_paradigms_and_eight_safety_probes() -> None:
    rows = _rows()
    positives = [row for row in rows if row.get("benchmark_role") == "positive"]
    unknowns = [row for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(rows) == 22
    assert len(positives) == 14
    assert len(unknowns) == 8
    assert len({row["surface"] for row in positives}) == 10
    assert {row["lemma"] for row in positives} == {"nadiifi", "qurxi"}
    assert all(row.get("part_of_speech") == "verb" for row in positives)
    assert all(row.get("conjugation") == "2A" for row in positives)
    assert all(row.get("tense_aspect") == "present" for row in positives)


def test_v10_preserves_person_syncretism_explicitly_printed_by_source() -> None:
    positives = [row for row in _rows() if row.get("benchmark_role") == "positive"]
    persons_by_lemma_surface: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in positives:
        persons_by_lemma_surface[(row["lemma"], row["surface"])].add(row["person"])

    assert persons_by_lemma_surface[("nadiifi", "nadiifiyaa")] == {"1sg", "3sg_m"}
    assert persons_by_lemma_surface[("nadiifi", "nadiifisaa")] == {"2sg", "3sg_f"}
    assert persons_by_lemma_surface[("qurxi", "qurxiyaa")] == {"1sg", "3sg_m"}
    assert persons_by_lemma_surface[("qurxi", "qurxisaa")] == {"2sg", "3sg_f"}

    assert persons_by_lemma_surface[("nadiifi", "nadiifinnaa")] == {"1pl"}
    assert persons_by_lemma_surface[("nadiifi", "nadiifisaan")] == {"2pl"}
    assert persons_by_lemma_surface[("nadiifi", "nadiifiyaan")] == {"3pl"}
    assert persons_by_lemma_surface[("qurxi", "qurxinnaa")] == {"1pl"}
    assert persons_by_lemma_surface[("qurxi", "qurxisaan")] == {"2pl"}
    assert persons_by_lemma_surface[("qurxi", "qurxiyaan")] == {"3pl"}


def test_v10_uses_only_hersi_exercise_7_4_and_marks_answers_evaluation_only() -> None:
    positives = [row for row in _rows() if row.get("benchmark_role") == "positive"]
    meta = json.loads(META.read_text(encoding="utf-8"))

    assert {row.get("source_page") for row in positives} == {"26"}
    assert all(
        row.get("source_family") == "Hersi 2022 Waan ku salaamay 1 Key to Exercises"
        for row in positives
    )
    assert meta["benchmark_version"] == "v10"
    assert meta["source_exercise"] == "7.4"
    assert meta["positive_case_count"] == 14
    assert meta["positive_unique_surface_count"] == 10
    assert meta["unknown_case_count"] == 8
    assert meta["benchmark_policy"]["answers_are_evaluation_only"] is True
    assert meta["benchmark_policy"]["runtime_rule_learning_from_v10_allowed"] is False
    assert meta["benchmark_policy"]["explicit_source_forms_only"] is True
    assert meta["benchmark_policy"]["inferred_unattested_forms_included"] is False
    assert meta["benchmark_policy"]["synthetic_unknowns_are_claimed_somali_forms"] is False


def test_v10_positive_lemmas_are_disjoint_from_current_finite_development_profiles() -> None:
    positive_lemmas = {
        str(row["lemma"]).casefold()
        for row in _rows()
        if row.get("benchmark_role") == "positive"
    }
    development = {
        value.casefold()
        for value in (*eligible_profile_lemmas(), *eligible_conj2_profile_lemmas())
    }

    assert positive_lemmas == {"nadiifi", "qurxi"}
    assert positive_lemmas.isdisjoint(development)


def test_v10_unknowns_are_distinct_synthetic_safety_strings() -> None:
    rows = _rows()
    positives = {row["surface"] for row in rows if row.get("benchmark_role") == "positive"}
    unknowns = [row["surface"] for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(unknowns) == len(set(unknowns)) == 8
    assert positives.isdisjoint(unknowns)
