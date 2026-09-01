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
from src.morphology_paradigm_v14 import report as v14_report
from src.morphology_paradigm_v15 import report as v15_report
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
    assert activation["authorized_persons"] == ["2sg", "2pl", "3pl"]
    assert activation["past_morphology"] == {
        "2sg": {"agreement": "t", "tam": "ay"},
        "2pl": {"agreement": "s", "tam": "een"},
        "3pl": {"agreement": "", "tam": "een"},
    }
    assert activation["required_processes"] == ["i_t_assibilation", "i_vowel_glide"]
    assert tuple(activation["activated_lemmas"]) == EXPECTED_LEMMAS

    primary = activation["development_evidence"]["primary"]
    assert "Puglielli" in primary["citation"]
    assert "Saeed" in primary["citation"]
    assert "joogi-s-ay" in primary["evidence"]
    assert "joogi+t+ay" in primary["evidence"]
    assert "2PL kariseen" in primary["evidence"]
    assert "3PL kariyeen" in primary["evidence"]
    assert "before v15 target selection and answer lookup" in primary["evidence"]
    assert "no v15 answer surface is used as runtime evidence" in primary["evidence"]

    corroboration = activation["development_evidence"]["independent_corroboration"]
    assert "Zorc" in corroboration["citation"]
    assert "karisey/karisay" in corroboration["evidence"]
    assert "buuxisay" in corroboration["evidence"]
    assert "without using" in corroboration["evidence"]

    limits = activation["scope_limits"]
    assert limits["only_2sg_2pl_and_3pl_past_are_authorized"] is True
    assert limits["other_past_persons_inferred"] is False
    assert limits["full_past_paradigm_claimed"] is False
    assert limits["orthographic_ay_ey_variant_question_deferred"] is True
    assert limits["first_plural_past_manner_alternation_deferred"] is True

    isolation = activation["benchmark_isolation"]
    for version in range(5, 16):
        assert isolation[f"v{version}_answers_used_as_runtime_evidence"] is False
    assert isolation["v13_afceli_special_case_allowed"] is False
    assert isolation["v14_buufi_special_case_allowed"] is False
    assert isolation["v14_caafi_special_case_allowed"] is False
    assert isolation["v15_buuxi_special_case_allowed"] is False
    assert isolation["v15_caajisi_special_case_allowed"] is False
    assert isolation["v15_historical_baseline_merge_commit"] == (
        "22959891cb4953e65a3037e4ace756f29febc8f8"
    )
    assert isolation[
        "complete_stage1o_class_cohort_activated_uniformly_for_2sg_2pl_and_3pl_past"
    ] is True


def test_past_activation_uniformly_covers_complete_stage1o_class_cohort() -> None:
    assert eligible_conj2_class_past_activation_lemmas() == EXPECTED_LEMMAS

    for lemma in EXPECTED_LEMMAS:
        candidate_2sg = generate_class_authorized_conj2_past(lemma, "2sg")
        assert candidate_2sg is not None
        assert candidate_2sg.surface == lemma + "say"
        assert candidate_2sg.lemma == lemma
        assert candidate_2sg.part_of_speech == "verb"
        assert candidate_2sg.conjugation_class == "2A"
        assert candidate_2sg.tense_aspect == "past"
        assert candidate_2sg.mood == "indicative"
        assert candidate_2sg.person == "2sg"
        assert candidate_2sg.status == "reviewed_rule_derived"
        assert candidate_2sg.rule_id == "MORPH-CONJ-IIA-CLASS-PST-ACT-001:i_t_assibilation"
        assert candidate_2sg.correction_allowed is False
        assert any(
            "Puglielli" in item and "joogi-s-ay" in item
            for item in candidate_2sg.evidence_summary
        )

        candidate_2pl = generate_class_authorized_conj2_past(lemma, "2pl")
        assert candidate_2pl is not None
        assert candidate_2pl.surface == lemma + "seen"
        assert candidate_2pl.lemma == lemma
        assert candidate_2pl.part_of_speech == "verb"
        assert candidate_2pl.conjugation_class == "2A"
        assert candidate_2pl.tense_aspect == "past"
        assert candidate_2pl.mood == "indicative"
        assert candidate_2pl.person == "2pl"
        assert candidate_2pl.status == "reviewed_rule_derived"
        assert candidate_2pl.rule_id == (
            "MORPH-CONJ-IIA-CLASS-PST-ACT-001:concatenative_elsewhere"
        )
        assert candidate_2pl.correction_allowed is False
        assert any(
            "Saeed" in item and "kariseen" in item
            for item in candidate_2pl.evidence_summary
        )

        candidate_3pl = generate_class_authorized_conj2_past(lemma, "3pl")
        assert candidate_3pl is not None
        assert candidate_3pl.surface == lemma + "yeen"
        assert candidate_3pl.lemma == lemma
        assert candidate_3pl.part_of_speech == "verb"
        assert candidate_3pl.conjugation_class == "2A"
        assert candidate_3pl.tense_aspect == "past"
        assert candidate_3pl.mood == "indicative"
        assert candidate_3pl.person == "3pl"
        assert candidate_3pl.status == "reviewed_rule_derived"
        assert candidate_3pl.rule_id == "MORPH-CONJ-IIA-CLASS-PST-ACT-001:i_vowel_glide"
        assert candidate_3pl.correction_allowed is False
        assert any(
            "Saeed" in item and "kariyeen" in item
            for item in candidate_3pl.evidence_summary
        )


