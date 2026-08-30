from src.lexicon import lookup_word


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


def test_ukun_can_be_known_from_reviewed_variant_layer_before_exact_seed_entry():
    result = lookup_word("ukun")
    assert result.known
    assert result.exact_entries == ()
    assert any(item.preference == "co_preferred" for item in result.regional_analyses)


def test_inflected_form_is_not_silently_lemmatized_yet():
    result = lookup_word("gabadha")
    assert not result.known
    assert result.exact_entries == ()
    assert "no analysis is guessed" in result.note


def test_unknown_word_is_not_guessed():
    result = lookup_word("erey-aan-jirin")
    assert not result.known
    assert result.exact_entries == ()
    assert result.regional_analyses == ()
