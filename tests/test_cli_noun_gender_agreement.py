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
    # The copula already matches masculine singular gender.
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


def test_cli_preserves_plural_way_examples_without_gender_conflict():
    for text in ("Baabuurtu way socdaan.", "Carruurtu way ciyaarayaan."):
        output = run_cli(text)
        assert "possible noun-subject gender/clitic agreement conflict" not in output
        assert "possible noun-subject predicate/copula agreement conflict" not in output


def test_cli_does_not_reclassify_independent_pronoun_as_noun():
    output = run_cli("Iyada way keentay.")
    assert "possible noun-subject gender/clitic agreement conflict" not in output
    assert "possible noun-subject predicate/copula agreement conflict" not in output
