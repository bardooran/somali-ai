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


def test_cli_keeps_reviewed_meeshu_gender_agreement_grammar_silent():
    output = run_cli("Meeshu way weyn tahay.")
    assert "possible noun-subject gender/clitic agreement conflict" not in output
    assert "possible noun-subject predicate/copula agreement conflict" not in output


def test_cli_reports_both_meeshu_masculine_conflicts_without_autofix():
    text = "Meeshu wuu weyn yahay."
    output = run_cli(text)
    assert "Grammar findings:" in output
    assert "possible noun-subject gender/clitic agreement conflict" in output
    assert "supported clitic is 'way'" in output
    assert "possible noun-subject predicate/copula agreement conflict" in output
    assert "supported copula" in output
    assert "'tahay'" in output
    assert "Safe corrected text:" in output
    assert text in output
    assert "Meeshu way weyn tahay." not in output


def test_cli_reports_dugsigu_wrong_clitic_with_reviewed_singular_number():
    text = "Dugsigu way weyn yahay."
    output = run_cli(text)
    assert "possible noun-subject gender/clitic agreement conflict" in output
    assert "supported clitic is 'wuu'" in output
    assert "possible noun-subject predicate/copula agreement conflict" not in output


def test_cli_reports_magaaladu_wrong_copula():
    text = "Magaaladu way qurux badan yahay."
    output = run_cli(text)
    assert "possible noun-subject gender/clitic agreement conflict" not in output
    assert "possible noun-subject predicate/copula agreement conflict" in output
    assert "'tahay'" in output


def test_cli_does_not_force_wuu_for_number_ambiguous_unreviewed_masculine_surface():
    output = run_cli("Macallinku way hadlayaan.")
    assert "possible noun-subject gender/clitic agreement conflict" not in output


def test_cli_preserves_native_reviewed_plural_way_examples():
    for text in ("Baabuurtu way socdaan.", "Carruurtu way ciyaarayaan."):
        output = run_cli(text)
        assert "possible noun-subject gender/clitic agreement conflict" not in output
        assert "possible noun-subject predicate/copula agreement conflict" not in output


def test_cli_accepts_morphology_backed_plural_way_for_both_plural_genders():
    for text in (
        "Miisasku way jiraan.",
        "Duruustu way jiraan.",
        "Macallimiintu way jiraan.",
        "Waddooyinku way jiraan.",
        "Daawooyinku way jiraan.",
    ):
        output = run_cli(text)
        assert "possible noun-subject gender/clitic agreement conflict" not in output


def test_cli_rejects_wuu_for_morphology_backed_plural_subjects():
    for text in (
        "Miisasku wuu jiraan.",
        "Duruustu wuu jiraan.",
        "Waddooyinku wuu jiraan.",
    ):
        output = run_cli(text)
        assert "Grammar findings:" in output
        assert "possible noun-subject gender/clitic agreement conflict" in output
        assert "supported clitic is 'way'" in output
        assert "No automatic rewrite" not in output or "no automatic rewrite" in output.casefold()
        assert text in output


def test_cli_does_not_reclassify_independent_pronoun_as_noun():
    output = run_cli("Iyada way keentay.")
    assert "possible noun-subject gender/clitic agreement conflict" not in output
    assert "possible noun-subject predicate/copula agreement conflict" not in output


def test_cli_accepts_reviewed_plural_past_and_progressive_verb_forms():
    for text in (
        "Macallimiintu way cuneen.",
        "Macallimiintu way cunayaan.",
    ):
        output = run_cli(text)
        assert "possible plural noun-subject/verb agreement conflict" not in output


def test_cli_reports_plural_subject_with_singular_compatible_past_verb():
    text = "Macallimiintu way cunay."
    output = run_cli(text)
    assert "Grammar findings:" in output
    assert "possible plural noun-subject/verb agreement conflict" in output
    assert "Expected 3pl" in output
    assert "1sg, 3sg_m" in output
    assert "Safe corrected text:" in output
    assert text in output
    assert "Macallimiintu way cuneen." not in output


def test_cli_reports_plural_subject_with_singular_compatible_progressive_verb():
    text = "Macallimiintu way cunayaa."
    output = run_cli(text)
    assert "possible plural noun-subject/verb agreement conflict" in output
    assert "Expected 3pl" in output
    assert "1sg, 3sg_m" in output
    assert text in output


def test_cli_keeps_unknown_plural_subject_verb_unjudged():
    output = run_cli("Macallimiintu way tijaabxyz.")
    assert "possible plural noun-subject/verb agreement conflict" not in output
