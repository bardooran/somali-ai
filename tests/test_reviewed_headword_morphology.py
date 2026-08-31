from src.morphology_candidates import analyze_surface_form, reviewed_candidates_for_lemma


def _pos(analyses):
    return {candidate.features.get("part_of_speech") for candidate in analyses}


def test_inan_and_gaban_preserve_reviewed_gender_homographs():
    inan = analyze_surface_form("inan")
    gaban = analyze_surface_form("gaban")

    assert len(inan) == 2
    assert {candidate.features.get("gender") for candidate in inan} == {
        "masculine",
        "feminine",
    }
    assert {candidate.raw.get("homograph_index") for candidate in inan} == {1, 2}

    assert len(gaban) == 2
    assert {candidate.features.get("gender") for candidate in gaban} == {
        "masculine",
        "feminine",
    }
    assert {candidate.raw.get("homograph_index") for candidate in gaban} == {1, 2}


def test_kor_and_gabay_preserve_noun_verb_ambiguity():
    kor = analyze_surface_form("kor")
    gabay = analyze_surface_form("gabay")

    assert {"noun", "verb"} <= _pos(kor)
    assert {"noun", "verb"} <= _pos(gabay)

    kor_verb = [candidate for candidate in kor if candidate.features.get("part_of_speech") == "verb"]
    gabay_verb = [candidate for candidate in gabay if candidate.features.get("part_of_speech") == "verb"]
    assert any(candidate.features.get("conjugation_class") == "I" for candidate in kor_verb)
    assert any(candidate.features.get("conjugation_class") == "I" for candidate in gabay_verb)


def test_duwan_family_keeps_explicit_dictionary_classes():
    duwan = analyze_surface_form("duwan")
    duwanow = analyze_surface_form("duwanow")

    assert any(candidate.features.get("conjugation_class") == "IV" for candidate in duwan)
    assert any(candidate.features.get("conjugation_class") == "III" for candidate in duwanow)
    assert all(candidate.executable is False for candidate in (*duwan, *duwanow))


def test_source_backed_noun_headwords_are_exactly_recognized():
    expected = {
        "diirad": ("noun", "feminine"),
        "diiradeeye": ("noun", "masculine"),
        "magacuyaal": ("noun", "masculine"),
        "magudbe": ("noun", "masculine"),
        "yeele": ("noun", "masculine"),
        "gabadh": ("noun", "feminine"),
        "gabar": ("noun", "feminine"),
        "beed": ("noun", "masculine"),
    }
    for surface, (part_of_speech, gender) in expected.items():
        analyses = analyze_surface_form(surface)
        assert any(
            candidate.features.get("part_of_speech") == part_of_speech
            and candidate.features.get("gender") == gender
            for candidate in analyses
        )


def test_headword_signatures_do_not_authorize_guessed_inflections():
    for form in (
        "inanXYZ",
        "gabanXYZ",
        "korXYZ",
        "gabayXYZ",
        "duwanowXYZ",
        "magacuyaalloXYZ",
    ):
        assert analyze_surface_form(form) == ()


def test_reviewed_lemma_lookup_exposes_all_homograph_records():
    inan = reviewed_candidates_for_lemma("inan", "noun_lemma")
    kor = reviewed_candidates_for_lemma("kor")

    assert len(inan) == 2
    assert {"noun", "verb"} <= _pos(kor)
