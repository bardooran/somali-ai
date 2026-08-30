import json
import subprocess
import sys
from pathlib import Path

from src.morphology_candidates import analyze_surface_form
from src.noun_gender_agreement import REVIEWED_SINGULAR_FORMS
from src.noun_singular_verb_agreement import analyze_noun_singular_verb_agreement


RULE_PATH = Path("rules/grammar/noun_singular_verb_agreement.jsonl")


def test_rule_is_review_only():
    records = [json.loads(line) for line in RULE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert records
    assert all(record["autofix"] is False for record in records)


def test_subject_holdouts_are_not_exact_reviewed_subjects_or_morphology_entries():
    for subject in ("baabuurku", "ushu"):
        assert subject not in REVIEWED_SINGULAR_FORMS
        assert analyze_surface_form(subject) == ()


def test_masculine_holdout_accepts_reviewed_3sg_m_verb():
    result = analyze_noun_singular_verb_agreement("Baabuurku wuu jabay.")
    assert result.recognized
    assert result.subject_gender == "masculine"
    assert result.subject_number == "singular"
    assert result.expected_person == "3sg_m"
    assert set(result.verb_persons) == {"1sg", "3sg_m"}
    assert result.agrees is True


def test_masculine_holdout_rejects_reviewed_3sg_f_verb():
    result = analyze_noun_singular_verb_agreement("Baabuurku wuu jabtay.")
    assert result.recognized
    assert result.expected_person == "3sg_m"
    assert set(result.verb_persons) == {"2sg", "3sg_f"}
    assert result.agrees is False


def test_feminine_holdout_accepts_reviewed_3sg_f_verb():
    result = analyze_noun_singular_verb_agreement("Ushu way jabtay.")
    assert result.recognized
    assert result.subject_gender == "feminine"
    assert result.subject_number == "singular"
    assert result.expected_person == "3sg_f"
    assert set(result.verb_persons) == {"2sg", "3sg_f"}
    assert result.agrees is True


def test_feminine_holdout_rejects_reviewed_3sg_m_verb():
    result = analyze_noun_singular_verb_agreement("Ushu way jabay.")
    assert result.recognized
    assert result.expected_person == "3sg_f"
    assert set(result.verb_persons) == {"1sg", "3sg_m"}
    assert result.agrees is False


def test_other_reviewed_verb_classes_work_without_sentence_memory():
    masculine = analyze_noun_singular_verb_agreement("Baabuurku wuu adkaaday.")
    feminine = analyze_noun_singular_verb_agreement("Ushu way adkaatay.")
    assert masculine.recognized and masculine.expected_person == "3sg_m" and masculine.agrees is True
    assert feminine.recognized and feminine.expected_person == "3sg_f" and feminine.agrees is True


def test_fake_lookalike_verb_is_unjudged_not_guessed():
    result = analyze_noun_singular_verb_agreement("Baabuurku wuu tijaabayxyz.")
    assert result.recognized
    assert result.verb is None
    assert result.agrees is None


def test_plural_subject_is_outside_singular_layer():
    assert analyze_noun_singular_verb_agreement("Miisasku way jabeen.").recognized is False


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_reports_singular_finite_verb_gender_conflict_without_autofix():
    output = _run_checker("Ushu way jabay.")
    assert "possible singular noun-subject/finite-verb agreement conflict" in output
    assert "Expected 3sg_f" in output
    assert "Safe corrected text:\nUshu way jabay." in output
