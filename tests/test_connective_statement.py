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


def test_wayna_keeps_reviewed_feminine_or_plural_person_compatibility():
    feminine = analyze_connective_statement("Cali wuu yimid, wayna cuntay.")
    assert feminine.recognized is True
    assert feminine.particle == "wayna"
    assert feminine.base_statement_clitic == "way"
    assert feminine.subject_persons == ("3sg_f", "3pl")
    assert feminine.verb == "cuntay"
    assert feminine.agreement_agrees is True

    plural = analyze_connective_statement("Cali wuu yimid; wayna cuneen.")
    assert plural.recognized is True
    assert plural.verb == "cuneen"
    assert plural.agreement_agrees is True


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
        "wuuna cunay.",
        "wayna cuntay.",
        "Cali wuu yimid, waana cunay.",
        "Cali wuu yimid, waadna cuntay.",
        "Cali wuu yimid, waanna cunnay.",
        "Cali wuu yimid, waydinna cunteen.",
    ):
        assert analyze_connective_statement(sentence).recognized is False

    assert _run_checker("wuuna cunay.") == NO_FINDINGS
    assert _run_checker("wayna cuntay.") == NO_FINDINGS


def test_connective_statement_does_not_guess_unknown_predicates():
    result = analyze_connective_statement("Cali wuu yimid, wuuna cunXYZ.")
    assert result.recognized is True
    assert result.agreement_agrees is None
    assert result.rule_id == "GRAM-CONNSTAT-001"
    assert _run_checker("Cali wuu yimid, wuuna cunXYZ.") == NO_FINDINGS


def test_cli_accepts_valid_connective_statement_and_reports_mismatch_without_rewrite():
    assert _run_checker("Cali wuu yimid, wuuna cunay.") == NO_FINDINGS
    assert _run_checker("Maryan way timid, wayna cuntay.") == NO_FINDINGS

    output = _run_checker("Cali wuu yimid, wuuna cuntay.")
    assert "possible subject-verb agreement conflict" in output
    assert "wuuna" in output
    assert "cuntay" in output
    assert "Safe corrected text:\nCali wuu yimid, wuuna cuntay." in output


def test_statement_connectives_remain_separate_from_connective_focus_forms():
    assert analyze_connective_statement("Cali wuu yimid, buuna cunay.").recognized is False
    assert analyze_connective_statement("Cali wuu yimid, beyna cuntay.").recognized is False
    assert analyze_connective_statement("Cali wuu yimid, ayaana cunay.").recognized is False
    assert analyze_connective_statement("Cali wuu yimid, baana cunay.").recognized is False
