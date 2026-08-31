from pathlib import Path

import pytest

from tools.importers.sls_extract import (
    STATUS,
    extract_checkout,
    parse_spec_rules,
    write_jsonl,
)


SLS_COMMIT = "737cf848bfa8291d5580f5c34db04daef858c955"


def test_extracts_rule_with_frontmatter_and_provenance():
    text = """---
id: \"0013\"
title: Pronouns
status: Draft
---

## Rule

- **G13-R3.** A subject clitic in a reviewed focus construction MUST agree with
  the subject in person, number, and gender.

## Examples
"""
    records = list(
        parse_spec_rules(
            text,
            source_path="spec/grammar/0013-pronouns.md",
            source_commit=SLS_COMMIT,
        )
    )

    assert len(records) == 1
    record = records[0]
    assert record.rule_id == "G13-R3"
    assert record.document_id == "0013"
    assert record.lifecycle_status == "Draft"
    assert "subject in person, number, and gender" in record.statement
    assert record.source_line == 9
    assert record.source_commit == SLS_COMMIT
    assert record.status == STATUS
    assert record.promotion_allowed is False
    assert record.source_license.startswith("CC-BY-4.0")
    assert "independent linguistic confirmation" in record.source_lineage_note


def test_extracts_multiple_wrapped_rules_without_examples():
    text = """---
id: 0015
status: Draft
---
## Rule
- **G15-R1.** Free `ma` MUST precede the verbal group and the verb MUST use
  its licensed negative form.
- **G15-R2.** A nominal predicate MUST use `ma aha` in the reviewed pattern.

## Examples
| Somali | status |
| --- | --- |
"""
    records = list(
        parse_spec_rules(
            text,
            source_path="spec/grammar/0015-negation.md",
            source_commit=SLS_COMMIT,
        )
    )

    assert [r.rule_id for r in records] == ["G15-R1", "G15-R2"]
    assert "licensed negative form" in records[0].statement
    assert "Examples" not in records[1].statement


def test_proposed_standard_metadata_is_preserved():
    text = """---
id: \"0018\"
sls_id: SLS-0003
version: 0.4.0
status: Proposed
---
- **R4.** A grammar implementation MUST use reviewed paradigms.
"""
    record = next(
        parse_spec_rules(
            text,
            source_path="spec/grammar/0018-somali-grammar-standard.md",
            source_commit=SLS_COMMIT,
        )
    )
    assert record.sls_id == "SLS-0003"
    assert record.version == "0.4.0"
    assert record.lifecycle_status == "Proposed"


def test_rejects_resources_dictionary_as_not_allowlisted():
    with pytest.raises(ValueError, match="not allowlisted"):
        list(
            parse_spec_rules(
                "- **R1.** candidate",
                source_path="resources/qaamuus/01-b.md",
                source_commit=SLS_COMMIT,
            )
        )


def test_requires_exact_source_commit():
    with pytest.raises(ValueError, match="source_commit"):
        list(
            parse_spec_rules(
                "- **G13-R1.** candidate",
                source_path="spec/grammar/0013-pronouns.md",
                source_commit="",
            )
        )


def test_checkout_can_extract_just_orthography(tmp_path: Path):
    paths = (
        "spec/orthography/0001-alphabet.md",
        "spec/orthography/0002-spelling-rules.md",
        "spec/orthography/0003-capitalization.md",
        "spec/orthography/0004-punctuation.md",
    )
    for index, relative_path in enumerate(paths, start=1):
        path = tmp_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\nid: '000{index}'\nstatus: Proposed\n---\n- **R{index}.** Rule {index}.\n",
            encoding="utf-8",
        )

    records = extract_checkout(
        tmp_path,
        source_commit=SLS_COMMIT,
        sections=["orthography"],
    )
    assert [r.rule_id for r in records] == ["R1", "R2", "R3", "R4"]


def test_jsonl_output_keeps_candidate_boundary(tmp_path: Path):
    records = list(
        parse_spec_rules(
            "---\nid: '0013'\nstatus: Draft\n---\n- **G13-R3.** Test rule.\n",
            source_path="spec/grammar/0013-pronouns.md",
            source_commit=SLS_COMMIT,
        )
    )
    output = tmp_path / "sls/rules.jsonl"
    assert write_jsonl(records, output) == 1
    text = output.read_text(encoding="utf-8")
    assert '"rule_id": "G13-R3"' in text
    assert '"status": "external_candidate_unreviewed"' in text
    assert '"promotion_allowed": false' in text
