from __future__ import annotations

import json
from pathlib import Path

from src.morphology_analysis import analyze_morphology
from src.morphophonology_generator import (
    analyze_morphophonological_surface,
    eligible_profile_lemmas,
    generate_profile_past,
)

V6 = Path("data/qa/morphology_paradigm_benchmark_v6.jsonl")
V7 = Path("data/qa/morphology_paradigm_benchmark_v7.jsonl")


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


def test_dil_past_uses_reviewed_l_assibilation_and_assimilation() -> None:
    assert _persons("dilay", "dil") == {"1sg", "3sg_m"}
    assert _persons("dishay", "dil") == {"2sg", "3sg_f"}
    assert _persons("dillay", "dil") == {"1pl"}
    assert _persons("disheen", "dil") == {"2pl"}
    assert _persons("dileen", "dil") == {"3pl"}

    dishay = analyze_morphophonological_surface("dishay")
    assert all(candidate.rule_id.endswith(":l_t_assibilation") for candidate in dishay)
    dillay = analyze_morphophonological_surface("dillay")
    assert dillay[0].rule_id.endswith(":l_n_assimilation")


def test_xidh_profile_is_restricted_to_reviewed_t_agreement_contexts() -> None:
    assert _persons("xidhdhay", "xidh") == {"2sg", "3sg_f"}
    assert _persons("xidhdheen", "xidh") == {"2pl"}
    assert generate_profile_past("xidh", "1sg") is None
    assert generate_profile_past("xidh", "1pl") is None
    assert analyze_morphophonological_surface("xidhay") == ()
    assert analyze_morphophonological_surface("xidhnay") == ()


def test_unified_analyzer_exposes_generated_features_without_correction_authority() -> None:
    analyses = [item for item in analyze_morphology("dishay") if item.lemma == "dil"]
    assert analyses
    assert {item.features.get("person") for item in analyses} == {"2sg", "3sg_f"}
    assert all(item.features.get("tense_aspect") == "past" for item in analyses)
    assert all(item.features.get("mood") == "indicative" for item in analyses)
    assert all(item.features.get("conjugation_class") == "I" for item in analyses)
    assert all(item.authority == "reviewed_rule_derived" for item in analyses)
    assert all(item.correction_allowed is False for item in analyses)


def test_morphophonology_remains_finite_and_does_not_reverse_guess() -> None:
    assert eligible_profile_lemmas() == ("dil", "xidh")
    for unknown in (
        "bilay",
        "bilshay",
        "dilzzay",
        "xidhzzay",
        "xidhdhzz",
    ):
        assert analyze_morphophonological_surface(unknown) == ()
        assert not any(item.authority == "reviewed_rule_derived" for item in analyze_morphology(unknown))


def test_development_profiles_are_disjoint_from_frozen_v6_and_v7_lemmas() -> None:
    development = {value.casefold() for value in eligible_profile_lemmas()}
    assert development.isdisjoint(_positive_lemmas(V6))
    assert development.isdisjoint(_positive_lemmas(V7))
