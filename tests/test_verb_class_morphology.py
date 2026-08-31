from src.vocabulary import lookup_word
from src.morphology_candidates import analyze_surface_form


def test_class_i_jab_signature_links_past_forms_to_lemma():
    masculine = analyze_surface_form("jabay")[0]
    feminine = analyze_surface_form("jabtay")[0]
    assert masculine.lemma == "jab"
    assert feminine.lemma == "jab"
    assert masculine.features["conjugation_class"] == "I"
    assert feminine.features["conjugation_class"] == "I"
    assert masculine.executable is False


def test_class_ii_preserves_jabi_and_adkee_families():
    jabi = analyze_surface_form("jabisay")[0]
    adkee = analyze_surface_form("adkeeyay")[0]
    assert jabi.lemma == "jabi"
    assert jabi.features["conjugation_class"] == "II"
    assert adkee.lemma == "adkee"
    assert adkee.features["conjugation_class"] == "II"
    assert adkee.features["possible_persons"] == ["1sg", "3sg_m"]


def test_class_iii_preserves_reflexive_or_inchoative_families():
    jabso = analyze_surface_form("jabsaday")[0]
    adkow = analyze_surface_form("adkaatay")[0]
    assert jabso.lemma == "jabso"
    assert jabso.features["conjugation_class"] == "III"
    assert adkow.lemma == "adkow"
    assert adkow.features["conjugation_class"] == "III"


def test_fal_sifo_iv_a_and_iv_b_are_not_treated_as_plain_adjectives():
    adag = analyze_surface_form("adagtahay")[0]
    fiican = analyze_surface_form("fiicanyahay")[0]
    assert adag.lemma == "adag"
    assert adag.analysis_type == "fal_sifo_finite"
    assert adag.features["conjugation_class"] == "IVa"
    assert adag.features["possible_persons"] == ["2sg", "3sg_f"]
    assert fiican.lemma == "fiican"
    assert fiican.features["conjugation_class"] == "IVb"
    assert fiican.features["person"] == "3sg_m"


def test_maydh_family_includes_native_reviewed_ongoing_surfaces():
    base = analyze_surface_form("maydh")[0]
    short_surface = analyze_surface_form("maydho")[0]
    ongoing = analyze_surface_form("maydhayaa")[0]
    ongoing_variant = analyze_surface_form("maydhanayaa")[0]

    assert base.lemma == "maydh"
    assert short_surface.lemma == "maydh"
    assert ongoing.lemma == "maydh"
    assert ongoing_variant.lemma == "maydh"
    assert ongoing.features["tense_aspect"] == "ongoing_current"
    assert ongoing.features["possible_persons"] == ["1sg", "3sg_m"]
    assert ongoing_variant.features["tense_aspect"] == "ongoing_current"
    assert ongoing.evidence_type == "native_speaker_project_review"
    assert ongoing.executable is False


def test_maydhayaadee_preserves_reviewed_discourse_nuance_without_overclaiming():
    analysis = analyze_surface_form("maydhayaadee")[0]
    assert analysis.lemma == "maydh"
    assert analysis.features["person"] == "1sg_in_reviewed_example"
    assert analysis.features["discourse_function"] == "speaker_emphasis_or_explanatory_tone_provisional"
    assert analysis.status == "native_reviewed_pragmatics_provisional"


def test_word_lookup_can_reach_maydh_lemma_from_reviewed_maydho_surface():
    result = lookup_word("maydho")
    assert result.known
    assert result.exact_entries == ()
    assert any(candidate.lemma == "maydh" for candidate in result.morphology_candidates)


def test_jabsadeen_is_reviewed_finite_verb_but_jabsadayaal_is_agent_noun_plural():
    verb = analyze_surface_form("jabsadeen")[0]
    agent_plural = analyze_surface_form("jabsadayaal")[0]

    assert verb.lemma == "jabso"
    assert verb.analysis_type == "native_reviewed_finite_verb_surface"
    assert verb.features["person"] == "3pl"
    assert verb.features["tense_aspect"] == "past"

    assert agent_plural.analysis_type == "native_reviewed_agent_noun_plural"
    assert agent_plural.features["part_of_speech"] == "noun"
    assert agent_plural.features["number"] == "plural"
    assert agent_plural.features["canonical_singular"] == "unreviewed"


def test_unknown_forms_are_not_generated_by_suffix_guessing():
    assert analyze_surface_form("maydhxyz") == ()
    assert analyze_surface_form("jabsadxyz") == ()
