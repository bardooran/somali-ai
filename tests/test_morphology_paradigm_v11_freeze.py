from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from src.morphology_analysis import analyze_morphology
from src.morphology_class_lexicon import reviewed_class_entry
from src.morphophonology_generator import eligible_conj2_profile_lemmas, generate_conj2_present

MANIFEST = Path("data/qa/morphology_paradigm_benchmark_v11.jsonl")
META = Path("data/qa/morphology_paradigm_benchmark_v11.meta.json")


def _rows() -> list[dict]:
    return [
        json.loads(line)
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_v11_manifest_is_frozen_to_one_full_preauthorized_c2a_present_paradigm() -> None:
    rows = _rows()
    positives = [row for row in rows if row.get("benchmark_role") == "positive"]
    unknowns = [row for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(rows) == 15
    assert len(positives) == 7
    assert len(unknowns) == 8
    assert len({row["surface"] for row in positives}) == 5
    assert {row["lemma"] for row in positives} == {"buubi"}
    assert all(row.get("part_of_speech") == "verb" for row in positives)
    assert all(row.get("conjugation") == "2A" for row in positives)
    assert all(row.get("tense_aspect") == "present" for row in positives)
    assert all(row.get("mood") == "indicative" for row in positives)


def test_v11_preserves_green_table_48_person_syncretism() -> None:
    positives = [row for row in _rows() if row.get("benchmark_role") == "positive"]
    persons_by_surface: dict[str, set[str]] = defaultdict(set)
    for row in positives:
        persons_by_surface[str(row["surface"])].add(str(row["person"]))

    assert persons_by_surface["buubiyaa"] == {"1sg", "3sg_m"}
    assert persons_by_surface["buubisaa"] == {"2sg", "3sg_f"}
    assert persons_by_surface["buubinnaa"] == {"1pl"}
    assert persons_by_surface["buubisaan"] == {"2pl"}
    assert persons_by_surface["buubiyaan"] == {"3pl"}


def test_v11_answer_source_and_evaluation_only_policy_are_locked() -> None:
    positives = [row for row in _rows() if row.get("benchmark_role") == "positive"]
    meta = json.loads(META.read_text(encoding="utf-8"))

    assert {row.get("source_family") for row in positives} == {"Green 2021 Somali Grammar"}
    assert {row.get("source_page") for row in positives} == {"166"}
    assert {row.get("source_table") for row in positives} == {"48"}

    assert meta["benchmark_version"] == "v11"
    assert meta["freeze_commit"] == "pending_merge"
    assert meta["pre_freeze_class_authorization_commit"] == "b7c57eeadc02282d3830bbf80399ea418917d6ea"
    assert meta["positive_case_count"] == 7
    assert meta["positive_unique_surface_count"] == 5
    assert meta["syncretic_surface_count"] == 2
    assert meta["unknown_case_count"] == 8
    assert meta["measurement_status"] == "pending_measurement"

    policy = meta["benchmark_policy"]
    assert policy["answers_are_evaluation_only"] is True
    assert policy["runtime_rule_learning_from_v11_allowed"] is False
    assert policy["explicit_source_forms_only"] is True
    assert policy["inferred_unattested_forms_included"] is False
    assert policy["synthetic_unknowns_are_claimed_somali_forms"] is False
    assert policy["pre_freeze_class_authorization_allowed"] is True
    assert policy["pre_freeze_surface_generation_for_target_enabled"] is False
    assert policy["post_freeze_activation_of_preexisting_general_rules_allowed"] is True
    assert policy["v11_answer_rows_may_authorize_special_case_runtime_forms"] is False

    assert meta["experimental_design"]["class_authorization_source_distinct_from_answer_source"] is True
    assert meta["experimental_design"]["class_authorization_predates_answer_freeze"] is True
    assert meta["independence_limits"]["fully_independent_of_all_runtime_source_authors"] is False
    assert meta["independence_limits"]["answer_source_independent_of_class_authorization_source"] is True


def test_v11_target_class_was_known_before_freeze_but_had_zero_surface_generation_authority() -> None:
    entry = reviewed_class_entry("buubi")
    assert entry is not None
    assert entry.part_of_speech == "verb"
    assert entry.conjugation_class == "2A"
    assert entry.status == "reviewed_class_only"
    assert entry.generation_enabled is False
    assert entry.correction_allowed is False
    assert "buubi" not in {lemma.casefold() for lemma in eligible_conj2_profile_lemmas()}

    persons = ("1sg", "2sg", "3sg_m", "3sg_f", "1pl", "2pl", "3pl")
    for person in persons:
        assert generate_conj2_present("buubi", person) is None

    for surface in {row["surface"] for row in _rows() if row.get("benchmark_role") == "positive"}:
        assert not any(
            item.lemma == "buubi" and item.authority == "reviewed_rule_derived"
            for item in analyze_morphology(str(surface))
        )


def test_v11_unknowns_are_distinct_synthetic_safety_strings() -> None:
    rows = _rows()
    positives = {row["surface"] for row in rows if row.get("benchmark_role") == "positive"}
    unknowns = [row["surface"] for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(unknowns) == len(set(unknowns)) == 8
    assert positives.isdisjoint(unknowns)
    assert all("z" in surface or "q" in surface or "v" in surface for surface in unknowns)
