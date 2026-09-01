from __future__ import annotations

import json
from pathlib import Path

from src.morphology_analysis import analyze_morphology
from src.morphology_class_lexicon import reviewed_class_entry
from src.morphophonology_conj2_class_past import (
    CONJ2_CLASS_PAST_ACTIVATION_PATH,
    generate_class_authorized_conj2_past,
)
from src.morphophonology_generator import eligible_conj2_profile_lemmas

MANIFEST = Path("data/qa/morphology_paradigm_benchmark_v15.jsonl")
META = Path("data/qa/morphology_paradigm_benchmark_v15.meta.json")
REGISTRY = Path("data/qa/morphology_paradigm_v15_target_registry.json")


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


def _past_activation() -> dict:
    return json.loads(CONJ2_CLASS_PAST_ACTIVATION_PATH.read_text(encoding="utf-8"))


def test_v15_manifest_scores_only_independently_attested_buuxi_surface() -> None:
    rows = _rows()
    positives = [row for row in rows if row.get("benchmark_role") == "positive"]
    unknowns = [row for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(rows) == 9
    assert len(positives) == 1
    assert len(unknowns) == 8
    assert positives[0]["id"] == "V15-BUUXI-PST-2SG"
    assert positives[0]["surface"] == "buuxisay"
    assert positives[0]["lemma"] == "buuxi"
    assert positives[0]["part_of_speech"] == "verb"
    assert positives[0]["conjugation"] == "2A"
    assert positives[0]["tense_aspect"] == "past"
    assert positives[0]["person"] == "2sg"
    assert positives[0]["feature_scope"] == [
        "lemma",
        "part_of_speech",
        "conjugation",
        "tense_aspect",
        "person",
    ]


def test_v15_target_registry_proves_selection_predated_answer_lookup() -> None:
    registry = _registry()

    assert registry["status"] == "pre_answer_target_registry"
    assert registry["target_lemmas"] == ["buuxi", "caajisi"]
    assert registry["target_tense_aspect"] == "past"
    assert registry["target_person"] == "2sg"
    assert registry["answer_surfaces_recorded"] is False
    assert registry["answer_source_search_started"] is False
    assert registry["pre_answer_state"]["generic_2sg_past_activation_exists"] is False
    assert registry["benchmark_policy"]["inferred_unattested_forms_allowed"] is False
    assert registry["selection_commit_base"] == (
        "ee5422f6864fcf435c94dc2422c2c4bdb5c07ed2"
    )


def test_v15_metadata_records_partial_attestation_without_guessing_caajisi() -> None:
    meta = _meta()

    assert meta["benchmark_version"] == "v15"
    assert meta["manifest_git_blob_sha"] == "0e0170f398c55c30ace8c14c5159052502afd19e"
    assert meta["freeze_commit"] is None
    assert meta["freeze_status"] == "freeze_candidate"
    assert meta["measurement_status"] == "not_measured"
    assert meta["pre_answer_target_registry_merge_commit"] == (
        "fb56031809f9b9e75d4d01aa4e023897f730235a"
    )
    assert meta["selected_target_lemmas"] == ["buuxi", "caajisi"]
    assert meta["scored_target_lemmas"] == ["buuxi"]
    assert meta["unresolved_target_lemmas"] == ["caajisi"]
    assert meta["positive_case_count"] == 1
    assert meta["unknown_case_count"] == 8

    unresolved = meta["unresolved_targets"]
    assert len(unresolved) == 1
    assert unresolved[0]["lemma"] == "caajisi"
    assert unresolved[0]["status"] == "unresolved_not_scored"
    assert "No surface is inferred" in unresolved[0]["reason"]

    source = meta["answer_sources"][0]
    assert source["target_lemma"] == "buuxi"
    assert source["surface"] == "buuxisay"
    assert "Minneapolis" in source["source_family"]
    assert source["verification"] == {
        "pdf_text_layer_verified": True,
        "web_screenshot_attempted": True,
        "web_screenshot_succeeded": False,
        "visual_screenshot_claimed": False,
        "screenshot_failure": "web screenshot endpoint returned a cache miss",
    }
    assert source["independent_corroboration"]["pdf_text_layer_verified"] is True
    assert source["independent_corroboration"]["visual_screenshot_claimed"] is False


def test_v15_freeze_pins_plural_only_class_past_scope_and_2sg_gap() -> None:
    meta = _meta()
    activation = _past_activation()

    assert activation["authorized_persons"] == ["2pl", "3pl"]
    assert set(activation["past_morphology"]) == {"2pl", "3pl"}
    state = meta["pre_freeze_runtime_state"]
    assert state["authorized_class_past_persons"] == ["2pl", "3pl"]
    assert state["generic_2sg_past_authorized"] is False
    assert state["buuxi_2sg_past_available"] is False
    assert state["caajisi_2sg_past_available"] is False

    for lemma in ("buuxi", "caajisi"):
        assert generate_class_authorized_conj2_past(lemma, "2sg") is None
        assert generate_class_authorized_conj2_past(lemma, "2pl") is not None
        assert generate_class_authorized_conj2_past(lemma, "3pl") is not None


def test_v15_targets_remain_class_entries_not_target_specific_profiles() -> None:
    profiles = set(eligible_conj2_profile_lemmas())

    for lemma in ("buuxi", "caajisi"):
        entry = reviewed_class_entry(lemma)
        assert entry is not None
        assert entry.part_of_speech == "verb"
        assert entry.conjugation_class == "2A"
        assert entry.status == "reviewed_class_only"
        assert entry.generation_enabled is False
        assert entry.correction_allowed is False
        assert lemma not in profiles


def test_v15_policy_keeps_answer_evidence_out_of_runtime_authority() -> None:
    policy = _meta()["benchmark_policy"]

    assert policy["answers_are_evaluation_only"] is True
    assert policy["runtime_rule_learning_from_v15_allowed"] is False
    assert policy["answer_sources_may_not_authorize_special_case_runtime_forms"] is True
    assert policy["explicit_source_surfaces_only"] is True
    assert policy["inferred_unattested_surfaces_included"] is False
    assert policy["unresolved_targets_may_not_be_guessed"] is True
    assert policy[
        "future_generic_2sg_past_improvement_allowed_from_independent_development_evidence"
    ] is True
    assert policy[
        "development_rule_authority_must_be_independent_of_v15_answer_sources"
    ] is True


def test_v15_unknowns_are_synthetic_distinct_and_remain_safe() -> None:
    rows = _rows()
    positives = {row["surface"] for row in rows if row.get("benchmark_role") == "positive"}
    unknowns = [row["surface"] for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(unknowns) == len(set(unknowns)) == 8
    assert positives.isdisjoint(unknowns)
    assert all("q" in surface or "v" in surface or "z" in surface for surface in unknowns)
    for surface in unknowns:
        assert analyze_morphology(surface) == ()
