import hashlib
import json
from collections import Counter
from pathlib import Path


MANIFEST_PATH = Path("data/qa/morphology_challenge_v2.jsonl")
METADATA_PATH = Path("data/qa/morphology_challenge_v2.meta.json")
EXPECTED_SHA256 = "79b3534f7b51c1cf8c963ba6515e028f7cc93ae2b771297847508867a889851e"
EXPECTED_SOURCE_COMMIT = "737cf848bfa8291d5580f5c34db04daef858c955"
EXPECTED_SEED = "somali-ai-morphology-challenge-v2-2026-08-31"


def _cases() -> list[dict]:
    return [
        json.loads(line)
        for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_v2_manifest_identity_is_frozen():
    content = MANIFEST_PATH.read_bytes()
    assert hashlib.sha256(content).hexdigest() == EXPECTED_SHA256

    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    assert metadata["benchmark_version"] == "v2"
    assert metadata["manifest_sha256"] == EXPECTED_SHA256
    assert metadata["source_commit"] == EXPECTED_SOURCE_COMMIT
    assert metadata["selection_seed"] == EXPECTED_SEED
    assert metadata["selection_is_analyzer_blind"] is True
    assert metadata["definitions_copied"] is False
    assert metadata["case_count"] == 136
    assert metadata["positive_case_count"] == 120
    assert metadata["unknown_probe_count"] == 16
    assert metadata["selected_pair_count"] == 120
    assert metadata["quotas"] == {
        "adjective": 16,
        "noun": 48,
        "numeral": 8,
        "verb": 48,
    }


def test_v2_manifest_structure_and_counts_are_frozen():
    cases = _cases()
    assert len(cases) == 136
    assert len({case["id"] for case in cases}) == 136

    split_counts = Counter(case["split"] for case in cases)
    assert split_counts == {"challenge": 120, "unknown": 16}

    positive_pairs = Counter()
    for case in cases:
        assert case["benchmark_version"] == "v2"
        if case["split"] == "unknown":
            assert case["expected_unknown"] is True
            assert case["expected_analyses"] == []
            assert case["surface"].startswith("pvz")
            continue

        assert case["expected_unknown"] is False
        assert case["expected_analyses"]
        source = case["source"]
        assert source["repository"] == "bardooran/goobolabs"
        assert source["commit"] == EXPECTED_SOURCE_COMMIT
        assert source["selection_seed"] == EXPECTED_SEED
        assert source["provenance"]
        for expected in case["expected_analyses"]:
            pos = expected["features"]["part_of_speech"]
            positive_pairs[pos] += 1

    assert positive_pairs == {
        "noun": 48,
        "verb": 48,
        "adjective": 16,
        "numeral": 8,
    }


def test_v2_manifest_contains_no_dictionary_definitions():
    content = MANIFEST_PATH.read_text(encoding="utf-8")
    assert '"definition"' not in content
    assert '"gloss"' not in content
