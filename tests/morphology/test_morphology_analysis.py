from __future__ import annotations

from src.morphology_analysis import analyze_finite_verb_morphology, analyze_morphology
from src.morphology_candidates import analyze_surface_form


def test_combined_analysis_recognizes_productive_reviewed_class_i_form() -> None:
    # qornay is not an exact reviewed row; it is derived from reviewed q-class evidence.
    assert analyze_surface_form("qornay") == ()
    analyses = analyze_morphology("qornay")
    assert len(analyses) == 1
    item = analyses[0]
    assert item.lemma == "qor"
    assert item.part_of_speech == "verb"
    assert item.features["conjugation_class"] == "I"
    assert item.features["tense_aspect"] == "past"
    assert item.features["person"] == "1pl"
    assert item.authority == "reviewed_rule_derived"
    assert item.correction_allowed is False


def test_combined_analysis_preserves_generated_person_ambiguity() -> None:
    analyses = analyze_finite_verb_morphology("qortay")
    generated = [item for item in analyses if item.authority == "reviewed_rule_derived"]
    assert {item.features["person"] for item in generated} == {"2sg", "3sg_f"}
    assert all(item.features["tense_aspect"] == "past" for item in generated)


def test_exact_reviewed_evidence_stays_first_and_generated_does_not_raise_authority() -> None:
    analyses = analyze_morphology("qoreen")
    assert analyses
    assert analyses[0].authority == "reviewed_exact"
    assert any(item.authority == "reviewed_rule_derived" for item in analyses)
    assert all(
        item.correction_allowed is False
        for item in analyses
        if item.authority == "reviewed_rule_derived"
    )


def test_combined_analysis_does_not_leak_frozen_v6_forms() -> None:
    # v6 was frozen before the productive rule was added, and its lemmas are not
    # authorized by the reviewed Class-I rule.  The combined analyzer must not
    # learn the exam merely because those forms now exist in data/qa.
    for form in ("dhisay", "dhisteen", "bexeen", "bukay", "akhriyeen"):
        assert not [
            item
            for item in analyze_morphology(form)
            if item.authority == "reviewed_rule_derived"
        ]


def test_combined_analysis_keeps_unknown_sentinels_unknown() -> None:
    for form in ("qorXYZ", "dhiszv", "magacaanlaaqoonXYZ"):
        assert analyze_morphology(form) == ()
