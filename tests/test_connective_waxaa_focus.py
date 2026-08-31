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
    for particle in ("waxayna", "waxaadna"):
        sentence = f"Cali wuu yimid, {particle} cunXYZ muus."
        result = analyze_connective_waxaa_focus(sentence)
        assert result.recognized is True
        assert result.verb == "cunXYZ"
        assert result.verb_persons == ()
        assert result.agreement_agrees is None
        assert result.rule_id == "GRAM-CONNWAXAA-005"
        assert "possible subject-verb agreement conflict" not in _run_checker(sentence)


def test_waxaa_connectives_require_overt_preceding_clause_context():
    for sentence in (
        "Waxaana gabi ahaan la xiray waddooyinkaas.",
        "Waxayna cuntay muus.",
        "Waxaadna cuntay muus.",
    ):
        assert analyze_connective_waxaa_focus(sentence).recognized is False


def test_independent_promotions_do_not_create_a_productive_connective_paradigm():
    for sentence in (
        "Cali wuu yimid, waxana la xiray albaabka.",
        "Cali wuu yimid, waxaanan cunay muus.",
        "Cali wuu yimid, waxXYZna cunay muus.",
    ):
        assert analyze_connective_waxaa_focus(sentence).recognized is False


def test_waxaa_connectives_remain_separate_from_connective_statement_family():
    for sentence in (
        "Cali wuu yimid, waxaana la xiray albaabka.",
        "Cali wuu yimid, waxayna cuntay muus.",
        "Cali wuu yimid, waxaadna cuntay muus.",
    ):
        assert analyze_connective_waxaa_focus(sentence).recognized is True
        assert analyze_connective_statement(sentence).recognized is False


def test_cli_accepts_valid_exact_waxaa_connectives_and_reports_only_real_mismatches():
    assert _run_checker("Cali wuu yimid, waxaana la xiray albaabka.") == NO_FINDINGS
    assert _run_checker("Cali wuu yimid, waxayna cuntay muus.") == NO_FINDINGS
    assert _run_checker("Cali wuu yimid, waxayna cuneen muus.") == NO_FINDINGS
    assert _run_checker("Cali wuu yimid, waxaadna cuntay muus.") == NO_FINDINGS
    assert _run_checker("Cali wuu yimid, waxaadna cunteen muus.") == NO_FINDINGS

    feminine_output = _run_checker("Cali wuu yimid, waxayna cunay muus.")
    assert "possible subject-verb agreement conflict" in feminine_output
    assert "waxayna" in feminine_output
    assert "cunay" in feminine_output
    assert "Safe corrected text:\nCali wuu yimid, waxayna cunay muus." in feminine_output

    second_output = _run_checker("Cali wuu yimid, waxaadna cunay muus.")
    assert "possible subject-verb agreement conflict" in second_output
    assert "waxaadna" in second_output
    assert "cunay" in second_output
