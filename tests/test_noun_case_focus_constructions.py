import json
from pathlib import Path


RULE_PATH = Path("rules/grammar/noun_case_focus_constructions.jsonl")


def load_rules():
    return [json.loads(line) for line in RULE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_rule_ids_are_unique():
    rules = load_rules()
    ids = [rule["id"] for rule in rules]
    assert len(ids) == len(set(ids))


def test_explicit_subject_controls_gender_agreement():
    rules = {rule["id"]: rule for rule in load_rules()}
    assert rules["GRAM-NCASE-001"]["agreement_controller"] == "libaaxu"
    assert rules["GRAM-NCASE-001"]["verb_form"] == "eryanayaa"
    assert rules["GRAM-NCASE-002"]["agreement_controller"] == "libaaxadu"
    assert rules["GRAM-NCASE-002"]["verb_form"] == "eryanaysaa"


def test_ayaa_forms_are_preserved_as_context_sensitive():
    rules = {rule["id"]: rule for rule in load_rules()}
    assert rules["GRAM-NCASE-003"]["noun_form"] == "libaaxa"
    assert rules["GRAM-NCASE-004"]["noun_form"] == "libaaxada"
    assert rules["GRAM-NCASE-003"]["status"] == "context_required"
    assert rules["GRAM-NCASE-004"]["status"] == "context_required"


def test_checker_must_not_normalize_between_attested_forms():
    rules = {rule["id"]: rule for rule in load_rules()}
    assert set(rules["GRAM-NCASE-005"]["forms"]) == {"libaaxu", "libaaxa"}
    assert set(rules["GRAM-NCASE-006"]["forms"]) == {"libaaxadu", "libaaxada"}
    for rule_id in ("GRAM-NCASE-005", "GRAM-NCASE-006"):
        assert "replacement" not in rules[rule_id]
        assert rules[rule_id]["status"] == "context_required"
