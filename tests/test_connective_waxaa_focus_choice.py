from src.connective_statement import analyze_connective_statement
from src.connective_waxaa_focus import analyze_connective_waxaa_focus
from src.sentence_agreement import scan_sentence_agreement


def test_neutral_same_subject_continuation_uses_statement_connective_family():
    masculine = analyze_connective_statement("Cali wuu yimid, wuuna cunay.")
    feminine = analyze_connective_statement("Maryan way timid, wayna cuntay.")

    assert masculine.recognized is True
    assert masculine.particle == "wuuna"
    assert masculine.subject_persons == ("3sg_m",)
    assert masculine.agreement_agrees is True

    assert feminine.recognized is True
    assert feminine.particle == "wayna"
    assert feminine.subject_persons == ("3sg_f", "3pl")
    assert feminine.agreement_agrees is True


def test_wuxuuna_is_exact_reviewed_masculine_waxa_connective_with_final_focus():
    result = analyze_connective_waxaa_focus("Cali wuu yimid, wuxuuna cunay muus.")

    assert result.recognized is True
    assert result.particle == "wuxuuna"
    assert result.base_focus_subject_form == "wuxuu"
    assert result.subject_clitic == "uu"
    assert result.subject_persons == ("3sg_m",)
    assert result.verb == "cunay"
    assert "3sg_m" in result.verb_persons
    assert result.agreement_agrees is True
    assert result.focus_material == ("muus",)
    assert result.focus_structure_agrees is True
    assert result.left_subject_clitic == "wuu"
    assert result.left_subject_persons == ("3sg_m",)
    assert result.same_subject_continuity_agrees is True
    assert result.focus_rule_id == "GRAM-CONNWAXAA-009"
    assert result.continuity_rule_id == "GRAM-CONNWAXAA-010"


def test_waxa_connective_without_postverbal_focus_tail_requires_review():
    masculine = analyze_connective_waxaa_focus("Cali wuu yimid, wuxuuna cunay.")
    feminine = analyze_connective_waxaa_focus("Maryan way timid, waxayna cuntay.")
    second = analyze_connective_waxaa_focus("Adigu waad timid, waxaadna cuntay.")

    for result in (masculine, feminine, second):
        assert result.recognized is True
        assert result.agreement_agrees is True
        assert result.focus_material == ()
        assert result.focus_structure_agrees is False
        assert result.focus_rule_id == "GRAM-CONNWAXAA-009"
        assert "none follows" in result.note
        assert "REVIEW" in result.note


def test_same_subject_focus_continuation_is_compatible_for_feminine_and_second_person():
    feminine = analyze_connective_waxaa_focus(
        "Maryan way timid, waxayna cuntay muus."
    )
    second = analyze_connective_waxaa_focus(
        "Adigu waad timid, waxaadna cuntay muus."
    )

    assert feminine.focus_structure_agrees is True
    assert feminine.left_subject_clitic == "way"
    assert feminine.same_subject_continuity_agrees is True

    assert second.focus_structure_agrees is True
    assert second.left_subject_clitic == "waad"
    assert second.same_subject_continuity_agrees is True


def test_subject_switch_is_context_required_not_plain_same_subject_correctness():
    feminine_switch = analyze_connective_waxaa_focus(
        "Cali wuu yimid, waxayna cuntay muus."
    )
    second_person_switch = analyze_connective_waxaa_focus(
        "Cali wuu yimid, waxaadna cuntay muus."
    )

    for result in (feminine_switch, second_person_switch):
        assert result.recognized is True
        assert result.agreement_agrees is True
        assert result.focus_structure_agrees is True
        assert result.left_subject_clitic == "wuu"
        assert result.left_subject_persons == ("3sg_m",)
        assert result.same_subject_continuity_agrees is False
        assert "subject switch" in result.note
        assert "context-required" in result.note


def test_wuxuuna_still_reports_real_right_verb_person_conflict():
    result = analyze_connective_waxaa_focus("Cali wuu yimid, wuxuuna cuntay muus.")
    assert result.recognized is True
    assert result.subject_persons == ("3sg_m",)
    assert result.verb == "cuntay"
    assert result.agreement_agrees is False
    assert result.focus_structure_agrees is True
    assert result.same_subject_continuity_agrees is True

    findings = scan_sentence_agreement("Cali wuu yimid, wuxuuna cuntay muus.")
    assert len(findings) == 1
    assert findings[0].pronoun == "wuxuuna"
    assert findings[0].verb == "cuntay"
    assert "3sg_m" in findings[0].expected_forms[0]


def test_unpunctuated_same_subject_wuxuuna_uses_reviewed_left_finite_boundary():
    result = analyze_connective_waxaa_focus("Cali wuu cunay wuxuuna cunay muus.")

    assert result.recognized is True
    assert result.boundary == "reviewed_left_finite"
    assert result.particle == "wuxuuna"
    assert result.focus_structure_agrees is True
    assert result.same_subject_continuity_agrees is True


def test_predicted_wuxuuna_spellings_remain_outside_this_promotion():
    for sentence in (
        "Cali wuu yimid, waxuuna cunay muus.",
        "Cali wuu yimid, wuxuna cunay muus.",
    ):
        assert analyze_connective_waxaa_focus(sentence).recognized is False
