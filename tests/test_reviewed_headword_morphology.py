from src.morphology_candidates import analyze_surface_form, reviewed_candidates_for_lemma
from src.morphology_competition import build_scorecard, cross_source_backlog


def _pos(analyses):
    return {candidate.features.get("part_of_speech") for candidate in analyses}


def _records(form, *record_ids):
    wanted = set(record_ids)
    return [candidate for candidate in analyze_surface_form(form) if candidate.record_id in wanted]


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


def test_fal_keeps_two_noun_senses_and_class_i_verb_homograph():
    records = _records("fal", "QHEAD-019", "QHEAD-020", "QHEAD-021")
    assert len(records) == 3
    assert {candidate.raw.get("homograph_index") for candidate in records} == {1, 2, 3}
    assert _pos(records) == {"noun", "verb"}
    verb = next(candidate for candidate in records if candidate.record_id == "QHEAD-021")
    assert verb.features.get("conjugation_class") == "I"
    assert verb.features.get("transitivity") == "transitive"


def test_qabow_keeps_noun_and_two_distinct_verb_classes():
    records = _records("qabow", "QHEAD-022", "QHEAD-023", "QHEAD-024")
    assert len(records) == 3
    assert {candidate.raw.get("homograph_index") for candidate in records} == {1, 2, 3}
    assert _pos(records) == {"noun", "verb"}
    verb_classes = {
        candidate.features.get("conjugation_class")
        for candidate in records
        if candidate.features.get("part_of_speech") == "verb"
    }
    assert verb_classes == {"I", "IV"}


def test_gudbe_preserves_lexical_and_grammar_term_noun_homographs():
    records = _records("gudbe", "QHEAD-025", "QHEAD-026")
    assert len(records) == 2
    assert {candidate.raw.get("homograph_index") for candidate in records} == {1, 2}
    assert _pos(records) == {"noun"}
    grammar = next(candidate for candidate in records if candidate.record_id == "QHEAD-026")
    assert grammar.features.get("semantic_domain") == "naxwe"
    assert grammar.features.get("possible_use") == "predicate"


def test_duwanaan_is_reviewed_as_source_stated_verbal_noun():
    records = _records("duwanaan", "QHEAD-027")
    assert len(records) == 1
    record = records[0]
    assert record.features.get("part_of_speech") == "noun"
    assert record.features.get("gender") == "feminine"
    assert record.features.get("morphology_type") == "verbal_noun"
    assert record.features.get("related_lemma") == "duwan"


def test_fog_and_dhow_keep_qaamuus_class_iv_state_verb_analysis():
    fog = _records("fog", "QHEAD-028")
    dhow = _records("dhow", "QHEAD-029")
    assert len(fog) == 1
    assert len(dhow) == 1
    for record in (*fog, *dhow):
        assert record.features.get("part_of_speech") == "verb"
        assert record.features.get("conjugation_class") == "IV"
        assert record.features.get("transitivity") == "intransitive"


def test_direct_qaamuus_mirror_records_preserve_provenance_and_nonexecution():
    ids = {f"QHEAD-{number:03d}" for number in range(19, 30)}
    found = []
    for surface in ("fal", "qabow", "gudbe", "duwanaan", "fog", "dhow"):
        found.extend(candidate for candidate in analyze_surface_form(surface) if candidate.record_id in ids)
    assert {candidate.record_id for candidate in found} == ids
    assert all(candidate.executable is False for candidate in found)
    assert all(candidate.raw.get("source_mirror") == "bardooran/goobolabs" for candidate in found)
    assert all(candidate.raw.get("source_family") == "qaamuus_2012" for candidate in found)
    assert all(candidate.raw.get("source_path", "").startswith("resources/qaamuus/") for candidate in found)


def test_taxonomy_disagreement_stays_visible_instead_of_being_auto_resolved():
    backlog_by_lemma = {item.lemma: item for item in cross_source_backlog()}
    assert "fog" in backlog_by_lemma
    assert "adjective" in backlog_by_lemma["fog"].candidate_types
    assert "verb" in backlog_by_lemma["fog"].reviewed_types

    assert "dhow" in backlog_by_lemma
    assert set(backlog_by_lemma["dhow"].candidate_types) & {"adjective", "noun"}
    assert "verb" in backlog_by_lemma["dhow"].reviewed_types

    assert build_scorecard().reviewed_giellalt_type_mismatch_lemma_count >= 2


def test_headword_signatures_do_not_authorize_guessed_inflections():
    for form in (
        "inanXYZ",
        "gabanXYZ",
        "korXYZ",
        "gabayXYZ",
        "duwanowXYZ",
        "magacuyaalloXYZ",
        "falXYZ",
        "qabowXYZ",
        "gudbeXYZ",
        "duwanaanXYZ",
        "fogXYZ",
        "dhowXYZ",
    ):
        assert analyze_surface_form(form) == ()


def test_reviewed_lemma_lookup_exposes_all_homograph_records():
    inan = reviewed_candidates_for_lemma("inan", "noun_lemma")
    kor = reviewed_candidates_for_lemma("kor")
    fal = reviewed_candidates_for_lemma("fal")
    qabow = reviewed_candidates_for_lemma("qabow")

    assert len(inan) == 2
    assert {"noun", "verb"} <= _pos(kor)
    assert {"noun", "verb"} <= _pos(fal)
    assert {"noun", "verb"} <= _pos(qabow)
