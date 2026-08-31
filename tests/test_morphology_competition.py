from src.morphology_competition import (
    SAFETY_PROBES,
    build_scorecard,
    cross_source_backlog,
)
from src.morphology_candidates import analyze_surface_form


def test_competitive_scorecard_measures_real_reviewed_and_external_breadth():
    scorecard = build_scorecard()
    assert scorecard.reviewed_surface_count >= 150
    assert scorecard.reviewed_lemma_count >= 10
    assert scorecard.giellalt_candidate_row_count >= 12_000
    assert scorecard.giellalt_candidate_unique_lemma_count >= 10_000
    assert scorecard.giellalt_reported_lemma_baseline == 14_500
    assert scorecard.reviewed_breadth_gap_to_reported_giellalt > 0


def test_reviewed_morphology_tracks_features_not_just_lemma_presence():
    dimensions = set(build_scorecard().reviewed_feature_dimensions)
    assert "part_of_speech" in dimensions
    assert "conjugation_class" in dimensions
    assert "tense_aspect" in dimensions
    assert dimensions & {"person", "possible_persons"}


def test_safety_probes_remain_unknown_instead_of_being_guessed():
    scorecard = build_scorecard()
    assert scorecard.safety_probe_count == len(SAFETY_PROBES)
    assert scorecard.safety_probe_guess_count == 0
    assert scorecard.safety_probe_guess_rate == 0.0
    for probe in SAFETY_PROBES:
        assert analyze_surface_form(probe) == ()


def test_cross_source_backlog_is_review_only_and_excludes_reviewed_lemmas():
    backlog = cross_source_backlog()
    for item in backlog:
        assert item.promotion_allowed is False
        assert item.candidate_types
        assert item.vocabulary_statuses
        assert item.source_paths
        assert analyze_surface_form(item.lemma) == ()


def test_backlog_priority_is_deterministic():
    backlog = cross_source_backlog()
    assert list(backlog) == sorted(backlog, key=lambda item: (-item.priority, item.lemma))
