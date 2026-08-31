from src.connective_focus import analyze_connective_subject_focus


def test_ayaana_is_ayaa_plus_connective_na_in_second_clause():
    result = analyze_connective_subject_focus("Cali baa yimid, Maryan ayaana timid.")
    assert result.recognized is True
    assert result.subject == "Maryan"
    assert result.particle == "ayaana"
    assert result.base_particle == "ayaa"
    assert result.conjunction == "-na"
    assert result.predicate == "timid"
    assert result.agreement_agrees is True
    assert result.normalized_clause.startswith("Maryan ayaa timid")
    assert "source_backed_focus_plus_conjunction_na" in (result.evidence or "")


def test_baana_is_baa_plus_connective_na_in_second_clause():
    result = analyze_connective_subject_focus("Maryan baa timid; Cali baana yimid.")
    assert result.recognized is True
    assert result.subject == "Cali"
    assert result.particle == "baana"
    assert result.base_particle == "baa"
    assert result.agreement_agrees is True


def test_common_noun_connective_subject_focus_reuses_absolute_case():
    result = analyze_connective_subject_focus("Wiilka baa yimid, Gabadha ayaana timid.")
    assert result.recognized is True
    assert result.subject == "Gabadha"
    assert result.case_agrees is True
    assert result.expected_subject_form == "Gabadha"
    assert result.agreement_agrees is True


def test_wrong_nominative_u_case_is_detected_inside_connective_subject_focus():
    result = analyze_connective_subject_focus("Wiilka baa yimid, Gabadhu ayaana timid.")
    assert result.recognized is True
    assert result.subject == "Gabadhu"
    assert result.case_agrees is False
    assert result.expected_subject_form == "Gabadha"
    # Agreement is not guessed from the wrong-case surface.
    assert result.agreement_agrees is None


def test_connective_subject_focus_reuses_restrictive_gender_agreement():
    result = analyze_connective_subject_focus("Wiilka baa yimid, Gabadha ayaana yimid.")
    assert result.recognized is True
    assert result.case_agrees is True
    assert result.expected_person == "3sg_f"
    assert result.agreement_agrees is False


def test_connective_plural_focus_reuses_restrictive_past_not_full_3pl():
    reduced = analyze_connective_subject_focus("Wiilka baa yimid, Carruurta ayaana yimid.")
    assert reduced.recognized is True
    assert reduced.case_agrees is True
    assert reduced.expected_person == "3pl"
    assert reduced.agreement_agrees is True

    full = analyze_connective_subject_focus("Wiilka baa yimid, Carruurta ayaana yimaaddeen.")
    assert full.recognized is True
    assert full.agreement_agrees is False


def test_standalone_ayaana_baana_are_left_context_dependent():
    for sentence in (
        "Carruurta ayaana yimid.",
        "Maryan baana timid.",
    ):
        assert analyze_connective_subject_focus(sentence).recognized is False


def test_ayaan_negative_focus_is_not_confused_with_ayaana_connective_focus():
    result = analyze_connective_subject_focus("Cali baa yimid, Carruurta ayaan cunin.")
    assert result.recognized is False


def test_connective_ayaana_does_not_turn_reduced_negative_surface_into_negative_focus():
    result = analyze_connective_subject_focus(
        "Cali baa yimid, Carruurta ayaana maanta waxba cunin."
    )
    assert result.recognized is True
    assert result.base_particle == "ayaa"
    assert result.case_agrees is True
    assert result.agreement_agrees is None
    assert "negative" not in (result.evidence or "")


def test_clitic_bearing_connective_focus_forms_are_pending():
    for sentence in (
        "Cali baa yimid, Maryan buuna arkay.",
        "Cali baa yimid, Maryan beyna aragtay.",
    ):
        assert analyze_connective_subject_focus(sentence).recognized is False
