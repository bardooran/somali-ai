import json
from pathlib import Path


VERB_RULES = Path("rules/morphology/verb_conjugation_samples.jsonl")


def _load_records():
    return [json.loads(line) for line in VERB_RULES.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_verb_reference_ids_are_unique():
    records = _load_records()
    ids = [record["id"] for record in records]
    assert len(ids) == len(set(ids))


def test_all_verb_records_are_descriptive_and_sourced():
    for record in _load_records():
        assert record["status"] == "descriptive"
        assert record["source"] == "SLS resources/sarfe/02-falalka.md"


def test_cun_person_number_paradigm_is_preserved():
    record = next(r for r in _load_records() if r["id"] == "MORPH-VERB-001")
    assert record["forms"]["present_habitual"]["1sg"] == "cunaa"
    assert record["forms"]["present_habitual"]["3sg_f"] == "cuntaa"
    assert record["forms"]["past_simple"]["1pl"] == "cunnay"
    assert record["forms"]["future"]["3pl"] == "cuni doonaan"


def test_three_conjugation_classes_have_examples():
    records = _load_records()
    examples = {r.get("conjugation_class") for r in records if r["category"] == "verb_class_example"}
    assert examples == {"I", "II", "III"}


def test_negative_forms_are_reference_pairs_not_rewrite_rule():
    record = next(r for r in _load_records() if r["id"] == "MORPH-VERB-008")
    pairs = record["affirmative_negative_pairs"]
    assert ["cunaa", "ma cuno"] in pairs
    assert ["cuni doonaa", "ma cuni doono"] in pairs
    assert "input" not in record
    assert "preferred_written" not in record
