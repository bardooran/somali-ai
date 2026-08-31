import subprocess
import sys

from src.connective_statement import analyze_connective_statement
from src.grammar_status import classify_connective_statement


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_attested_wayna_subject_switch_is_context_required_not_local_error():
    result = analyze_connective_statement("wuuna dhunkaday, wayna ooyeen.")

    assert result.recognized is True
    assert result.particle == "wayna"
    assert result.subject_persons == ("3sg_f", "3pl")
    assert result.left_subject_clitic == "wuuna"
    assert result.left_subject_persons == ("3sg_m",)
    assert result.same_subject_continuity_agrees is False
    assert result.agreement_agrees is None

    decision = classify_connective_statement(result)
    assert decision.status == "context_required"
    assert "possible_subject_switch" in decision.reasons


def test_attested_wuu_to_wuuna_same_subject_control_is_compatible():
    result = analyze_connective_statement("Dhulku wuu baroortaa, wuuna qallalaa.")

    assert result.recognized is True
    assert result.particle == "wuuna"
    assert result.left_subject_clitic == "wuu"
    assert result.left_subject_persons == ("3sg_m",)
    assert result.same_subject_continuity_agrees is True


def test_local_right_agreement_does_not_erase_subject_switch_uncertainty():
    result = analyze_connective_statement("Cali wuu yimid, wayna cuntay muus.")

    assert result.recognized is True
    assert result.agreement_agrees is True
    assert result.same_subject_continuity_agrees is False

    decision = classify_connective_statement(result)
    assert decision.status == "context_required"
    assert "possible_subject_switch" in decision.reasons


def test_cli_surfaces_context_required_switch_without_claiming_local_verb_error():
    output = _run_checker("Cali wuu yimid, wayna cuntay muus.")

    assert "possible connective-statement subject switch" in output
    assert "context is required" in output
    assert "possible subject-verb agreement conflict" not in output


def test_person_neutral_waana_does_not_invent_subject_continuity():
    result = analyze_connective_statement("Cali wuu yimid, waana arrin muhiim ah.")

    assert result.recognized is True
    assert result.particle == "waana"
    assert result.subject_persons == ()
    assert result.same_subject_continuity_agrees is None
    assert result.left_subject_persons == ("3sg_m",)
