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


def test_everyday_seed_preserves_inan_gender_homographs():
    result = lookup_word("inan")
    assert result.known
    assert len(result.exact_entries) == 2
    assert {entry.homograph_index for entry in result.exact_entries} == {1, 2}
    assert {entry.source_pos for entry in result.exact_entries} == {"m.l", "m.dh"}


def test_everyday_seed_preserves_kor_noun_and_verb_analyses():
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
