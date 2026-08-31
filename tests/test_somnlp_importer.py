import io
import json
from pathlib import Path

import pytest

from tools.importers.somnlp_extract import (
    STATUS,
    iter_jsonl_candidates,
    parse_corpus_record,
    write_jsonl,
)


SOMNLP_COMMIT = "5281c76787b69ddbf3a8fc8c45cfcc3ad927467b"


def record(source: str, license_id: str, text: str = "Cali ayaa buugga akhriyey.", **overrides):
    value = {
        "id": f"{source}:abc123",
        "text": text,
        "provenance": {"source": source, "lang": "so", "collected_at": "2026-08-31T00:00:00Z"},
        "license": license_id,
        "quality": {"disposition": "kept", "flags": []},
        "schema_version": 1,
    }
    value.update(overrides)
    return value


def test_wikipedia_is_tier_a_but_never_correctness_authority():
    candidate = parse_corpus_record(
        record("wikipedia", "CC-BY-SA-4.0"),
        source_commit=SOMNLP_COMMIT,
    )
    assert candidate is not None
    assert candidate.evidence_tier == "A"
    assert candidate.evidence_role == "edited_native_use_qa"
    assert candidate.status == STATUS
    assert candidate.promotion_allowed is False
    assert candidate.correctness_inference_allowed is False


def test_web_and_parallel_sources_keep_distinct_roles():
    web = parse_corpus_record(
        record("hplt", "CC0-1.0"), source_commit=SOMNLP_COMMIT
    )
    parallel = parse_corpus_record(
        record("nllb", "ODC-BY"), source_commit=SOMNLP_COMMIT
    )
    assert web is not None and parallel is not None
    assert web.evidence_tier == "B"
    assert web.evidence_role == "broad_web_attestation"
    assert parallel.evidence_tier == "C"
    assert parallel.evidence_role == "parallel_translation_attestation"


def test_unresolved_religious_source_is_blocked_by_default():
    quran = record("quran", "Other")
    assert parse_corpus_record(quran, source_commit=SOMNLP_COMMIT) is None

    allowed = parse_corpus_record(
        quran,
        source_commit=SOMNLP_COMMIT,
        allow_unresolved_license=True,
    )
    assert allowed is not None
    assert allowed.evidence_tier == "D"
    assert allowed.evidence_role == "specialized_religious_translation"


def test_rejected_and_review_records_do_not_enter_normal_sample():
    rejected = record("wikipedia", "CC-BY-SA-4.0")
    rejected["quality"] = {"disposition": "rejected", "flags": ["not_somali"]}
    review = record("wikipedia", "CC-BY-SA-4.0")
    review["quality"] = {"disposition": "review", "flags": ["high_symbol_ratio"]}

    assert parse_corpus_record(rejected, source_commit=SOMNLP_COMMIT) is None
    assert parse_corpus_record(review, source_commit=SOMNLP_COMMIT) is None


def test_missing_provenance_or_license_fails_loudly():
    missing_provenance = record("hplt", "CC0-1.0")
    missing_provenance.pop("provenance")
    with pytest.raises(ValueError, match="provenance"):
        parse_corpus_record(missing_provenance, source_commit=SOMNLP_COMMIT)

    missing_license = record("hplt", "CC0-1.0")
    missing_license.pop("license")
    with pytest.raises(ValueError, match="license"):
        parse_corpus_record(missing_license, source_commit=SOMNLP_COMMIT)


def test_known_source_license_mismatch_is_rejected():
    with pytest.raises(ValueError, match="license mismatch"):
        parse_corpus_record(
            record("wikipedia", "CC0-1.0"),
            source_commit=SOMNLP_COMMIT,
        )


def test_unknown_source_and_missing_commit_are_rejected():
    with pytest.raises(ValueError, match="unrecognized"):
        parse_corpus_record(
            record("mystery", "CC0-1.0"),
            source_commit=SOMNLP_COMMIT,
        )
    with pytest.raises(ValueError, match="source_commit"):
        parse_corpus_record(record("hplt", "CC0-1.0"), source_commit="")


def test_grammar_bearing_words_are_preserved_not_removed_as_stopwords():
    text = "Wiilku moos ayuu cunay, gabadhuna way qososhay."
    candidate = parse_corpus_record(
        record("wikipedia", "CC-BY-SA-4.0", text=text),
        source_commit=SOMNLP_COMMIT,
    )
    assert candidate is not None
    assert candidate.text == text
    assert "ayuu" in candidate.text
    assert "way" in candidate.text


def test_streaming_sample_is_bounded_per_source():
    lines = [
        record("hplt", "CC0-1.0", text="HPLT one sentence with enough text."),
        record("hplt", "CC0-1.0", text="HPLT second sentence with enough text."),
        record("wikipedia", "CC-BY-SA-4.0", text="Wikipedia one sentence with enough text."),
        record("wikipedia", "CC-BY-SA-4.0", text="Wikipedia second sentence with enough text."),
    ]
    handle = io.StringIO("\n".join(json.dumps(item) for item in lines))
    candidates = list(
        iter_jsonl_candidates(
            handle,
            source_commit=SOMNLP_COMMIT,
            requested_sources={"hplt", "wikipedia"},
            per_source_limit=1,
        )
    )
    assert [(c.source, c.evidence_tier) for c in candidates] == [
        ("hplt", "B"),
        ("wikipedia", "A"),
    ]


def test_jsonl_writer_keeps_attestation_boundary(tmp_path: Path):
    candidate = parse_corpus_record(
        record("xlsum", "CC-BY-4.0"),
        source_commit=SOMNLP_COMMIT,
    )
    assert candidate is not None
    output = tmp_path / "somnlp/sample.jsonl"
    assert write_jsonl([candidate], output) == 1
    text = output.read_text(encoding="utf-8")
    assert '"status": "external_corpus_attestation_unreviewed"' in text
    assert '"promotion_allowed": false' in text
    assert '"correctness_inference_allowed": false' in text
