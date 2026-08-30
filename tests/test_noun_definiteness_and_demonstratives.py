import json
from pathlib import Path


RULE_PATH = Path("rules/morphology/noun_definiteness_and_demonstratives.jsonl")


def load_rules():
    return [json.loads(line) for line in RULE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_rule_ids_are_unique():
    rules = load_rules()
    ids = [rule["id"] for rule in rules]
    assert len(ids) == len(set(ids))


def test_reference_definite_forms_are_preserved():
    rules = {rule["id"]: rule for rule in load_rules()}
    assert rules["MORPH-NOUN-DEF-001"]["definite"] == "ninka"
    assert rules["MORPH-NOUN-DEF-002"]["definite"] == "naagta"
    assert rules["MORPH-NOUN-DEF-003"]["definite"] == "buugga"


def test_demonstratives_keep_base_relationship():
    rules = {rule["id"]: rule for rule in load_rules()}
    assert rules["MORPH-NOUN-DEF-004"]["base_definite"] == "ninka"
    assert rules["MORPH-NOUN-DEF-004"]["form"] == "ninkan"
    assert rules["MORPH-NOUN-DEF-005"]["form"] == "naagtaas"
    assert rules["MORPH-NOUN-DEF-006"]["form"] == "buuggaas"


def test_gender_polarity_and_stability_are_both_represented():
    rules = {rule["id"]: rule for rule in load_rules()}
    assert rules["MORPH-NOUN-DEF-008"]["gender_singular"] == "masculine"
    assert rules["MORPH-NOUN-DEF-008"]["gender_plural"] == "feminine"
    assert rules["MORPH-NOUN-DEF-009"]["gender_singular"] == "feminine"
    assert rules["MORPH-NOUN-DEF-009"]["gender_plural"] == "masculine"
    assert rules["MORPH-NOUN-DEF-010"]["gender_singular"] == "masculine"
    assert rules["MORPH-NOUN-DEF-010"]["gender_plural"] == "masculine"


def test_reference_layer_does_not_autogenerate_corrections():
    for rule in load_rules():
        assert rule["status"] == "descriptive"
        assert "replacement" not in rule
        assert "preferred_written" not in rule
