import subprocess
import sys

from src.connective_statement import analyze_connective_statement
from src.connective_waxaa_focus import analyze_connective_waxaa_focus
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


def test_waxaana_remains_reviewed_person_neutral_waxaa_plus_connective_na():
    result = analyze_connective_waxaa_focus(
        "Booliisku goobta way tageen, waxaana gabi ahaan la xiray waddooyinkaas."
    )
    assert result.recognized is True
    assert result.particle == "waxaana"
    assert result.base_focus_particle == "waxaa"
    assert result.base_focus_subject_form is None
    assert result.subject_clitic is None
    assert result.conjunction == "-na"
    assert result.subject_persons == ()
    assert result.verb is None
    assert result.agreement_agrees is None
    assert result.following_material[:3] == ("gabi", "ahaan", "la")
    assert result.rule_id == "GRAM-CONNWAXAA-001"


def test_waxaana_does_not_invent_subject_person_before_reviewed_finite_surface():
    result = analyze_connective_waxaa_focus("Cali wuu yimid, waxaana cunay muus.")
    assert result.recognized is True
    assert result.subject_persons == ()
    assert result.verb is None
    assert result.agreement_agrees is None
    assert scan_sentence_agreement("Cali wuu yimid, waxaana cunay muus.") == []


def test_waxayna_is_independently_reviewed_ay_connective_for_feminine_and_plural():
    feminine = analyze_connective_waxaa_focus("Cali wuu yimid, waxayna cuntay muus.")
    assert feminine.recognized is True
    assert feminine.particle == "waxayna"
    assert feminine.base_focus_particle == "waxaa"
    assert feminine.base_focus_subject_form == "waxay"
    assert feminine.subject_clitic == "ay"
    assert feminine.subject_persons == ("3sg_f", "3pl")
    assert feminine.verb == "cuntay"
    assert "3sg_f" in feminine.verb_persons
    assert feminine.agreement_agrees is True
    assert feminine.rule_id == "GRAM-CONNWAXAA-006"

    plural = analyze_connective_waxaa_focus("Cali wuu yimid; waxayna cuneen muus.")
    assert plural.recognized is True
    assert plural.verb == "cuneen"
    assert plural.verb_persons == ("3pl",)
    assert plural.agreement_agrees is True


def test_waxaadna_is_independently_reviewed_aad_connective_for_second_person():
    singular = analyze_connective_waxaa_focus("Cali wuu yimid, waxaadna cuntay muus.")
    assert singular.recognized is True
    assert singular.particle == "waxaadna"
    assert singular.base_focus_subject_form == "waxaad"
    assert singular.subject_clitic == "aad"
    assert singular.subject_persons == ("2sg", "2pl")
    assert singular.verb == "cuntay"
    assert "2sg" in singular.verb_persons
    assert singular.agreement_agrees is True
    assert singular.rule_id == "GRAM-CONNWAXAA-006"

    plural = analyze_connective_waxaa_focus("Cali wuu yimid; waxaadna cunteen muus.")
    assert plural.recognized is True
    assert plural.verb == "cunteen"
    assert "2pl" in plural.verb_persons
    assert plural.agreement_agrees is True


def test_waxayna_reports_exact_finite_person_conflict():
    result = analyze_connective_waxaa_focus("Cali wuu yimid, waxayna cunay muus.")
    assert result.recognized is True
    assert result.subject_persons == ("3sg_f", "3pl")
    assert result.verb == "cunay"
    assert result.agreement_agrees is False

    findings = scan_sentence_agreement("Cali wuu yimid, waxayna cunay muus.")
    assert len(findings) == 1
    assert findings[0].pronoun == "waxayna"
    assert findings[0].verb == "cunay"
    assert "3sg_f/3pl" in findings[0].expected_forms[0]


def test_waxaadna_reports_exact_finite_person_conflict():
    result = analyze_connective_waxaa_focus("Cali wuu yimid, waxaadna cunay muus.")
    assert result.recognized is True
    assert result.subject_persons == ("2sg", "2pl")
    assert result.verb == "cunay"
    assert result.agreement_agrees is False

    findings = scan_sentence_agreement("Cali wuu yimid, waxaadna cunay muus.")
    assert len(findings) == 1
    assert findings[0].pronoun == "waxaadna"
    assert findings[0].verb == "cunay"
    assert "2sg/2pl" in findings[0].expected_forms[0]


def test_clitic_bearing_waxaa_connectives_do_not_guess_unknown_predicates():
    for sentence in (
        "Cali wuu yimid, waxayna cunXYZ muus.",
        "Cali wuu yimid, waxaadna cunXYZ muus.",
        "Waxayna cunXYZ muus.",
        "Waxaadna cunXYZ muus.",
    ):
        result = analyze_connective_waxaa_focus(sentence)
        assert result.recognized is True
        assert result.verb == "cunXYZ"
        assert result.verb_persons == ()
        assert result.agreement_agrees is None
        assert result.rule_id == "GRAM-CONNWAXAA-005"
        assert "possible subject-verb agreement conflict" not in _run_checker(sentence)


def test_source_backed_sentence_initial_waxaana_is_recognized_without_hidden_subject():
    result = analyze_connective_waxaa_focus(
        "Waxaana gabi ahaan la xiray waddooyinkaas."
    )
    assert result.recognized is True
    assert result.particle == "Waxaana"
    assert result.boundary == "input_start"
    assert result.subject_persons == ()
    assert result.agreement_agrees is None
    assert "sentence_or_clause_initial_distribution" in (result.evidence or "")


