import subprocess
import sys

from src.noun_subject_case import analyze_noun_subject_case
from src.subject_focus_agreement import analyze_subject_focus_agreement


NO_FINDINGS = "No supported orthography or grammar findings found."


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_reviewed_absolute_common_noun_focus_case_is_accepted():
    for sentence, noun in (
        ("Wiilka baa yimid.", "Wiilka"),
        ("Wiilka ayaa yimid.", "Wiilka"),
        ("Gabadha baa timid.", "Gabadha"),
        ("Gabadha ayaa timid.", "Gabadha"),
        ("Carruurta ayaa yimid.", "Carruurta"),
    ):
        result = analyze_noun_subject_case(sentence)
        assert result.recognized is True
        assert result.noun_form == noun
        assert result.agrees is True
        assert result.rule_id == "GRAM-SUBJFOCUS-005"


def test_reviewed_u_subject_surface_is_wrong_in_true_noun_focus():
    cases = (
        ("Wiilku baa yimid.", "Wiilka"),
        ("Gabadhu ayaa timid.", "Gabadha"),
        ("Carruurtu ayaa yimid.", "Carruurta"),
    )
    for sentence, expected in cases:
        result = analyze_noun_subject_case(sentence)
        assert result.recognized is True
        assert result.agrees is False
        assert result.expected_subject_form == expected
        assert result.rule_id == "GRAM-SUBJFOCUS-005"


def test_unreviewed_noun_pair_is_not_guessed_from_suffix_shape():
    result = analyze_noun_subject_case("Bisadda ayaa timid.")
    assert result.recognized is False


def test_singular_common_noun_focus_reuses_exact_reviewed_surface_morphology():
    masculine = analyze_subject_focus_agreement("Wiilka ayaa yimid.")
    assert masculine.recognized is True
    assert masculine.expected_person == "3sg_m"
    assert masculine.predicate_persons == ("3sg_m",)
    assert masculine.agrees is True
    assert masculine.rule_id == "GRAM-SUBJFOCUS-005"

    feminine = analyze_subject_focus_agreement("Gabadha baa timid.")
    assert feminine.recognized is True
    assert feminine.expected_person == "3sg_f"
    assert "3sg_f" in feminine.predicate_persons
    assert feminine.agrees is True
    assert feminine.rule_id == "GRAM-SUBJFOCUS-005"


def test_singular_common_noun_focus_detects_gender_person_conflict():
    masculine = analyze_subject_focus_agreement("Wiilka baa timid.")
    assert masculine.recognized is True
    assert masculine.expected_person == "3sg_m"
    assert masculine.agrees is False

    feminine = analyze_subject_focus_agreement("Gabadha ayaa yimid.")
    assert feminine.recognized is True
    assert feminine.expected_person == "3sg_f"
    assert feminine.agrees is False


def test_reviewed_plural_focus_uses_restrictive_simple_past():
    reduced = analyze_subject_focus_agreement("Carruurta ayaa yimid.")
    assert reduced.recognized is True
    assert reduced.expected_person == "3pl"
    assert reduced.agrees is True
    assert reduced.evidence and "restrictive_simple_past" in reduced.evidence
    assert reduced.rule_id == "GRAM-SUBJFOCUS-006"

    full = analyze_subject_focus_agreement("Carruurta ayaa yimaaddeen.")
    assert full.recognized is True
    assert full.expected_person == "3pl"
    assert full.agrees is False
    assert full.evidence and "restrictive_simple_past" in full.evidence
    assert full.rule_id == "GRAM-SUBJFOCUS-006"

    other_plural = analyze_subject_focus_agreement("Baabuurta baa yimid.")
    assert other_plural.recognized is True
    assert other_plural.expected_person == "3pl"
    assert other_plural.agrees is True
    assert other_plural.rule_id == "GRAM-SUBJFOCUS-006"


def test_cli_accepts_reviewed_singular_common_noun_subject_focus():
    for sentence in (
        "Wiilka baa yimid.",
        "Wiilka ayaa yimi.",
        "Gabadha baa timid.",
        "Gabadha ayaa timid.",
    ):
        assert _run_checker(sentence) == NO_FINDINGS


def test_cli_reports_wrong_noun_case_in_subject_focus():
    output = _run_checker("Wiilku baa yimid.")
    assert "possible definite-noun subject-case conflict" in output
    assert "Wiilka" in output
    assert "GRAM-SUBJFOCUS-005" in output

    output = _run_checker("Gabadhu ayaa timid.")
    assert "possible definite-noun subject-case conflict" in output
    assert "Gabadha" in output
    assert "GRAM-SUBJFOCUS-005" in output


def test_cli_reports_singular_common_noun_focus_predicate_conflict():
    output = _run_checker("Gabadha ayaa yimid.")
    assert "possible subject-verb agreement conflict" in output
    assert "'Gabadha' + 'yimid'" in output
    assert "a reviewed 3sg_f predicate" in output


def test_cli_uses_restrictive_plural_focus_simple_past():
    assert _run_checker("Carruurta ayaa yimid.") == NO_FINDINGS

    output = _run_checker("Carruurta ayaa yimaaddeen.")
    assert "possible subject-verb agreement conflict" in output
    assert "'Carruurta' + 'yimaaddeen'" in output
    assert "a reviewed 3pl predicate under restrictive focused-subject simple-past agreement" in output


def test_cli_still_reports_wrong_plural_noun_case_before_focus_particle():
    output = _run_checker("Carruurtu ayaa yimid.")
    assert "possible definite-noun subject-case conflict" in output
    assert "Carruurta" in output
    assert "GRAM-SUBJFOCUS-005" in output
