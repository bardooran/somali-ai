import json
import subprocess
import sys
from pathlib import Path

from src.future_auxiliary_agreement import analyze_future_auxiliary_agreement
from src.morphology_candidates import analyze_surface_form
from src.reviewed_finite_verb import analyze_reviewed_finite_verb


RULE_PATH = Path("rules/grammar/future_auxiliary_agreement.jsonl")


def test_future_rule_is_review_only():
    records = [json.loads(line) for line in RULE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert records
    assert all(record["autofix"] is False for record in records)


def test_future_auxiliaries_are_reviewed_context_forms_not_ordinary_finite_verbs():
    assert any(c.analysis_type == "future_auxiliary" for c in analyze_surface_form("doonaa"))
    assert any(c.analysis_type == "future_auxiliary" for c in analyze_surface_form("doontaa"))
    assert any(c.analysis_type == "future_auxiliary" for c in analyze_surface_form("doonaan"))
    assert analyze_reviewed_finite_verb("doonaa").recognized is False
    assert analyze_reviewed_finite_verb("doontaa").recognized is False
    assert analyze_reviewed_finite_verb("doonaan").recognized is False


def test_masculine_singular_future_auxiliary_agrees():
    result = analyze_future_auxiliary_agreement("Ninku wuu cuni doonaa.")
    assert result.recognized
    assert result.future_stem == "cuni"
    assert result.future_lemma == "cun"
    assert result.subject_number == "singular"
    assert result.subject_gender == "masculine"
    assert result.expected_person == "3sg_m"
    assert set(result.auxiliary_persons) == {"1sg", "3sg_m"}
    assert result.tense_aspect == "timaaddo"
    assert result.agrees is True


def test_masculine_singular_rejects_feminine_future_auxiliary():
    result = analyze_future_auxiliary_agreement("Ninku wuu cuni doontaa.")
    assert result.recognized
    assert result.expected_person == "3sg_m"
    assert set(result.auxiliary_persons) == {"2sg", "3sg_f"}
    assert result.agrees is False


def test_feminine_singular_future_auxiliary_agrees():
    result = analyze_future_auxiliary_agreement("Gabadhu way cuni doontaa.")
    assert result.recognized
    assert result.subject_number == "singular"
    assert result.subject_gender == "feminine"
    assert result.expected_person == "3sg_f"
    assert set(result.auxiliary_persons) == {"2sg", "3sg_f"}
    assert result.agrees is True


def test_feminine_singular_rejects_masculine_future_auxiliary():
    result = analyze_future_auxiliary_agreement("Gabadhu way cuni doonaa.")
    assert result.recognized
    assert result.expected_person == "3sg_f"
    assert set(result.auxiliary_persons) == {"1sg", "3sg_m"}
    assert result.agrees is False


def test_plural_future_auxiliary_agrees():
    result = analyze_future_auxiliary_agreement("Macallimiintu way cuni doonaan.")
    assert result.recognized
    assert result.subject_number == "plural"
    assert result.expected_person == "3pl"
    assert result.auxiliary_persons == ("3pl",)
    assert result.agrees is True


def test_plural_rejects_singular_future_auxiliary():
    result = analyze_future_auxiliary_agreement("Macallimiintu way cuni doonaa.")
    assert result.recognized
    assert result.expected_person == "3pl"
    assert "3pl" not in result.auxiliary_persons
    assert result.agrees is False


def test_unknown_lookalike_auxiliary_is_unjudged_not_guessed():
    result = analyze_future_auxiliary_agreement("Ninku wuu cuni doonaaXYZ.")
    assert result.recognized
    assert result.auxiliary == "doonaaXYZ"
    assert result.auxiliary_persons == ()
    assert result.agrees is None


def test_non_future_stem_does_not_trigger_future_layer():
    assert analyze_future_auxiliary_agreement("Ninku wuu tijaabi doonaa.").recognized is False


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_reports_future_auxiliary_conflict_without_autofix():
    output = _run_checker("Gabadhu way cuni doonaa.")
    assert "possible future auxiliary agreement conflict" in output
    assert "Expected 3sg_f" in output
    assert "Safe corrected text:\nGabadhu way cuni doonaa." in output
