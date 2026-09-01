from __future__ import annotations

from src.morphology_paradigm_v16 import report


def test_v16_untouched_1pl_past_baseline_is_zero_before_activation() -> None:
    result = report()
    combined = result["combined"]
    master = result["master"]
    authority = combined["authority_diagnostics"]

    assert combined["recognized_unique_surface_count"] == 0
    assert combined["lemma_matched_unique_surface_count"] == 0
    assert combined["pos_matched_unique_surface_count"] == 0
    assert combined["conjugation_matched_unique_surface_count"] == 0
    assert combined["tense_matched_unique_surface_count"] == 0
    assert combined["person_matched_unique_surface_count"] == 0
    assert combined["deep_feature_matched_row_count"] == 0
    assert authority["reviewed_exact_surfaces"] == []
    assert authority["reviewed_rule_derived_surfaces"] == []
    assert master["recognized_unique_surface_count"] == 0
    assert combined["unknown_rejected_count"] == 8
    assert master["unknown_rejected_count"] == 8
