import subprocess
import sys

from src.connective_statement import analyze_connective_statement
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


def test_wuuna_is_reviewed_statement_clitic_plus_connective_na():
    result = analyze_connective_statement("Cali wuu yimid, wuuna cunay.")
    assert result.recognized is True
    assert result.particle == "wuuna"
    assert result.base_statement_clitic == "wuu"
    assert result.subject_persons == ("3sg_m",)
    assert result.verb == "cunay"
    assert result.agreement_agrees is True
    assert result.conjunction == "-na"
    assert result.rule_id == "GRAM-CONNSTAT-003"
    assert result.left_subject_clitic == "wuu"
    assert result.left_subject_persons == ("3sg_m",)
    assert result.same_subject_continuity_agrees is True
    assert result.continuity_rule_id == "GRAM-CONNSTAT-006"


def test_wayna_keeps_reviewed_feminine_or_plural_person_compatibility():
    feminine = analyze_connective_statement("Cali wuu yimid, wayna cuntay.")
    assert feminine.recognized is True
    assert feminine.particle == "wayna"
    assert feminine.base_statement_clitic == "way"
    assert feminine.subject_persons == ("3sg_f", "3pl")
    assert feminine.verb == "cuntay"
    assert feminine.agreement_agrees is True
    assert feminine.left_subject_clitic == "wuu"
    assert feminine.same_subject_continuity_agrees is False

    plural = analyze_connective_statement("Cali wuu yimid; wayna cuneen.")
    assert plural.recognized is True
    assert plural.verb == "cuneen"
    assert plural.agreement_agrees is True
    assert plural.same_subject_continuity_agrees is False


def test_same_subject_statement_continuity_is_compatible_for_reviewed_clitics():
    masculine = analyze_connective_statement("Axmed wuu yimid, wuuna ila hadlay.")
    assert masculine.recognized is True
    assert masculine.left_subject_clitic == "wuu"
    assert masculine.left_subject_persons == ("3sg_m",)
    assert masculine.subject_persons == ("3sg_m",)
    assert masculine.same_subject_continuity_agrees is True

    feminine = analyze_connective_statement("Maryan way timid, wayna cuntay.")
    assert feminine.recognized is True
    assert feminine.left_subject_clitic == "way"
    assert feminine.left_subject_persons == ("3sg_f", "3pl")
    assert feminine.subject_persons == ("3sg_f", "3pl")
    assert feminine.same_subject_continuity_agrees is True


def test_disjoint_statement_clitics_require_subject_shift_context_not_rewrite():
    feminine_shift = analyze_connective_statement("Cali wuu yimid, wayna cuntay.")
    masculine_shift = analyze_connective_statement("Maryan way timid, wuuna cunay.")

    assert feminine_shift.agreement_agrees is True
    assert feminine_shift.same_subject_continuity_agrees is False
    assert feminine_shift.continuity_rule_id == "GRAM-CONNSTAT-006"
    assert "context-required" in feminine_shift.note

    assert masculine_shift.agreement_agrees is True
    assert masculine_shift.same_subject_continuity_agrees is False
    assert masculine_shift.continuity_rule_id == "GRAM-CONNSTAT-006"
    assert "context-required" in masculine_shift.note


def test_person_neutral_or_missing_left_subject_context_stays_unjudged():
    person_neutral = analyze_connective_statement(
        "Qoyskeennu waxa uu ka kooban yahay aabbe iyo hooyo, waana qoys tiro yar."
    )
    assert person_neutral.recognized is True
    assert person_neutral.same_subject_continuity_agrees is None
    assert person_neutral.continuity_rule_id is None

    no_reviewed_left_clitic = analyze_connective_statement("Cali baa yimid, wuuna cunay.")
    assert no_reviewed_left_clitic.recognized is True
    assert no_reviewed_left_clitic.left_subject_clitic is None
    assert no_reviewed_left_clitic.left_subject_persons == ()
    assert no_reviewed_left_clitic.same_subject_continuity_agrees is None
    assert no_reviewed_left_clitic.continuity_rule_id == "GRAM-CONNSTAT-006"


def test_waana_is_waa_plus_connective_na_without_subject_person():
    result = analyze_connective_statement(
        "Qoyskeennu waxa uu ka kooban yahay aabbe iyo hooyo, waana qoys tiro yar."
    )
    assert result.recognized is True
    assert result.particle == "waana"
    assert result.base_statement_clitic == "waa"
    assert result.subject_persons == ()
    assert result.verb is None
    assert result.agreement_agrees is None
    assert result.conjunction == "-na"
    assert result.rule_id == "GRAM-CONNSTAT-005"
    assert "person_neutral" in (result.evidence or "")


