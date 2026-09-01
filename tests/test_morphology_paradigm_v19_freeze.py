from __future__ import annotations

import hashlib
import json
from pathlib import Path

from src.morphology_paradigm_v19 import report
from src.morphophonology_generator import eligible_conj2_profile_lemmas

BENCHMARK = Path("data/qa/morphology_paradigm_benchmark_v19.jsonl")
METADATA = Path("data/qa/morphology_paradigm_benchmark_v19.meta.json")
REGISTRY = Path("data/qa/morphology_paradigm_v19_target_registry.json")


def _rows() -> tuple[dict, ...]:
    return tuple(
        json.loads(line)
        for line in BENCHMARK.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def _git_blob_sha(path: Path) -> str:
    content = path.read_bytes()
    payload = f"blob {len(content)}\0".encode() + content
    return hashlib.sha1(payload).hexdigest()


def test_v19_manifest_is_frozen_to_two_attested_3sg_f_rows_and_eight_unknowns() -> None:
    rows = _rows()
    positives = [row for row in rows if row["benchmark_role"] == "positive"]
    unknowns = [row for row in rows if row["benchmark_role"] == "unknown"]

    assert [(row["lemma"], row["surface"], row["person"]) for row in positives] == [
        ("caafi", "caafisay", "3sg_f"),
        ("bushi", "bushisay", "3sg_f"),
    ]
    assert all(row["conjugation"] == "2A" for row in positives)
    assert all(row["tense_aspect"] == "past" for row in positives)
    assert all(row["feature_scope"] == [
        "lemma",
        "part_of_speech",
        "conjugation",
        "tense_aspect",
        "person",
    ] for row in positives)
    assert len(unknowns) == 8
    assert len({row["surface"] for row in unknowns}) == 8


def test_v19_metadata_pins_manifest_and_pre_freeze_scope_historically() -> None:
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))

    assert metadata["benchmark_version"] == "v19"
    assert metadata["manifest_git_blob_sha"] == _git_blob_sha(BENCHMARK)
    assert metadata["pre_answer_target_registry_merge_commit"] == (
        "bcf86d494a0fbd62096df982868f714521670e41"
    )
    assert metadata["selected_target_lemmas"] == ["caafi", "bushi"]
    assert metadata["scored_target_lemmas"] == ["caafi", "bushi"]
    assert metadata["unresolved_target_lemmas"] == []
    assert metadata["positive_case_count"] == 2
    assert metadata["unknown_case_count"] == 8

    state = metadata["pre_freeze_runtime_state"]
    assert state["authorized_class_past_persons"] == [
        "1sg",
        "1pl",
        "2sg",
        "2pl",
        "3sg_m",
        "3pl",
    ]
    assert state["generic_3sg_feminine_past_authorized"] is False
    assert state["existing_2sg_3sg_feminine_syncretism_documented"] is True
    assert state["existing_2sg_surface_generation_authorized"] is True


def test_v19_answer_evidence_is_lexicographic_and_runtime_isolation_is_explicit() -> None:
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    sources = metadata["answer_sources"]

    assert [(item["target_lemma"], item["surface"]) for item in sources] == [
        ("caafi", "caafisay"),
        ("bushi", "bushisay"),
    ]
    assert all("(-iyay, -isay)" in item["attested_entry"] for item in sources)
    assert all(
        item["evidence_type"]
        == "lemma_specific_dictionary_principal_part_with_dictionary_grammar_resolution"
        for item in sources
    )

    policy = metadata["benchmark_policy"]
    assert policy["answers_are_evaluation_only"] is True
    assert policy["runtime_rule_learning_from_v19_allowed"] is False
    assert policy["answer_sources_may_not_authorize_special_case_runtime_forms"] is True
    assert policy["inferred_unattested_surfaces_included"] is False
    assert policy["syncretic_person_values_must_be_preserved"] is True
    assert policy[
        "surface_recognition_must_not_be_equated_with_3sg_feminine_person_resolution"
    ] is True
    assert policy[
        "development_rule_authority_must_be_independent_of_v19_answer_sources"
    ] is True


def test_v19_registry_proves_targets_were_fixed_without_answers() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    assert registry["status"] == "pre_answer_target_registry"
    assert registry["target_lemmas"] == ["caafi", "bushi"]
    assert registry["answer_surfaces_recorded"] is False
    assert registry["answer_source_search_started"] is False
    assert "answer_surfaces" not in registry
    assert "expected_surfaces" not in registry


def test_v19_targets_remain_outside_target_specific_profile_path() -> None:
    profiles = set(eligible_conj2_profile_lemmas())
    assert "caafi" not in profiles
    assert "bushi" not in profiles


def test_v19_scorer_separates_recognition_person_resolution_and_syncretism() -> None:
    result = report()
    combined = result["combined"]
    diagnostics = combined["syncretism_diagnostics"]

    assert combined["positive_row_count"] == 2
    assert combined["positive_unique_surface_count"] == 2
    assert combined["unknown_count"] == 8
    assert combined["unknown_rejected_count"] == 8
    assert diagnostics["expected_persons"] == ["2sg", "3sg_f"]
    assert diagnostics["syncretic_surface_count"] == 2
    # 2SG is already a reviewed class-level past cell before v19 and shares the
    # same surface shape; future 3SG-f activation must add, not replace, it.
    assert diagnostics["surface_has_2sg_analysis_count"] == 2
    assert result["interpretation"]["surface_recognition_is_not_person_resolution"] is True
    assert result["interpretation"]["syncretism_with_2sg_is_expected"] is True
