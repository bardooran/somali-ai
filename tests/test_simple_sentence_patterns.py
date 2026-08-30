import json
from pathlib import Path


RULE_PATH = Path("rules/grammar/simple_sentence_patterns.jsonl")


def load_rules():
    return [json.loads(line) for line in RULE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_sentence_rule_ids_are_unique():
    rules = load_rules()
    ids = [rule["id"] for rule in rules]
    assert len(ids) == len(set(ids))


def test_native_reviewed_basic_baa_examples_are_preserved():
    rules = {rule["id"]: rule for rule in load_rules()}
    assert rules["GRAM-SENT-001"]["example"] == "Cali baa yimid."
    assert rules["GRAM-SENT-002"]["example"] == "Maryan baa qososhay."
    assert rules["GRAM-SENT-001"]["review_evidence"] == "native_speaker_project_review"


def test_reviewed_transitive_semantic_roles_are_explicit():
    rules = {rule["id"]: rule for rule in load_rules()}
    for rule_id in ("GRAM-SENT-003", "GRAM-SENT-004"):
        rule = rules[rule_id]
        assert rule["semantic_agent"] == "wiil"
        assert rule["semantic_patient"] == "muus"
    feminine = rules["GRAM-SENT-005"]
    assert feminine["semantic_agent"] == "Maryan"
    assert feminine["semantic_patient"] == "muus"


def test_disputed_baa_sentence_is_not_promoted_as_normal_pattern():
    rules = {rule["id"]: rule for rule in load_rules()}
    disputed = rules["GRAM-SENT-006"]
    assert disputed["status"] == "context_required"
    assert disputed["native_review_reading"] == "the banana ate the boy"
    assert "source_conflict" in disputed


def test_sentence_reference_layer_has_no_automatic_replacements():
    for rule in load_rules():
        assert "replacement" not in rule
        assert "autofix" not in rule
