from __future__ import annotations

import json
from pathlib import Path

from src.morphology_class_lexicon import reviewed_class_entry
from src.morphophonology_generator import (
    analyze_morphophonological_surface,
    eligible_conj2_class_activation_lemmas,
    eligible_conj2_profile_lemmas,
    generate_class_authorized_conj2_present,
)

MANIFEST = Path("data/qa/morphology_paradigm_benchmark_v13.jsonl")
META = Path("data/qa/morphology_paradigm_benchmark_v13.meta.json")

TARGETS = {
    "abhi": "abhiyaa",
    "afceli": "afceliyeen",
}


def _rows() -> list[dict]:
    return [
        json.loads(line)
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _meta() -> dict:
    return json.loads(META.read_text(encoding="utf-8"))


def test_v13_manifest_is_two_row_mixed_tense_reserve_challenge() -> None:
    rows = _rows()
    positives = [row for row in rows if row.get("benchmark_role") == "positive"]
    unknowns = [row for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(rows) == 10
    assert len(positives) == 2
    assert len(unknowns) == 8
    assert {row["lemma"]: row["surface"] for row in positives} == TARGETS
    assert {row["id"] for row in positives} == {
        "V13-ABHI-PRS-3SGM",
        "V13-AFCELI-PST-3PL",
    }
    assert all(row["part_of_speech"] == "verb" for row in positives)
    assert all(row["conjugation"] == "2A" for row in positives)
    assert all(row["feature_scope"] == [
        "lemma",
        "part_of_speech",
        "conjugation",
        "tense_aspect",
        "person",
    ] for row in positives)

    by_lemma = {row["lemma"]: row for row in positives}
    assert by_lemma["abhi"]["tense_aspect"] == "present"
    assert by_lemma["abhi"]["person"] == "3sg_m"
    assert by_lemma["afceli"]["tense_aspect"] == "past"
    assert by_lemma["afceli"]["person"] == "3pl"


def test_v13_freeze_metadata_pins_pre_answer_runtime_state() -> None:
    meta = _meta()

    assert meta["benchmark_version"] == "v13"
    assert meta["manifest_git_blob_sha"] == "fe0d0617cdeb40b22c95633dc3b644c238583309"
    assert meta["freeze_commit"] == "5dd761c6c0187b15e0039f7e6f9cdb8d8c67140b"
    assert meta["freeze_status"] == "frozen"
    assert meta["measurement_status"] == "measured"
    assert meta["freeze_validation"] == {
        "pull_request": 35,
        "tested_head_commit": "d829b6ab59d03b02e13839d418afa6467bdf1c36",
        "workflow_run_id": 33459430413,
        "workflow_job_id": 99706272358,
        "full_test_suite": "1103/1103 passed",
    }
    assert meta["pre_answer_activation_commit"] == (
        "4b2bed488dbbb89d26ac48ca7f87a4de7464d6c3"
    )
    assert meta["pre_answer_runtime_blob_identities"] == {
        "rules/morphology/reviewed_conjugation_2_class_lexicon.json": (
            "2c4cbf5e2736cb6bd4fee7614c5495258a44c3b3"
        ),
        "rules/morphology/reviewed_conjugation_2_class_activation.json": (
            "c51ca1e4ff4cdbbae7d65e8687a890f5324f41db"
        ),
        "src/morphophonology_generator.py": (
            "43a62617d4f6ad9c0fad0a446afcbd9724dc703b"
        ),
    }
    assert set(meta["target_lemmas"]) == {"abhi", "afceli"}
    assert meta["positive_case_count"] == 2
    assert meta["unknown_case_count"] == 8

    policy = meta["benchmark_policy"]
    assert policy["answers_are_evaluation_only"] is True
    assert policy["runtime_rule_learning_from_v13_allowed"] is False
    assert policy["answer_sources_may_not_authorize_special_case_runtime_forms"] is True
    assert policy["pre_answer_activation_is_intentional"] is True
    assert policy["future_generic_past_improvement_allowed_from_independent_development_evidence"] is True

    design = meta["experimental_design"]
    assert design["activation_predates_answer_lookup"] is True
    assert design["abhi_row_is_prediction_validation"] is True
    assert design["afceli_row_is_tense_gap_probe"] is True


def test_v13_targets_are_class_known_and_activated_without_target_profiles() -> None:
    activated = set(eligible_conj2_class_activation_lemmas())
    profiles = set(eligible_conj2_profile_lemmas())

    for lemma in TARGETS:
        entry = reviewed_class_entry(lemma)
        assert entry is not None
        assert entry.part_of_speech == "verb"
        assert entry.conjugation_class == "2A"
        assert entry.status == "reviewed_class_only"
        assert entry.generation_enabled is False
        assert entry.correction_allowed is False
        assert lemma in activated
        assert lemma not in profiles


def test_v13_abhi_prediction_existed_before_answer_lookup_and_preserves_syncretism() -> None:
    one_sg = generate_class_authorized_conj2_present("abhi", "1sg")
    three_sg_m = generate_class_authorized_conj2_present("abhi", "3sg_m")

    assert one_sg is not None
    assert three_sg_m is not None
    assert one_sg.surface == "abhiyaa"
    assert three_sg_m.surface == "abhiyaa"
    assert one_sg.status == "reviewed_rule_derived"
    assert three_sg_m.status == "reviewed_rule_derived"
    assert one_sg.rule_id == "MORPH-CONJ-IIA-CLASS-ACT-001:i_vowel_glide"
    assert three_sg_m.rule_id == "MORPH-CONJ-IIA-CLASS-ACT-001:i_vowel_glide"
    assert one_sg.correction_allowed is False
    assert three_sg_m.correction_allowed is False

    people = {
        candidate.person
        for candidate in analyze_morphophonological_surface("abhiyaa")
        if candidate.lemma == "abhi"
    }
    assert people == {"1sg", "3sg_m"}


def test_v13_freeze_records_past_gap_historically_without_forbidding_future_generic_past() -> None:
    meta = _meta()
    prediction = meta["pre_answer_prediction_state"]["afceliyeen"]
    measured = meta["measured_result"]

    assert prediction["prediction_existed_before_answer_lookup"] is False
    assert "no class-level past generator" in prediction["reason"]
    assert measured["somali_ai_combined_positive_surface_recognition"] == "1/2"
    assert measured["somali_ai_combined_deep_feature_rows"] == "1/2"
    assert meta["benchmark_policy"][
        "future_generic_past_improvement_allowed_from_independent_development_evidence"
    ] is True


def test_v13_unknowns_are_synthetic_distinct_and_not_rule_derived() -> None:
    rows = _rows()
    positives = {row["surface"] for row in rows if row.get("benchmark_role") == "positive"}
    unknowns = [row["surface"] for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(unknowns) == len(set(unknowns)) == 8
    assert positives.isdisjoint(unknowns)
    assert all("z" in surface or "q" in surface or "v" in surface for surface in unknowns)

    for surface in unknowns:
        assert not any(
            candidate.status == "reviewed_rule_derived"
            and candidate.lemma in TARGETS
            for candidate in analyze_morphophonological_surface(surface)
        )
