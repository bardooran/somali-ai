from src.morphology_benchmark import BENCHMARK_PATH, build_score, load_cases, report
from src.morphology_candidates import analyze_surface_form


FROZEN_HOLDOUTS = {
    "aabburan",
    "aabee",
    "qoran",
    "xiran",
    "toosan",
    "qorrax",
    "xirfad",
    "jirrid",
    "qorshe",
    "hoose",
}


def test_benchmark_v1_has_fixed_split_sizes_and_unique_ids():
    cases = load_cases()
    assert BENCHMARK_PATH.is_file()
    assert len(cases) == 41
    assert len({case["id"] for case in cases}) == 41
    assert sum(case["split"] == "development" for case in cases) == 25
    assert sum(case["split"] == "holdout" for case in cases) == 10
    assert sum(case["split"] == "unknown" for case in cases) == 6


def test_frozen_holdout_surface_set_is_stable_and_not_in_runtime_baseline():
    cases = load_cases()
    holdouts = {
        str(case["surface"]).casefold()
        for case in cases
        if case["split"] == "holdout"
    }
    assert holdouts == FROZEN_HOLDOUTS
    # Benchmark v1 freezes these before direct promotion. If this fails later,
    # move to a new benchmark version rather than silently training on v1.
    assert all(analyze_surface_form(surface) == () for surface in holdouts)


def test_development_split_is_fully_covered_without_false_analyses():
    score = build_score()
    assert score.development.case_coverage == 1.0
    assert score.development.analysis_recall == 1.0
    assert score.development.analysis_precision == 1.0
    assert score.development.false_analysis_count == 0


def test_v1_holdout_starts_as_a_real_unseen_generalization_gap():
    score = build_score()
    assert score.holdout.positive_case_count == 10
    assert score.holdout.covered_case_count == 0
    assert score.holdout.case_coverage == 0.0
    assert score.holdout.analysis_recall == 0.0


def test_unknown_probes_remain_unjudged():
    score = build_score()
    assert score.unknown_case_count == 6
    assert score.unknown_unsafe_count == 0
    assert score.unknown_safety_rate == 1.0


def test_ambiguity_metric_rewards_preserving_multiple_valid_analyses():
    score = build_score()
    assert score.ambiguous_case_count >= 6
    assert score.ambiguity_preserved_count >= 4
    assert 0.0 <= score.ambiguity_preservation_rate <= 1.0


def test_giellalt_candidate_metric_is_explicitly_not_a_runtime_win():
    score = build_score()
    payload = report()
    assert score.giellalt_candidate_expected_type_count > 0
    assert 0.0 <= score.giellalt_candidate_type_coverage <= 1.0
    assert score.giellalt_compiled_fst_evaluated is False
    assert score.runtime_winner_declared is False
    assert payload["interpretation"]["giellalt_candidate_inventory_is_not_compiled_fst"] is True
    assert payload["interpretation"]["runtime_model_vs_model_claim_allowed"] is False
