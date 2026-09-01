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

MANIFEST = Path("data/qa/morphology_paradigm_benchmark_v12.jsonl")
META = Path("data/qa/morphology_paradigm_benchmark_v12.meta.json")

TARGETS = {
    "aaddi": "aaddiyaan",
    "aammusi": "aammusiyaan",
}
RESERVE_STAGE1N = {"abhi", "afceli"}


def _rows() -> list[dict]:
    return [
        json.loads(line)
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_v12_manifest_is_two_lemma_natural_3pl_challenge() -> None:
    rows = _rows()
    positives = [row for row in rows if row.get("benchmark_role") == "positive"]
    unknowns = [row for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(rows) == 10
    assert len(positives) == 2
    assert len(unknowns) == 8
    assert {row["lemma"]: row["surface"] for row in positives} == TARGETS
    assert all(row.get("part_of_speech") == "verb" for row in positives)
    assert all(row.get("conjugation") == "2A" for row in positives)
    assert all(row.get("tense_aspect") == "present" for row in positives)
    assert all(row.get("mood") == "indicative" for row in positives)
    assert all(row.get("person") == "3pl" for row in positives)


def test_v12_uses_two_distinct_post_class_authorization_answer_sources() -> None:
    positives = [row for row in _rows() if row.get("benchmark_role") == "positive"]
    families = {row.get("source_family") for row in positives}
    assert families == {
        "Dalka Journal 2023 Somali natural text",
        "Kapchits 2005 Sentence particles in the Somali language",
    }
    assert {row.get("surface") for row in positives} == {"aaddiyaan", "aammusiyaan"}


def test_v12_policy_and_pre_freeze_runtime_identity_are_locked() -> None:
    meta = json.loads(META.read_text(encoding="utf-8"))
    assert meta["benchmark_version"] == "v12"
    assert meta["manifest_git_blob_sha"] == "6ddfc6e97245911569e833472a2c4c71af76e17d"
    assert meta["freeze_commit"] == "83c7a7d06a3a988b07a43835847e180b9b0d1fc3"
    assert meta["pre_freeze_class_authorization_commit"] == (
        "0ab8f13d2e5bc932048b413ebb3a82b445193b6a"
    )
    assert meta["pre_freeze_runtime_commit"] == (
        "0ab8f13d2e5bc932048b413ebb3a82b445193b6a"
    )
    assert meta["pre_freeze_blob_identities"] == {
        "rules/morphology/reviewed_conjugation_2_class_lexicon.json": (
            "2c4cbf5e2736cb6bd4fee7614c5495258a44c3b3"
        ),
        "rules/morphology/reviewed_conjugation_2_class_activation.json": (
            "2ff0e40c4d85784fe2d7e0d94ab8f96c2287aeea"
        ),
        "src/morphophonology_generator.py": (
            "43a62617d4f6ad9c0fad0a446afcbd9724dc703b"
        ),
    }
    assert meta["positive_case_count"] == 2
    assert meta["positive_unique_surface_count"] == 2
    assert meta["target_lemma_count"] == 2
    assert meta["unknown_case_count"] == 8
    assert set(meta["stage1n_reserve_class_only_lemmas"]) == RESERVE_STAGE1N
    assert meta["measurement_status"] == "pending_measurement"

    policy = meta["benchmark_policy"]
    assert policy["answers_are_evaluation_only"] is True
    assert policy["runtime_rule_learning_from_v12_allowed"] is False
    assert policy["explicit_source_surfaces_only"] is True
    assert policy["inferred_unattested_surfaces_included"] is False
    assert policy["pre_freeze_class_authorization_allowed"] is True
    assert policy["pre_freeze_surface_generation_for_targets_enabled"] is False
    assert policy["post_freeze_uniform_activation_of_stage1n_cohort_allowed"] is True
    assert policy["v12_answer_rows_may_authorize_special_case_runtime_forms"] is False


def test_v12_targets_were_class_known_but_unactivated_before_freeze() -> None:
    activated = set(eligible_conj2_class_activation_lemmas())
    explicit_profiles = set(eligible_conj2_profile_lemmas())

    for lemma in set(TARGETS) | RESERVE_STAGE1N:
        entry = reviewed_class_entry(lemma)
        assert entry is not None
        assert entry.part_of_speech == "verb"
        assert entry.conjugation_class == "2A"
        assert entry.status == "reviewed_class_only"
        assert entry.generation_enabled is False
        assert entry.correction_allowed is False
        assert lemma not in activated
        assert lemma not in explicit_profiles
        for person in ("1sg", "2sg", "3sg_m", "3sg_f", "1pl", "2pl", "3pl"):
            assert generate_class_authorized_conj2_present(lemma, person) is None


def test_v12_target_surfaces_have_zero_class_activation_authority_at_freeze() -> None:
    for lemma, surface in TARGETS.items():
        assert not any(
            candidate.lemma == lemma
            and candidate.rule_id.startswith("MORPH-CONJ-IIA-CLASS-ACT-001:")
            for candidate in analyze_morphophonological_surface(surface)
        )


def test_v12_unknowns_are_distinct_synthetic_safety_strings() -> None:
    rows = _rows()
    positives = {row["surface"] for row in rows if row.get("benchmark_role") == "positive"}
    unknowns = [row["surface"] for row in rows if row.get("benchmark_role") == "unknown"]

    assert len(unknowns) == len(set(unknowns)) == 8
    assert positives.isdisjoint(unknowns)
    assert all("z" in surface or "q" in surface or "v" in surface for surface in unknowns)
