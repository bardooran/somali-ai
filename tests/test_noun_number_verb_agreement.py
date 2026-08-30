import json
from pathlib import Path

from src.noun_number_verb_agreement import analyze_noun_number_verb_agreement


RULE_PATH = Path("rules/grammar/noun_number_verb_agreement.jsonl")


def load_rules():
    return [
        json.loads(line)
        for line in RULE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_rule_ids_are_unique_and_review_only():
    rules = load_rules()
    ids = [record["id"] for record in rules]
    assert len(ids) == len(set(ids))
    for record in rules:
        assert record["autofix"] is False


def test_reviewed_plural_subject_accepts_past_3pl_cun_form():
    result = analyze_noun_number_verb_agreement("Macallimiintu way cuneen.")
    assert result.recognized
    assert result.subject_number == "plural"
    assert result.verb == "cuneen"
    assert result.verb_persons == ("3pl",)
    assert result.agrees is True
    assert result.expected_person == "3pl"


def test_reviewed_plural_subject_rejects_singular_compatible_past_form():
    result = analyze_noun_number_verb_agreement("Macallimiintu way cunay.")
    assert result.recognized
    assert result.subject_number == "plural"
    assert "3pl" not in result.verb_persons
    assert set(result.verb_persons) == {"1sg", "3sg_m"}
    assert result.agrees is False


def test_reviewed_plural_subject_accepts_progressive_3pl_form():
    result = analyze_noun_number_verb_agreement("Macallimiintu way cunayaan.")
    assert result.recognized
    assert result.verb_persons == ("3pl",)
    assert result.agrees is True


def test_reviewed_plural_subject_rejects_progressive_singular_form():
    result = analyze_noun_number_verb_agreement("Macallimiintu way cunayaa.")
    assert result.recognized
    assert set(result.verb_persons) == {"1sg", "3sg_m"}
    assert result.agrees is False


def test_masculine_plural_noun_still_requires_3pl_verb_person():
    correct = analyze_noun_number_verb_agreement("Miisasku way cuneen.")
    wrong = analyze_noun_number_verb_agreement("Miisasku way cunay.")
    assert correct.recognized and correct.subject_number == "plural"
    assert correct.agrees is True
    assert wrong.recognized and wrong.agrees is False


def test_wrong_clitic_does_not_change_plural_verb_person_analysis():
    result = analyze_noun_number_verb_agreement("Macallimiintu wuu cuneen.")
    assert result.recognized
    assert result.subject_number == "plural"
    assert result.agrees is True
    # Clitic agreement belongs to the noun gender/number layer; this analyzer
    # only verifies the finite verb person's number.
    assert result.clitic == "wuu"


def test_unknown_verb_is_left_unjudged():
    result = analyze_noun_number_verb_agreement("Macallimiintu way tijaabxyz.")
    assert result.recognized
    assert result.verb is None
    assert result.agrees is None


def test_singular_subject_is_outside_plural_verb_layer():
    assert analyze_noun_number_verb_agreement("Dugsigu wuu cunay.").recognized is False


def test_independent_pronoun_is_not_reclassified_as_noun_subject():
    assert analyze_noun_number_verb_agreement("Iyagu way cuneen.").recognized is False
