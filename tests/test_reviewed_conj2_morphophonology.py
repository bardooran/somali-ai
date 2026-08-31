from __future__ import annotations

import json
from pathlib import Path

from src.morphology_analysis import analyze_morphology
from src.morphophonology_generator import (
    analyze_morphophonological_surface,
    eligible_conj2_profile_lemmas,
    generate_conj2_present,
)

V5 = Path("data/qa/morphology_paradigm_benchmark_v5.jsonl")
V6 = Path("data/qa/morphology_paradigm_benchmark_v6.jsonl")
V7 = Path("data/qa/morphology_paradigm_benchmark_v7.jsonl")
V8 = Path("data/qa/morphology_paradigm_benchmark_v8.jsonl")


def _positive_lemmas(path: Path) -> set[str]:
    result: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("benchmark_role") == "positive" and row.get("lemma"):
            result.add(str(row["lemma"]).casefold())
    return result


def _persons(surface: str, lemma: str) -> set[str]:
    return {
        str(candidate.person)
        for candidate in analyze_morphophonological_surface(surface)
        if candidate.lemma == lemma and candidate.person
    }


def test_kari_present_t_agreement_uses_reviewed_i_t_assibilation() -> None:
    assert _persons("karisaa", "kari") == {"2sg", "3sg_f"}
    candidates = [
        item for item in analyze_morphophonological_surface("karisaa") if item.lemma == "kari"
    ]
    assert len(candidates) == 2
    assert all(item.rule_id.endswith(":i_t_assibilation") for item in candidates)
    assert all(item.tense_aspect == "present" for item in candidates)
    assert all(item.mood == "indicative" for item in candidates)
    assert all(item.conjugation_class == "2A" for item in candidates)
    assert all(item.correction_allowed is False for item in candidates)


def test_kari_profile_is_deliberately_narrow() -> None:
    assert generate_conj2_present("kari", "2sg") is not None
    assert generate_conj2_present("kari", "3sg_f") is not None
    assert generate_conj2_present("kari", "1sg") is None
    assert generate_conj2_present("kari", "1pl") is None
    assert generate_conj2_present("kari", "2pl") is None
    assert generate_conj2_present("kari", "3pl") is None

    for ungenerated in (
        "kariyaa",
        "karinnaa",
        "karisaan",
        "kariyaan",
        "karisay",
        "kariseen",
        "akhrisaa",
    ):
        assert not any(
            item.lemma == "kari" and item.authority == "reviewed_rule_derived"
            for item in analyze_morphology(ungenerated)
        )


def test_unified_analyzer_preserves_kari_person_syncretism_without_correction_authority() -> None:
    analyses = [item for item in analyze_morphology("karisaa") if item.lemma == "kari"]
    assert {item.features.get("person") for item in analyses} == {"2sg", "3sg_f"}
    assert all(item.features.get("tense_aspect") == "present" for item in analyses)
    assert all(item.features.get("mood") == "indicative" for item in analyses)
    assert all(item.features.get("conjugation_class") == "2A" for item in analyses)
    assert all(item.authority == "reviewed_rule_derived" for item in analyses)
    assert all(item.correction_allowed is False for item in analyses)


def test_conj2_profile_does_not_reverse_guess_similar_surfaces() -> None:
    assert eligible_conj2_profile_lemmas() == ("kari",)
    for synthetic_unknown in (
        "karizzsaa",
        "kariszz",
        "kariqsaa",
        "kariiszz",
    ):
        assert analyze_morphophonological_surface(synthetic_unknown) == ()
        assert not any(
            item.authority == "reviewed_rule_derived"
            for item in analyze_morphology(synthetic_unknown)
        )


def test_conj2_development_profile_is_disjoint_from_frozen_v5_v6_v7_v8_lemmas() -> None:
    development = {value.casefold() for value in eligible_conj2_profile_lemmas()}
    assert development.isdisjoint(_positive_lemmas(V5))
    assert development.isdisjoint(_positive_lemmas(V6))
    assert development.isdisjoint(_positive_lemmas(V7))
    assert development.isdisjoint(_positive_lemmas(V8))
