from __future__ import annotations

import json
from pathlib import Path

from src.morphology_analysis import analyze_morphology
from src.morphology_class_lexicon import reviewed_class_entry
from src.morphophonology_conj2_class_past import generate_class_authorized_conj2_past
from src.morphophonology_generator import eligible_conj2_profile_lemmas

MANIFEST = Path("data/qa/morphology_paradigm_benchmark_v14.jsonl")
META = Path("data/qa/morphology_paradigm_benchmark_v14.meta.json")
REGISTRY = Path("data/qa/morphology_paradigm_v14_target_registry.json")


def _rows() -> list[dict]:
    return [
        json.loads(line)
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _meta() -> dict:
    return json.loads(META.read_text(encoding="utf-8"))


def _registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_v14_manifest_scores_only_independently_attested_buufi_surface() -> None:
    rows = _rows()
    positives = [row for row in rows if row.get("benchmark_role") == "positive"]
    unknowns = [row for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(rows) == 9
    assert len(positives) == 1
    assert len(unknowns) == 8
    assert positives[0]["id"] == "V14-BUUFI-PST-2PL"
    assert positives[0]["surface"] == "buufiseen"
    assert positives[0]["lemma"] == "buufi"
    assert positives[0]["part_of_speech"] == "verb"
    assert positives[0]["conjugation"] == "2A"
    assert positives[0]["tense_aspect"] == "past"
    assert positives[0]["person"] == "2pl"
    assert positives[0]["feature_scope"] == [
        "lemma",
        "part_of_speech",
        "conjugation",
        "tense_aspect",
        "person",
    ]


def test_v14_target_registry_proves_selection_predated_answer_lookup() -> None:
    registry = _registry()

    assert registry["status"] == "pre_answer_target_registry"
    assert registry["target_lemmas"] == ["buufi", "caafi"]
    assert registry["target_tense_aspect"] == "past"
    assert registry["target_person"] == "2pl"
    assert registry["answer_surfaces_recorded"] is False
    assert registry["answer_source_search_started"] is False
    assert registry["pre_answer_state"]["generic_2pl_past_activation_exists"] is False
    assert registry["benchmark_policy"]["inferred_unattested_forms_allowed"] is False


def test_v14_metadata_records_partial_attestation_without_guessing_caafi() -> None:
    meta = _meta()

    assert meta["benchmark_version"] == "v14"
    assert meta["manifest_git_blob_sha"] == "67786024c209abed20388bf47a6287b3d99efcd7"
    assert meta["freeze_commit"] == "pending_merge"
    assert meta["freeze_status"] == "candidate"
    assert meta["measurement_status"] == "not_measured"
    assert meta["pre_answer_target_registry_merge_commit"] == (
        "107b733021e27b8da6ba1470e76946d0b7181a78"
    )
    assert meta["selected_target_lemmas"] == ["buufi", "caafi"]
    assert meta["scored_target_lemmas"] == ["buufi"]
    assert meta["unresolved_target_lemmas"] == ["caafi"]
    assert meta["positive_case_count"] == 1
    assert meta["unknown_case_count"] == 8

    unresolved = meta["unresolved_targets"]
    assert len(unresolved) == 1
    assert unresolved[0]["lemma"] == "caafi"
    assert unresolved[0]["status"] == "unresolved_not_scored"
    assert "No surface is inferred" in unresolved[0]["reason"]

    verification = meta["answer_sources"][0]["verification"]
    assert verification["pdf_text_layer_verified"] is True
    assert verification["web_screenshot_attempted"] is True
    assert verification["web_screenshot_succeeded"] is False
    assert verification["visual_screenshot_claimed"] is False

    policy = meta["benchmark_policy"]
    assert policy["answers_are_evaluation_only"] is True
    assert policy["runtime_rule_learning_from_v14_allowed"] is False
    assert policy["unresolved_targets_may_not_be_guessed"] is True
    assert policy[
        "future_generic_2pl_past_improvement_allowed_from_independent_development_evidence"
    ] is True


def test_v14_pre_freeze_runtime_really_has_no_generic_2pl_past() -> None:
    meta = _meta()
    state = meta["pre_freeze_runtime_state"]

    assert state["authorized_class_past_persons"] == ["3pl"]
    assert state["generic_2pl_past_authorized"] is False
    assert generate_class_authorized_conj2_past("buufi", "2pl") is None
    assert generate_class_authorized_conj2_past("caafi", "2pl") is None
    assert analyze_morphology("buufiseen") == ()


def test_v14_targets_are_longstanding_class_entries_not_special_profiles() -> None:
    profiles = set(eligible_conj2_profile_lemmas())

    for lemma in ("buufi", "caafi"):
        entry = reviewed_class_entry(lemma)
        assert entry is not None
        assert entry.part_of_speech == "verb"
        assert entry.conjugation_class == "2A"
        assert entry.status == "reviewed_class_only"
        assert entry.generation_enabled is False
        assert entry.correction_allowed is False
        assert lemma not in profiles


def test_v14_unknowns_are_synthetic_distinct_and_safe_at_freeze() -> None:
    rows = _rows()
    positives = {row["surface"] for row in rows if row.get("benchmark_role") == "positive"}
    unknowns = [row["surface"] for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(unknowns) == len(set(unknowns)) == 8
    assert positives.isdisjoint(unknowns)
    assert all("q" in surface or "v" in surface or "z" in surface for surface in unknowns)
    for surface in unknowns:
        assert analyze_morphology(surface) == ()
