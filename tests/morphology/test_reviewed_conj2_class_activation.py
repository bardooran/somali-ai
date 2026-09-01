from __future__ import annotations

import json
from pathlib import Path

import src.morphophonology_generator as morphophonology_generator
from src.morphology_analysis import analyze_morphology
from src.morphology_class_lexicon import (
    ReviewedMorphologyClassEntry,
    reviewed_class_lemmas,
)
from src.morphology_paradigm_v11 import report as v11_report
from src.morphology_paradigm_v12 import report as v12_report
from src.morphophonology_generator import (
    analyze_morphophonological_surface,
    eligible_conj2_class_activation_lemmas,
    eligible_conj2_profile_lemmas,
    generate_class_authorized_conj2_present,
    generate_conj2_past,
)

ACTIVATION = Path("rules/morphology/reviewed_conjugation_2_class_activation.json")
V10 = Path("data/qa/morphology_paradigm_benchmark_v10.jsonl")
V11 = Path("data/qa/morphology_paradigm_benchmark_v11.jsonl")
V12 = Path("data/qa/morphology_paradigm_benchmark_v12.jsonl")

PRE_V11_LEMMAS = (
    "bushi",
    "butaaci",
    "buubi",
    "buufi",
    "buuxi",
    "caafi",
    "caajisi",
)
STAGE1N_LEMMAS = ("aaddi", "aammusi", "abhi", "afceli")
EXPECTED_ACTIVATED_LEMMAS = (
    "aaddi",
    "aammusi",
    "abhi",
    "afceli",
    "bushi",
    "butaaci",
    "buubi",
    "buufi",
    "buuxi",
    "caafi",
    "caajisi",
)

PERSON_PROCESS = {
    "1sg": "i_vowel_glide",
    "2sg": "i_t_assibilation",
    "3sg_m": "i_vowel_glide",
    "3sg_f": "i_t_assibilation",
    "1pl": "i_n_weak_causative_manner_alternation",
    "2pl": "i_t_assibilation",
    "3pl": "i_vowel_glide",
}


def _expected_present_surface(lemma: str, person: str) -> str:
    if person in {"1sg", "3sg_m"}:
        return lemma + "yaa"
    if person in {"2sg", "3sg_f"}:
        return lemma + "saa"
    if person == "1pl":
        return lemma + "nnaa"
    if person == "2pl":
        return lemma + "saan"
    if person == "3pl":
        return lemma + "yaan"
    raise AssertionError(person)


def test_activation_cohort_is_explicit_and_stage1n_was_delayed_until_after_v12_baseline() -> None:
    activation = json.loads(ACTIVATION.read_text(encoding="utf-8"))
    assert tuple(activation["activated_lemmas"]) == EXPECTED_ACTIVATED_LEMMAS
    assert tuple(activation["activation_cohorts"]["pre_v11"]) == PRE_V11_LEMMAS
    assert tuple(activation["activation_cohorts"]["stage1n_post_v12_baseline"]) == STAGE1N_LEMMAS
    assert activation["stage1n_class_authorization_commit"] == (
        "0ab8f13d2e5bc932048b413ebb3a82b445193b6a"
    )
    assert activation["stage1n_class_lexicon_blob_sha"] == (
        "2c4cbf5e2736cb6bd4fee7614c5495258a44c3b3"
    )
    assert activation["v12_freeze_commit"] == (
        "83c7a7d06a3a988b07a43835847e180b9b0d1fc3"
    )
    assert activation["v12_baseline_measurement_merge_commit"] == (
        "ea0366f7f785ced58fc11022702c42900135c19f"
    )

    policy = activation["eligibility_policy"]
    assert policy["explicit_activated_lemma_allowlist"] is True
    assert policy["future_class_lexicon_entries_auto_activate"] is False
    assert policy["arbitrary_i_final_lemma_allowed"] is False

    isolation = activation["benchmark_isolation"]
    assert isolation["v12_answers_used_as_runtime_evidence"] is False
    assert isolation["v12_answer_sources_used_as_stage1o_activation_evidence"] is False
    assert isolation["v12_targets_special_cased"] is False
    assert isolation["stage1n_complete_cohort_activated_uniformly"] is True


