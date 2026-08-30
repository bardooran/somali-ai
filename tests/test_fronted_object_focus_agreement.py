import json
from pathlib import Path

from src.fronted_object_focus_agreement import analyze_fronted_object_focus_agreement


RULE_PATH = Path("rules/grammar/fronted_object_focus_agreement.jsonl")


def test_fronted_object_focus_rule_is_review_only():
    record = json.loads(RULE_PATH.read_text(encoding="utf-8").strip())
    assert record["id"] == "GRAM-OBJFOCUS-FRONT-001"
    assert record["licensed_lemmas"] == ["cun"]
    assert record["autofix"] is False


def test_native_reviewed_masculine_object_first_sentence():
    result = analyze_fronted_object_focus_agreement("Muus ayuu wiilku cunay.")
    assert result.recognized is True
    assert result.focused_object == ("Muus",)
    assert result.focus_clitic == "ayuu"
    assert result.subject == "wiilku"
    assert result.expected_person == "3sg_m"
    assert result.verb == "cunay"
    assert result.verb_lemmas == ("cun",)
    assert result.clitic_agrees is True
    assert result.verb_agrees is True
    assert result.agrees is True


def test_object_first_structure_generalizes_over_reviewed_subject_agreement():
    feminine = analyze_fronted_object_focus_agreement("Muus ayay gabadhu cuntay.")
    assert feminine.recognized is True
    assert feminine.subject == "gabadhu"
    assert feminine.expected_person == "3sg_f"
    assert feminine.clitic_agrees is True
    assert feminine.verb_agrees is True
    assert feminine.agrees is True

    plural = analyze_fronted_object_focus_agreement("Muus ayay carruurtu cuneen.")
    assert plural.recognized is True
    assert plural.subject == "carruurtu"
    assert plural.expected_person == "3pl"
    assert plural.clitic_agrees is True
    assert plural.verb_agrees is True
    assert plural.agrees is True


def test_fronted_object_does_not_control_agreement():
    result = analyze_fronted_object_focus_agreement("Gabadha ayuu wiilku cunay.")
    assert result.recognized is True
    assert result.focused_object == ("Gabadha",)
    assert result.subject == "wiilku"
    assert result.expected_person == "3sg_m"
    assert result.agrees is True


def test_reports_clitic_conflict_against_post_focus_subject():
    result = analyze_fronted_object_focus_agreement("Muus ayay wiilku cunay.")
    assert result.recognized is True
    assert result.subject == "wiilku"
    assert result.expected_person == "3sg_m"
    assert result.clitic_agrees is False
    assert result.verb_agrees is True
    assert result.agrees is False


def test_reports_verb_conflict_against_post_focus_subject():
    result = analyze_fronted_object_focus_agreement("Muus ayuu wiilku cuntay.")
    assert result.recognized is True
    assert result.expected_person == "3sg_m"
    assert result.clitic_agrees is True
    assert result.verb_agrees is False
    assert result.agrees is False


def test_reports_plural_clitic_and_verb_conflicts_separately():
    clitic = analyze_fronted_object_focus_agreement("Muus ayuu carruurtu cuneen.")
    assert clitic.recognized is True
    assert clitic.expected_person == "3pl"
    assert clitic.clitic_agrees is False
    assert clitic.verb_agrees is True
    assert clitic.agrees is False

    verb = analyze_fronted_object_focus_agreement("Muus ayay carruurtu cunteen.")
    assert verb.recognized is True
    assert verb.expected_person == "3pl"
    assert verb.clitic_agrees is True
    assert verb.verb_agrees is False
    assert verb.agrees is False


def test_multiword_fronted_object_is_allowed_without_becoming_subject():
    result = analyze_fronted_object_focus_agreement("Muus bisil ayuu wiilku cunay.")
    assert result.recognized is True
    assert result.focused_object == ("Muus", "bisil")
    assert result.subject == "wiilku"
    assert result.agrees is True


def test_unknown_verb_is_not_guessed():
    result = analyze_fronted_object_focus_agreement("Muus ayuu wiilku cunXYZ.")
    assert result.recognized is True
    assert result.verb == "cunXYZ"
    assert result.verb_agrees is None
    assert result.agrees is None


def test_known_but_unlicensed_lemma_remains_unjudged():
    result = analyze_fronted_object_focus_agreement("Hadal ayuu wiilku yidhi.")
    assert result.recognized is True
    assert "dheh" in result.verb_lemmas
    assert result.verb_agrees is None
    assert result.agrees is None


def test_possession_is_not_reclassified_as_fronted_object_rule():
    result = analyze_fronted_object_focus_agreement("Guri ayuu wiilku leeyahay.")
    assert result.recognized is True
    assert "leeyahay" in result.verb_lemmas
    assert result.verb_agrees is None
    assert result.agrees is None


def test_unknown_subject_evidence_leaves_structure_unjudged():
    result = analyze_fronted_object_focus_agreement("Muus ayuu qofxyz cunay.")
    assert result.recognized is False
    assert result.agrees is None
