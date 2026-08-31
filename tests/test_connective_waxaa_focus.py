import subprocess
import sys

from src.connective_statement import analyze_connective_statement
from src.connective_waxaa_focus import analyze_connective_waxaa_focus


NO_FINDINGS = "No supported orthography or grammar findings found."


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_waxaana_is_reviewed_waxaa_plus_connective_na():
    result = analyze_connective_waxaa_focus(
        "Booliisku goobta way tageen, waxaana gabi ahaan la xiray waddooyinkaas."
    )
    assert result.recognized is True
    assert result.particle == "waxaana"
    assert result.base_focus_particle == "waxaa"
    assert result.conjunction == "-na"
    assert result.subject_persons == ()
    assert result.agreement_agrees is None
    assert result.following_material[:3] == ("gabi", "ahaan", "la")
    assert result.rule_id == "GRAM-CONNWAXAA-001"
    assert "focus_particle_plus_conjunction_na" in (result.evidence or "")


def test_waxaana_does_not_invent_subject_person_before_reviewed_finite_surface():
    result = analyze_connective_waxaa_focus("Cali wuu yimid, waxaana cunay muus.")
    assert result.recognized is True
    assert result.base_focus_particle == "waxaa"
    assert result.subject_persons == ()
    assert result.agreement_agrees is None


def test_waxaana_remains_separate_from_connective_statement_family():
    sentence = "Cali wuu yimid, waxaana la xiray albaabka."
    assert analyze_connective_waxaa_focus(sentence).recognized is True
    assert analyze_connective_statement(sentence).recognized is False


def test_waxaana_keeps_context_and_exact_form_safety_boundaries():
    for sentence in (
        "Waxaana gabi ahaan la xiray waddooyinkaas.",
        "Cali wuu yimid, waxana la xiray albaabka.",
        "Cali wuu yimid, waxaadna cuntay muus.",
        "Cali wuu yimid, waxayna cuntay muus.",
        "Cali wuu yimid, waxaanan cunay muus.",
    ):
        assert analyze_connective_waxaa_focus(sentence).recognized is False


def test_cli_leaves_valid_waxaana_clause_unchanged():
    sentence = "Cali wuu yimid, waxaana la xiray albaabka."
    assert _run_checker(sentence) == NO_FINDINGS


def test_cli_does_not_promote_predicted_waxaa_connective_forms():
    for sentence in (
        "Cali wuu yimid, waxaadna cuntay muus.",
        "Cali wuu yimid, waxayna cuntay muus.",
    ):
        # These may later receive independent evidence, but this waxaana stage
        # must not create grammar findings or rewrites for them by analogy.
        assert "possible subject-verb agreement conflict" not in _run_checker(sentence)
