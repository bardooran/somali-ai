import subprocess
import sys


def run_cli(text: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", text],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def test_cli_reports_agreement_conflict_without_autofixing_it():
    output = run_cli("Iyada way keenay.")

    assert "Grammar findings:" in output
    assert "[REVIEW]" in output
    assert "possible subject-verb agreement conflict" in output
    assert "keentay" in output
    assert "Safe corrected text:" in output
    # Agreement itself is not auto-fixed. The existing orthography rule may still
    # expand the sentence marker way -> waa ay.
    assert "Iyada waa ay keenay." in output
    assert "Iyada waa ay keentay." not in output


def test_cli_keeps_matching_agreement_silent_while_orthography_can_still_apply():
    output = run_cli("Iyada way keentay.")

    assert "Grammar findings:" not in output
    assert "Orthography findings:" in output
    assert "'way' -> 'waa ay'" in output
    assert "Iyada waa ay keentay." in output


def test_cli_can_show_orthography_and_grammar_findings_together():
    output = run_cli("iyada way keenay.")

    assert "Orthography findings:" in output
    assert "Grammar findings:" in output
    assert "Safe corrected text:" in output
    assert "Iyada" in output
