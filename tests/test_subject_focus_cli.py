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


def test_cli_accepts_reviewed_true_subject_focus_with_bare_baa():
    for sentence in (
        "Cali baa yimid.",
        "Cali baa yimi.",
        "Maryan baa qososhay.",
        "Maryan baa timid.",
    ):
        assert _run_checker(sentence) == NO_FINDINGS


def test_cli_reports_maryan_with_masculine_predicate():
    output = _run_checker("Maryan baa yimid.")
    assert "possible subject-verb agreement conflict" in output
    assert "'Maryan' + 'yimid'" in output
    assert "a reviewed 3sg_f predicate" in output
    assert "Safe corrected text:\nMaryan baa yimid." in output


def test_cli_reports_cali_with_feminine_predicate():
    output = _run_checker("Cali baa timid.")
    assert "possible subject-verb agreement conflict" in output
    assert "'Cali' + 'timid'" in output
    assert "a reviewed 3sg_m predicate" in output
    assert "Safe corrected text:\nCali baa timid." in output


def test_cli_uses_exact_qososhay_sentence_evidence_without_deriving_paradigm():
    output = _run_checker("Cali baa qososhay.")
    assert "possible subject-verb agreement conflict" in output
    assert "'Cali' + 'qososhay'" in output
    assert "a reviewed 3sg_m predicate" in output
    assert "Safe corrected text:\nCali baa qososhay." in output


def test_cli_leaves_unknown_subject_focus_predicate_unjudged():
    assert _run_checker("Cali baa yimidXYZ.") == NO_FINDINGS


def test_cli_does_not_guess_proper_name_gender_outside_reviewed_profiles():
    assert _run_checker("Axmed baa yimid.") == NO_FINDINGS


def test_subject_focus_does_not_weaken_object_focus_clitic_requirement():
    output = _run_checker("Wiilku muus baa cunay.")
    assert "No supported orthography or grammar findings found." not in output
    # Existing object-focus evidence still rejects bare baa when an explicit
    # third-person subject precedes a separately focused object.
    assert "Grammar findings:" in output
