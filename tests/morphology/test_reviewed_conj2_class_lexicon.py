from __future__ import annotations

import json
from pathlib import Path

from src.morphology_analysis import analyze_morphology
from src.morphology_class_lexicon import reviewed_class_entries, reviewed_class_entry, reviewed_class_lemmas
from src.morphophonology_generator import (
    eligible_conj2_class_activation_lemmas,
    generate_class_authorized_conj2_present,
    generate_conj2_present,
)

BENCHMARKS_V5_TO_V10 = tuple(
    Path(f"data/qa/morphology_paradigm_benchmark_v{version}.jsonl")
    for version in range(5, 11)
)
BENCHMARKS_V5_TO_V11 = BENCHMARKS_V5_TO_V10 + (
    Path("data/qa/morphology_paradigm_benchmark_v11.jsonl"),
)

PRE_V11_CLASS_ONLY = {
    "bushi",
    "butaaci",
    "buubi",
    "buufi",
    "buuxi",
    "caafi",
    "caajisi",
}
STAGE1N_CLASS_ONLY = {
    "aaddi",
    "aammusi",
    "abhi",
    "afceli",
}
EXPECTED_CLASS_ONLY = PRE_V11_CLASS_ONLY | STAGE1N_CLASS_ONLY


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


def test_stage1n_class_only_batch_has_exact_zorc_labels_and_pages() -> None:
    expected = {
        "aaddi": (2, "v2a="),
        "aammusi": (3, "v2a="),
        "abhi": (6, "v2a="),
        "afceli": (10, "v2a=cmp"),
    }
    for lemma, (page, label) in expected.items():
        entry = reviewed_class_entry(lemma)
        assert entry is not None
        assert entry.source_page == page
        assert entry.source_label == label


def test_class_only_lookup_does_not_guess_unknown_lemmas() -> None:
    assert reviewed_class_entry("buubi") is not None
    assert reviewed_class_entry("BUUBI") is not None
    assert reviewed_class_entry("aaddi") is not None
    assert reviewed_class_entry("AADDI") is not None
    assert reviewed_class_entry("buubizz") is None
    assert reviewed_class_entry("nadiifi") is None
    assert reviewed_class_entry("qurxi") is None


def test_pre_v11_class_lemmas_are_disjoint_from_frozen_v5_to_v10() -> None:
    development = {lemma.casefold() for lemma in PRE_V11_CLASS_ONLY}
    for benchmark in BENCHMARKS_V5_TO_V10:
        assert development.isdisjoint(_positive_lemmas(benchmark))


def test_stage1n_batch_is_disjoint_from_every_frozen_v5_to_v11_target() -> None:
    development = {lemma.casefold() for lemma in STAGE1N_CLASS_ONLY}
    for benchmark in BENCHMARKS_V5_TO_V11:
        assert development.isdisjoint(_positive_lemmas(benchmark))


def test_class_lexicon_itself_does_not_turn_entries_into_explicit_profiles() -> None:
    for lemma in reviewed_class_lemmas():
        for person in ("1sg", "2sg", "3sg_m", "3sg_f", "1pl", "2pl", "3pl"):
            assert generate_conj2_present(lemma, person) is None

    for entry in reviewed_class_entries():
        assert entry.generation_enabled is False
        assert entry.status == "reviewed_class_only"
        assert entry.correction_allowed is False


def test_stage1n_batch_is_class_only_but_explicitly_activated_by_separate_policy() -> None:
    activated = set(eligible_conj2_class_activation_lemmas())
    assert activated == EXPECTED_CLASS_ONLY

    for lemma in STAGE1N_CLASS_ONLY:
        entry = reviewed_class_entry(lemma)
        assert entry is not None
        assert entry.generation_enabled is False
        assert entry.status == "reviewed_class_only"
        for person in ("1sg", "2sg", "3sg_m", "3sg_f", "1pl", "2pl", "3pl"):
            candidate = generate_class_authorized_conj2_present(lemma, person)
            assert candidate is not None
            assert candidate.lemma == lemma
            assert candidate.status == "reviewed_rule_derived"
            assert candidate.correction_allowed is False


def test_stage1n_activation_still_rejects_malformed_synthetic_surfaces() -> None:
    probes = (
        "aaddizz",
        "aammusizz",
        "abhizz",
        "afcelizz",
    )
    for surface in probes:
        assert not any(
            item.lemma in STAGE1N_CLASS_ONLY and item.authority == "reviewed_rule_derived"
            for item in analyze_morphology(surface)
        )
