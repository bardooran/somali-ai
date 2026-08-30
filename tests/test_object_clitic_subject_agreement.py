import json
from pathlib import Path


RULE_PATH = Path("rules/grammar/object_clitic_subject_agreement.jsonl")


def load_rules():
    return [json.loads(line) for line in RULE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_rule_ids_are_unique_and_native_reviewed():
    rules = load_rules()
    ids = [rule["id"] for rule in rules]
    assert len(ids) == len(set(ids))
    assert all(rule["review_evidence"] == "native_speaker_project_review" for rule in rules)


def test_idin_is_object_not_agreement_controller():
    by_id = {rule["id"]: rule for rule in load_rules()}
    for rule_id in ["GRAM-OBJAGR-001", "GRAM-OBJAGR-002", "GRAM-OBJAGR-003", "GRAM-OBJAGR-004"]:
        rule = by_id[rule_id]
        assert rule["object_clitic"] == "idin"
        assert rule["verb_agreement_controller"] in {"understood_subject", "subject"}
        assert rule["verb_agreement_controller"] != "object"


def test_masculine_and_feminine_lion_agreement_stays_distinct():
    by_id = {rule["id"]: rule for rule in load_rules()}
    masc = by_id["GRAM-OBJAGR-003"]
    fem = by_id["GRAM-OBJAGR-004"]
    assert "Libaaxu maydin eryanayaa?" in masc["positive_question_examples"]
    assert masc["subject_gender"] == "masculine"
    assert fem["question_example"] == "Libaaxadu maydin eryanaysaa?"
    assert fem["subject_gender"] == "feminine"


def test_definite_and_subject_marked_noun_forms_are_not_collapsed():
    rule = {rule["id"]: rule for rule in load_rules()}["GRAM-OBJAGR-005"]
    assert rule["masculine_example"] == "Libaaxa ayaa eryanayaa."
    assert rule["feminine_example"] == "Libaaxada ayaa eryanaysa."
    assert "Libaaxu maydin eryanayaa?" in rule["contrast_examples"]
    assert "Libaaxadu maydin eryanaysaa?" in rule["contrast_examples"]


def test_ongoing_question_can_switch_idin_to_na_in_answer():
    rule = {rule["id"]: rule for rule in load_rules()}["GRAM-OBJAGR-002"]
    assert rule["example"] == "Maydin cunaysaa?"
    assert rule["answer_example"] == "Haa, way na cunaysaa."
    assert rule["aspect"] == "ongoing"


def test_general_and_ongoing_cun_forms_stay_separate():
    by_id = {rule["id"]: rule for rule in load_rules()}
    assert by_id["GRAM-OBJAGR-001"]["example"] == "Maydin cuntaa?"
    assert by_id["GRAM-OBJAGR-001"]["aspect"] == "general_or_habitual"
    assert by_id["GRAM-OBJAGR-002"]["example"] == "Maydin cunaysaa?"
    assert by_id["GRAM-OBJAGR-002"]["aspect"] == "ongoing"


def test_native_review_rules_do_not_define_string_replacements():
    for rule in load_rules():
        assert "input" not in rule
        assert "preferred_written" not in rule
        assert "replacement" not in rule
