import subprocess
import sys


NO_FINDINGS = "No supported orthography or grammar findings found."


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_keeps_supported_waxa_focus_and_neutral_statement_examples_silent():
    for sentence in (
        "Cali wuu yimid, wuxuuna cunay muus.",
        "Maryan way timid, waxayna cuntay muus.",
        "Cali wuu yimid, wuuna cunay.",
        "Maryan way timid, wayna cuntay.",
    ):
        assert _run_checker(sentence) == NO_FINDINGS


def test_cli_reports_missing_postverbal_focus_tail_without_autofix():
    sentence = "Cali wuu yimid, wuxuuna cunay."
    output = _run_checker(sentence)

    assert "Grammar findings:" in output
    assert "possible incomplete waxa/waxaa final-focus construction" in output
    assert "neutral waa-family connective statement" in output
    assert "GRAM-CONNWAXAA-009" in output
    assert "Safe corrected text:\n" + sentence in output


def test_cli_reports_subject_switch_as_context_required_not_agreement_error():
    sentence = "Cali wuu yimid, waxayna cuntay muus."
    output = _run_checker(sentence)

    assert "Grammar findings:" in output
    assert "possible subject switch" in output
    assert "context is required" in output
    assert "plain same-subject continuation" in output
    assert "GRAM-CONNWAXAA-010" in output
    assert "possible subject-verb agreement conflict" not in output
    assert "Safe corrected text:\n" + sentence in output


def test_cli_can_report_focus_tail_and_subject_switch_as_separate_review_conditions():
    sentence = "Cali wuu yimid, waxayna cuntay."
    output = _run_checker(sentence)

    assert "possible incomplete waxa/waxaa final-focus construction" in output
    assert "possible subject switch" in output
    assert "GRAM-CONNWAXAA-009" in output
    assert "GRAM-CONNWAXAA-010" in output
    assert "Safe corrected text:\n" + sentence in output