def test_activation_uniformly_covers_all_explicitly_activated_c2a_lemmas() -> None:
    known_c2a = set(reviewed_class_lemmas("2A"))
    assert set(EXPECTED_ACTIVATED_LEMMAS).issubset(known_c2a)
    assert eligible_conj2_class_activation_lemmas() == EXPECTED_ACTIVATED_LEMMAS

    for lemma in EXPECTED_ACTIVATED_LEMMAS:
        for person, process in PERSON_PROCESS.items():
            candidate = generate_class_authorized_conj2_present(lemma, person)
            assert candidate is not None
            assert candidate.surface == _expected_present_surface(lemma, person)
            assert candidate.lemma == lemma
            assert candidate.part_of_speech == "verb"
            assert candidate.conjugation_class == "2A"
            assert candidate.tense_aspect == "present"
            assert candidate.mood == "indicative"
            assert candidate.person == person
            assert candidate.status == "reviewed_rule_derived"
            assert candidate.rule_id == f"MORPH-CONJ-IIA-CLASS-ACT-001:{process}"
            assert candidate.correction_allowed is False


def test_future_reviewed_class_entry_does_not_auto_activate(monkeypatch) -> None:
    future_entry = ReviewedMorphologyClassEntry(
        lemma="mustaqbali",
        part_of_speech="verb",
        conjugation_class="2A",
        status="reviewed_class_only",
        generation_enabled=False,
        correction_allowed=False,
        source_label="v2a=",
        source_page=999,
        gloss="synthetic test entry, not a claimed Somali form",
    )
    monkeypatch.setattr(
        morphophonology_generator,
        "reviewed_class_entry",
        lambda lemma: future_entry if lemma.casefold() == "mustaqbali" else None,
    )

    for person in PERSON_PROCESS:
        assert (
            morphophonology_generator.generate_class_authorized_conj2_present(
                "mustaqbali", person
            )
            is None
        )


def test_activation_generalizes_on_non_benchmark_lemmas_and_preserves_syncretism() -> None:
    for lemma in ("buufi", "buuxi", "caajisi"):
        singular_common = _expected_present_surface(lemma, "1sg")
        t_common = _expected_present_surface(lemma, "2sg")

        singular_people = {
            item.person
            for item in analyze_morphophonological_surface(singular_common)
            if item.lemma == lemma
        }
        t_people = {
            item.person
            for item in analyze_morphophonological_surface(t_common)
            if item.lemma == lemma
        }
        assert singular_people == {"1sg", "3sg_m"}
        assert t_people == {"2sg", "3sg_f"}

        analyses = [item for item in analyze_morphology(singular_common) if item.lemma == lemma]
        assert {item.features.get("person") for item in analyses} >= {"1sg", "3sg_m"}
        assert all(item.features.get("conjugation_class") == "2A" for item in analyses)
        assert all(item.features.get("tense_aspect") == "present" for item in analyses)
        assert all(item.features.get("mood") == "indicative" for item in analyses)
        assert all(item.correction_allowed is False for item in analyses)


def test_stage1n_activation_is_cohort_wide_not_v12_target_specific() -> None:
    explicit_profiles = set(eligible_conj2_profile_lemmas())
    assert explicit_profiles == {"joogi", "kari"}

    for lemma in STAGE1N_LEMMAS:
        assert lemma not in explicit_profiles
        for person in PERSON_PROCESS:
            candidate = generate_class_authorized_conj2_present(lemma, person)
            assert candidate is not None
            assert candidate.rule_id.startswith("MORPH-CONJ-IIA-CLASS-ACT-001:")
            assert candidate.correction_allowed is False

        assert generate_conj2_past(lemma, "1sg") is None
        assert generate_conj2_past(lemma, "2sg") is None
        assert generate_conj2_past(lemma, "3pl") is None

    # These reserve forms are mechanics tests only. They are not claims that the
    # surfaces have been independently attested in a post-activation benchmark.
    assert generate_class_authorized_conj2_present("abhi", "3pl").surface == "abhiyaan"
    assert generate_class_authorized_conj2_present("afceli", "3pl").surface == "afceliyaan"


