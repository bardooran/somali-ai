import json
from pathlib import Path


RULE_PATH = Path("rules/grammar/negation_patterns.jsonl")


def load_rules():
    return [json.loads(line) for line in RULE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_negation_rule_ids_are_unique():
    rules = load_rules()
    ids = [rule["id"] for rule in rules]
    assert len(ids) == len(set(ids))


def test_cun_negation_preserves_distinct_paradigms():
    rules = {rule["id"]: rule for rule in load_rules()}
    assert rules["GRAM-NEG-001"]["negative"] == "ma cuno"
    assert rules["GRAM-NEG-002"]["negative"] == "ma cunayo"
    assert rules["GRAM-NEG-003"]["negative"] == "ma cunin"
    assert rules["GRAM-NEG-004"]["negative"] == "ma cuni jirin"
    assert rules["GRAM-NEG-005"]["negative"] == "ma cuni doono"
    assert len({rules[f"GRAM-NEG-00{i}"]["paradigm"] for i in range(1, 6)}) == 5


def test_negative_class_samples_remain_separate():
    rules = {rule["id"]: rule for rule in load_rules()}
    expected = {
        "GRAM-NEG-006": ("I", "cunin"),
        "GRAM-NEG-007": ("IIA", "toosin"),
        "GRAM-NEG-008": ("IIB", "caddaynin"),
        "GRAM-NEG-009": ("IIIA", "dhaqanin"),
        "GRAM-NEG-010": ("IIIB", "qabsanin"),
    }
    for rule_id, (verb_class, form) in expected.items():
        assert rules[rule_id]["conjugation_class"] == verb_class
        assert rules[rule_id]["negative_sample"] == form


def test_negation_reference_is_not_autocorrection_data():
    for rule in load_rules():
        assert rule["status"] == "descriptive"
        assert "replacement" not in rule
        assert "preferred_written" not in rule
