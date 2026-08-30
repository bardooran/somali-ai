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
    text = "Iyada way keenay."
    output = run_cli(text)

    assert "Grammar findings:" in output
    assert "[REVIEW]" in output
    assert "possible subject-verb agreement conflict" in output
    assert "keentay" in output
    assert "Safe corrected text:" in output
    assert text in output


def test_cli_stays_quiet_for_supported_matching_agreement():
    output = run_cli("Iyada way keentay.")

    assert output.strip() == "No supported orthography or agreement findings found."


def test_cli_can_show_orthography_and_grammar_findings_together():
    output = run_cli("iyada way keenay.")

    assert "Orthography findings:" in output
    assert "Grammar findings:" in output
    assert "Safe corrected text:" in output
    assert "Iyada" in output
