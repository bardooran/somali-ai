import subprocess
import sys

from src.connective_focus import (
    analyze_connective_clitic_focus,
    analyze_connective_subject_focus,
)
from src.noun_subject_case import analyze_noun_subject_case
from src.sentence_agreement import scan_sentence_agreement


NO_FINDINGS = "No supported orthography or grammar findings found."


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


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

    case = analyze_noun_subject_case("Wiilka baa yimid, Gabadhu ayaana timid.")
    assert case.recognized is True
    assert case.agrees is False
    assert case.marker == "ayaana"
    assert case.expected_subject_form == "Gabadha"
    assert case.rule_id == "GRAM-CONNFOCUS-003"


def test_connective_subject_focus_reuses_restrictive_gender_agreement():
    result = analyze_connective_subject_focus("Wiilka baa yimid, Gabadha ayaana yimid.")
    assert result.recognized is True
    assert result.case_agrees is True
    assert result.expected_person == "3sg_f"
    assert result.agreement_agrees is False

    findings = scan_sentence_agreement("Wiilka baa yimid, Gabadha ayaana yimid.")
    assert len(findings) == 1
    assert findings[0].pronoun == "Gabadha"
    assert findings[0].verb == "yimid"
    assert "connective -na" in findings[0].note


def test_connective_plural_focus_reuses_restrictive_past_not_full_3pl():
    reduced = analyze_connective_subject_focus("Wiilka baa yimid, Carruurta ayaana yimid.")
    assert reduced.recognized is True
    assert reduced.case_agrees is True
    assert reduced.expected_person == "3pl"
    assert reduced.agreement_agrees is True
    assert scan_sentence_agreement("Wiilka baa yimid, Carruurta ayaana yimid.") == []

    full = analyze_connective_subject_focus("Wiilka baa yimid, Carruurta ayaana yimaaddeen.")
    assert full.recognized is True
    assert full.agreement_agrees is False
    findings = scan_sentence_agreement("Wiilka baa yimid, Carruurta ayaana yimaaddeen.")
    assert len(findings) == 1
    assert findings[0].pronoun == "Carruurta"
    assert findings[0].verb == "yimaaddeen"


def test_standalone_ayaana_baana_are_left_context_dependent():
    for sentence in (
        "Carruurta ayaana yimid.",
        "Maryan baana timid.",
    ):
        assert analyze_connective_subject_focus(sentence).recognized is False
        assert _run_checker(sentence) == NO_FINDINGS


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


def test_buuna_is_buu_plus_connective_na_and_checks_3sg_m_finite_agreement():
    result = analyze_connective_clitic_focus("Cali baa yimid, Muus buuna cunay.")
    assert result.recognized is True
    assert result.focused_phrase == ("Muus",)
    assert result.particle == "buuna"
    assert result.base_focus_clitic == "buu"
    assert result.subject_persons == ("3sg_m",)
    assert result.verb == "cunay"
    assert result.agreement_agrees is True
    assert result.rule_id == "GRAM-CONNFOCUS-007"
    assert analyze_connective_subject_focus("Cali baa yimid, Muus buuna cunay.").recognized is False


def test_beyna_is_bay_plus_connective_na_and_checks_feminine_or_plural_agreement():
    result = analyze_connective_clitic_focus("Maryan baa timid, Muus beyna cuntay.")
    assert result.recognized is True
    assert result.focused_phrase == ("Muus",)
    assert result.particle == "beyna"
    assert result.base_focus_clitic == "bay"
    assert result.subject_persons == ("3sg_f", "3pl")
    assert result.verb == "cuntay"
    assert result.agreement_agrees is True
    assert result.rule_id == "GRAM-CONNFOCUS-007"
    assert analyze_connective_subject_focus("Maryan baa timid, Muus beyna cuntay.").recognized is False


def test_connective_clitic_focus_reports_exact_finite_person_conflicts():
    masculine = analyze_connective_clitic_focus("Cali baa yimid, Muus buuna cuntay.")
    assert masculine.recognized is True
    assert masculine.agreement_agrees is False

    feminine = analyze_connective_clitic_focus("Maryan baa timid, Muus beyna cunay.")
    assert feminine.recognized is True
    assert feminine.agreement_agrees is False

    findings = scan_sentence_agreement("Cali baa yimid, Muus buuna cuntay.")
    assert len(findings) == 1
    assert findings[0].pronoun == "buuna"
    assert findings[0].verb == "cuntay"
    assert "encoded subject person" in findings[0].note


def test_connective_clitic_focus_keeps_context_and_paradigm_safety_boundaries():
    for sentence in (
        "Muus buuna cunay.",
        "Muus beyna cuntay.",
        "Cali baa yimid, Muus baadna cuntay.",
        "Cali baa yimid, Muus baanna cunnay.",
        "Cali baa yimid, Muus baydinna cunteen.",
    ):
        assert analyze_connective_clitic_focus(sentence).recognized is False

    assert _run_checker("Muus buuna cunay.") == NO_FINDINGS
    assert _run_checker("Muus beyna cuntay.") == NO_FINDINGS


def test_connective_clitic_focus_does_not_promote_unreviewed_finite_surfaces():
    # arkay is familiar elsewhere in the project, but it is not independently
    # promoted into the shared exact finite-morphology layer. Keep it unjudged.
    result = analyze_connective_clitic_focus("Cali baa yimid, Maryan buuna arkay.")
    assert result.recognized is True
    assert result.agreement_agrees is None
    assert result.rule_id == "GRAM-CONNFOCUS-006"
    assert _run_checker("Cali baa yimid, Maryan buuna arkay.") == NO_FINDINGS

    unknown = analyze_connective_clitic_focus("Cali baa yimid, Maryan buuna arkXYZ.")
    assert unknown.recognized is True
    assert unknown.agreement_agrees is None
    assert _run_checker("Cali baa yimid, Maryan buuna arkXYZ.") == NO_FINDINGS


def test_cli_accepts_valid_clitic_connective_focus_and_reports_mismatch_without_rewrite():
    assert _run_checker("Cali baa yimid, Muus buuna cunay.") == NO_FINDINGS
    assert _run_checker("Maryan baa timid, Muus beyna cuntay.") == NO_FINDINGS

    output = _run_checker("Cali baa yimid, Muus buuna cuntay.")
    assert "possible subject-verb agreement conflict" in output
    assert "buuna" in output
    assert "cuntay" in output
    assert "Safe corrected text:\nCali baa yimid, Muus buuna cuntay." in output


def test_cli_accepts_valid_connective_focus_and_reports_agreement_conflict():
    assert _run_checker("Cali baa yimid, Maryan ayaana timid.") == NO_FINDINGS
    assert _run_checker("Maryan baa timid; Cali baana yimid.") == NO_FINDINGS

    output = _run_checker("Cali baa yimid, Maryan ayaana yimid.")
    assert "possible subject-verb agreement conflict" in output
    assert "Maryan" in output
    assert "yimid" in output
    assert "Safe corrected text:\nCali baa yimid, Maryan ayaana yimid." in output


def test_cli_reports_connective_focus_case_conflict_without_rewrite():
    output = _run_checker("Wiilka baa yimid, Gabadhu ayaana timid.")
    assert "possible definite-noun subject-case conflict" in output
    assert "reviewed subject-form candidate is 'Gabadha'" in output
    assert "GRAM-CONNFOCUS-003" in output
    assert "Safe corrected text:\nWiilka baa yimid, Gabadhu ayaana timid." in output
