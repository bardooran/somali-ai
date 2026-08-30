import json
from pathlib import Path


RULE_PATH = Path("rules/morphology/verb_aspect_arag.jsonl")


def load_rules():
    return [json.loads(line) for line in RULE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_rule_ids_are_unique():
    rules = load_rules()
    ids = [rule["id"] for rule in rules]
    assert len(ids) == len(set(ids))


def test_first_person_affirmative_aspect_pair():
    by_id = {rule["id"]: rule for rule in load_rules()}
    rule = by_id["MORPH-ASPECT-ARAG-001"]
    assert rule["simple_or_general"] == "arkaa"
    assert rule["ongoing_or_current"] == "arkayaa"
    assert "Ninka waan arkaa." in rule["examples"]["simple_or_general"]
    assert "Ninka waan arkayaa." in rule["examples"]["ongoing_or_current"]


def test_second_person_question_aspect_pair():
    rule = {rule["id"]: rule for rule in load_rules()}["MORPH-ASPECT-ARAG-002"]
    assert rule["simple_or_general"] == "aragtaa"
    assert rule["ongoing_or_current"] == "arkaysaa"
    assert rule["examples"]["simple_or_general"] == ["Guriga ma aragtaa?"]
    assert rule["examples"]["ongoing_or_current"] == ["Guriga ma arkaysaa?"]


def test_negative_aspect_pair():
    rule = {rule["id"]: rule for rule in load_rules()}["MORPH-ASPECT-ARAG-003"]
    assert rule["simple_or_general"] == "ma arko"
    assert rule["ongoing_or_current"] == "ma arkayo"


def test_both_first_person_idin_constructions_are_preserved():
    rule = {rule["id"]: rule for rule in load_rules()}["MORPH-ASPECT-ARAG-004"]
    assert "Maydin arkaa?" in rule["forms"]
    assert "Maan idin arkaa?" in rule["forms"]
    assert rule["subject"] == "1sg"
    assert rule["object_clitic"] == "idin"
    assert rule["status"] == "context_required"


def test_aspect_evidence_never_defines_autocorrection():
    for rule in load_rules():
        assert rule["safe_autocorrect"] is False
        assert "replacement" not in rule
        assert "preferred_written" not in rule
