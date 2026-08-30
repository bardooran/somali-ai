import json
from pathlib import Path


RULE_PATH = Path("rules/grammar/special_clitics.jsonl")


def load_rules():
    return [json.loads(line) for line in RULE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_special_clitic_ids_unique():
    rules = load_rules()
    ids = [rule["id"] for rule in rules]
    assert len(ids) == len(set(ids))


def test_is_keeps_reflexive_and_reciprocal_analyses():
    rule = next(rule for rule in load_rules() if rule["id"] == "GRAM-CLITIC-001")
    assert set(rule["roles"]) == {"reflexive", "reciprocal"}
    assert rule["status"] == "context_required"


def test_native_reviewed_reciprocal_example_is_preserved():
    rule = next(rule for rule in load_rules() if rule["id"] == "GRAM-CLITIC-002")
    assert rule["example"] == "Ma is arkaysaan?"
    assert rule["review_evidence"] == "native_speaker_project_review"


def test_la_idin_roles_are_separate():
    rules = {rule["id"]: rule for rule in load_rules()}
    assert rules["GRAM-CLITIC-004"]["forms"]["impersonal"] == "la"
    assert rules["GRAM-CLITIC-004"]["forms"]["object"] == "idin"
    assert rules["GRAM-CLITIC-004"]["object_number"] == "plural"
    assert rules["GRAM-CLITIC-005"]["forms"]["object"] == "idin"


def test_special_clitics_are_not_autocorrection_rules():
    for rule in load_rules():
        assert rule["status"] in {"provisional", "context_required"}
        assert "replacement" not in rule
        assert "preferred_written" not in rule
