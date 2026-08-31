from __future__ import annotations

import hashlib
import json
from pathlib import Path

BENCHMARK = Path("data/qa/morphology_paradigm_benchmark_v5.jsonl")


def _rows() -> list[dict]:
    return [json.loads(line) for line in BENCHMARK.read_text(encoding="utf-8").splitlines() if line.strip()]


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def test_v5_shape_and_source_family_are_frozen() -> None:
    rows = _rows()
    positives = [row for row in rows if row["benchmark_role"] == "positive"]
    unknowns = [row for row in rows if row["benchmark_role"] == "unknown"]

    assert len(rows) == 45
    assert len(positives) == 37
    assert len(unknowns) == 8
    assert {row["part_of_speech"] for row in positives} == {"verb"}
    assert {row["source_family"] for row in positives} == {
        "Nilsson 2025 Learner's Somali Grammar"
    }
    assert {row["source_url"] for row in positives} == {
        "https://morgannilsson.se/LearnersSomaliGrammar.pdf"
    }


def test_v5_ids_are_unique_and_unknowns_are_not_positive_surfaces() -> None:
    rows = _rows()
    assert len({row["id"] for row in rows}) == len(rows)
    positives = {row["surface"].casefold() for row in rows if row["benchmark_role"] == "positive"}
    unknowns = {row["surface"].casefold() for row in rows if row["benchmark_role"] == "unknown"}
    assert positives.isdisjoint(unknowns)
    assert all("z" in surface or "v" in surface or "x" in surface for surface in unknowns)


def test_v5_preserves_known_syncretism() -> None:
    rows = _rows()
    heesaa = [row for row in rows if row["surface"] == "heesaa"]
    heestaa = [row for row in rows if row["surface"] == "heestaa"]
    heesay = [row for row in rows if row["surface"] == "heesay"]
    heestay = [row for row in rows if row["surface"] == "heestay"]

    assert {row["person"] for row in heesaa} == {"1sg", "3sg_m"}
    assert {row["person"] for row in heestaa} == {"2sg", "3sg_f"}
    assert {row["person"] for row in heesay} == {"1sg", "3sg_m"}
    assert {row["person"] for row in heestay} == {"2sg", "3sg_f"}


def test_v5_manifest_identity_is_versioned_in_metadata_file() -> None:
    metadata = json.loads(Path("data/qa/morphology_paradigm_benchmark_v5.meta.json").read_text(encoding="utf-8"))
    assert metadata["manifest_git_blob_sha"] == _git_blob_sha(BENCHMARK)
    assert metadata["benchmark_version"] == "v5"
    assert metadata["positive_case_count"] == 37
    assert metadata["unknown_case_count"] == 8
