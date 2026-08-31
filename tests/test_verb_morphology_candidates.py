from src.vocabulary import lookup_word
from src.morphology_candidates import analyze_surface_form


def test_cun_present_and_past_syncretism_is_preserved():
    present = analyze_surface_form("cunaa")
    past = analyze_surface_form("cunay")

    assert len(present) == 1
    assert present[0].lemma == "cun"
    assert present[0].features["possible_persons"] == ["1sg", "3sg_m"]
    assert present[0].features["tense_aspect"] == "joogto_caadaley"

    assert len(past) == 1
    assert past[0].lemma == "cun"
    assert past[0].features["possible_persons"] == ["1sg", "3sg_m"]
    assert past[0].features["tense_aspect"] == "tagto"


def test_cun_t_forms_preserve_2sg_3sg_f_ambiguity():
    present = analyze_surface_form("cuntaa")[0]
    progressive = analyze_surface_form("cunaysaa")[0]
    past = analyze_surface_form("cuntay")[0]

    for analysis in (present, progressive, past):
        assert analysis.lemma == "cun"
        assert analysis.features["possible_persons"] == ["2sg", "3sg_f"]
        assert analysis.executable is False


def test_cun_plural_person_forms_are_explicit_not_guessed():
    expected = {
        "cunnaa": "1pl",
        "cuntaan": "2pl",
        "cunaan": "3pl",
        "cunaynaa": "1pl",
        "cunaysaan": "2pl",
        "cunayaan": "3pl",
        "cunnay": "1pl",
        "cunteen": "2pl",
        "cuneen": "3pl",
    }
    for surface, person in expected.items():
        analysis = analyze_surface_form(surface)[0]
        assert analysis.lemma == "cun"
        assert analysis.features["person"] == person


def test_cunin_is_kept_context_required_because_it_has_multiple_functions():
    analysis = analyze_surface_form("cunin")[0]
    assert analysis.lemma == "cun"
    assert analysis.status == "source_backed_context_required"
    assert "past_negative_after_ma" in analysis.features["possible_functions"]
    assert "negative_imperative_2sg" in analysis.features["possible_functions"]


def test_dheh_multi_stem_source_forms_map_to_one_lemma():
    expected = {
        "dheh": "imperative",
        "dhaha": "imperative",
        "dhihi": "masdar",
        "oran": "masdar_or_suppletive_stem",
        "iraahdaa": "finite_verb",
        "tiraahdaa": "finite_verb",
        "yiraahdaa": "finite_verb",
        "niraahdaa": "finite_verb",
        "iri": "finite_verb",
        "tiri": "finite_verb",
        "yiri": "finite_verb",
        "niri": "finite_verb",
    }
    for surface, analysis_type in expected.items():
        analysis = analyze_surface_form(surface)[0]
        assert analysis.lemma == "dheh"
        assert analysis.analysis_type == analysis_type
        assert analysis.executable is False


def test_jigjiga_dheh_forms_are_native_reviewed_not_misattributed_to_qaamuus():
    yidhi = analyze_surface_form("yidhi")[0]
    tidhi = analyze_surface_form("tidhi")[0]
    odhan = analyze_surface_form("odhan")[0]

    assert yidhi.lemma == "dheh"
    assert yidhi.features["preference"] == "preferred"
    assert yidhi.evidence_type == "native_speaker_project_review"
    assert "Project native review" in yidhi.source

    assert tidhi.features["possible_persons"] == ["2sg", "3sg_f"]
    assert tidhi.features["preference"] == "preferred"

    assert odhan.features["preference"] == "preferred"
    assert odhan.evidence_type == "native_speaker_project_review_plus_source_variant_evidence"


def test_lookup_combines_yidhi_morphology_and_regional_preference():
    result = lookup_word("yidhi")
    assert result.known
    assert result.morphology_candidates[0].lemma == "dheh"
    assert any(item.preference == "preferred" for item in result.regional_analyses)


def test_lookup_combines_yiri_morphology_and_recognized_variant_status():
    result = lookup_word("yiri")
    assert result.known
    assert result.morphology_candidates[0].lemma == "dheh"
    assert any(item.preference == "recognized_variant" for item in result.regional_analyses)


def test_unreviewed_verb_like_surface_is_not_guessed():
    assert analyze_surface_form("cunaytaan") == ()
    assert analyze_surface_form("yidhiyow") == ()
