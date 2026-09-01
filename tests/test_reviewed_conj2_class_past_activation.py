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
from src.morphology_paradigm_v16 import report as v16_report
from src.morphology_paradigm_v17 import report as v17_report
from src.morphology_paradigm_v18 import report as v18_report
from src.morphology_paradigm_v19 import report as v19_report
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
EXPECTED_PERSONS = ("1sg", "1pl", "2sg", "2pl", "3sg_m", "3sg_f", "3pl")


def test_past_activation_is_narrow_independent_and_benchmark_isolated() -> None:
    activation = json.loads(ACTIVATION.read_text(encoding="utf-8"))

    assert activation["tense_aspect"] == "past"
    assert activation["mood"] == "indicative"
    assert activation["authorized_persons"] == list(EXPECTED_PERSONS)
    assert activation["past_morphology"] == {
        "1sg": {"agreement": "", "tam": "ay"},
        "1pl": {"agreement": "n", "tam": "ay"},
        "2sg": {"agreement": "t", "tam": "ay"},
        "2pl": {"agreement": "s", "tam": "een"},
        "3sg_m": {"agreement": "", "tam": "ay"},
        "3sg_f": {"agreement": "t", "tam": "ay"},
        "3pl": {"agreement": "", "tam": "een"},
    }
    assert activation["required_processes"] == [
        "i_n_weak_causative_manner_alternation",
        "i_t_assibilation",
        "i_vowel_glide",
    ]
    assert tuple(activation["activated_lemmas"]) == EXPECTED_LEMMAS
    assert activation["open_class_generation"] is False
    assert activation["reverse_suffix_stripping"] is False
    assert activation["correction_authority"] is False

    primary = activation["development_evidence"]["primary"]
    assert "Puglielli" in primary["citation"]
    assert "Saeed" in primary["citation"]
    assert "waad joogi-s-ay" in primary["evidence"]
    assert "wey kari-s-ay" in primary["evidence"]
    assert "2PL kariseen" in primary["evidence"]
    assert "3PL kariyeen" in primary["evidence"]

    corroboration = activation["development_evidence"]["independent_corroboration"]
    assert "Zorc" in corroboration["citation"]
    assert "karisey/karisay" in corroboration["evidence"]
    assert "2SG/3SGF" in corroboration["evidence"]
    assert "caafisay" in corroboration["evidence"]
    assert "bushisay" in corroboration["evidence"]

    first_plural = activation["development_evidence"]["first_plural_independent"]
    assert "Orwin" in first_plural["citation"]
    assert "karinnay" in first_plural["evidence"]
    assert "i+n -> inn" in first_plural["evidence"]
    assert "buubinnay is never used to author the rule" in first_plural["evidence"]

    first_singular = activation["development_evidence"]["first_singular_independent"]
    assert "Orwin" in first_singular["citation"]
    assert "Zorc" in first_singular["citation"]
    assert "kari + ay -> kariyay" in first_singular["evidence"]
    assert "1SG" in first_singular["evidence"]
    assert "3SG masculine" in first_singular["evidence"]
    assert "v17 and v18 target answers remain evaluation-only" in first_singular["benchmark_boundary"]

    third_feminine = activation["development_evidence"]["third_singular_feminine_independent"]
    assert "Puglielli" in third_feminine["citation"]
    assert "Zorc" in third_feminine["citation"]
    assert "wey kari-s-ay" in third_feminine["evidence"]
    assert "agreement t plus past ay" in third_feminine["evidence"]
    assert "2SG and 3SG feminine" in third_feminine["evidence"]
    assert "caafisay and bushisay remain evaluation-only" in third_feminine["benchmark_boundary"]

    limits = activation["scope_limits"]
    assert limits["all_seven_staged_past_person_cells_authorized"] is True
    assert limits["other_past_persons_inferred"] is False
    assert limits["full_open_class_past_paradigm_claimed"] is False
    assert limits["orthographic_ay_ey_variant_question_deferred"] is True
    assert limits["first_plural_past_manner_alternation_deferred"] is False
    assert limits["first_singular_and_third_singular_masculine_syncretism_documented"] is True
    assert limits["second_singular_and_third_singular_feminine_syncretism_documented"] is True
    assert limits["third_singular_masculine_runtime_activation_deferred"] is False
    assert limits["third_singular_feminine_runtime_activation_deferred"] is False

    isolation = activation["benchmark_isolation"]
    for version in range(5, 20):
        assert isolation[f"v{version}_answers_used_as_runtime_evidence"] is False
    for key in (
        "v13_afceli_special_case_allowed",
        "v14_buufi_special_case_allowed",
        "v14_caafi_special_case_allowed",
        "v15_buuxi_special_case_allowed",
        "v15_caajisi_special_case_allowed",
        "v16_buubi_special_case_allowed",
        "v16_bushi_special_case_allowed",
        "v16_butaaci_special_case_allowed",
        "v17_aaddi_special_case_allowed",
        "v17_buufi_special_case_allowed",
        "v17_afceli_special_case_allowed",
        "v18_aammusi_special_case_allowed",
        "v18_abhi_special_case_allowed",
        "v19_caafi_special_case_allowed",
        "v19_bushi_special_case_allowed",
    ):
        assert isolation[key] is False
    assert isolation["v13_historical_baseline_merge_commit"] == "10e41ed8578672b015f8f51bfa1ee8de0158c5eb"
    assert isolation["v14_historical_baseline_merge_commit"] == "36ea856fc4ad322ee4e8d41fb3a5a9ef579147f9"
    assert isolation["v15_historical_baseline_merge_commit"] == "22959891cb4953e65a3037e4ace756f29febc8f8"
    assert isolation["v16_historical_baseline_merge_commit"] == "385af8091945c7c40f058e8f0d262c02638333a2"
    assert isolation["v17_historical_baseline_merge_commit"] == "6c818b3603f0cd73ce8ac6c6b6d4c6f21cda822d"
    assert isolation["v18_historical_baseline_merge_commit"] == "3e6d10840dad48d578da53490b6e6b37605f7e16"
    assert isolation["v19_historical_baseline_merge_commit"] == "695ca642ab5f9f1ab8da628bff8cb99b5874c210"
    assert isolation[
        "complete_stage1o_class_cohort_activated_uniformly_for_all_seven_staged_past_person_cells"
    ] is True