def test_source_backed_sentence_initial_waxayna_keeps_reviewed_person_set():
    singular = analyze_connective_waxaa_focus("Waxayna cuntay muus.")
    assert singular.recognized is True
    assert singular.boundary == "input_start"
    assert singular.subject_clitic == "ay"
    assert singular.subject_persons == ("3sg_f", "3pl")
    assert singular.verb == "cuntay"
    assert singular.agreement_agrees is True

    plural = analyze_connective_waxaa_focus("Waxayna cuneen muus.")
    assert plural.recognized is True
    assert plural.boundary == "input_start"
    assert plural.verb_persons == ("3pl",)
    assert plural.agreement_agrees is True


def test_source_backed_sentence_initial_waxaadna_keeps_reviewed_person_set():
    singular = analyze_connective_waxaa_focus("Waxaadna cuntay muus.")
    assert singular.recognized is True
    assert singular.boundary == "input_start"
    assert singular.subject_clitic == "aad"
    assert singular.subject_persons == ("2sg", "2pl")
    assert singular.verb == "cuntay"
    assert singular.agreement_agrees is True

    plural = analyze_connective_waxaa_focus("Waxaadna cunteen muus.")
    assert plural.recognized is True
    assert plural.boundary == "input_start"
    assert "2pl" in plural.verb_persons
    assert plural.agreement_agrees is True


def test_sentence_initial_clitic_connectives_still_report_real_mismatches():
    feminine = analyze_connective_waxaa_focus("Waxayna cunay muus.")
    second = analyze_connective_waxaa_focus("Waxaadna cunay muus.")
    assert feminine.agreement_agrees is False
    assert second.agreement_agrees is False

    feminine_findings = scan_sentence_agreement("Waxayna cunay muus.")
    second_findings = scan_sentence_agreement("Waxaadna cunay muus.")
    assert len(feminine_findings) == 1
    assert feminine_findings[0].pronoun == "Waxayna"
    assert feminine_findings[0].verb == "cunay"
    assert len(second_findings) == 1
    assert second_findings[0].pronoun == "Waxaadna"
    assert second_findings[0].verb == "cunay"


def test_full_sentence_punctuation_can_supply_the_connective_boundary():
    period = analyze_connective_waxaa_focus("Cali wuu yimid. Waxayna cuneen muus.")
    exclamation = analyze_connective_waxaa_focus("Cali wuu yimid! Waxaadna cunteen muus.")
    question = analyze_connective_waxaa_focus("Cali ma yimid? Waxayna cuntay muus.")

    assert period.recognized is True and period.boundary == "."
    assert period.agreement_agrees is True
    assert exclamation.recognized is True and exclamation.boundary == "!"
    assert exclamation.agreement_agrees is True
    assert question.recognized is True and question.boundary == "?"
    assert question.agreement_agrees is True


def test_unpunctuated_mid_sentence_connective_remains_outside_this_stage():
    for sentence in (
        "Cali wuu yimid waxayna cuntay muus.",
        "Cali wuu yimid waxaadna cuntay muus.",
    ):
        assert analyze_connective_waxaa_focus(sentence).recognized is False


def test_independent_promotions_do_not_create_a_productive_connective_paradigm():
    for sentence in (
        "Cali wuu yimid, waxana la xiray albaabka.",
        "Cali wuu yimid, waxaanan cunay muus.",
        "Cali wuu yimid, waxXYZna cunay muus.",
        "Waxana la xiray albaabka.",
        "Waxaanan cunay muus.",
        "WaxXYZna cunay muus.",
    ):
        assert analyze_connective_waxaa_focus(sentence).recognized is False


def test_waxaa_connectives_remain_separate_from_connective_statement_family():
    for sentence in (
        "Cali wuu yimid, waxaana la xiray albaabka.",
        "Cali wuu yimid, waxayna cuntay muus.",
        "Cali wuu yimid, waxaadna cuntay muus.",
        "Waxayna cuntay muus.",
        "Waxaadna cuntay muus.",
    ):
        assert analyze_connective_waxaa_focus(sentence).recognized is True
        assert analyze_connective_statement(sentence).recognized is False


def test_cli_accepts_valid_exact_waxaa_connectives_and_reports_only_real_mismatches():
    for sentence in (
        "Cali wuu yimid, waxaana la xiray albaabka.",
        "Cali wuu yimid, waxayna cuntay muus.",
        "Cali wuu yimid, waxayna cuneen muus.",
        "Cali wuu yimid, waxaadna cuntay muus.",
        "Cali wuu yimid, waxaadna cunteen muus.",
        "Waxaana gabi ahaan la xiray waddooyinkaas.",
        "Waxayna cuntay muus.",
        "Waxayna cuneen muus.",
        "Waxaadna cuntay muus.",
        "Waxaadna cunteen muus.",
    ):
        assert _run_checker(sentence) == NO_FINDINGS

    feminine_output = _run_checker("Waxayna cunay muus.")
    assert "possible subject-verb agreement conflict" in feminine_output
    assert "Waxayna" in feminine_output
    assert "cunay" in feminine_output
    assert "Safe corrected text:\nWaxayna cunay muus." in feminine_output

    second_output = _run_checker("Waxaadna cunay muus.")
    assert "possible subject-verb agreement conflict" in second_output
    assert "Waxaadna" in second_output
    assert "cunay" in second_output
