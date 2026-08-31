import json
from pathlib import Path

import pytest

from src.master_recognition import (
    clear_master_recognition_cache,
    is_recognized,
    recognize_form,
)


def _write_index(path: Path) -> None:
    rows = [
        {
            "surface": "erey",
            "lemma": "erey",
            "part_of_speech": "noun",
            "record_type": "vocabulary",
            "confidence_tier": "provisional",
            "status": "provisional",
            "correction_authority": False,
            "promotion_allowed": False,
            "regions": [],
            "master_record_id": "p1",
            "master_data_commit": "abc",
            "master_data_path": "data/vocabulary/provisional/example.jsonl",
            "sources": [{"source_id": "example"}],
        },
        {
            "surface": "Erey",
            "lemma": "erey",
            "part_of_speech": "noun",
            "record_type": "vocabulary",
            "confidence_tier": "trusted",
            "status": "reviewed",
            "correction_authority": True,
            "promotion_allowed": True,
            "regions": ["Jigjiga"],
            "master_record_id": "t1",
            "master_data_commit": "abc",
            "master_data_path": "data/vocabulary/reviewed/example.jsonl",
            "sources": [{"source_id": "reviewed"}],
        },
        {
            "surface": "erey",
            "lemma": "erey",
            "part_of_speech": "verb",
            "record_type": "morphology",
            "confidence_tier": "supported",
            "status": "context_required",
            "correction_authority": False,
            "promotion_allowed": False,
            "regions": [],
            "master_record_id": "s1",
            "master_data_commit": "abc",
            "master_data_path": "data/morphology/supported/example.jsonl",
            "sources": [{"source_id": "cross-source"}],
        },
    ]
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_master_recognition_is_exact_and_orders_confidence(tmp_path):
    path = tmp_path / "index.jsonl"
    _write_index(path)
    clear_master_recognition_cache()

    values = recognize_form("EREY", path=path)
    assert [value.confidence_tier for value in values] == ["trusted", "supported", "provisional"]
    assert values[0].correction_authority is True
    assert values[1].correction_authority is False
    assert values[2].correction_authority is False
    assert is_recognized("erey", path=path)
    assert recognize_form("ereyada", path=path) == ()


def test_master_recognition_confidence_filter(tmp_path):
    path = tmp_path / "index.jsonl"
    _write_index(path)
    clear_master_recognition_cache()

    assert [item.confidence_tier for item in recognize_form("erey", path=path, minimum_confidence="trusted")] == ["trusted"]
    assert [item.confidence_tier for item in recognize_form("erey", path=path, minimum_confidence="supported")] == ["trusted", "supported"]
    assert len(recognize_form("erey", path=path, minimum_confidence="provisional")) == 3
    with pytest.raises(ValueError):
        recognize_form("erey", path=path, minimum_confidence="guessed")


def test_missing_master_index_is_safe_unknown(tmp_path):
    path = tmp_path / "missing.jsonl"
    clear_master_recognition_cache()
    assert recognize_form("erey", path=path) == ()
