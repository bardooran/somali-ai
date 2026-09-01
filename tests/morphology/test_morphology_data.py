import json
from pathlib import Path


NOUN_PLURALS = Path("rules/morphology/noun_plural_patterns.jsonl")


def _records():
    with NOUN_PLURALS.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def test_noun_plural_records_have_unique_ids():
    records = _records()
    ids = [record["id"] for record in records]
    assert len(ids) == len(set(ids))


def test_noun_plural_records_keep_source_and_examples():
    records = _records()
    for record in records:
        assert record["status"] == "descriptive"
        assert record["source"]
        assert record["example_singular"]
        assert record["example_plural"]
        assert record["gender_singular"] in {"masculine", "feminine"}
        assert record["gender_plural"] in {"masculine", "feminine"}


def test_gender_polarity_is_preserved_for_known_classes():
    records = {record["class"]: record for record in _records()}
    assert records["L1"]["gender_plural"] == "masculine"
    assert records["L2a"]["gender_plural"] == "feminine"
    assert records["L2d"]["gender_plural"] == "masculine"
    assert records["F-o"]["gender_plural"] == "masculine"


def test_pitch_only_plural_is_not_treated_as_simple_surface_replacement():
    records = {record["class"]: record for record in _records()}
    l6 = records["L6"]
    assert l6["example_singular"] == l6["example_plural"] == "awr"
    assert "pitch" in l6["pattern"].lower()
