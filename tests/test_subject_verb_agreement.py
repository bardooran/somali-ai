import json
from pathlib import Path


AGREEMENT_RULES = Path("rules/grammar/subject_verb_agreement.jsonl")


def _load_records():
    return [
        json.loads(line)
        for line in AGREEMENT_RULES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_agreement_records_have_unique_ids_and_sources():
    records = _load_records()
    ids = [record["id"] for record in records]
    assert len(ids) == len(set(ids))
    assert all(record["source"] for record in records)


def test_all_agreement_records_are_reference_only():
    records = _load_records()
    assert all(record["status"] == "provisional" for record in records)
    assert all("input" not in record for record in records)
    assert all("preferred_written" not in record for record in records)


def test_person_and_number_inventory_is_represented():
    records = _load_records()
    features = {
        (record["subject"]["person"], record["subject"]["number"])
        for record in records
    }
    assert ("1", "singular") in features
    assert ("2", "singular") in features
    assert ("3", "singular") in features
    assert ("1", "plural") in features
    assert ("2", "plural") in features
    assert ("3", "plural") in features


def test_third_person_singular_gender_contrast_is_preserved():
    records = _load_records()
    masculine = [
        record
        for record in records
        if record["subject"] == {
            "person": "3",
            "number": "singular",
            "gender": "masculine",
        }
        and record["verb_example"]["lemma"] == "cun"
    ][0]
    feminine = [
        record
        for record in records
        if record["subject"] == {
            "person": "3",
            "number": "singular",
            "gender": "feminine",
        }
        and record["verb_example"]["lemma"] == "cun"
    ][0]

    assert masculine["verb_example"]["past"] == "cunay"
    assert feminine["verb_example"]["past"] == "cuntay"
    assert masculine["verb_example"]["future"] == "cuni doonaa"
    assert feminine["verb_example"]["future"] == "cuni doontaa"
