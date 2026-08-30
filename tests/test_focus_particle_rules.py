import json
from pathlib import Path


RULE_PATH = Path("rules/grammar/focus_particle_subject_clitic.jsonl")


def load_rules():
    return [json.loads(line) for line in RULE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_focus_particle_rule_ids_are_unique():
    rules = load_rules()
    ids = [rule["id"] for rule in rules]
    assert len(ids) == len(set(ids))


def test_focus_particle_rules_are_provisional_and_sourced():
    for rule in load_rules():
        assert rule["status"] == "provisional"
        assert rule["source"] == "SLS resources/naxwe/09-weer-fudud.md"
        assert set(rule["particle_family"]) == {"baa", "ayaa"}


def test_required_and_optional_contexts_remain_distinct():
    by_id = {rule["id"]: rule for rule in load_rules()}
    assert by_id["GRAM-FOCUS-001"]["clitic_requirement"] == "required"
    assert by_id["GRAM-FOCUS-002"]["clitic_requirement"] == "optional"
    assert by_id["GRAM-FOCUS-003"]["clitic_requirement"] == "required"


def test_source_examples_preserve_required_clitic_contrast():
    by_id = {rule["id"]: rule for rule in load_rules()}
    assert by_id["GRAM-FOCUS-001"]["positive_example"] == "Wiilkii moos buu cunay."
    assert by_id["GRAM-FOCUS-001"]["negative_example"] == "Wiilkii moos baa cunay."
    assert by_id["GRAM-FOCUS-005"]["positive_example"] == "Maryan moos bay cuntay."
    assert by_id["GRAM-FOCUS-005"]["negative_example"] == "Maryan moos baa cuntay."


def test_optional_context_keeps_both_source_accepted_examples():
    by_id = {rule["id"]: rule for rule in load_rules()}
    examples = set(by_id["GRAM-FOCUS-002"]["positive_examples"])
    assert examples == {"Moos buu wiilkii cunay.", "Moos baa wiilkii cunay."}


def test_focus_rules_are_reference_only_not_replacement_rules():
    for rule in load_rules():
        assert "input" not in rule
        assert "preferred_written" not in rule
