"""Three-way comparison for frozen independent morphology paradigm v5."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _leader(somali: float, giella: float) -> str:
    if somali > giella:
        return "somali_ai"
    if giella > somali:
        return "giellalt"
    return "tie"


def compare(somali_ai: dict, giellalt: dict) -> dict:
    reviewed = somali_ai["reviewed"]["score"]
    master = somali_ai["master"]["score"]
    giella = giellalt["score"]
    overlap = somali_ai["pre_freeze_overlap"]

    expected_surface_count = overlap["positive_unique_surface_count"]
    if master["positive_unique_surface_count"] != expected_surface_count:
        raise ValueError("Somali master denominator differs from v5 overlap denominator")
    if giella["positive_unique_surface_count"] != expected_surface_count:
        raise ValueError("GiellaLT denominator differs from frozen v5 denominator")

    unseen = {surface.casefold() for surface in overlap["master_unseen_surfaces"]}
    raw = giellalt.get("raw_analyses_by_surface", {})
    giella_unseen_recognized = sum(bool(raw.get(surface, ())) for surface in unseen)

    metrics = {
        "exact_surface_recognition": {
            "somali_ai_master": master["recognition_rate"],
            "giellalt": giella["recognition_rate"],
            "leader": _leader(master["recognition_rate"], giella["recognition_rate"]),
        },
        "lemma_recall": {
            "somali_ai_master": master["lemma_recall"],
            "giellalt": giella["lemma_recall"],
            "leader": _leader(master["lemma_recall"], giella["lemma_recall"]),
        },
        "pos_recall": {
            "somali_ai_master": master["pos_recall"],
            "giellalt": giella["pos_recall"],
            "leader": _leader(master["pos_recall"], giella["pos_recall"]),
        },
        "deep_comparable_feature_recall": {
            "somali_ai_reviewed": reviewed["deep_feature_recall"],
            "giellalt": giella["comparable_feature_recall"],
            "leader": _leader(reviewed["deep_feature_recall"], giella["comparable_feature_recall"]),
            "note": "Master recognition is not credited with person/tense/mood detail it does not expose; Somali AI deep analysis comes from the reviewed morphology layer.",
        },
        "syncretic_person_ambiguity_preservation": {
            "somali_ai_reviewed": reviewed["ambiguity_preservation_rate"],
            "giellalt": giella["ambiguity_preservation_rate"],
            "leader": _leader(reviewed["ambiguity_preservation_rate"], giella["ambiguity_preservation_rate"]),
        },
        "unknown_safety": {
            "somali_ai_reviewed": reviewed["unknown_safety_rate"],
            "somali_ai_master": master["unknown_safety_rate"],
            "giellalt": giella["unknown_safety_rate"],
            "leader": "tie" if reviewed["unknown_safety_rate"] == master["unknown_safety_rate"] == giella["unknown_safety_rate"] else "mixed",
        },
    }

    return {
        "benchmark_version": "v5",
        "source_family": somali_ai["benchmark"]["source_family"],
        "frozen_manifest_git_blob_sha": somali_ai["benchmark"]["manifest_git_blob_sha"],
        "pre_freeze_runtime_commit": somali_ai["benchmark"]["pre_freeze_runtime_commit"],
        "metrics": metrics,
        "master_unseen_subset": {
            "surface_count": len(unseen),
            "somali_ai_master_recognized_count": 0,
            "giellalt_recognized_count": giella_unseen_recognized,
            "giellalt_recognition_rate": giella_unseen_recognized / len(unseen) if unseen else 1.0,
            "interpretation": "This is the cleanest v5 breadth/generalization slice because these surfaces were absent from Somali AI master recognition before the benchmark freeze.",
        },
        "generation": {
            "somali_ai_runtime_generator_evaluated": False,
            "giellalt": giellalt.get("generation", {}),
            "leader_declared": False,
            "reason": "Somali AI does not yet expose a directly comparable general lemma+feature generator; GiellaLT generation is measured diagnostically but not used for a head-to-head win claim yet.",
        },
        "global_winner_declared": False,
        "why_no_global_winner": "v5 reports separate breadth, analysis-detail, ambiguity, safety, and diagnostic generation metrics; no principled composite weighting has been defined.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--somali-ai", required=True, type=Path)
    parser.add_argument("--giellalt", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(_load(args.somali_ai), _load(args.giellalt)), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
