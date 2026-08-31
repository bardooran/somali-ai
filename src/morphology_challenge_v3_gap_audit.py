"""Diagnostic-only source audit for frozen morphology challenge v3 gaps.

This module is intentionally evaluation/research code. It may inspect the
frozen benchmark labels to explain misses, but it never writes runtime data,
never promotes a record, and never treats corpus occurrence as correctness.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from .master_recognition import recognize_form
from .morphology_challenge_v3 import MANIFEST_PATH, TARGET_TYPES, expected_types, load_cases

GIELLALT_CANDIDATES_PATH = Path("data/imported/giellalt/lexical_candidates.jsonl")
TIER_A_USAGE_PATHS = (
    Path("data/usage/external/wikipedia_usage_candidates.jsonl"),
    Path("data/usage/external/xlsum_usage_candidates.jsonl"),
)


def _load_jsonl(path: Path) -> tuple[dict, ...]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                value = json.loads(text)
                if not isinstance(value, dict):
                    raise ValueError(f"{path} contains a non-object row")
                rows.append(value)
    return tuple(rows)


def _giellalt_index(path: Path = GIELLALT_CANDIDATES_PATH) -> dict[str, set[str]]:
    result: dict[str, set[str]] = defaultdict(set)
    for row in _load_jsonl(path):
        lemma = str(row.get("lemma", "")).strip().casefold()
        part_of_speech = str(row.get("record_type", "")).strip().casefold()
        if lemma and part_of_speech in TARGET_TYPES:
            result[lemma].add(part_of_speech)
    return dict(result)


def _usage_rows(paths: tuple[Path, ...] = TIER_A_USAGE_PATHS) -> tuple[dict, ...]:
    rows: list[dict] = []
    for path in paths:
        rows.extend(_load_jsonl(path))
    return tuple(rows)


def _usage_attestations(surface: str, rows: tuple[dict, ...]) -> tuple[int, list[str]]:
    pattern = re.compile(rf"(?<!\w){re.escape(surface)}(?!\w)", re.IGNORECASE)
    count = 0
    sources: set[str] = set()
    for row in rows:
        text = str(row.get("text", ""))
        hits = len(pattern.findall(text))
        if hits:
            count += hits
            sources.add(str(row.get("source", "unknown")))
    return count, sorted(sources)


def audit(path: Path = MANIFEST_PATH) -> dict:
    giellalt = _giellalt_index()
    usage = _usage_rows()
    rows: list[dict] = []
    state_counts: Counter[str] = Counter()
    pos_state_counts: dict[str, Counter[str]] = defaultdict(Counter)

    positives = tuple(case for case in load_cases(path) if case["split"] == "challenge")
    for case in positives:
        surface = str(case["surface"])
        key = surface.casefold()
        expected = expected_types(case)
        master = recognize_form(surface)
        master_types = {
            str(item.part_of_speech).casefold().strip()
            for item in master
            if item.part_of_speech and str(item.part_of_speech).casefold().strip() in TARGET_TYPES
        }
        master_confidence = sorted({item.confidence_tier for item in master})
        master_source_ids = sorted({source for item in master for source in item.source_ids})
        giellalt_types = sorted(giellalt.get(key, set()))
        usage_count, usage_sources = _usage_attestations(surface, usage)

        if master and expected <= master_types:
            state = "covered_expected_type"
        elif master:
            state = "master_type_mismatch"
        elif giellalt_types:
            state = "master_missing_cross_source_candidate"
        elif usage_count:
            state = "master_missing_tier_a_attested"
        else:
            state = "master_missing_benchmark_source_only"

        state_counts[state] += 1
        for part_of_speech in expected:
            pos_state_counts[part_of_speech][state] += 1

        rows.append(
            {
                "case_id": case["id"],
                "surface": surface,
                "expected_types": sorted(expected),
                "benchmark_label_role": "evaluation_only",
                "master_recognized": bool(master),
                "master_types": sorted(master_types),
                "master_confidence_tiers": master_confidence,
                "master_source_ids": master_source_ids,
                "giellalt_candidate_present": bool(giellalt_types),
                "giellalt_candidate_types": giellalt_types,
                "tier_a_usage_occurrence_count": usage_count,
                "tier_a_usage_sources": usage_sources,
                "diagnostic_state": state,
                "automatic_promotion_allowed": False,
                "correctness_inference_from_usage_allowed": False,
            }
        )

    return {
        "benchmark_version": "v3",
        "benchmark_manifest_sha256": "7222ef7a4e4f0c9b960b5feece50aaba11737dc7f3265040cfdac6a3e99ffd6c",
        "positive_case_count": len(positives),
        "diagnostic_state_counts": dict(sorted(state_counts.items())),
        "per_pos_state_counts": {
            pos: dict(sorted(counts.items())) for pos, counts in sorted(pos_state_counts.items())
        },
        "records": rows,
        "safety": {
            "diagnostic_only": True,
            "writes_runtime_data": False,
            "automatic_promotion_allowed": False,
            "benchmark_labels_feed_runtime": False,
            "tier_a_occurrence_proves_correctness": False,
            "giellalt_candidate_proves_correctness": False,
        },
    }


def main() -> int:
    print(json.dumps(audit(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
