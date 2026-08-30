import json
from pathlib import Path


RULE_PATH = Path("rules/grammar/noun_gender_agreement.jsonl")


def load_rules():
    return [json.loads(line) for line in RULE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_ids_are_unique():
    rules = load_rules()
    ids = [rule["id"] for rule in rules]
    assert len(ids) == len(set(ids))


def test_gender_polarity_examples_are_preserved():
    rules = {rule["id"]: rule for rule in load_rules()}
    assert rules["GRAM-NOUNAGR-003"]["singular_gender"] == "masculine"
    assert rules["GRAM-NOUNAGR-003"]["plural_gender"] == "feminine"
    assert rules["GRAM-NOUNAGR-004"]["singular_gender"] == "feminine"
    assert rules["GRAM-NOUNAGR-004"]["plural_gender"] == "masculine"


def test_non_polarity_examples_are_preserved():
    rules = {rule["id"]: rule for rule in load_rules()}
    assert rules["GRAM-NOUNAGR-005"]["plural_gender"] == "masculine"
    assert rules["GRAM-NOUNAGR-006"]["plural_gender"] == "masculine"


def test_agreement_principle_rejects_immutable_lemma_gender_model():
    rules = {rule["id"]: rule for rule in load_rules()}
    assert rules["GRAM-NOUNAGR-007"]["principle"] == "agreement_controller_is_surface_number_gender_analysis"


def test_reference_layer_is_not_autocorrection_data():
    for rule in load_rules():
        assert rule["status"] == "descriptive"
        assert "replacement" not in rule
        assert "preferred_written" not in rule
