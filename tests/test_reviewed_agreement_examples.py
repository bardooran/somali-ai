import json
from pathlib import Path


RULE_PATH = Path("rules/grammar/reviewed_agreement_examples.jsonl")


def load_rules():
    return [json.loads(line) for line in RULE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_reviewed_agreement_ids_are_unique():
    rules = load_rules()
    ids = [rule["id"] for rule in rules]
    assert len(ids) == len(set(ids))


def test_ordinary_second_person_plural_uses_waad_examples():
    rules = [rule for rule in load_rules() if rule.get("person") == 2 and rule.get("number") == "plural"]
    assert len(rules) >= 5
    for rule in rules:
        assert rule["focus_subject_surface"] == "waad"
        assert rule["subject_form"] == "Idinku"
        assert rule["review_evidence"] == "native_speaker_project_review"


def test_object_clitics_do_not_control_gender_agreement():
    rules = {rule["id"]: rule for rule in load_rules()}
    masculine = rules["GRAM-RAGR-006"]
    feminine = rules["GRAM-RAGR-007"]
    assert masculine["gender"] == "masculine"
    assert masculine["verb"] == "eryanayaa"
    assert masculine["object_clitic"] == "idin"
    assert feminine["gender"] == "feminine"
    assert feminine["verb"] == "eryanaysaa"
    assert feminine["object_clitic"] == "na"


def test_bare_maydin_gender_is_carried_by_reviewed_verb_form():
    rules = {rule["id"]: rule for rule in load_rules()}
    assert rules["GRAM-RAGR-008"]["verb"] == "cunayaa"
    assert rules["GRAM-RAGR-008"]["gender"] == "masculine"
    assert rules["GRAM-RAGR-009"]["verb"] == "cunaysaa"
    assert rules["GRAM-RAGR-009"]["gender"] == "feminine"
    assert rules["GRAM-RAGR-008"]["object_clitic"] == "idin"
    assert rules["GRAM-RAGR-009"]["object_clitic"] == "idin"


def test_reviewed_agreement_layer_does_not_autofix():
    for rule in load_rules():
        assert "replacement" not in rule
        assert "autofix" not in rule
