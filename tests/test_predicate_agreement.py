import json
from pathlib import Path

from src.predicate_agreement import analyze_predicate_agreement


RULE_PATH = Path("rules/grammar/predicate_copula_agreement.jsonl")


def load_rules():
    return [json.loads(line) for line in RULE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_predicate_rule_ids_are_unique():
    rules = load_rules()
    ids = [rule["id"] for rule in rules]
    assert len(ids) == len(set(ids))


def test_masculine_and_feminine_copula_evidence_is_preserved():
    rules = {rule["id"]: rule for rule in load_rules()}
    assert rules["GRAM-COP-001"]["copula"] == "yahay"
    assert rules["GRAM-COP-002"]["copula"] == "tahay"


def test_expanded_adjective_ah_forms_are_reference_only():
    rules = {rule["id"]: rule for rule in load_rules()}
    assert rules["GRAM-COP-003"]["surface"] == "waa ladan ahay"
    assert rules["GRAM-COP-004"]["surface"] == "waa ladan tahay"
    for rule_id in ("GRAM-COP-003", "GRAM-COP-004"):
        assert rules[rule_id]["status"] == "descriptive"


def test_reviewed_predicate_agreement_matches_gender():
    masculine = analyze_predicate_agreement("Ninku", "yahay")
    feminine = analyze_predicate_agreement("Naagtu", "tahay")
    assert masculine.recognized and masculine.agrees is True
    assert feminine.recognized and feminine.agrees is True


def test_reviewed_predicate_gender_conflicts_are_reviewable():
    masculine_wrong = analyze_predicate_agreement("Ninku", "tahay")
    feminine_wrong = analyze_predicate_agreement("Naagtu", "yahay")
    assert masculine_wrong.recognized and masculine_wrong.agrees is False
    assert masculine_wrong.expected_copula == "yahay"
    assert feminine_wrong.recognized and feminine_wrong.agrees is False
    assert feminine_wrong.expected_copula == "tahay"


def test_unknown_subject_is_not_guessed():
    result = analyze_predicate_agreement("Macallinku", "yahay")
    assert result.recognized is False
    assert result.agrees is None
    assert result.expected_copula is None


def test_predicate_layer_has_no_autofix_fields():
    for rule in load_rules():
        assert "replacement" not in rule
        assert "autofix" not in rule