def test_other_class_level_past_persons_remain_unjudged() -> None:
    for lemma in EXPECTED_LEMMAS:
        for person in ("1sg", "3sg_m", "3sg_f", "1pl"):
            assert generate_class_authorized_conj2_past(lemma, person) is None


def test_generic_past_is_not_inferred_from_i_final_spelling() -> None:
    for lemma in ("zzabi", "qarqari", "nadiifi", "qurxi", "kari", "joogi"):
        assert generate_class_authorized_conj2_past(lemma, "2sg") is None
        assert generate_class_authorized_conj2_past(lemma, "2pl") is None
        assert generate_class_authorized_conj2_past(lemma, "3pl") is None

    for surface in (
        "zzabisay",
        "zzabiseen",
        "zzabiyeen",
        "qarqarisay",
        "qarqariseen",
        "qarqariyeen",
        "nadiifisay",
        "nadiifiseen",
        "nadiifiyeen",
        "qurxisay",
        "qurxiseen",
        "qurxiyeen",
        "karisay",
        "kariseen",
        "kariyeen",
        "joogisay",
        "joogiseen",
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

    assert generate_class_authorized_conj2_past("mustaqbali", "2sg") is None
    assert generate_class_authorized_conj2_past("mustaqbali", "2pl") is None
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


def test_v14_buufiseen_is_reached_only_through_generic_2pl_rule() -> None:
    direct = generate_class_authorized_conj2_past("buufi", "2pl")
    assert direct is not None
    assert direct.surface == "buufiseen"

    candidates = [
        item
        for item in analyze_morphology("buufiseen")
        if item.lemma == "buufi"
    ]
    assert candidates
    assert {item.features.get("person") for item in candidates} == {"2pl"}
    assert {item.features.get("tense_aspect") for item in candidates} == {"past"}
    assert all(item.authority == "reviewed_rule_derived" for item in candidates)
    assert all(
        item.evidence_id
        == "MORPH-CONJ-IIA-CLASS-PST-ACT-001:concatenative_elsewhere"
        for item in candidates
    )
    assert all(item.correction_allowed is False for item in candidates)


def test_v15_buuxisay_is_reached_only_through_generic_2sg_rule() -> None:
    direct = generate_class_authorized_conj2_past("buuxi", "2sg")
    assert direct is not None
    assert direct.surface == "buuxisay"

    candidates = [
        item
        for item in analyze_morphology("buuxisay")
        if item.lemma == "buuxi"
    ]
    assert candidates
    assert {item.features.get("person") for item in candidates} == {"2sg"}
    assert {item.features.get("tense_aspect") for item in candidates} == {"past"}
    assert all(item.authority == "reviewed_rule_derived" for item in candidates)
    assert all(
        item.evidence_id == "MORPH-CONJ-IIA-CLASS-PST-ACT-001:i_t_assibilation"
        for item in candidates
    )
    assert all(item.correction_allowed is False for item in candidates)


def test_non_v15_lemmas_use_same_generic_2sg_mechanics() -> None:
    # Mechanics-only predictions. These assertions do not claim that the
    # generated surfaces below are independently attested Somali forms.
    for lemma in ("aaddi", "aammusi", "abhi", "afceli", "buubi", "buufi", "caafi", "caajisi"):
        surface = lemma + "say"
        candidates = analyze_conj2_class_past_surface(surface)
        assert len(candidates) == 1
        assert candidates[0].lemma == lemma
        assert candidates[0].person == "2sg"
        assert candidates[0].rule_id == (
            "MORPH-CONJ-IIA-CLASS-PST-ACT-001:i_t_assibilation"
        )
        assert candidates[0].correction_allowed is False

    # caajisi was selected for v15 but remained unresolved as attestation
    # evidence. Generic activation may mechanically analyze caajisisay, but
    # this is not promoted to an independently attested answer.
    caajisi_prediction = generate_class_authorized_conj2_past("caajisi", "2sg")
    assert caajisi_prediction is not None
    assert caajisi_prediction.surface == "caajisisay"
    assert caajisi_prediction.status == "reviewed_rule_derived"
    assert caajisi_prediction.correction_allowed is False


def test_non_v14_lemmas_use_same_generic_2pl_mechanics() -> None:
    for lemma in ("aaddi", "aammusi", "abhi", "afceli", "buubi", "buuxi", "caajisi"):
        surface = lemma + "seen"
        candidates = analyze_conj2_class_past_surface(surface)
        assert len(candidates) == 1
        assert candidates[0].lemma == lemma
        assert candidates[0].person == "2pl"
        assert candidates[0].rule_id == (
            "MORPH-CONJ-IIA-CLASS-PST-ACT-001:concatenative_elsewhere"
        )

    caafi_prediction = generate_class_authorized_conj2_past("caafi", "2pl")
    assert caafi_prediction is not None
    assert caafi_prediction.surface == "caafiseen"
    assert caafi_prediction.status == "reviewed_rule_derived"
    assert caafi_prediction.correction_allowed is False


def test_non_v13_lemmas_keep_same_generic_3pl_mechanics() -> None:
    for lemma in ("buubi", "buuxi", "caajisi", "aaddi"):
        surface = lemma + "yeen"
        candidates = analyze_conj2_class_past_surface(surface)
        assert len(candidates) == 1
        assert candidates[0].lemma == lemma
        assert candidates[0].person == "3pl"
        assert candidates[0].rule_id == (
            "MORPH-CONJ-IIA-CLASS-PST-ACT-001:i_vowel_glide"
        )


def test_frozen_benchmarks_preserve_v10_to_v14_and_improve_live_v15() -> None:
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

    v13 = v13_report()
    live13 = v13["combined"]
    assert live13["recognized_unique_surface_count"] == 2
    assert live13["deep_feature_matched_row_count"] == 2
    assert live13["unknown_rejected_count"] == 8
    assert live13["authority_diagnostics"]["reviewed_exact_surfaces"] == []
    assert live13["authority_diagnostics"]["reviewed_rule_derived_surfaces"] == [
        "abhiyaa",
        "afceliyeen",
    ]

    v14 = v14_report()
    live14 = v14["combined"]
    assert live14["recognized_unique_surface_count"] == 1
    assert live14["deep_feature_matched_row_count"] == 1
    assert live14["lemma_matched_unique_surface_count"] == 1
    assert live14["pos_matched_unique_surface_count"] == 1
    assert live14["conjugation_matched_unique_surface_count"] == 1
    assert live14["tense_matched_unique_surface_count"] == 1
    assert live14["person_matched_unique_surface_count"] == 1
    assert live14["unknown_rejected_count"] == 8
    assert live14["authority_diagnostics"]["reviewed_exact_surfaces"] == []
    assert live14["authority_diagnostics"]["reviewed_rule_derived_surfaces"] == [
        "buufiseen"
    ]

    historical14 = v14["benchmark"]["measured_result"]
    assert historical14["somali_ai_combined_positive_surface_recognition"] == "0/1"
    assert historical14["somali_ai_combined_deep_feature_rows"] == "0/1"
    assert historical14[
        "somali_ai_reviewed_rule_derived_positive_surface_recognition"
    ] == "0/1"

    v15 = v15_report()
    live15 = v15["combined"]
    assert live15["recognized_unique_surface_count"] == 1
    assert live15["lemma_matched_unique_surface_count"] == 1
    assert live15["pos_matched_unique_surface_count"] == 1
    assert live15["conjugation_matched_unique_surface_count"] == 1
    assert live15["tense_matched_unique_surface_count"] == 1
    assert live15["person_matched_unique_surface_count"] == 1
    assert live15["deep_feature_matched_row_count"] == 1
    assert live15["unknown_rejected_count"] == 8
    assert live15["authority_diagnostics"]["reviewed_exact_surfaces"] == []
    assert live15["authority_diagnostics"]["reviewed_rule_derived_surfaces"] == [
        "buuxisay"
    ]

    # Class-level morphology improves the combined analyzer only. The separate
    # master-exact inventory remains intentionally unchanged by a generated rule.
    master15 = v15["master"]
    assert master15["recognized_unique_surface_count"] == 0
    assert master15["lemma_matched_unique_surface_count"] == 0
    assert master15["pos_matched_unique_surface_count"] == 0
    assert master15["unknown_rejected_count"] == 8

    historical15 = v15["benchmark"]["measured_result"]
    assert historical15["somali_ai_combined_positive_surface_recognition"] == "0/1"
    assert historical15["somali_ai_combined_deep_feature_rows"] == "0/1"
    assert historical15[
        "somali_ai_reviewed_rule_derived_positive_surface_recognition"
    ] == "0/1"
    assert v15["preauthorization"]["generic_2sg_past_authorized_at_freeze"] is False
