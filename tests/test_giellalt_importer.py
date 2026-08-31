from pathlib import Path

import pytest

from tools.importers.giellalt_extract import (
    STATUS,
    extract_checkout,
    parse_lexc_candidates,
    write_jsonl,
)


MIRROR_COMMIT = "5278929712e9c0c67f254f1a1dc64c80ea7b2b8d"


def test_extracts_clean_noun_candidates_and_preserves_provenance():
    text = """
LEXICON D1_F
jidh NOUN1_F ;
hawl+Err/Orth:howl NOUN1_F ;
qayb+Use/NG:qeyb NOUN1_F ;
sannad+Use/NG:sanad NOUN1_F ;
"""

    records = list(
        parse_lexc_candidates(
            text,
            source_path="src/fst/morphology/stems/nouns.lexc",
            source_commit=MIRROR_COMMIT,
        )
    )

    assert [record.lemma for record in records] == ["jidh"]
    record = records[0]
    assert record.record_type == "noun"
    assert record.source_line == 3
    assert record.source_commit == MIRROR_COMMIT
    assert record.status == STATUS
    assert record.promotion_allowed is False
    assert "LGPL-3.0" in record.source_license
    assert "per-file" in record.source_license


def test_extracts_lemma_before_morphophonological_stem_mapping():
    text = """
LEXICON V1
arag:ar%^ak V1_TV_VerbMorf ;
aa' V1_VerbMorf ;
"""

    records = list(
        parse_lexc_candidates(
            text,
            source_path="src/fst/morphology/stems/verbs.lexc",
            source_commit=MIRROR_COMMIT,
        )
    )

    assert [(r.lemma, r.raw_lexical_token) for r in records] == [
        ("arag", "arag:ar%^ak"),
        ("aa'", "aa'"),
    ]


def test_extracts_reviewable_numerals_without_promoting_them():
    text = """
LEXICON cardinal
  toddoba NUM1_FEMd ;
  siddeed NUM1_FEM ;
LEXICON ordinal
  kowaad ORD2 ;
  siddeedaad ORD2 ;
"""

    records = list(
        parse_lexc_candidates(
            text,
            source_path="src/fst/morphology/stems/numerals.lexc",
            source_commit=MIRROR_COMMIT,
        )
    )

    assert [r.lemma for r in records] == ["toddoba", "siddeed", "kowaad", "siddeedaad"]
    assert all(r.record_type == "numeral" for r in records)
    assert all(r.promotion_allowed is False for r in records)


def test_extracts_plain_adjective_candidates_but_skips_tagged_irregular_rows():
    text = """
LEXICON IrregularAdjective
xun+A:xun Clitics ;
badan+A+Attr:bad%^an StatePerson ;
LEXICON Attr
badan AdjBase ;
caato AdjBase ;
cagaar AdjBase ;
"""

    records = list(
        parse_lexc_candidates(
            text,
            source_path="src/fst/morphology/stems/adjectives.lexc",
            source_commit=MIRROR_COMMIT,
        )
    )

    assert [record.lemma for record in records] == ["badan", "caato", "cagaar"]
    assert all(record.record_type == "adjective" for record in records)
    assert all(record.promotion_allowed is False for record in records)
    assert all(record.source_path.endswith("adjectives.lexc") for record in records)


def test_rejects_non_allowlisted_files_and_missing_commit():
    with pytest.raises(ValueError, match="not allowlisted"):
        list(
            parse_lexc_candidates(
                "foo BAR ;",
                source_path="tools/grammarcheckers/grammarchecker.cg3",
                source_commit=MIRROR_COMMIT,
            )
        )

    with pytest.raises(ValueError, match="source_commit"):
        list(
            parse_lexc_candidates(
                "jidh NOUN1_F ;",
                source_path="src/fst/morphology/stems/nouns.lexc",
                source_commit="",
            )
        )


def test_checkout_extraction_is_limited_to_requested_kind(tmp_path: Path):
    noun_path = tmp_path / "src/fst/morphology/stems/nouns.lexc"
    noun_path.parent.mkdir(parents=True)
    noun_path.write_text("jidh NOUN1_F ;\n", encoding="utf-8")

    records = extract_checkout(
        tmp_path,
        source_commit=MIRROR_COMMIT,
        kinds=["noun"],
    )

    assert [r.lemma for r in records] == ["jidh"]


def test_checkout_can_extract_adjectives_as_a_separate_review_kind(tmp_path: Path):
    path = tmp_path / "src/fst/morphology/stems/adjectives.lexc"
    path.parent.mkdir(parents=True)
    path.write_text("cagaar AdjBase ;\n", encoding="utf-8")

    records = extract_checkout(
        tmp_path,
        source_commit=MIRROR_COMMIT,
        kinds=["adjective"],
    )

    assert [(record.lemma, record.record_type) for record in records] == [
        ("cagaar", "adjective")
    ]


def test_jsonl_writer_creates_candidate_output(tmp_path: Path):
    records = list(
        parse_lexc_candidates(
            "jidh NOUN1_F ;\n",
            source_path="src/fst/morphology/stems/nouns.lexc",
            source_commit=MIRROR_COMMIT,
        )
    )
    output = tmp_path / "nested/candidates.jsonl"

    assert write_jsonl(records, output) == 1
    text = output.read_text(encoding="utf-8")
    assert '"lemma": "jidh"' in text
    assert '"status": "external_candidate_unreviewed"' in text
    assert '"promotion_allowed": false' in text
