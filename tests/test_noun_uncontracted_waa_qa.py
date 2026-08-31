import subprocess
import sys

from src.noun_gender_agreement import analyze_noun_gender_agreement
from src.noun_subject_case import analyze_noun_subject_case


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_attested_feminine_uncontracted_waa_ay_is_recognized():
    result = analyze_noun_gender_agreement("Gabadhu waa ay ordaysaa.")

    assert result.recognized is True
    assert result.subject == "Gabadhu"
    assert result.gender == "feminine"
    assert result.number == "singular"
    assert result.clitic == "waa ay"
    assert result.expected_clitic == "waa ay"
    assert result.clitic_agrees is True


def test_attested_masculine_uncontracted_waa_uu_is_recognized():
    result = analyze_noun_gender_agreement("Wiilku waa uu ordayaa.")

    assert result.recognized is True
    assert result.subject == "Wiilku"
    assert result.gender == "masculine"
    assert result.number == "singular"
    assert result.clitic == "waa uu"
    assert result.expected_clitic == "waa uu"
    assert result.clitic_agrees is True


def test_uncontracted_gender_cross_pairs_are_reported_not_silently_accepted():
    feminine = analyze_noun_gender_agreement("Gabadhu waa uu ordayaa.")
    masculine = analyze_noun_gender_agreement("Wiilku waa ay ordaysaa.")

    assert feminine.recognized is True
    assert feminine.expected_clitic == "waa ay"
    assert feminine.clitic_agrees is False

    assert masculine.recognized is True
    assert masculine.expected_clitic == "waa uu"
    assert masculine.clitic_agrees is False


def test_uncontracted_statement_keeps_reviewed_definite_subject_case():
    correct = analyze_noun_subject_case("Wiilku waa uu ordayaa.")
    wrong = analyze_noun_subject_case("Wiilka waa uu ordayaa.")

    assert correct.recognized is True
    assert correct.agrees is True
    assert correct.expected_subject_form == "Wiilku"

    assert wrong.recognized is True
    assert wrong.agrees is False
    assert wrong.expected_subject_form == "Wiilku"


def test_cli_reports_uncontracted_noun_gender_conflict_without_autofix():
    output = _run_checker("Gabadhu waa uu ordayaa.")

    assert "possible noun-subject gender/clitic agreement conflict" in output
    assert "supported clitic is 'waa ay'" in output
    assert "Safe corrected text:\nGabadhu waa uu ordayaa." in output


def test_cli_reports_uncontracted_subject_case_conflict_without_autofix():
    output = _run_checker("Wiilka waa uu ordayaa.")

    assert "possible definite-noun subject-case conflict" in output
    assert "reviewed subject-form candidate is 'Wiilku'" in output
    assert "Safe corrected text:\nWiilka waa uu ordayaa." in output
