#!/usr/bin/env python3
"""Build a compact exact-recognition index from somali-ai-data.

The index is intentionally not a grammar-correction database. It exposes
retrieval-eligible surfaces and their confidence/provenance so Somali AI can
recognize broad master-store knowledge while keeping correction authority
restricted to records that explicitly allow correctness inference.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Iterator

ALLOWED_ROOTS = ("morphology", "vocabulary", "grammar")
ALLOWED_TIERS = {"trusted", "supported", "provisional"}
CONFIDENCE_RANK = {"trusted": 0, "supported": 1, "provisional": 2}
OUTPUT_PATH = Path("data/master/recognition_index.jsonl")
MANIFEST_PATH = Path("data/master/recognition_index.meta.json")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_jsonl(path: Path) -> Iterator[dict]:
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            value = json.loads(text)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_no}: expected JSON object")
            yield value


def _source_files(data_root: Path) -> tuple[Path, ...]:
    files: list[Path] = []
    for family in ALLOWED_ROOTS:
        root = data_root / "data" / family
        if not root.is_dir():
            continue
        for path in root.rglob("*.jsonl"):
            relative = path.relative_to(data_root).as_posix().casefold()
            if "/qa/" in relative or "benchmark" in relative or "holdout" in relative:
                raise ValueError(f"evaluation data must not enter master recognition index: {relative}")
            files.append(path)
    return tuple(sorted(files))


def _part_of_speech(row: dict) -> str | None:
    features = row.get("features")
    if not isinstance(features, dict):
        return None
    value = features.get("part_of_speech")
    if isinstance(value, str) and value.strip():
        return value.strip()
    nested = features.get("source_features")
    if isinstance(nested, dict):
        value = nested.get("part_of_speech")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _compact_sources(row: dict) -> list[dict]:
    compact: list[dict] = []
    sources = row.get("sources")
    if not isinstance(sources, list):
        return compact
    for source in sources:
        if not isinstance(source, dict):
            continue
        compact.append(
            {
                "source_id": source.get("source_id"),
                "source_version": source.get("source_version"),
                "locator": source.get("locator"),
                "evidence_role": source.get("evidence_role"),
            }
        )
    return compact


def build_index(data_root: Path, *, data_commit: str) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    input_files = _source_files(data_root)
    input_row_count = 0

    for path in input_files:
        relative = path.relative_to(data_root).as_posix()
        for row in _read_jsonl(path):
            input_row_count += 1
            if row.get("retrieval_allowed") is not True:
                continue
            tier = str(row.get("confidence_tier", "")).strip()
            if tier not in ALLOWED_TIERS:
                continue
            surface = row.get("surface")
            if not isinstance(surface, str) or not surface.strip():
                # Structured rules without a surface are useful elsewhere but
                # are not lexical recognition entries.
                continue
            surface = surface.strip()
            lemma = row.get("lemma")
            lemma = lemma.strip() if isinstance(lemma, str) and lemma.strip() else surface
            rows.append(
                {
                    "surface": surface,
                    "lemma": lemma,
                    "part_of_speech": _part_of_speech(row),
                    "record_type": row.get("record_type"),
                    "confidence_tier": tier,
                    "status": row.get("status"),
                    "correction_authority": bool(row.get("correctness_inference_allowed", False)),
                    "promotion_allowed": bool(row.get("promotion_allowed", False)),
                    "regions": row.get("regions") if isinstance(row.get("regions"), list) else [],
                    "master_record_id": row.get("record_id"),
                    "master_data_commit": data_commit,
                    "master_data_path": relative,
                    "sources": _compact_sources(row),
                }
            )

    # Preserve distinct analyses/sources, but remove exact duplicate master rows.
    unique: dict[str, dict] = {}
    for row in rows:
        key = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        unique[key] = row
    rows = list(unique.values())
    rows.sort(
        key=lambda row: (
            row["surface"].casefold(),
            CONFIDENCE_RANK[row["confidence_tier"]],
            str(row.get("part_of_speech") or ""),
            row["lemma"].casefold(),
            str(row.get("master_record_id") or ""),
        )
    )

    confidence_counts = Counter(row["confidence_tier"] for row in rows)
    record_type_counts = Counter(str(row.get("record_type") or "unknown") for row in rows)
    unique_surfaces = {row["surface"].casefold() for row in rows}
    metadata = {
        "source_repository": "bardooran/somali-ai-data",
        "source_commit": data_commit,
        "input_file_count": len(input_files),
        "input_row_count": input_row_count,
        "recognition_record_count": len(rows),
        "unique_surface_count": len(unique_surfaces),
        "confidence_counts": dict(sorted(confidence_counts.items())),
        "record_type_counts": dict(sorted(record_type_counts.items())),
        "evaluation_data_included": False,
        "correction_policy": "only records with correction_authority=true may support correctness inference; recognition alone never authorizes correction",
        "matching_policy": "exact Unicode-preserving casefolded surface matching only; no suffix guessing",
    }
    return rows, metadata


def write_index(rows: Iterable[dict], metadata: dict, *, output_root: Path) -> dict:
    output_path = output_root / OUTPUT_PATH
    metadata_path = output_root / MANIFEST_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    output_path.write_text(payload, encoding="utf-8")
    metadata = {
        **metadata,
        "output": str(OUTPUT_PATH),
        "output_sha256": _sha256(payload.encode("utf-8")),
    }
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Somali AI master exact-recognition index")
    parser.add_argument("data_root", type=Path, help="Checkout of bardooran/somali-ai-data")
    parser.add_argument("--data-commit", required=True)
    parser.add_argument("--output-root", type=Path, default=Path("."))
    args = parser.parse_args()

    rows, metadata = build_index(args.data_root.resolve(), data_commit=args.data_commit)
    metadata = write_index(rows, metadata, output_root=args.output_root.resolve())
    print(json.dumps(metadata, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
