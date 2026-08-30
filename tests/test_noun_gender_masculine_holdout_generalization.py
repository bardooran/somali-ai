"""Holdout tests for masculine noun case and agreement generalization.

The subject forms in this file are deliberately absent from the exact native-
reviewed subject list and from the exact morphology datasets. Their paired non-
subject forms are source-backed, so the runtime must combine source morphology
with the reviewed subject-surface rules instead of memorizing subject forms or
complete sentences.
"""

import subprocess
import sys

from src.morphology_candidates import analyze_surface_form
from src.noun_gender_agreement import (
    REVIEWED_SINGULAR_FORMS,
    analyze_noun_gender_agreement,
    infer_subject_gender,
    infer_subject_number,
)
from src.noun_subject_case import analyze_noun_subject_case


# subject surface -> source-backed paired non-subject surface
HOLDOUT_MASCULINE_SINGULARS = {
    "ninku": "ninka",
    "baabuurku": "baabuurka",
}


def test_masculine_holdouts_are_not_memorized_or_direct_morphology_entries():
    for subject in HOLDOUT_MASCULINE_SINGULARS:
        assert subject not in REVIEWED_SINGULAR_FORMS
        assert analyze_surface_form(subject) == ()


def test_masculine_holdout_number_comes_from_source_backed_paired_morphology():
    for subject, paired_surface in HOLDOUT_MASCULINE_SINGULARS.items():
        candidates = analyze_surface_form(paired_surface)
        assert candidates
        assert any(
            candidate.features.get("number") == "singular"
            and candidate.features.get("gender") == "masculine"
            for candidate in candidates
        )

        number, evidence = infer_subject_number(subject)
        assert number == "singular"
        assert evidence == "paired_reviewed_morphology"


def test_masculine_holdout_gender_comes_from_subject_surface_rule():
    for subject in HOLDOUT_MASCULINE_SINGULARS:
        gender, evidence = infer_subject_gender(subject)
        assert gender == "masculine"
        assert evidence == "strong_subject_suffix:ku"


def test_masculine_holdout_subject_case_generalizes():
    for subject, non_subject in HOLDOUT_MASCULINE_SINGULARS.items():
        correct = analyze_noun_subject_case(f"{subject} wuu weyn yahay.")
        assert correct.recognized
        assert correct.agrees is True
        assert correct.expected_subject_form.casefold() == subject

        wrong = analyze_noun_subject_case(f"{non_subject} wuu weyn yahay.")
        assert wrong.recognized
        assert wrong.agrees is False
        assert wrong.expected_subject_form.casefold() == subject


def test_masculine_singular_agreement_generalizes_without_sentence_memory():
    for subject in HOLDOUT_MASCULINE_SINGULARS:
        result = analyze_noun_gender_agreement(f"{subject} wuu weyn yahay.")
        assert result.recognized
        assert result.gender == "masculine"
        assert result.number == "singular"
        assert result.expected_clitic == "wuu"
        assert result.clitic_agrees is True
        assert result.expected_copula == "yahay"
        assert result.copula_agrees is True


def test_feminine_agreement_is_rejected_for_masculine_holdouts():
    for subject in HOLDOUT_MASCULINE_SINGULARS:
        result = analyze_noun_gender_agreement(f"{subject} way weyn tahay.")
        assert result.recognized
        assert result.gender == "masculine"
        assert result.number == "singular"
        assert result.expected_clitic == "wuu"
        assert result.clitic_agrees is False
        assert result.expected_copula == "yahay"
        assert result.copula_agrees is False


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_reports_masculine_subject_case_conflict_without_autofix():
    output = _run_checker("Ninka wuu weyn yahay.")
    assert "possible definite-noun subject-case conflict" in output
    assert "reviewed subject-form candidate is 'Ninku'" in output
    assert "Safe corrected text:\nNinka wuu weyn yahay." in output


def test_cli_reports_masculine_gender_conflict_without_autofix():
    output = _run_checker("Baabuurku way weyn tahay.")
    assert "possible noun-subject gender/clitic agreement conflict" in output
    assert "possible noun-subject predicate/copula agreement conflict" in output
    assert "supported clitic is 'wuu'" in output
    assert "supported copula" in output
    assert "'yahay'" in output
    assert "Safe corrected text:\nBaabuurku way weyn tahay." in output
