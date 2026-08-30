from src.morphology_candidates import analyze_surface_form


def test_exact_source_backed_definite_forms_are_analyzed():
    expected = {
        "buugga": ("buug", "masculine"),
        "marada": ("maro", "feminine"),
        "badda": ("bad", "feminine"),
        "qodaxda": ("qodax", "feminine"),
        "bacda": ("bac", "feminine"),
        "usha": ("ul", "feminine"),
        "isha": ("il", "feminine"),
        "bisha": ("bil", "feminine"),
    }
    for surface, (lemma, gender) in expected.items():
        analyses = analyze_surface_form(surface)
        assert len(analyses) == 1
        assert analyses[0].lemma == lemma
        assert analyses[0].analysis_type == "definite_singular"
        assert analyses[0].features["gender"] == gender
        assert analyses[0].executable is False


def test_plural_patterns_are_lemma_specific():
    expected = {
        "buugag": "buug",
        "kabo": "kab",
        "gacmo": "gacan",
        "mindiyo": "mindi",
    }
    processes = set()
    for surface, lemma in expected.items():
        analysis = analyze_surface_form(surface)[0]
        assert analysis.lemma == lemma
        assert analysis.analysis_type == "plural"
        processes.add(analysis.raw["surface_process"])
    assert len(processes) == 4


def test_possessive_forms_keep_possessor_information():
    buug = analyze_surface_form("buuggayga")[0]
    dal = analyze_surface_form("dalkeenna")[0]
    ul = analyze_surface_form("ushiinna")[0]
    assert buug.features["possessor_person"] == "1sg"
    assert dal.features["possessor_person"] == "1pl_inclusive"
    assert ul.features["possessor_person"] == "2pl"


def test_gabadha_is_marked_as_rule_derived_not_explicit_table_example():
    analysis = analyze_surface_form("gabadha")[0]
    assert analysis.lemma == "gabadh"
    assert analysis.evidence_type == "derived_from_qaamuus_article_rule_plus_reviewed_gabadh_lemma"
    assert analysis.status == "source_rule_derived_reviewed"
    assert analysis.executable is False


def test_casefold_matching_does_not_change_the_reported_surface():
    analysis = analyze_surface_form("BUUGGA")[0]
    assert analysis.surface == "buugga"
    assert analysis.lemma == "buug"


def test_unreviewed_inflected_looking_form_is_not_guessed():
    assert analyze_surface_form("buugtayda") == ()
    assert analyze_surface_form("magacaanlaaqoon") == ()
