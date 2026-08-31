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


def test_cli_accepts_reviewed_true_subject_focus_with_bare_baa_or_ayaa():
    for sentence in (
        "Cali baa yimid.",
        "Cali ayaa yimid.",
        "Cali baa yimi.",
        "Cali ayaa yimi.",
        "Maryan baa qososhay.",
        "Maryan ayaa qososhay.",
        "Maryan baa timid.",
        "Maryan ayaa timid.",
    ):
        assert _run_checker(sentence) == NO_FINDINGS


def test_cli_reports_maryan_with_masculine_predicate_for_baa_and_ayaa():
    for sentence in ("Maryan baa yimid.", "Maryan ayaa yimid."):
        output = _run_checker(sentence)
        assert "possible subject-verb agreement conflict" in output
        assert "'Maryan' + 'yimid'" in output
        assert "a reviewed 3sg_f predicate" in output
        assert f"Safe corrected text:\n{sentence}" in output


def test_cli_reports_cali_with_feminine_predicate_for_baa_and_ayaa():
    for sentence in ("Cali baa timid.", "Cali ayaa timid."):
        output = _run_checker(sentence)
        assert "possible subject-verb agreement conflict" in output
        assert "'Cali' + 'timid'" in output
        assert "a reviewed 3sg_m predicate" in output
        assert f"Safe corrected text:\n{sentence}" in output


def test_cli_uses_exact_qososhay_sentence_evidence_without_deriving_paradigm():
    for sentence in ("Cali baa qososhay.", "Cali ayaa qososhay."):
        output = _run_checker(sentence)
        assert "possible subject-verb agreement conflict" in output
        assert "'Cali' + 'qososhay'" in output
        assert "a reviewed 3sg_m predicate" in output
        assert f"Safe corrected text:\n{sentence}" in output


def test_cli_leaves_unknown_subject_focus_predicate_unjudged():
    assert _run_checker("Cali baa yimidXYZ.") == NO_FINDINGS
    assert _run_checker("Cali ayaa yimidXYZ.") == NO_FINDINGS


def test_cli_does_not_guess_proper_name_gender_outside_reviewed_profiles():
    assert _run_checker("Axmed baa yimid.") == NO_FINDINGS
    assert _run_checker("Axmed ayaa yimid.") == NO_FINDINGS


def test_cli_does_not_treat_ayuu_or_ayay_as_bare_subject_focus():
    # These contracted forms contain a subject clitic and belong to a different
    # structural analysis. Subject-focus evidence must not be used to judge them.
    assert _run_checker("Cali ayuu yimidXYZ.") == NO_FINDINGS
    assert _run_checker("Maryan ayay qososhayXYZ.") == NO_FINDINGS


def test_subject_focus_does_not_weaken_object_focus_clitic_requirement():
    for sentence in ("Wiilku muus baa cunay.", "Wiilku muus ayaa cunay."):
        output = _run_checker(sentence)
        assert NO_FINDINGS not in output
        # Existing object-focus evidence still rejects bare baa/ayaa when an
        # explicit third-person subject precedes a separately focused object.
        assert "Grammar findings:" in output
