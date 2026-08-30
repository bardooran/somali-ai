import json
from pathlib import Path


PATH = Path("rules/grammar/subject_focus_baa.jsonl")


def _records():
    return [json.loads(line) for line in PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_basic_baa_subject_focus_examples_are_preserved():
    record = next(item for item in _records() if item["id"] == "GRAM-BAA-SUBJ-001")
    texts = {example["text"] for example in record["reviewed_examples"]}
    assert "Cali baa yimid." in texts
    assert "Maryan baa qososhay." in texts
    assert record["review_evidence"] == "native_speaker_project_review"


def test_basic_baa_rule_is_not_an_autofix_or_transitive_generalization():
    record = next(item for item in _records() if item["id"] == "GRAM-BAA-SUBJ-001")
    assert record["autofix"] is False
    assert record["pattern"] == "subject + baa + predicate"
    assert "must not be generalized" in record["analysis_note"]