def test_past_activation_uniformly_covers_complete_stage1o_class_cohort() -> None:
    assert eligible_conj2_class_past_activation_lemmas() == EXPECTED_LEMMAS

    expected = {
        "1sg": ("yay", "i_vowel_glide"),
        "1pl": ("nnay", "i_n_weak_causative_manner_alternation"),
        "2sg": ("say", "i_t_assibilation"),
        "2pl": ("seen", "concatenative_elsewhere"),
        "3sg_m": ("yay", "i_vowel_glide"),
        "3sg_f": ("say", "i_t_assibilation"),
        "3pl": ("yeen", "i_vowel_glide"),
    }
    for lemma in EXPECTED_LEMMAS:
        for person, (suffix, process) in expected.items():
            candidate = generate_class_authorized_conj2_past(lemma, person)
            assert candidate is not None
            assert candidate.surface == lemma + suffix
            assert candidate.lemma == lemma
            assert candidate.part_of_speech == "verb"
            assert candidate.conjugation_class == "2A"
            assert candidate.tense_aspect == "past"
            assert candidate.mood == "indicative"
            assert candidate.person == person
            assert candidate.status == "reviewed_rule_derived"
            assert candidate.rule_id == f"MORPH-CONJ-IIA-CLASS-PST-ACT-001:{process}"
            assert candidate.correction_allowed is False

        one_singular = generate_class_authorized_conj2_past(lemma, "1sg")
        third_singular_m = generate_class_authorized_conj2_past(lemma, "3sg_m")
        second_singular = generate_class_authorized_conj2_past(lemma, "2sg")
        third_singular_f = generate_class_authorized_conj2_past(lemma, "3sg_f")
        assert one_singular is not None and third_singular_m is not None
        assert second_singular is not None and third_singular_f is not None
        assert one_singular.surface == third_singular_m.surface
        assert second_singular.surface == third_singular_f.surface
        assert any("Orwin" in item and "kariyay" in item and "Zorc" in item for item in third_singular_m.evidence_summary)
        assert any("Puglielli" in item and "wey kari-s-ay" in item and "Zorc" in item for item in third_singular_f.evidence_summary)


