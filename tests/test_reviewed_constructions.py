import json
from pathlib import Path


PATH = Path("rules/grammar/reviewed_constructions.jsonl")


def _records():
    return [json.loads(line) for line in PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_waydinkii_is_separate_context_required_construction():
    record = next(item for item in _records() if item["id"] == "GRAM-CONSTR-001")
    assert record["surface_form"] == "waydinkii"
    assert record["status"] == "context_required"
    assert record["autofix"] is False


def test_native_reviewed_waydinkii_examples_are_preserved():
    record = next(item for item in _records() if item["id"] == "GRAM-CONSTR-001")
    texts = {example["text"] for example in record["reviewed_examples"]}
    assert "Waydinkii shalay yimid." in texts
    assert "Waydinkii ballanka qaaday." in texts


def test_waydin_is_not_recorded_as_ordinary_idinku_statement():
    record = next(item for item in _records() if item["id"] == "GRAM-CONSTR-001")
    ordinary = set(record["contrast"]["ordinary_second_person_plural"])
    rejected = set(record["contrast"]["rejected_as_ordinary_pattern"])
    assert "Idinku waad timaaddeen." in ordinary
    assert "Idinku waydin timaaddeen." in rejected
    assert ordinary.isdisjoint(rejected)
