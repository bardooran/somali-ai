from __future__ import annotations

import json
from pathlib import Path

import src.morphophonology_conj2_class_past as class_past
from src.morphology_analysis import analyze_morphology
from src.morphology_class_lexicon import ReviewedMorphologyClassEntry
from src.morphology_paradigm_v10 import report as v10_report
from src.morphology_paradigm_v11 import report as v11_report
from src.morphology_paradigm_v12 import report as v12_report
from src.morphology_paradigm_v13 import report as v13_report
from src.morphophonology_conj2_class_past import (
    analyze_conj2_class_past_surface,
    eligible_conj2_class_past_activation_lemmas,
    generate_class_authorized_conj2_past,
)

ACTIVATION = Path("rules/morphology/reviewed_conjugation_2_class_past_activation.json")
EXPECTED_LEMMAS = (
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


def test_past_activation_is_narrow_independent_and_benchmark_isolated() -> None:
    activation = json.loads(ACTIVATION.read_text(encoding="utf-8"))

    assert activation["tense_aspect"] == "past"
    assert activation["mood"] == "indicative"
    assert activation["authorized_persons"] == ["3pl"]
    assert activation["past_morphology"] == {
        "3pl": {"agreement": "", "tam": "een"}
    }
    assert activation["required_processes"] == ["i_vowel_glide"]
    assert tuple(activation["activated_lemmas"]) == EXPECTED_LEMMAS

    limits = activation["scope_limits"]
    assert limits["only_3pl_past_is_authorized"] is True
    assert limits["other_past_persons_inferred"] is False
    assert limits["full_past_paradigm_claimed"] is False
    assert limits["orthographic_ay_ey_variant_question_deferred"] is True
    assert limits["first_plural_past_manner_alternation_deferred"] is True

    isolation = activation["benchmark_isolation"]
    for version in range(5, 14):
        assert isolation[f"v{version}_answers_used_as_runtime_evidence"] is False
    assert isolation["v13_afceli_special_case_allowed"] is False
    assert isolation[
        "complete_stage1o_class_cohort_activated_uniformly_for_3pl_past"
    ] is True


def test_past_activation_uniformly_covers_complete_stage1o_class_cohort() -> None:
    assert eligible_conj2_class_past_activation_lemmas() == EXPECTED_LEMMAS

    for lemma in EXPECTED_LEMMAS:
        candidate = generate_class_authorized_conj2_past(lemma, "3pl")
        assert candidate is not None
        assert candidate.surface == lemma + "yeen"
        assert candidate.lemma == lemma
        assert candidate.part_of_speech == "verb"
        assert candidate.conjugation_class == "2A"
        assert candidate.tense_aspect == "past"
        assert candidate.mood == "indicative"
        assert candidate.person == "3pl"
        assert candidate.status == "reviewed_rule_derived"
        assert candidate.rule_id == "MORPH-CONJ-IIA-CLASS-PST-ACT-001:i_vowel_glide"
        assert candidate.correction_allowed is False
        assert any("Saeed" in item and "kariyeen" in item for item in candidate.evidence_summary)
        assert any("Livnat" in item and "kariyeen" in item for item in candidate.evidence_summary)


def test_other_class_level_past_persons_remain_unjudged() -> None:
    for lemma in EXPECTED_LEMMAS:
        for person in ("1sg", "2sg", "3sg_m", "3sg_f", "1pl", "2pl"):
            assert generate_class_authorized_conj2_past(lemma, person) is None


def test_generic_past_is_not_inferred_from_i_final_spelling() -> None:
    for lemma in ("zzabi", "qarqari", "nadiifi", "qurxi", "kari", "joogi"):
        assert generate_class_authorized_conj2_past(lemma, "3pl") is None

    for surface in (
        "zzabiyeen",
        "qarqariyeen",
        "nadiifiyeen",
        "qurxiyeen",
        "kariyeen",
        "joogiyeen",
    ):
        assert analyze_conj2_class_past_surface(surface) == ()


def test_future_class_entry_does_not_auto_activate_for_past(monkeypatch) -> None:
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
        class_past,
        "reviewed_class_entry",
        lambda lemma: future_entry if lemma.casefold() == "mustaqbali" else None,
    )

    assert generate_class_authorized_conj2_past("mustaqbali", "3pl") is None


def test_v13_afceliyeen_is_reached_only_through_generic_past_rule() -> None:
    direct = generate_class_authorized_conj2_past("afceli", "3pl")
    assert direct is not None
    assert direct.surface == "afceliyeen"

    candidates = [
        item
        for item in analyze_morphology("afceliyeen")
        if item.lemma == "afceli"
    ]
    assert candidates
    assert {item.features.get("person") for item in candidates} == {"3pl"}
    assert {item.features.get("tense_aspect") for item in candidates} == {"past"}
    assert all(item.authority == "reviewed_rule_derived" for item in candidates)
    assert all(
        item.evidence_id == "MORPH-CONJ-IIA-CLASS-PST-ACT-001:i_vowel_glide"
        for item in candidates
    )
    assert all(item.correction_allowed is False for item in candidates)


def test_non_v13_lemmas_use_the_same_generic_past_mechanics() -> None:
    # These are mechanics tests, not claims that the resulting surfaces are
    # independently attested.  They demonstrate that afceli is not special-cased.
    for lemma in ("buubi", "buuxi", "caajisi", "aaddi"):
        surface = lemma + "yeen"
        candidates = analyze_conj2_class_past_surface(surface)
        assert len(candidates) == 1
        assert candidates[0].lemma == lemma
        assert candidates[0].person == "3pl"
        assert candidates[0].rule_id == (
            "MORPH-CONJ-IIA-CLASS-PST-ACT-001:i_vowel_glide"
        )


def test_frozen_benchmarks_preserve_v10_v11_v12_and_improve_live_v13() -> None:
    v10 = v10_report()["combined"]
    assert v10["recognized_unique_surface_count"] == 0
    assert v10["deep_feature_matched_row_count"] == 0
    assert v10["syncretic_surface_preserved_count"] == 0
    assert v10["unknown_rejected_count"] == 8

    v11 = v11_report()["combined"]
    assert v11["recognized_unique_surface_count"] == 5
    assert v11["deep_feature_matched_row_count"] == 7
    assert v11["syncretic_surface_preserved_count"] == 2
    assert v11["unknown_rejected_count"] == 8

    v12 = v12_report()["combined"]
    assert v12["recognized_unique_surface_count"] == 2
    assert v12["deep_feature_matched_row_count"] == 2
    assert v12["unknown_rejected_count"] == 8

    result = v13_report()
    live = result["combined"]
    assert live["recognized_unique_surface_count"] == 2
    assert live["deep_feature_matched_row_count"] == 2
    assert live["lemma_matched_unique_surface_count"] == 2
    assert live["pos_matched_unique_surface_count"] == 2
    assert live["conjugation_matched_unique_surface_count"] == 2
    assert live["tense_matched_unique_surface_count"] == 2
    assert live["person_matched_unique_surface_count"] == 2
    assert live["unknown_rejected_count"] == 8
    assert live["authority_diagnostics"]["reviewed_exact_surfaces"] == []
    assert live["authority_diagnostics"]["reviewed_rule_derived_surfaces"] == [
        "abhiyaa",
        "afceliyeen",
    ]

    historical = result["benchmark"]["measured_result"]
    assert historical["somali_ai_combined_positive_surface_recognition"] == "1/2"
    assert historical["somali_ai_combined_deep_feature_rows"] == "1/2"
    assert historical[
        "somali_ai_reviewed_rule_derived_positive_surface_recognition"
    ] == "1/2 (abhiyaa)"
