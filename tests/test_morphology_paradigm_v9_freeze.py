from __future__ import annotations

import json
from pathlib import Path

from src.morphophonology_generator import (
    eligible_conj2_profile_lemmas,
    eligible_profile_lemmas,
)

MANIFEST = Path("data/qa/morphology_paradigm_benchmark_v9.jsonl")
META = Path("data/qa/morphology_paradigm_benchmark_v9.meta.json")


def _rows() -> list[dict]:
    return [
        json.loads(line)
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_v9_manifest_is_frozen_to_seven_explicit_infinitives_and_eight_safety_probes() -> None:
    rows = _rows()
    positives = [row for row in rows if row.get("benchmark_role") == "positive"]
    unknowns = [row for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(rows) == 15
    assert len(positives) == 7
    assert len(unknowns) == 8
    assert len({row["surface"] for row in positives}) == 7
    assert {row["surface"] for row in positives} == {
        "cafin",
        "cafiyi",
        "laylin",
        "layliyi",
        "caddayn",
        "cashayn",
        "malayn",
    }
    assert all(row.get("part_of_speech") == "verb" for row in positives)
    assert all(row.get("form") == "infinitive" for row in positives)
    assert {row.get("conjugation") for row in positives} == {"2A", "2B"}


def test_v9_uses_only_fayruus_pages_52_53_and_marks_answers_evaluation_only() -> None:
    rows = _rows()
    positives = [row for row in rows if row.get("benchmark_role") == "positive"]
    meta = json.loads(META.read_text(encoding="utf-8"))

    assert {row.get("source_page") for row in positives} == {"52", "53"}
    assert all(
        row.get("source_family") == "Fayruus 2015 Isrogrogidda Falka Af-soomaaliga"
        for row in positives
    )
    assert meta["benchmark_version"] == "v9"
    assert meta["positive_case_count"] == 7
    assert meta["unknown_case_count"] == 8
    assert meta["benchmark_policy"]["answers_are_evaluation_only"] is True
    assert meta["benchmark_policy"]["runtime_rule_learning_from_v9_allowed"] is False
    assert meta["benchmark_policy"]["explicit_source_forms_only"] is True
    assert meta["benchmark_policy"]["inferred_unattested_forms_included"] is False
    assert meta["benchmark_policy"]["synthetic_unknowns_are_claimed_somali_forms"] is False


def test_v9_positive_lemmas_are_disjoint_from_current_finite_development_profiles() -> None:
    positive_lemmas = {
        str(row["lemma"]).casefold()
        for row in _rows()
        if row.get("benchmark_role") == "positive"
    }
    development = {
        value.casefold()
        for value in (*eligible_profile_lemmas(), *eligible_conj2_profile_lemmas())
    }

    assert positive_lemmas == {"cafi", "layli", "caddee", "cashee", "malee"}
    # The development inventory is expected to grow after the freeze. The
    # permanent holdout guard is disjointness: no v9 answer lemma may become a
    # finite runtime development profile.
    assert positive_lemmas.isdisjoint(development)


def test_v9_unknowns_are_distinct_synthetic_safety_strings() -> None:
    rows = _rows()
    positives = {row["surface"] for row in rows if row.get("benchmark_role") == "positive"}
    unknowns = [row["surface"] for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(unknowns) == len(set(unknowns)) == 8
    assert positives.isdisjoint(unknowns)