def test_class_activation_never_infers_class_from_i_final_spelling() -> None:
    for unknown_lemma in ("zzabi", "qarqari", "nadiifi", "qurxi", "kari", "joogi"):
        for person in PERSON_PROCESS:
            assert generate_class_authorized_conj2_present(unknown_lemma, person) is None

    for synthetic_surface in (
        "zzabiyaa",
        "zzabisaa",
        "zzabinnaa",
        "qarqariyaan",
        "qarqarisaan",
    ):
        assert not any(
            item.rule_id.startswith("MORPH-CONJ-IIA-CLASS-ACT-001:")
            for item in analyze_morphophonological_surface(synthetic_surface)
        )


def test_frozen_v10_remains_outside_class_activation() -> None:
    for line in V10.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("benchmark_role") != "positive":
            continue
        assert not any(
            item.rule_id.startswith("MORPH-CONJ-IIA-CLASS-ACT-001:")
            for item in analyze_morphophonological_surface(str(row["surface"]))
        )


def test_v11_target_is_reached_only_through_generic_class_activation() -> None:
    positive_surfaces = {
        str(row["surface"])
        for row in (
            json.loads(line)
            for line in V11.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
        if row.get("benchmark_role") == "positive"
    }
    assert len(positive_surfaces) == 5

    for surface in positive_surfaces:
        candidates = [
            item
            for item in analyze_morphophonological_surface(surface)
            if item.lemma == "buubi"
        ]
        assert candidates
        assert all(
            item.rule_id.startswith("MORPH-CONJ-IIA-CLASS-ACT-001:")
            for item in candidates
        )
        assert all(item.correction_allowed is False for item in candidates)


def test_v11_score_remains_perfect_after_stage1n_activation() -> None:
    result = v11_report()
    combined = result["combined"]

    assert combined["recognized_unique_surface_count"] == 5
    assert combined["lemma_matched_unique_surface_count"] == 5
    assert combined["pos_matched_unique_surface_count"] == 5
    assert combined["conjugation_matched_unique_surface_count"] == 5
    assert combined["tense_matched_unique_surface_count"] == 5
    assert combined["mood_matched_unique_surface_count"] == 5
    assert combined["deep_feature_matched_row_count"] == 7
    assert combined["syncretic_surface_preserved_count"] == 2
    assert combined["unknown_rejected_count"] == 8
    assert combined["unknown_safety_rate"] == 1.0
    assert combined["authority_diagnostics"]["reviewed_exact_surfaces"] == []
    assert len(combined["authority_diagnostics"]["reviewed_rule_derived_surfaces"]) == 5


def test_v12_targets_are_reached_only_through_uniform_stage1n_activation() -> None:
    positive_rows = [
        json.loads(line)
        for line in V12.read_text(encoding="utf-8").splitlines()
        if line.strip() and json.loads(line).get("benchmark_role") == "positive"
    ]
    assert {row["lemma"] for row in positive_rows} == {"aaddi", "aammusi"}

    for row in positive_rows:
        candidates = [
            item
            for item in analyze_morphophonological_surface(str(row["surface"]))
            if item.lemma == row["lemma"]
        ]
        assert candidates
        assert {item.person for item in candidates} == {"3pl"}
        assert all(
            item.rule_id == "MORPH-CONJ-IIA-CLASS-ACT-001:i_vowel_glide"
            for item in candidates
        )
        assert all(item.correction_allowed is False for item in candidates)


def test_v12_score_demonstrates_post_baseline_multi_lemma_generalization() -> None:
    result = v12_report()
    combined = result["combined"]

    assert combined["recognized_unique_surface_count"] == 2
    assert combined["lemma_matched_unique_surface_count"] == 2
    assert combined["pos_matched_unique_surface_count"] == 2
    assert combined["conjugation_matched_unique_surface_count"] == 2
    assert combined["tense_matched_unique_surface_count"] == 2
    assert combined["mood_matched_unique_surface_count"] == 2
    assert combined["deep_feature_matched_row_count"] == 2
    assert combined["unknown_rejected_count"] == 8
    assert combined["unknown_safety_rate"] == 1.0
    assert combined["authority_diagnostics"]["reviewed_exact_surfaces"] == []
    assert combined["authority_diagnostics"]["reviewed_rule_derived_surfaces"] == [
        "aaddiyaan",
        "aammusiyaan",
    ]

    master = result["master"]
    assert master["recognized_unique_surface_count"] == 0
    assert master["unknown_rejected_count"] == 8
