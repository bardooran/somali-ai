import json
from pathlib import Path


PRONOUNS = Path("rules/grammar/personal_pronouns.jsonl")


def _load():
    return [json.loads(line) for line in PRONOUNS.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_pronoun_ids_are_unique_and_source_backed():
    rows = _load()
    ids = [row["id"] for row in rows]
    assert len(ids) == len(set(ids))
    assert all(row.get("source") for row in rows)


def test_independent_pronouns_cover_person_number_and_third_singular_gender():
    rows = [row for row in _load() if row["category"] == "personal_pronoun"]
    forms = {row["form"] for row in rows}
    assert {"aniga", "adiga", "isaga", "iyada", "annaga", "innaga", "idinka", "iyaga"} <= forms
    third_singular = {(row["form"], row.get("gender")) for row in rows if row["person"] == 3 and row["number"] == "singular"}
    assert ("isaga", "masculine") in third_singular
    assert ("iyada", "feminine") in third_singular


def test_first_person_plural_preserves_inclusive_exclusive_distinction():
    rows = _load()
    mapping = {(row["form"], row.get("clusivity")) for row in rows}
    assert ("annaga", "exclusive") in mapping
    assert ("innaga", "inclusive") in mapping
    assert ("aynu", "inclusive") in mapping


def test_clitics_are_reference_only_not_replacement_rules():
    rows = _load()
    clitics = [row for row in rows if row["category"] in {"subject_clitic", "object_clitic"}]
    assert clitics
    assert all("input" not in row and "preferred_written" not in row for row in clitics)


def test_ina_conflict_is_preserved_as_source_note():
    row = next(row for row in _load() if row["form"] == "ina")
    assert "conflict" in row["status_note"].lower()
