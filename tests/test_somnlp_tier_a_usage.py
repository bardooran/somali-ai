import json

import pytest

from tools.importers.somnlp_tier_a_usage import (
    SOURCES,
    bounded_excerpt,
    iter_raw_usage_candidates,
)


def _line(text):
    return json.dumps({"text": text}, ensure_ascii=False)


def test_bounded_excerpt_keeps_short_natural_text():
    text = "Soomaaliya waa dal ku yaal Geeska Afrika, waxaana ku nool dad Soomaaliyeed oo badan."
    assert bounded_excerpt(text) == text


def test_bounded_excerpt_rejects_too_short_text():
    assert bounded_excerpt("Qoraal aad u gaaban.") is None


def test_bounded_excerpt_limits_long_documents_without_inventing_text():
    first = "Soomaaliya waa dal ku yaal Geeska Afrika oo leh taariikh dheer iyo bulshooyin kala duwan."
    second = "Caasimaddu waa Muqdisho, magaalo weyn oo ku taalla xeebta Badweynta Hindiya."
    tail = " ".join(["eray"] * 150)
    text = f"{first} {second} {tail}"
    excerpt = bounded_excerpt(text, maximum_words=30)
    assert excerpt
    assert excerpt in text
    assert len(excerpt.split()) <= 30


def test_wikipedia_candidate_preserves_provenance_and_cannot_promote():
    rows = list(
        iter_raw_usage_candidates(
            [_line("Soomaaliya waa dal ku yaal Geeska Afrika waxaana ku nool bulsho ku hadasha Af-Soomaali.")],
            source="wikipedia",
            source_commit="abc123",
        )
    )
    assert len(rows) == 1
    row = rows[0]
    assert row.source == "wikipedia"
    assert row.dataset == "wikimedia/wikipedia"
    assert row.dataset_config == "20231101.so"
    assert row.source_license == "CC-BY-SA-4.0"
    assert row.evidence_tier == "A"
    assert row.promotion_allowed is False
    assert row.correctness_inference_allowed is False
    assert row.source_commit == "abc123"
    assert row.content_hash.startswith("sha256:")


def test_xlsum_candidate_uses_news_attestation_policy():
    rows = list(
        iter_raw_usage_candidates(
            [_line("Warbixintu waxay sheegtay in dadka deegaanka ay ka wada hadleen arrimaha bulshada iyo horumarka magaalada.")],
            source="xlsum",
            source_commit="def456",
        )
    )
    assert len(rows) == 1
    row = rows[0]
    assert row.source_license == "CC-BY-4.0"
    assert row.evidence_role == "edited_news_summary_attestation"


def test_duplicate_usage_text_is_removed_within_source():
    text = "Dadka magaalada ayaa maanta ka hadlay qorshe cusub oo lagu horumarinayo adeegyada bulshada."
    rows = list(
        iter_raw_usage_candidates(
            [_line(text), _line(text)],
            source="wikipedia",
            source_commit="abc123",
        )
    )
    assert len(rows) == 1


def test_unknown_source_is_rejected():
    with pytest.raises(ValueError, match="unsupported Tier-A source"):
        list(
            iter_raw_usage_candidates(
                [_line("Qoraalkan waxa uu leeyahay erayo ku filan si loo tijaabiyo habka cusub ee xog ururinta.")],
                source="unknown",
                source_commit="abc123",
            )
        )


def test_source_policy_registry_is_intentionally_tier_a_only():
    assert set(SOURCES) == {"wikipedia", "xlsum"}
