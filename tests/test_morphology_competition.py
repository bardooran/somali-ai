from src.morphology_competition import (
    SAFETY_PROBES,
    _ambiguous_surfaces,
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
    assert scorecard.giellalt_candidate_unique_lemma_type_count >= (
        scorecard.giellalt_candidate_unique_lemma_count
    )
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


def test_cross_source_backlog_is_review_only_and_type_aware():
    backlog = cross_source_backlog()
    for item in backlog:
        assert item.promotion_allowed is False
        assert item.candidate_types
        assert item.vocabulary_statuses
        assert item.source_paths

        reviewed_types = {
            candidate.features.get("part_of_speech")
            for candidate in analyze_surface_form(item.lemma)
            if candidate.features.get("part_of_speech")
        }
        assert set(item.candidate_types).isdisjoint(reviewed_types)
        assert set(item.reviewed_types) <= reviewed_types


def test_backlog_keeps_unreviewed_pos_when_same_lemma_has_reviewed_pos():
    reviewed = (
        {
            "surface": "tusaale",
            "lemma": "tusaale",
            "analysis_type": "noun_lemma",
            "features": {"part_of_speech": "noun"},
        },
    )
    giellalt = (
        {
            "lemma": "tusaale",
            "record_type": "noun",
            "source_path": "nouns.lexc",
        },
        {
            "lemma": "tusaale",
            "record_type": "verb",
            "source_path": "verbs.lexc",
        },
    )
    vocabulary = (
        {
            "lemma": "tusaale",
            "status": "source_backed",
            "domain": "naxwe",
        },
    )

    backlog = cross_source_backlog(
        reviewed=reviewed,
        giellalt=giellalt,
        vocabulary=vocabulary,
    )
    assert len(backlog) == 1
    assert backlog[0].lemma == "tusaale"
    assert backlog[0].reviewed_types == ("noun",)
    assert backlog[0].candidate_types == ("verb",)


def test_homographs_count_as_morphological_ambiguity():
    records = (
        {
            "surface": "kor",
            "lemma": "kor",
            "analysis_type": "noun_lemma",
            "homograph_index": 1,
            "features": {"part_of_speech": "noun", "gender": "masculine"},
        },
        {
            "surface": "kor",
            "lemma": "kor",
            "analysis_type": "verb_lemma",
            "homograph_index": 2,
            "features": {"part_of_speech": "verb", "conjugation_class": "I"},
        },
        {
            "surface": "inan",
            "lemma": "inan",
            "analysis_type": "noun_lemma",
            "homograph_index": 1,
            "features": {"part_of_speech": "noun", "gender": "masculine"},
        },
        {
            "surface": "inan",
            "lemma": "inan",
            "analysis_type": "noun_lemma",
            "homograph_index": 2,
            "features": {"part_of_speech": "noun", "gender": "feminine"},
        },
    )
    assert _ambiguous_surfaces(records) == {"kor", "inan"}


def test_live_scorecard_counts_new_reviewed_homographs():
    scorecard = build_scorecard()
    assert scorecard.reviewed_ambiguous_surface_count >= 143
    assert len(analyze_surface_form("inan")) >= 2
    assert len(analyze_surface_form("gaban")) >= 2
    assert {"noun", "verb"} <= {
        item.features.get("part_of_speech")
        for item in analyze_surface_form("kor")
    }
    assert {"noun", "verb"} <= {
        item.features.get("part_of_speech")
        for item in analyze_surface_form("gabay")
    }


def test_scorecard_tracks_lemma_type_overlap_separately_from_lemma_overlap():
    scorecard = build_scorecard()
    assert scorecard.reviewed_giellalt_shared_lemma_count >= 1
    assert scorecard.reviewed_giellalt_shared_lemma_type_count >= 1
    assert scorecard.reviewed_giellalt_type_mismatch_lemma_count >= 0
    assert scorecard.reviewed_giellalt_shared_lemma_type_count <= (
        scorecard.giellalt_candidate_unique_lemma_type_count
    )
    assert scorecard.cross_source_backlog_analysis_count >= (
        scorecard.cross_source_backlog_count
    )


def test_backlog_priority_is_deterministic():
    backlog = cross_source_backlog()
    assert list(backlog) == sorted(backlog, key=lambda item: (-item.priority, item.lemma))
