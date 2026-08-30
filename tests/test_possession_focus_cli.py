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


def test_cli_accepts_reviewed_focused_possession_sentences():
    for sentence in (
        "Ninku guri buu leeyahay.",
        "Gabadhu guri bay leedahay.",
        "Macallimiintu guri bay leeyihiin.",
        "Ninku guri ayuu lahaa.",
        "Gabadhu guri ayay lahayd.",
        "Macallimiintu guri ayay lahaayeen.",
    ):
        assert _run_checker(sentence) == "No supported orthography or grammar findings found."


def test_cli_reports_focus_clitic_conflict_without_autofix():
    output = _run_checker("Ninku guri bay leeyahay.")
    assert "possible focused possession agreement conflict" in output
    assert "contracted focus/subject clitic" in output
    assert "explicit subject expects 3sg_m" in output
    assert "Intervening focused material does not control agreement" in output
    assert "Safe corrected text:\nNinku guri bay leeyahay." in output


def test_cli_reports_possession_verb_conflict_without_autofix():
    output = _run_checker("Gabadhu guri bay leeyahay.")
    assert "possible focused possession agreement conflict" in output
    assert "finite possession verb" in output
    assert "explicit subject expects 3sg_f" in output
    assert "Safe corrected text:\nGabadhu guri bay leeyahay." in output


def test_cli_reports_plural_conflict_from_explicit_subject_not_guri():
    output = _run_checker("Macallimiintu guri bay leedahay.")
    assert "possible focused possession agreement conflict" in output
    assert "explicit subject expects 3pl" in output
    assert "finite possession verb" in output
    assert "Safe corrected text:\nMacallimiintu guri bay leedahay." in output


def test_cli_leaves_unknown_and_conditional_following_forms_unjudged():
    assert _run_checker("Ninku guri buu leeyahaXYZ.") == "No supported orthography or grammar findings found."
    assert _run_checker("Ninku cunto buu cuni lahaa.") == "No supported orthography or grammar findings found."
