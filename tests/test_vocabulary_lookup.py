from src.vocabulary import lookup_word


def test_ka_preserves_three_dictionary_analyses():
    result = lookup_word("ka")
    assert result.known
    assert len(result.exact_entries) == 3
    assert {entry.homograph_index for entry in result.exact_entries} == {1, 2, 3}
    assert "multiple dictionary analyses" in result.note


def test_kee_preserves_two_dictionary_analyses():
    result = lookup_word("kee")
    assert len(result.exact_entries) == 2
    assert {entry.homograph_index for entry in result.exact_entries} == {1, 2}


def test_gabadh_has_dictionary_and_preferred_profile_evidence():
    result = lookup_word("gabadh")
    assert result.known
    assert len(result.exact_entries) == 1
    assert result.exact_entries[0].source_pos == "m.dh"
    assert any(item.preference == "preferred" for item in result.regional_analyses)


def test_gabar_is_dictionary_headword_and_recognized_variant():
    result = lookup_word("gabar")
    assert result.known
    assert result.exact_entries[0].homograph_index == 2
    assert any(item.preference == "recognized_variant" for item in result.regional_analyses)


def test_beed_has_source_definition_and_co_preferred_status():
    result = lookup_word("beed")
    assert result.exact_entries[0].somali_definition_summary == "Ukun."
    assert any(item.preference == "co_preferred" for item in result.regional_analyses)


def test_ukun_can_be_known_from_reviewed_variant_layer_before_exact_vocabulary_entry():
    result = lookup_word("ukun")
    assert result.known
    assert result.exact_entries == ()
    assert any(item.preference == "co_preferred" for item in result.regional_analyses)


def test_everyday_vocabulary_preserves_inan_gender_homographs():
    result = lookup_word("inan")
    assert result.known
    assert len(result.exact_entries) == 2
    assert {entry.homograph_index for entry in result.exact_entries} == {1, 2}
    assert {entry.source_pos for entry in result.exact_entries} == {"m.l", "m.dh"}


def test_everyday_vocabulary_preserves_kor_noun_and_verb_analyses():
    result = lookup_word("kor")
    assert len(result.exact_entries) == 2
    assert {entry.source_pos for entry in result.exact_entries} == {"m.l", "f.mg1"}


def test_gabay_preserves_poetry_noun_and_verb_analyses():
    result = lookup_word("gabay")
    assert len(result.exact_entries) == 2
    assert {entry.domain for entry in result.exact_entries} == {"suugaan"}
    assert {entry.source_pos for entry in result.exact_entries} == {"m.l", "f.mg1"}


def test_duwan_combines_dictionary_evidence_with_regional_variant_status():
    result = lookup_word("duwan")
    assert result.known
    assert len(result.exact_entries) == 1
    assert result.exact_entries[0].source_pos == "f.mg4"
    assert any(item.preference == "recognized_variant" for item in result.regional_analyses)


def test_dugan_is_preferred_regional_form_without_claiming_qaamuus_headword_evidence():
    result = lookup_word("dugan")
    assert result.known
    assert result.exact_entries == ()
    assert any(item.preference == "preferred" for item in result.regional_analyses)


def test_gabadha_links_to_gabadh_through_reviewed_morphology_mapping():
    result = lookup_word("gabadha")
    assert result.known
    assert result.exact_entries == ()
    assert len(result.morphology_candidates) == 1
    candidate = result.morphology_candidates[0]
    assert candidate.lemma == "gabadh"
    assert candidate.analysis_type == "definite_singular"
    assert candidate.features["gender"] == "feminine"
    assert candidate.executable is False
    assert "stored evidence" in result.note


def test_buugga_links_to_buug_without_open_ended_suffix_stripping():
    result = lookup_word("buugga")
    assert result.known
    candidate = result.morphology_candidates[0]
    assert candidate.lemma == "buug"
    assert candidate.features["definiteness"] == "definite"
    assert candidate.features["gender"] == "masculine"


def test_reviewed_plural_mappings_preserve_irregular_patterns():
    expected = {
        "buugag": "buug",
        "kabo": "kab",
        "gacmo": "gacan",
        "mindiyo": "mindi",
    }
    for surface, lemma in expected.items():
        result = lookup_word(surface)
        assert result.known
        assert len(result.morphology_candidates) == 1
        assert result.morphology_candidates[0].lemma == lemma
        assert result.morphology_candidates[0].analysis_type == "plural"


def test_source_attested_feminine_article_surfaces_return_lemmas():
    expected = {
        "marada": "maro",
        "badda": "bad",
        "qodaxda": "qodax",
        "bacda": "bac",
        "usha": "ul",
        "isha": "il",
        "bisha": "bil",
    }
    for surface, lemma in expected.items():
        result = lookup_word(surface)
        assert result.morphology_candidates[0].lemma == lemma
        assert result.morphology_candidates[0].analysis_type == "definite_singular"


def test_source_attested_possessive_surfaces_return_possessor_features():
    first_person = lookup_word("buuggayga").morphology_candidates[0]
    inclusive = lookup_word("dalkeenna").morphology_candidates[0]
    second_plural = lookup_word("ushiinna").morphology_candidates[0]
    assert first_person.lemma == "buug"
    assert first_person.features["possessor_person"] == "1sg"
    assert inclusive.lemma == "dal"
    assert inclusive.features["possessor_person"] == "1pl_inclusive"
    assert second_plural.lemma == "ul"
    assert second_plural.features["possessor_person"] == "2pl"


def test_unknown_inflected_looking_word_is_still_not_guessed():
    result = lookup_word("ereygaqiyaaska")
    assert not result.known
    assert result.exact_entries == ()
    assert result.morphology_candidates == ()
    assert "no analysis is guessed" in result.note


def test_unknown_word_is_not_guessed():
    result = lookup_word("erey-aan-jirin")
    assert not result.known
    assert result.exact_entries == ()
    assert result.morphology_candidates == ()
    assert result.regional_analyses == ()
