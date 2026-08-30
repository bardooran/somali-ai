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


def test_cli_accepts_reviewed_object_focus_sentences():
    for sentence in (
        "Wiilku muus buu cunay.",
        "Gabadhu muus bay cuntay.",
        "Carruurtu muus bay cuneen.",
        "Wiilku muus ayuu cunay.",
        "Gabadhu Cali bay aragtay.",
    ):
        assert _run_checker(sentence) == "No supported orthography or grammar findings found."


def test_cli_reports_object_focus_clitic_conflict_without_autofix():
    output = _run_checker("Wiilku muus bay cunay.")
    assert "possible focused-object agreement conflict" in output
    assert "contracted focus/subject clitic" in output
    assert "explicit subject expects 3sg_m" in output
    assert "The focused object does not control agreement" in output
    assert "Safe corrected text:\nWiilku muus bay cunay." in output


def test_cli_reports_object_focus_verb_conflict_without_autofix():
    output = _run_checker("Gabadhu muus bay cunay.")
    assert "possible focused-object agreement conflict" in output
    assert "finite verb" in output
    assert "explicit subject expects 3sg_f" in output
    assert "Safe corrected text:\nGabadhu muus bay cunay." in output


def test_cli_reports_plural_object_focus_conflict_from_subject():
    output = _run_checker("Carruurtu muus buu cuneen.")
    assert "possible focused-object agreement conflict" in output
    assert "explicit subject expects 3pl" in output
    assert "contracted focus/subject clitic" in output
    assert "Safe corrected text:\nCarruurtu muus buu cuneen." in output


def test_cli_reports_source_attested_arag_agreement_conflict():
    output = _run_checker("Wiilku Cali buu aragtay.")
    assert "possible focused-object agreement conflict" in output
    assert "finite verb" in output
    assert "explicit subject expects 3sg_m" in output
    assert "Safe corrected text:\nWiilku Cali buu aragtay." in output


def test_cli_leaves_unknown_and_unlicensed_focus_verbs_unjudged():
    assert _run_checker("Wiilku muus buu cunXYZ.") == "No supported orthography or grammar findings found."
    assert _run_checker("Wiilku hadal buu yidhi.") == "No supported orthography or grammar findings found."


def test_cli_does_not_duplicate_specialized_possession_focus():
    assert _run_checker("Ninku guri buu leeyahay.") == "No supported orthography or grammar findings found."
