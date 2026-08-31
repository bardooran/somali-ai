from __future__ import annotations

from src.morphology_generator import (
    analyze_generated_surface,
    eligible_lemmas,
    generate_verb,
    paradigm_for_lemma,
)


def _surfaces(lemma: str) -> set[str]:
    return {item.surface for item in paradigm_for_lemma(lemma)}


def test_class_i_rule_is_finite_and_reviewed_lemma_gated() -> None:
    assert set(eligible_lemmas()) == {"cun", "jab", "qor", "xir"}
    assert generate_verb("dhis", tense_aspect="past", person="1sg") == ()
    assert generate_verb("tag", tense_aspect="past", person="1sg") == ()
    assert generate_verb("qorXYZ", tense_aspect="past", person="1sg") == ()


def test_regular_class_i_qor_paradigm_is_productive() -> None:
    surfaces = _surfaces("qor")
    assert {
        "qoraa",
        "qortaa",
        "qornaa",
        "qortaan",
        "qoraan",
        "qoray",
        "qortay",
        "qornay",
        "qorteen",
        "qoreen",
        "qor",
        "qora",
        "qori",
    } <= surfaces


def test_cun_concatenation_preserves_expected_gemination() -> None:
    assert generate_verb("cun", tense_aspect="present", person="1pl")[0].surface == "cunnaa"
    assert generate_verb("cun", tense_aspect="past", person="1pl")[0].surface == "cunnay"


def test_generated_surface_analysis_preserves_syncretic_people() -> None:
    qortay = analyze_generated_surface("qortay")
    assert {item.person for item in qortay} == {"2sg", "3sg_f"}
    assert {item.lemma for item in qortay} == {"qor"}
    assert all(item.tense_aspect == "past" for item in qortay)
    assert all(item.correction_allowed is False for item in qortay)


def test_generated_surface_analysis_does_not_suffix_strip_unknowns() -> None:
    assert analyze_generated_surface("dhisteen") == ()
    assert analyze_generated_surface("qorXYZ") == ()
    assert analyze_generated_surface("magacaanlaaqoonXYZ") == ()
