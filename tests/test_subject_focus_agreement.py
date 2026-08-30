from src.subject_focus_agreement import analyze_subject_focus_agreement


def test_reviewed_cali_baa_yimid_is_valid_subject_focus():
    result = analyze_subject_focus_agreement("Cali baa yimid.")
    assert result.recognized is True
    assert result.subject == "Cali"
    assert result.particle == "baa"
    assert result.predicate == "yimid"
    assert result.expected_person == "3sg_m"
    assert result.predicate_persons == ("3sg_m",)
    assert result.agrees is True
    assert result.evidence == "exact_reviewed_finite_morphology"


def test_source_backed_yimi_variant_also_agrees_with_cali():
    result = analyze_subject_focus_agreement("Cali baa yimi.")
    assert result.recognized is True
    assert result.agrees is True
    assert "3sg_m" in result.predicate_persons


def test_reviewed_maryan_baa_qososhay_uses_exact_sentence_surface():
    result = analyze_subject_focus_agreement("Maryan baa qososhay.")
    assert result.recognized is True
    assert result.expected_person == "3sg_f"
    assert result.predicate_persons == ("3sg_f",)
    assert result.agrees is True
    assert result.evidence == "exact_native_reviewed_sentence_surface"


def test_known_feminine_imow_past_can_generalize_in_subject_focus():
    result = analyze_subject_focus_agreement("Maryan baa timid.")
    assert result.recognized is True
    assert result.expected_person == "3sg_f"
    assert "3sg_f" in result.predicate_persons
    assert result.agrees is True


def test_maryan_with_masculine_yimid_is_conflict():
    result = analyze_subject_focus_agreement("Maryan baa yimid.")
    assert result.recognized is True
    assert result.expected_person == "3sg_f"
    assert result.predicate_persons == ("3sg_m",)
    assert result.agrees is False


def test_cali_with_feminine_timid_is_conflict():
    result = analyze_subject_focus_agreement("Cali baa timid.")
    assert result.recognized is True
    assert result.expected_person == "3sg_m"
    assert "3sg_f" in result.predicate_persons
    assert result.agrees is False


def test_cali_with_reviewed_feminine_qososhay_is_conflict():
    result = analyze_subject_focus_agreement("Cali baa qososhay.")
    assert result.recognized is True
    assert result.expected_person == "3sg_m"
    assert result.predicate_persons == ("3sg_f",)
    assert result.agrees is False


def test_unknown_predicate_is_recognized_but_unjudged():
    result = analyze_subject_focus_agreement("Cali baa yimidXYZ.")
    assert result.recognized is True
    assert result.agrees is None
    assert result.predicate_persons == ()
    assert result.evidence == "predicate_unreviewed"


def test_unreviewed_name_is_not_gender_guessed():
    result = analyze_subject_focus_agreement("Axmed baa yimid.")
    assert result.recognized is False


def test_ayaa_is_not_silently_generalized_from_baa_evidence():
    result = analyze_subject_focus_agreement("Cali ayaa yimid.")
    assert result.recognized is False


def test_object_focus_sentence_is_outside_subject_focus_rule():
    result = analyze_subject_focus_agreement("Wiilku muus buu cunay.")
    assert result.recognized is False
