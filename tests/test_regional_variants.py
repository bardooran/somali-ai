from src.regional_variants import analyze_regional_form, preferred_forms_for_concept


def _one(form):
    analyses = analyze_regional_form(form)
    assert analyses
    return analyses[0]


def test_jigjiga_dheh_form_is_preferred():
    result = _one("yidhi")
    assert result.preference == "preferred"
    assert result.concept == "dheh"


def test_yiri_is_recognized_not_rejected():
    result = _one("yiri")
    assert result.preference == "recognized_variant"
    assert "yidhi" in result.preferred_forms


def test_egg_forms_are_co_preferred():
    assert _one("beed").preference == "co_preferred"
    assert _one("ukun").preference == "co_preferred"
    assert set(preferred_forms_for_concept("egg")) == {"beed", "ukun"}


def test_after_phrases_are_co_preferred():
    assert _one("ka bacdi").preference == "co_preferred"
    assert _one("ka dib").preference == "co_preferred"


def test_body_jir_variant_requires_sense_context():
    result = _one("jir")
    assert result.preference == "recognized_variant"
    assert result.concept == "body"
    assert result.sense_sensitive is True
    assert "jidh" in result.preferred_forms


def test_dhaq_variant_is_limited_to_washing_sense():
    result = _one("dhaq")
    assert result.preference == "recognized_variant"
    assert result.concept == "wash_clothes_or_body"
    assert result.sense_sensitive is True
    assert "maydh" in result.preferred_forms


def test_unverified_xabuub_is_not_promoted_to_preferred():
    result = _one("xabuub")
    assert result.preference == "candidate_unverified"
    assert result.status == "candidate_needs_source_crosscheck"


def test_unknown_form_gets_no_invented_variant_analysis():
    assert analyze_regional_form("erey-aan-jirin") == ()
