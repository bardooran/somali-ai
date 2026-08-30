import subprocess
import sys


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_accepts_reviewed_fronted_object_focus_order():
    for sentence in (
        "Muus ayuu wiilku cunay.",
        "Muus ayay gabadhu cuntay.",
        "Muus ayay carruurtu cuneen.",
        "Muus bisil ayuu wiilku cunay.",
    ):
        assert _run_checker(sentence) == "No supported orthography or grammar findings found."


def test_cli_reports_fronted_focus_clitic_conflict_against_post_focus_subject():
    output = _run_checker("Muus ayay wiilku cunay.")
    assert "possible focused-object agreement conflict" in output
    assert "contracted focus/subject clitic" in output
    assert "explicit subject expects 3sg_m" in output
    assert "The focused object does not control agreement" in output
    assert "GRAM-OBJFOCUS-FRONT-001" in output
    assert "Safe corrected text:\nMuus ayay wiilku cunay." in output


def test_cli_reports_fronted_focus_verb_conflict_against_post_focus_subject():
    output = _run_checker("Muus ayuu wiilku cuntay.")
    assert "possible focused-object agreement conflict" in output
    assert "finite verb" in output
    assert "explicit subject expects 3sg_m" in output
    assert "GRAM-OBJFOCUS-FRONT-001" in output
    assert "Safe corrected text:\nMuus ayuu wiilku cuntay." in output


def test_cli_reports_plural_fronted_focus_conflict():
    output = _run_checker("Muus ayuu carruurtu cuneen.")
    assert "possible focused-object agreement conflict" in output
    assert "explicit subject expects 3pl" in output
    assert "contracted focus/subject clitic" in output
    assert "GRAM-OBJFOCUS-FRONT-001" in output


def test_cli_leaves_unknown_and_unlicensed_fronted_focus_verbs_unjudged():
    assert _run_checker("Muus ayuu wiilku cunXYZ.") == "No supported orthography or grammar findings found."
    assert _run_checker("Hadal ayuu wiilku yidhi.") == "No supported orthography or grammar findings found."
    assert _run_checker("Guri ayuu wiilku leeyahay.") == "No supported orthography or grammar findings found."
