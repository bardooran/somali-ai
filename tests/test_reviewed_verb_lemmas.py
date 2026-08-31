from src.morphology_candidates import (
    analyze_surface_form,
    reviewed_candidates_for_lemma,
)
from src.morphology_competition import build_scorecard, cross_source_backlog


EXPECTED_CLASSES = {
    "tag": "I",
    "qor": "I",
    "xir": "I",
    "jab": "I",
    "jabi": "II",
    "adkee": "II",
    "cidlee": "II",
    "jabso": "III",
    "adkow": "III",
    "yarow": "III",
}


def test_reviewed_everyday_verb_headwords_are_exactly_analyzable():
    for lemma, expected_class in EXPECTED_CLASSES.items():
        hits = [
            hit for hit in analyze_surface_form(lemma)
            if hit.analysis_type == "verb_lemma"
        ]
        assert hits, lemma
        assert {hit.lemma for hit in hits} == {lemma}
        assert {hit.features["conjugation_class"] for hit in hits} == {expected_class}
        assert all(hit.status == "source_backed" for hit in hits)


def test_headword_records_do_not_authorize_open_ended_paradigm_generation():
    for unsupported in ("qorXYZ", "yarowXYZ", "cidleeXYZ"):
        assert analyze_surface_form(unsupported) == ()


def test_yarow_is_canonical_lemma_while_yaraad_remains_derived_past_stem():
    headword = reviewed_candidates_for_lemma("yarow", analysis_type="verb_lemma")
    assert len(headword) == 1
    assert headword[0].features["derived_past_stem"] == "yaraad"

    past = analyze_surface_form("yaraadeen")
    assert any(hit.features.get("derivation") == "yarow_plus_at" for hit in past)


def test_competition_backlog_no_longer_misclassifies_yarow_as_unreviewed():
    assert "yarow" not in {item.lemma for item in cross_source_backlog()}
    assert build_scorecard().reviewed_lemma_count >= 50
