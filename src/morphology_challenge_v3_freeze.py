"""Freeze a disjoint analyzer-blind morphology challenge v3.

v3 is selected from the same pinned Qaamuus source as v2 with a new fixed seed,
but every positive v2 surface is excluded before hashing. This module must not
import or call Somali AI analyzers, GiellaLT, or HFST.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from .morphology_challenge_v2_freeze import (
    DEFAULT_QUOTAS,
    SOMALI_LETTERS,
    SOURCE_COMMIT,
    SOURCE_REPOSITORY,
    source_pool,
)

V2_MANIFEST_PATH = Path("data/qa/morphology_challenge_v2.jsonl")
SELECTION_SEED = "somali-ai-morphology-challenge-v3-2026-08-31"
UNKNOWN_PROBE_COUNT = 16


def v2_positive_surfaces(path: Path = V2_MANIFEST_PATH) -> set[str]:
    surfaces: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            case = json.loads(stripped)
            if isinstance(case, dict) and case.get("split") == "challenge":
                surface = str(case.get("surface", "")).casefold().strip()
                if surface:
                    surfaces.add(surface)
    return surfaces


def selection_hash(surface: str, pos: str) -> str:
    payload = f"{SELECTION_SEED}\0{pos}\0{surface}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def select_pairs(
    pool: dict[tuple[str, str], list[dict]],
    excluded_surfaces: set[str],
    quotas: dict[str, int] = DEFAULT_QUOTAS,
) -> tuple[tuple[str, str, str], ...]:
    selected: list[tuple[str, str, str]] = []
    excluded = {surface.casefold() for surface in excluded_surfaces}
    for pos, quota in quotas.items():
        candidates = [
            (selection_hash(surface, candidate_pos), surface, candidate_pos)
            for surface, candidate_pos in pool
            if candidate_pos == pos and surface.casefold() not in excluded
        ]
        candidates.sort()
        if len(candidates) < quota:
            raise ValueError(
                f"not enough disjoint {pos} candidates: need {quota}, found {len(candidates)}"
            )
        selected.extend(candidates[:quota])
    selected.sort()
    return tuple((surface, pos, digest) for digest, surface, pos in selected)


def synthetic_unknown(index: int, occupied: set[str]) -> str:
    counter = 0
    while True:
        digest = hashlib.sha256(
            f"{SELECTION_SEED}\0unknown\0{index}\0{counter}".encode("utf-8")
        ).digest()
        tail = "".join(SOMALI_LETTERS[value % len(SOMALI_LETTERS)] for value in digest[:7])
        surface = f"zvp{tail}"
        if surface not in occupied:
            return surface
        counter += 1


def build_manifest(
    source_root: Path,
    *,
    v2_path: Path = V2_MANIFEST_PATH,
    quotas: dict[str, int] = DEFAULT_QUOTAS,
    unknown_probe_count: int = UNKNOWN_PROBE_COUNT,
) -> tuple[list[dict], dict]:
    pool = source_pool(source_root)
    excluded = v2_positive_surfaces(v2_path)
    selected_pairs = select_pairs(pool, excluded, quotas)

    selected_by_surface: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for surface, pos, digest in selected_pairs:
        selected_by_surface[surface].append((pos, digest))

    ordered_surfaces = sorted(
        selected_by_surface,
        key=lambda surface: min(digest for _, digest in selected_by_surface[surface]),
    )
    overlap = set(ordered_surfaces) & excluded
    if overlap:
        raise ValueError(f"v3 selection overlaps v2: {sorted(overlap)[:5]}")

    cases: list[dict] = []
    for index, surface in enumerate(ordered_surfaces, start=1):
        selected = sorted(selected_by_surface[surface])
        provenance: list[dict] = []
        for pos, digest in selected:
            for source in pool[(surface, pos)]:
                provenance.append(
                    {
                        "part_of_speech": pos,
                        "selection_hash": digest,
                        **source,
                    }
                )
        provenance.sort(
            key=lambda item: (
                item["part_of_speech"],
                item["source_path"],
                item["source_line"],
            )
        )
        cases.append(
            {
                "id": f"MCV3-{index:04d}",
                "benchmark_version": "v3",
                "split": "challenge",
                "surface": surface,
                "expected_unknown": False,
                "expected_analyses": [
                    {"lemma": surface, "features": {"part_of_speech": pos}}
                    for pos, _ in selected
                ],
                "source": {
                    "repository": SOURCE_REPOSITORY,
                    "commit": SOURCE_COMMIT,
                    "selection_seed": SELECTION_SEED,
                    "excluded_benchmark": "v2",
                    "provenance": provenance,
                },
            }
        )

    occupied = {surface for surface, _ in pool} | excluded
    for unknown_index in range(1, unknown_probe_count + 1):
        surface = synthetic_unknown(unknown_index, occupied)
        cases.append(
            {
                "id": f"MCV3-U{unknown_index:03d}",
                "benchmark_version": "v3",
                "split": "unknown",
                "surface": surface,
                "expected_unknown": True,
                "expected_analyses": [],
                "source": {
                    "kind": "deterministic_synthetic_nonsense_probe",
                    "selection_seed": SELECTION_SEED,
                    "orthography_note": "contains z/v/p outside standard Somali orthography",
                },
            }
        )

    pool_counts = {
        pos: sum(1 for _, candidate_pos in pool if candidate_pos == pos)
        for pos in DEFAULT_QUOTAS
    }
    metadata = {
        "benchmark_version": "v3",
        "source_repository": SOURCE_REPOSITORY,
        "source_commit": SOURCE_COMMIT,
        "selection_seed": SELECTION_SEED,
        "selection_is_analyzer_blind": True,
        "definitions_copied": False,
        "excluded_benchmark": "v2",
        "excluded_v2_positive_surface_count": len(excluded),
        "v2_positive_overlap_count": 0,
        "quotas": dict(quotas),
        "candidate_pool_type_counts": pool_counts,
        "selected_pair_count": sum(quotas.values()),
        "positive_case_count": len(ordered_surfaces),
        "unknown_probe_count": unknown_probe_count,
        "case_count": len(cases),
    }
    return cases, metadata


def serialize_jsonl(cases: Iterable[dict]) -> str:
    return "".join(
        json.dumps(case, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for case in cases
    )


def freeze(*, source_root: Path, output_path: Path, metadata_path: Path, v2_path: Path) -> dict:
    cases, metadata = build_manifest(source_root, v2_path=v2_path)
    content = serialize_jsonl(cases)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    metadata = {**metadata, "manifest_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()}
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--v2", default=V2_MANIFEST_PATH, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    args = parser.parse_args()
    metadata = freeze(
        source_root=args.source_root,
        output_path=args.output,
        metadata_path=args.metadata,
        v2_path=args.v2,
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
