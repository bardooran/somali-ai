import json
from pathlib import Path


RULE_PATH = Path("rules/grammar/focus_particle_subject_clitic.jsonl")


def load_rules():
    return [json.loads(line) for line in RULE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_focus_particle_rule_ids_are_unique():
    rules = load_rules()
    ids = [rule["id"] for rule in rules]
    assert len(ids) == len(set(ids))


def test_focus_particle_rules_are_sourced_and_use_known_statuses():
    for rule in load_rules():
        assert rule["status"] in {"provisional", "context_required"}
        assert rule["source"] == "SLS resources/naxwe/09-weer-fudud.md"
        assert set(rule["particle_family"]) == {"baa", "ayaa"}


def test_required_and_disputed_contexts_remain_distinct():
    by_id = {rule["id"]: rule for rule in load_rules()}
    assert by_id["GRAM-FOCUS-001"]["clitic_requirement"] == "required"
    assert by_id["GRAM-FOCUS-002"]["clitic_requirement"] == "disputed"
    assert by_id["GRAM-FOCUS-002"]["status"] == "context_required"
    assert by_id["GRAM-FOCUS-003"]["clitic_requirement"] == "required"


def test_native_review_preserves_masculine_and_feminine_clitic_models():
    by_id = {rule["id"]: rule for rule in load_rules()}
    examples = set(by_id["GRAM-FOCUS-001"]["positive_examples"])
    assert "Wiilku muus buu cunay." in examples
    assert "Maryan muus bay cuntay." in examples
    assert by_id["GRAM-FOCUS-005"]["positive_example"] == "Maryan muus bay cuntay."
    assert by_id["GRAM-FOCUS-005"]["negative_example"] == "Maryan muus baa cuntay."


def test_disputed_bare_baa_example_preserves_semantic_role_review():
    by_id = {rule["id"]: rule for rule in load_rules()}
    rule = by_id["GRAM-FOCUS-002"]
    assert "Moos baa wiilkii cunay." in rule["source_examples"]
    assert "Muus ayuu wiilku cunay." in rule["reviewed_preferred_examples"]
    assert "Moos baa wiilkii cunay." not in rule["reviewed_preferred_examples"]
    review = rule["native_review_interpretation"]
    assert review["reviewer_reading"] == "The banana ate the boy."
    assert review["intended_boy_eats_banana_reading"] is False
    assert review["evidence"] == "native_speaker_project_review"


def test_focus_rules_are_reference_only_not_replacement_rules():
    for rule in load_rules():
        assert "input" not in rule
        assert "preferred_written" not in rule
