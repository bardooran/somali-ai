"""Holdout tests for plural noun + finite-verb agreement generalization.

The subject surfaces here are not stored as exact morphology entries or exact
native-reviewed plural subjects. Their paired definite non-subject forms are
source-backed, while the verb paradigm is independently source-backed. The
runtime must combine those two evidence layers instead of memorizing sentences.
"""

import subprocess
import sys

from src.morphology_candidates import analyze_surface_form
from src.noun_gender_agreement import REVIEWED_PLURAL_FORMS, infer_subject_number
from src.noun_number_verb_agreement import analyze_noun_number_verb_agreement


# subject surface -> source-backed paired definite plural surface
HOLDOUT_PLURAL_SUBJECTS = {
    "miisasku": "miisaska",
    "duruustu": "duruusta",
    "macallimiintu": "macallimiinta",
    "waddooyinku": "waddooyinka",
    "daawooyinku": "daawooyinka",
}


def test_plural_subject_holdouts_are_not_memorized_exactly():
    for subject in HOLDOUT_PLURAL_SUBJECTS:
        assert subject not in REVIEWED_PLURAL_FORMS
        assert analyze_surface_form(subject) == ()


def test_plural_number_is_recovered_from_paired_source_morphology():
    for subject, paired_surface in HOLDOUT_PLURAL_SUBJECTS.items():
        candidates = analyze_surface_form(paired_surface)
        assert candidates
        assert any(candidate.features.get("number") == "plural" for candidate in candidates)

        number, evidence = infer_subject_number(subject)
        assert number == "plural"
        assert evidence == "paired_reviewed_morphology"


def test_yaraad_paradigm_has_independent_reviewed_person_evidence():
    plural = analyze_surface_form("yaraadeen")
    singular = analyze_surface_form("yaraaday")

    assert any(
        candidate.features.get("part_of_speech") == "verb"
        and candidate.features.get("person") == "3pl"
        for candidate in plural
    )
    assert any(
        candidate.features.get("part_of_speech") == "verb"
        and set(candidate.features.get("possible_persons", [])) == {"1sg", "3sg_m"}
        for candidate in singular
    )


def test_plural_holdouts_accept_source_backed_third_person_plural_verb():
    for subject in HOLDOUT_PLURAL_SUBJECTS:
        result = analyze_noun_number_verb_agreement(f"{subject} way yaraadeen.")
        assert result.recognized
        assert result.subject_number == "plural"
        assert result.number_evidence == "paired_reviewed_morphology"
        assert result.verb == "yaraadeen"
        assert result.verb_persons == ("3pl",)
        assert result.expected_person == "3pl"
        assert result.agrees is True


def test_plural_holdouts_reject_singular_compatible_yaraad_form():
    for subject in HOLDOUT_PLURAL_SUBJECTS:
        result = analyze_noun_number_verb_agreement(f"{subject} way yaraaday.")
        assert result.recognized
        assert result.subject_number == "plural"
        assert result.verb == "yaraaday"
        assert "3pl" not in result.verb_persons
        assert set(result.verb_persons) == {"1sg", "3sg_m"}
        assert result.expected_person == "3pl"
        assert result.agrees is False


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_reports_holdout_plural_verb_conflict_without_autofix():
    output = _run_checker("Waddooyinku way yaraaday.")
    assert "possible plural noun-subject/verb agreement conflict" in output
    assert "Expected 3pl" in output
    assert "Safe corrected text:\nWaddooyinku way yaraaday." in output
