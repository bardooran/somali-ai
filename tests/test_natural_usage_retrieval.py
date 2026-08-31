import json

from src.assistant.prompts import build_instructions
from src.assistant.retrieval import KnowledgeIndex


def _write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_external_usage_has_distinct_lower_trust_class(tmp_path):
    usage = tmp_path / "data" / "usage" / "external" / "wikipedia.jsonl"
    _write(
        usage,
        [
            {
                "text": "Dadka magaalada ayaa ka wada hadlay qorshaha cusub ee adeegyada bulshada.",
                "status": "external_natural_usage_unreviewed",
                "promotion_allowed": False,
                "correctness_inference_allowed": False,
            }
        ],
    )
    index = KnowledgeIndex.build([tmp_path / "data" / "usage"])
    hits = index.search("qorshaha adeegyada")
    assert hits
    assert hits[0].trust == "external_usage"


def test_reviewed_linguistic_record_beats_comparable_external_usage(tmp_path):
    reviewed = tmp_path / "data" / "vocabulary" / "reviewed.jsonl"
    usage = tmp_path / "data" / "usage" / "external" / "wikipedia.jsonl"
    _write(reviewed, [{"lemma": "qorshe", "status": "reviewed", "note": "qorshe adeeg"}])
    _write(
        usage,
        [
            {
                "text": "Qorshe adeeg ayaa la diyaariyey si bulshada loo caawiyo.",
                "status": "external_natural_usage_unreviewed",
            }
        ],
    )
    index = KnowledgeIndex.build([tmp_path / "data"])
    hits = index.search("qorshe", limit=2)
    assert len(hits) == 2
    assert hits[0].trust == "reviewed"
    assert hits[1].trust == "external_usage"


def test_usage_text_is_in_evidence_excerpt(tmp_path):
    usage = tmp_path / "data" / "usage" / "external" / "xlsum.jsonl"
    sentence = "Warbixintu waxay sheegtay in bulshada ay ka wada hadashay qorshaha cusub."
    _write(usage, [{"text": sentence, "status": "external_natural_usage_unreviewed"}])
    hit = KnowledgeIndex.build([usage]).search("warbixintu")[0]
    assert sentence in hit.excerpt


def test_prompt_explicitly_limits_external_usage_authority(tmp_path):
    usage = tmp_path / "data" / "usage" / "external" / "xlsum.jsonl"
    _write(
        usage,
        [{"text": "Bulshada ayaa maanta ka hadashay qorshe cusub oo horumarineed.", "status": "external_natural_usage_unreviewed"}],
    )
    hit = KnowledgeIndex.build([usage]).search("bulshada")[0]
    prompt = build_instructions([hit])
    assert "external_usage" in prompt
    assert "never as proof of correctness" in prompt