def test_generic_past_is_not_inferred_from_i_final_spelling() -> None:
    outsiders = ("zzabi", "qarqari", "nadiifi", "qurxi", "kari", "joogi")
    for lemma in outsiders:
        for person in EXPECTED_PERSONS:
            assert generate_class_authorized_conj2_past(lemma, person) is None

    for surface in (
        "zzabiyay", "zzabinnay", "zzabisay", "zzabiseen", "zzabiyeen",
        "qarqariyay", "qarqarinnay", "qarqarisay", "qarqariseen", "qarqariyeen",
        "nadiifiyay", "nadiifinnay", "nadiifisay", "nadiifiseen", "nadiifiyeen",
        "qurxiyay", "qurxinnay", "qurxisay", "qurxiseen", "qurxiyeen",
        "kariyay", "karinnay", "karisay", "kariseen", "kariyeen",
        "joogiyay", "jooginnay", "joogisay", "joogiseen", "joogiyeen",
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
    for person in EXPECTED_PERSONS:
        assert generate_class_authorized_conj2_past("mustaqbali", person) is None


def _assert_runtime_target(surface: str, lemma: str, person: str, process: str) -> None:
    direct = generate_class_authorized_conj2_past(lemma, person)
    assert direct is not None
    assert direct.surface == surface
    assert direct.rule_id == f"MORPH-CONJ-IIA-CLASS-PST-ACT-001:{process}"
    assert direct.correction_allowed is False

    candidates = [
        item
        for item in analyze_morphology(surface)
        if item.lemma == lemma and item.features.get("person") == person
    ]
    assert candidates
    assert {item.features.get("tense_aspect") for item in candidates} == {"past"}
    assert {item.features.get("conjugation_class") for item in candidates} == {"2A"}
    assert all(item.authority == "reviewed_rule_derived" for item in candidates)
    assert all(item.evidence_id == f"MORPH-CONJ-IIA-CLASS-PST-ACT-001:{process}" for item in candidates)
    assert all(item.correction_allowed is False for item in candidates)


def test_frozen_targets_are_reached_only_through_generic_past_rules() -> None:
    _assert_runtime_target("afceliyeen", "afceli", "3pl", "i_vowel_glide")
    _assert_runtime_target("buufiseen", "buufi", "2pl", "concatenative_elsewhere")
    _assert_runtime_target("buuxisay", "buuxi", "2sg", "i_t_assibilation")
    _assert_runtime_target("buubinnay", "buubi", "1pl", "i_n_weak_causative_manner_alternation")
    _assert_runtime_target("aaddiyay", "aaddi", "1sg", "i_vowel_glide")
    _assert_runtime_target("buufiyay", "buufi", "1sg", "i_vowel_glide")
    _assert_runtime_target("aammusiyay", "aammusi", "3sg_m", "i_vowel_glide")
    _assert_runtime_target("abhiyay", "abhi", "3sg_m", "i_vowel_glide")
    _assert_runtime_target("caafisay", "caafi", "3sg_f", "i_t_assibilation")
    _assert_runtime_target("bushisay", "bushi", "3sg_f", "i_t_assibilation")


def test_syncretic_surface_index_preserves_both_person_pairs() -> None:
    for surface, lemma in (("aammusiyay", "aammusi"), ("abhiyay", "abhi")):
        direct = [item for item in analyze_conj2_class_past_surface(surface) if item.lemma == lemma]
        assert {item.person for item in direct} >= {"1sg", "3sg_m"}
        analyzed = [item for item in analyze_morphology(surface) if item.lemma == lemma]
        assert {item.features.get("person") for item in analyzed} >= {"1sg", "3sg_m"}
        assert all(item.correction_allowed is False for item in direct)

    for surface, lemma in (("caafisay", "caafi"), ("bushisay", "bushi")):
        direct = [item for item in analyze_conj2_class_past_surface(surface) if item.lemma == lemma]
        assert {item.person for item in direct} >= {"2sg", "3sg_f"}
        analyzed = [item for item in analyze_morphology(surface) if item.lemma == lemma]
        assert {item.features.get("person") for item in analyzed} >= {"2sg", "3sg_f"}
        assert all(item.correction_allowed is False for item in direct)


def test_unresolved_targets_can_be_mechanical_candidates_but_not_attestations() -> None:
    for lemma in ("bushi", "butaaci"):
        candidate = generate_class_authorized_conj2_past(lemma, "1pl")
        assert candidate is not None
        assert candidate.surface == lemma + "nnay"
        assert candidate.status == "reviewed_rule_derived"
        assert candidate.correction_allowed is False

    v16 = v16_report()
    assert v16["benchmark"]["unresolved_target_lemmas"] == ["bushi", "butaaci"]
    assert v16["preauthorization"]["unresolved_target_lemmas"] == ["bushi", "butaaci"]

    candidate = generate_class_authorized_conj2_past("afceli", "1sg")
    assert candidate is not None
    assert candidate.surface == "afceliyay"
    assert candidate.status == "reviewed_rule_derived"
    assert candidate.correction_allowed is False

    v17 = v17_report()
    assert v17["benchmark"]["unresolved_target_lemmas"] == ["afceli"]
    assert v17["preauthorization"]["unresolved_target_lemmas"] == ["afceli"]


def test_frozen_benchmarks_preserve_history_and_improve_live_v19() -> None:
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

    v13 = v13_report()["combined"]
    assert v13["recognized_unique_surface_count"] == 2
    assert v13["deep_feature_matched_row_count"] == 2
    assert v13["authority_diagnostics"]["reviewed_exact_surfaces"] == []
    assert v13["authority_diagnostics"]["reviewed_rule_derived_surfaces"] == ["abhiyaa", "afceliyeen"]

    v14 = v14_report()
    assert v14["combined"]["recognized_unique_surface_count"] == 1
    assert v14["combined"]["deep_feature_matched_row_count"] == 1
    assert v14["benchmark"]["measured_result"]["somali_ai_combined_positive_surface_recognition"] == "0/1"

    v15 = v15_report()
    assert v15["combined"]["recognized_unique_surface_count"] == 1
    assert v15["combined"]["deep_feature_matched_row_count"] == 1
    assert v15["benchmark"]["measured_result"]["somali_ai_combined_positive_surface_recognition"] == "0/1"

    v16 = v16_report()
    assert v16["combined"]["recognized_unique_surface_count"] == 1
    assert v16["combined"]["deep_feature_matched_row_count"] == 1
    assert v16["combined"]["unknown_rejected_count"] == 8
    assert v16["benchmark"]["measured_result"]["somali_ai_combined_positive_surface_recognition"] == "0/1"
    assert v16["benchmark"]["measured_result"]["somali_ai_combined_deep_feature_rows"] == "0/1"

    v17 = v17_report()
    assert v17["combined"]["recognized_unique_surface_count"] == 2
    assert v17["combined"]["person_matched_unique_surface_count"] == 2
    assert v17["combined"]["deep_feature_matched_row_count"] == 2
    assert v17["combined"]["unknown_rejected_count"] == 8
    assert v17["master"]["recognized_unique_surface_count"] == 0
    assert v17["benchmark"]["measured_result"]["somali_ai_combined_positive_surface_recognition"] == "0/2"
    assert v17["benchmark"]["measured_result"]["somali_ai_combined_deep_feature_rows"] == "0/2"

    v18 = v18_report()
    live18 = v18["combined"]
    assert live18["recognized_unique_surface_count"] == 2
    assert live18["person_matched_unique_surface_count"] == 2
    assert live18["deep_feature_matched_row_count"] == 2
    assert live18["unknown_rejected_count"] == 8
    assert live18["syncretism_diagnostics"]["surface_has_1sg_analysis_count"] == 2
    assert live18["syncretism_diagnostics"]["surface_has_3sg_m_analysis_count"] == 2
    assert live18["syncretism_diagnostics"]["syncretic_surface_preserved_count"] == 2
    assert v18["master"]["recognized_unique_surface_count"] == 0
    historical18 = v18["benchmark"]["measured_result"]
    assert historical18["somali_ai_combined_positive_surface_recognition"] == "2/2"
    assert historical18["somali_ai_combined_3sg_m_person_matches"] == "0/2"
    assert historical18["somali_ai_combined_deep_feature_rows"] == "0/2"
    assert historical18["tested_head_commit"] == "32904a205ba8f789415e3b1e9acaa1e75227d1a2"

    v19 = v19_report()
    live19 = v19["combined"]
    assert live19["recognized_unique_surface_count"] == 2
    assert live19["lemma_matched_unique_surface_count"] == 2
    assert live19["pos_matched_unique_surface_count"] == 2
    assert live19["conjugation_matched_unique_surface_count"] == 2
    assert live19["tense_matched_unique_surface_count"] == 2
    assert live19["person_matched_unique_surface_count"] == 2
    assert live19["deep_feature_matched_row_count"] == 2
    assert live19["unknown_rejected_count"] == 8
    assert live19["authority_diagnostics"]["reviewed_exact_surfaces"] == []
    assert live19["authority_diagnostics"]["reviewed_rule_derived_surfaces"] == ["bushisay", "caafisay"]
    diagnostics19 = live19["syncretism_diagnostics"]
    assert diagnostics19["surface_has_2sg_analysis_count"] == 2
    assert diagnostics19["surface_has_3sg_f_analysis_count"] == 2
    assert diagnostics19["syncretic_surface_preserved_count"] == 2

    master19 = v19["master"]
    assert master19["recognized_unique_surface_count"] == 0
    assert master19["unknown_rejected_count"] == 8

    historical19 = v19["benchmark"]["measured_result"]
    assert historical19["somali_ai_combined_positive_surface_recognition"] == "2/2"
    assert historical19["somali_ai_combined_3sg_f_person_matches"] == "0/2"
    assert historical19["somali_ai_combined_deep_feature_rows"] == "0/2"
    assert historical19["somali_ai_existing_2sg_analysis"] == "2/2"
    assert historical19["somali_ai_2sg_3sg_f_syncretism_preserved"] == "0/2"
    assert historical19["somali_ai_master_positive_surface_recognition"] == "0/2"
    assert historical19["unknown_safety"] == "8/8 for combined runtime and master exact"
    assert historical19["tested_head_commit"] == "0d002a2076bb27f6d7eef12f5c437f75df65067a"
    assert historical19["workflow_run_id"] == 33500358318
    assert historical19["workflow_job_id"] == 99832016710
    assert v19["preauthorization"]["generic_3sg_feminine_past_authorized_at_freeze"] is False
