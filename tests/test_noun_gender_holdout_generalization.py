"""Holdout tests for noun case and gender/number agreement generalization.

These subjects are deliberately absent from the exact native-reviewed subject
list and from the exact morphology datasets. Their paired non-subject definite
forms are source-backed in the Qaamuus morphology data, so the runtime must
combine that evidence with reviewed subject-surface case and gender rules
instead of memorizing subject forms or whole sentences.
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
HOLDOUT_FEMININE_SINGULARS = {
    "maradu": "marada",
    "baddu": "badda",
    "qodaxdu": "qodaxda",
    "bacdu": "bacda",
    "gallaydu": "gallayda",
    "bu'du": "bu'da",
    "ushu": "usha",
    "ishu": "isha",
    "bishu": "bisha",
}


def test_holdouts_are_not_memorized_or_direct_morphology_entries():
    for subject in HOLDOUT_FEMININE_SINGULARS:
        assert subject not in REVIEWED_SINGULAR_FORMS
        assert analyze_surface_form(subject) == ()


def test_holdout_number_comes_from_paired_source_backed_morphology():
    for subject, paired_surface in HOLDOUT_FEMININE_SINGULARS.items():
        candidates = analyze_surface_form(paired_surface)
        assert candidates
        assert any(
            candidate.features.get("number") == "singular"
            and candidate.features.get("gender") == "feminine"
            for candidate in candidates
        )

        number, evidence = infer_subject_number(subject)
        assert number == "singular"
        assert evidence == "paired_reviewed_morphology"


def test_holdout_gender_comes_from_subject_surface_not_exact_sentence_memory():
    for subject in HOLDOUT_FEMININE_SINGULARS:
        gender, evidence = infer_subject_gender(subject)
        assert gender == "feminine"
        assert evidence.startswith("strong_subject_suffix:")


def test_holdout_subject_case_generalizes_from_source_backed_pairs():
    for subject, non_subject in HOLDOUT_FEMININE_SINGULARS.items():
        correct = analyze_noun_subject_case(f"{subject} way weyn tahay.")
        assert correct.recognized
        assert correct.agrees is True
        assert correct.expected_subject_form.casefold() == subject

        wrong = analyze_noun_subject_case(f"{non_subject} way weyn tahay.")
        assert wrong.recognized
        assert wrong.agrees is False
        assert wrong.expected_subject_form.casefold() == subject


def test_holdout_feminine_singular_agreement_generalizes():
    for subject in HOLDOUT_FEMININE_SINGULARS:
        result = analyze_noun_gender_agreement(f"{subject} way weyn tahay.")
        assert result.recognized
        assert result.gender == "feminine"
        assert result.number == "singular"
        assert result.expected_clitic == "way"
        assert result.clitic_agrees is True
        assert result.expected_copula == "tahay"
        assert result.copula_agrees is True


def test_holdout_masculine_agreement_is_rejected():
    for subject in HOLDOUT_FEMININE_SINGULARS:
        result = analyze_noun_gender_agreement(f"{subject} wuu weyn yahay.")
        assert result.recognized
        assert result.gender == "feminine"
        assert result.number == "singular"
        assert result.expected_clitic == "way"
        assert result.clitic_agrees is False
        assert result.expected_copula == "tahay"
        assert result.copula_agrees is False


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_exposes_holdout_subject_case_conflict_without_autofixing():
    output = _run_checker("Marada way weyn tahay.")
    assert "possible definite-noun subject-case conflict" in output
    assert "reviewed subject-form candidate is 'Maradu'" in output
    assert "Safe corrected text:\nMarada way weyn tahay." in output


def test_cli_exposes_holdout_gender_conflict_without_autofixing():
    output = _run_checker("Maradu wuu weyn yahay.")
    assert "possible noun-subject gender/clitic agreement conflict" in output
    assert "possible noun-subject predicate/copula agreement conflict" in output
    assert "supported clitic is 'way'" in output
    assert "supported copula" in output
    assert "'tahay'" in output
    assert "Safe corrected text:\nMaradu wuu weyn yahay." in output