def test_waana_does_not_invent_hidden_subject_agreement_even_before_reviewed_finite_verb():
    result = analyze_connective_statement("Cali wuu yimid, waana cunay.")
    assert result.recognized is True
    assert result.base_statement_clitic == "waa"
    assert result.subject_persons == ()
    assert result.verb is None
    assert result.agreement_agrees is None
    assert result.same_subject_continuity_agrees is None
    assert scan_sentence_agreement("Cali wuu yimid, waana cunay.") == []
    assert _run_checker("Cali wuu yimid, waana cunay.") == NO_FINDINGS


def test_connective_statement_reports_exact_finite_person_conflicts():
    masculine = analyze_connective_statement("Cali wuu yimid, wuuna cuntay.")
    assert masculine.recognized is True
    assert masculine.agreement_agrees is False

    feminine_or_plural = analyze_connective_statement("Cali wuu yimid, wayna cunay.")
    assert feminine_or_plural.recognized is True
    assert feminine_or_plural.agreement_agrees is False

    findings = scan_sentence_agreement("Cali wuu yimid, wuuna cuntay.")
    assert len(findings) == 1
    assert findings[0].pronoun == "wuuna"
    assert findings[0].verb == "cuntay"
    assert "connective statement" in findings[0].expected_forms[0]


def test_connective_statement_keeps_context_and_paradigm_safety_boundaries():
    for sentence in (
        "Wuuna cunay.",
        "Wayna cuntay.",
        "Waana qoys tiro yar.",
        "Cali wuu yimid, waadna cuntay.",
        "Cali wuu yimid, waanna cunnay.",
        "Cali wuu yimid, waydinna cunteen.",
    ):
        assert analyze_connective_statement(sentence).recognized is False

    assert _run_checker("Wuuna cunay.") == NO_FINDINGS
    assert _run_checker("Wayna cuntay.") == NO_FINDINGS
    assert _run_checker("Waana qoys tiro yar.") == NO_FINDINGS


def test_connective_statement_does_not_guess_unknown_predicates():
    result = analyze_connective_statement("Cali wuu yimid, wuuna cunXYZ.")
    assert result.recognized is True
    assert result.agreement_agrees is None
    assert result.same_subject_continuity_agrees is True
    assert result.rule_id == "GRAM-CONNSTAT-001"
    assert _run_checker("Cali wuu yimid, wuuna cunXYZ.") == NO_FINDINGS


def test_cli_accepts_valid_connective_statement_and_reports_mismatch_without_rewrite():
    assert _run_checker("Cali wuu yimid, wuuna cunay.") == NO_FINDINGS
    assert _run_checker("Maryan way timid, wayna cuntay.") == NO_FINDINGS
    assert _run_checker("Cali wuu yimid, waana qoys tiro yar.") == NO_FINDINGS

    output = _run_checker("Cali wuu yimid, wuuna cuntay.")
    assert "possible subject-verb agreement conflict" in output
    assert "wuuna" in output
    assert "cuntay" in output
    assert "Safe corrected text:\nCali wuu yimid, wuuna cuntay." in output


def test_cli_reports_context_required_statement_subject_shift_without_rewrite():
    output = _run_checker("Cali wuu yimid, wayna cuntay.")
    assert "possible subject switch" in output
    assert "statement-connective subject clitic" in output
    assert "3sg_m" in output
    assert "3sg_f/3pl" in output
    assert "context is required" in output
    assert "GRAM-CONNSTAT-006" in output
    assert "Safe corrected text:\nCali wuu yimid, wayna cuntay." in output
    assert "possible subject-verb agreement conflict" not in output

    reverse = _run_checker("Maryan way timid, wuuna cunay.")
    assert "possible subject switch" in reverse
    assert "3sg_f/3pl" in reverse
    assert "3sg_m" in reverse
    assert "Safe corrected text:\nMaryan way timid, wuuna cunay." in reverse


def test_novel_statement_continuity_examples_generalize_without_new_forms():
    same_subject = analyze_connective_statement("Cali wuu cunay, wuuna yimid.")
    assert same_subject.recognized is True
    assert same_subject.agreement_agrees is True
    assert same_subject.same_subject_continuity_agrees is True

    subject_shift = analyze_connective_statement("Maryan way cuntay, wuuna yimid.")
    assert subject_shift.recognized is True
    assert subject_shift.agreement_agrees is True
    assert subject_shift.same_subject_continuity_agrees is False


def test_statement_connectives_remain_separate_from_connective_focus_forms():
    assert analyze_connective_statement("Cali wuu yimid, buuna cunay.").recognized is False
    assert analyze_connective_statement("Cali wuu yimid, beyna cuntay.").recognized is False
    assert analyze_connective_statement("Cali wuu yimid, ayaana cunay.").recognized is False
    assert analyze_connective_statement("Cali wuu yimid, baana cunay.").recognized is False
