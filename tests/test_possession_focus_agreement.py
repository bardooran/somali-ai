import json
from pathlib import Path

from src.possession_focus_agreement import analyze_possession_focus_agreement


RULE_PATH = Path("rules/grammar/possession_focus_agreement.jsonl")


def test_possession_focus_rule_is_review_only():
    records = [
        json.loads(line)
        for line in RULE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 1
    assert records[0]["id"] == "GRAM-POSS-FOCUS-001"
    assert records[0]["autofix"] is False


def test_masculine_feminine_and_plural_baa_contractions_agree():
    masculine = analyze_possession_focus_agreement("Ninku guri buu leeyahay.")
    feminine = analyze_possession_focus_agreement("Gabadhu guri bay leedahay.")
    plural = analyze_possession_focus_agreement("Macallimiintu guri bay leeyihiin.")

    assert masculine.recognized and masculine.agrees is True
    assert masculine.expected_person == "3sg_m"
    assert masculine.focus_clitic_persons == ("3sg_m",)
    assert masculine.verb_agrees is True

    assert feminine.recognized and feminine.agrees is True
    assert feminine.expected_person == "3sg_f"
    assert set(feminine.focus_clitic_persons) == {"3sg_f", "3pl"}
    assert feminine.verb_agrees is True

    assert plural.recognized and plural.agrees is True
    assert plural.expected_person == "3pl"
    assert set(plural.focus_clitic_persons) == {"3sg_f", "3pl"}
    assert plural.verb_agrees is True


def test_ayaa_contractions_are_supported_without_normalizing_to_baa():
    assert analyze_possession_focus_agreement("Ninku guri ayuu leeyahay.").agrees is True
    assert analyze_possession_focus_agreement("Gabadhu guri ayay leedahay.").agrees is True
    assert analyze_possession_focus_agreement("Macallimiintu guri ayay leeyihiin.").agrees is True


def test_focus_clitic_is_controlled_by_subject_not_focused_noun():
    masculine_wrong = analyze_possession_focus_agreement("Ninku guri bay leeyahay.")
    feminine_wrong = analyze_possession_focus_agreement("Gabadhu guri buu leedahay.")
    plural_wrong = analyze_possession_focus_agreement("Macallimiintu guri buu leeyihiin.")

    for result in (masculine_wrong, feminine_wrong, plural_wrong):
        assert result.recognized
        assert result.clitic_agrees is False
        assert result.verb_agrees is True
        assert result.agrees is False
        assert result.focused_material == ("guri",)


def test_possession_verb_agreement_is_controlled_by_explicit_subject():
    masculine_wrong = analyze_possession_focus_agreement("Ninku guri buu leedahay.")
    feminine_wrong = analyze_possession_focus_agreement("Gabadhu guri bay leeyahay.")
    plural_wrong = analyze_possession_focus_agreement("Macallimiintu guri bay leedahay.")

    for result in (masculine_wrong, feminine_wrong, plural_wrong):
        assert result.recognized
        assert result.clitic_agrees is True
        assert result.verb_agrees is False
        assert result.agrees is False


def test_multiword_focused_material_does_not_change_controller():
    result = analyze_possession_focus_agreement("Ninku guri weyn buu leeyahay.")
    assert result.recognized and result.agrees is True
    assert result.subject == "Ninku"
    assert result.focused_material == ("guri", "weyn")
    assert result.verb == "leeyahay"


def test_past_possession_uses_same_focus_structure():
    assert analyze_possession_focus_agreement("Ninku guri buu lahaa.").agrees is True
    assert analyze_possession_focus_agreement("Gabadhu guri bay lahayd.").agrees is True
    assert analyze_possession_focus_agreement("Macallimiintu guri bay lahaayeen.").agrees is True

    assert analyze_possession_focus_agreement("Ninku guri buu lahayd.").agrees is False
    assert analyze_possession_focus_agreement("Gabadhu guri bay lahaa.").agrees is False
    assert analyze_possession_focus_agreement("Macallimiintu guri bay lahaa.").agrees is False


def test_conditional_after_focus_is_not_reinterpreted_as_possession():
    result = analyze_possession_focus_agreement("Ninku cunto buu cuni lahaa.")
    assert result.recognized is True
    assert result.focus_clitic == "buu"
    assert result.verb == "cuni"
    assert result.clitic_agrees is True
    assert result.verb_agrees is None
    assert result.agrees is None


def test_unknown_possession_lookalike_is_unjudged_not_guessed():
    result = analyze_possession_focus_agreement("Ninku guri buu leeyahaXYZ.")
    assert result.recognized is True
    assert result.clitic_agrees is True
    assert result.verb_agrees is None
    assert result.agrees is None


def test_subject_focus_and_unknown_subject_are_outside_current_scope():
    assert analyze_possession_focus_agreement("Ninku buu leeyahay.").recognized is False
    assert analyze_possession_focus_agreement("QofXYZ guri buu leeyahay.").recognized is False
