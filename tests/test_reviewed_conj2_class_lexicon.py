from __future__ import annotations

import json
from pathlib import Path

from src.morphology_class_lexicon import reviewed_class_entries, reviewed_class_entry, reviewed_class_lemmas
from src.morphophonology_generator import generate_conj2_present

BENCHMARKS = tuple(
    Path(f"data/qa/morphology_paradigm_benchmark_v{version}.jsonl")
    for version in range(5, 11)
)

EXPECTED_CLASS_ONLY = {
    "bushi",
    "butaaci",
    "buubi",
    "buufi",
    "buuxi",
    "caafi",
    "caajisi",
}


def _positive_lemmas(path: Path) -> set[str]:
    result: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("benchmark_role") == "positive" and row.get("lemma"):
            result.add(str(row["lemma"]).casefold())
    return result


def test_reviewed_class_lexicon_is_class_only_and_explicitly_c2a() -> None:
    entries = reviewed_class_entries()
    assert {entry.lemma for entry in entries} == EXPECTED_CLASS_ONLY
    assert reviewed_class_lemmas("2A") == tuple(sorted(EXPECTED_CLASS_ONLY))

    for entry in entries:
        assert entry.part_of_speech == "verb"
        assert entry.conjugation_class == "2A"
        assert entry.status == "reviewed_class_only"
        assert entry.generation_enabled is False
        assert entry.correction_allowed is False
        assert entry.source_label.startswith("v2a")


def test_class_only_lookup_does_not_guess_unknown_lemmas() -> None:
    assert reviewed_class_entry("buubi") is not None
    assert reviewed_class_entry("BUUBI") is not None
    assert reviewed_class_entry("buubizz") is None
    assert reviewed_class_entry("nadiifi") is None
    assert reviewed_class_entry("qurxi") is None


def test_class_only_lemmas_are_disjoint_from_all_frozen_v5_to_v10_positive_lemmas() -> None:
    development = {lemma.casefold() for lemma in reviewed_class_lemmas()}
    for benchmark in BENCHMARKS:
        assert development.isdisjoint(_positive_lemmas(benchmark))


def test_class_lexicon_itself_does_not_turn_entries_into_explicit_profiles() -> None:
    # The original finite-profile API remains profile-only. Generic class activation
    # is a separate authority path and must not rewrite this historical class registry.
    for lemma in reviewed_class_lemmas():
        for person in ("1sg", "2sg", "3sg_m", "3sg_f", "1pl", "2pl", "3pl"):
            assert generate_conj2_present(lemma, person) is None

    for entry in reviewed_class_entries():
        assert entry.generation_enabled is False
        assert entry.status == "reviewed_class_only"
        assert entry.correction_allowed is False
