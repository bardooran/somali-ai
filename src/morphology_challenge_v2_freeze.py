"""Freeze the source-independent morphology challenge v2.

This module MUST NOT import or call Somali AI morphology analyzers or GiellaLT.
It selects cases only from the pinned Qaamuus source plus deterministic synthetic
unknown probes. The resulting JSONL is intended to be committed before either
runtime is evaluated on it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable

SOURCE_REPOSITORY = "bardooran/goobolabs"
SOURCE_COMMIT = "737cf848bfa8291d5580f5c34db04daef858c955"
SELECTION_SEED = "somali-ai-morphology-challenge-v2-2026-08-31"
DEFAULT_QUOTAS = {
    "noun": 48,
    "verb": 48,
    "adjective": 16,
    "numeral": 8,
}
UNKNOWN_PROBE_COUNT = 16

ENTRY_RE = re.compile(r"^- \*\*(?P<headword>.+?)\*\*\s+(?P<code>\S+)")
SINGLE_TOKEN_RE = re.compile(r"^[A-Za-z][A-Za-z'\-]{0,23}$")
SUPERSCRIPT_DIGITS = str.maketrans("", "", "⁰¹²³⁴⁵⁶⁷⁸⁹")
SOMALI_LETTERS = "abcdeghijklmnopqrstuwxy"


def normalize_surface(headword: str) -> str:
    value = headword.translate(SUPERSCRIPT_DIGITS).strip()
    value = value.replace("’", "'").replace("‘", "'")
    return value.casefold()


def coarse_pos(code: str) -> str | None:
    token = code.casefold().strip()
    segments = set(re.split(r"[./]", token))
    # Qaamuus numerals are commonly encoded inside a nominal code, e.g. m.l.t.
    # The explicit tiraale marker therefore takes precedence for this challenge.
    if "t" in segments:
        return "numeral"
    if token == "m" or token.startswith("m."):
        return "noun"
    if token == "f" or token.startswith("f."):
        return "verb"
    if token == "s" or token.startswith("s."):
        return "adjective"
    return None


def selection_hash(surface: str, pos: str) -> str:
    payload = f"{SELECTION_SEED}\0{pos}\0{surface}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def iter_source_entries(source_root: Path) -> Iterable[dict]:
    for path in sorted(source_root.glob("[0-9][0-9]-*.md")):
        if path.name.startswith("00-"):
            continue
        relative_path = f"resources/qaamuus/{path.name}"
        with path.open("r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                match = ENTRY_RE.match(raw_line.rstrip("\n"))
                if not match:
                    continue
                surface = normalize_surface(match.group("headword"))
                pos = coarse_pos(match.group("code"))
                if pos is None or not SINGLE_TOKEN_RE.fullmatch(surface):
                    continue
                yield {
                    "surface": surface,
                    "part_of_speech": pos,
                    "source_code": match.group("code"),
                    "source_path": relative_path,
                    "source_line": line_number,
                }


def source_pool(source_root: Path) -> dict[tuple[str, str], list[dict]]:
    pool: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for entry in iter_source_entries(source_root):
        key = (entry["surface"], entry["part_of_speech"])
        pool[key].append(
            {
                "source_path": entry["source_path"],
                "source_line": entry["source_line"],
                "source_code": entry["source_code"],
            }
        )
    return dict(pool)


def select_pairs(
    pool: dict[tuple[str, str], list[dict]],
    quotas: dict[str, int] = DEFAULT_QUOTAS,
) -> tuple[tuple[str, str, str], ...]:
    selected: list[tuple[str, str, str]] = []
    for pos, quota in quotas.items():
        candidates = [
            (selection_hash(surface, candidate_pos), surface, candidate_pos)
            for surface, candidate_pos in pool
            if candidate_pos == pos
        ]
        candidates.sort()
        if len(candidates) < quota:
            raise ValueError(
                f"not enough {pos} candidates: need {quota}, found {len(candidates)}"
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
        # p/v/z are outside standard Somali orthography, making these explicit
        # nonsense safety probes rather than claims that an unattested Somali-like
        # form is ungrammatical.
        surface = f"pvz{tail}"
        if surface not in occupied:
            return surface
        counter += 1


def build_manifest(
    source_root: Path,
    quotas: dict[str, int] = DEFAULT_QUOTAS,
    unknown_probe_count: int = UNKNOWN_PROBE_COUNT,
) -> tuple[list[dict], dict]:
    pool = source_pool(source_root)
    selected_pairs = select_pairs(pool, quotas)

    selected_by_surface: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for surface, pos, digest in selected_pairs:
        selected_by_surface[surface].append((pos, digest))

    ordered_surfaces = sorted(
        selected_by_surface,
        key=lambda surface: min(digest for _, digest in selected_by_surface[surface]),
    )

    cases: list[dict] = []
    for index, surface in enumerate(ordered_surfaces, start=1):
        selected = sorted(selected_by_surface[surface])
        expected_types = [pos for pos, _ in selected]
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
                "id": f"MCV2-{index:04d}",
                "benchmark_version": "v2",
                "split": "challenge",
                "surface": surface,
                "expected_unknown": False,
                "expected_analyses": [
                    {
                        "lemma": surface,
                        "features": {"part_of_speech": pos},
                    }
                    for pos in expected_types
                ],
                "source": {
                    "repository": SOURCE_REPOSITORY,
                    "commit": SOURCE_COMMIT,
                    "selection_seed": SELECTION_SEED,
                    "provenance": provenance,
                },
            }
        )

    occupied = {surface for surface, _ in pool}
    for unknown_index in range(1, unknown_probe_count + 1):
        surface = synthetic_unknown(unknown_index, occupied)
        cases.append(
            {
                "id": f"MCV2-U{unknown_index:03d}",
                "benchmark_version": "v2",
                "split": "unknown",
                "surface": surface,
                "expected_unknown": True,
                "expected_analyses": [],
                "source": {
                    "kind": "deterministic_synthetic_nonsense_probe",
                    "selection_seed": SELECTION_SEED,
                    "orthography_note": "contains p/v/z outside standard Somali orthography",
                },
            }
        )

    pool_counts = {
        pos: sum(1 for _, candidate_pos in pool if candidate_pos == pos)
        for pos in DEFAULT_QUOTAS
    }
    metadata = {
        "benchmark_version": "v2",
        "source_repository": SOURCE_REPOSITORY,
        "source_commit": SOURCE_COMMIT,
        "selection_seed": SELECTION_SEED,
        "selection_is_analyzer_blind": True,
        "definitions_copied": False,
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


def freeze(
    *,
    source_root: Path,
    output_path: Path,
    metadata_path: Path,
) -> dict:
    cases, metadata = build_manifest(source_root)
    content = serialize_jsonl(cases)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    metadata = {
        **metadata,
        "manifest_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
    }
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    args = parser.parse_args()
    metadata = freeze(
        source_root=args.source_root,
        output_path=args.output,
        metadata_path=args.metadata,
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
