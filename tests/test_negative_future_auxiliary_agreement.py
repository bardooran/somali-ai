import json
import subprocess
import sys
from pathlib import Path

from src.morphology_candidates import analyze_surface_form
from src.negative_future_auxiliary_agreement import (
    analyze_negative_future_auxiliary_agreement,
)
from src.reviewed_finite_verb import analyze_reviewed_finite_verb


RULE_PATH = Path("rules/grammar/negative_future_auxiliary_agreement.jsonl")


def test_negative_future_rules_are_review_only():
    records = [
        json.loads(line)
        for line in RULE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert records
    assert all(record["autofix"] is False for record in records)


def test_negative_future_auxiliaries_are_context_forms_not_ordinary_finite_verbs():
    assert any(c.analysis_type == "future_negative_auxiliary" for c in analyze_surface_form("doono"))
    assert any(c.analysis_type == "future_negative_auxiliary" for c in analyze_surface_form("doonto"))
    assert any(c.analysis_type == "future_negative_auxiliary" for c in analyze_surface_form("doonno"))
    assert analyze_reviewed_finite_verb("doono").recognized is False
    assert analyze_reviewed_finite_verb("doonto").recognized is False
    assert analyze_reviewed_finite_verb("doonno").recognized is False


def test_plural_auxiliary_surfaces_keep_affirmative_negative_ambiguity():
    doontaan_types = {c.analysis_type for c in analyze_surface_form("doontaan")}
    doonaan_types = {c.analysis_type for c in analyze_surface_form("doonaan")}
    assert {"future_auxiliary", "future_negative_auxiliary"} <= doontaan_types
    assert {"future_auxiliary", "future_negative_auxiliary"} <= doonaan_types


def test_masculine_singular_negative_future_agrees():
    result = analyze_negative_future_auxiliary_agreement("Ninku ma cuni doono.")
    assert result.recognized
    assert result.future_stem == "cuni"
    assert result.future_lemma == "cun"
    assert result.subject_number == "singular"
    assert result.subject_gender == "masculine"
    assert result.expected_person == "3sg_m"
    assert result.auxiliary_polarity == "negative"
    assert set(result.auxiliary_persons) == {"1sg", "3sg_m"}
    assert result.agrees is True


def test_masculine_singular_rejects_feminine_negative_auxiliary():
    result = analyze_negative_future_auxiliary_agreement("Ninku ma cuni doonto.")
    assert result.recognized
    assert result.expected_person == "3sg_m"
    assert set(result.auxiliary_persons) == {"2sg", "3sg_f"}
    assert result.agrees is False


def test_feminine_singular_negative_future_agrees():
    result = analyze_negative_future_auxiliary_agreement("Gabadhu ma cuni doonto.")
    assert result.recognized
    assert result.subject_number == "singular"
    assert result.subject_gender == "feminine"
    assert result.expected_person == "3sg_f"
    assert set(result.auxiliary_persons) == {"2sg", "3sg_f"}
    assert result.agrees is True


def test_feminine_singular_rejects_masculine_negative_auxiliary():
    result = analyze_negative_future_auxiliary_agreement("Gabadhu ma cuni doono.")
    assert result.recognized
    assert result.expected_person == "3sg_f"
    assert set(result.auxiliary_persons) == {"1sg", "3sg_m"}
    assert result.agrees is False


def test_plural_negative_future_agrees_with_syncretic_surface():
    result = analyze_negative_future_auxiliary_agreement("Macallimiintu ma cuni doonaan.")
    assert result.recognized
    assert result.subject_number == "plural"
    assert result.expected_person == "3pl"
    assert result.auxiliary_polarity == "negative"
    assert result.auxiliary_persons == ("3pl",)
    assert result.agrees is True


def test_plural_rejects_singular_negative_auxiliary():
    result = analyze_negative_future_auxiliary_agreement("Macallimiintu ma cuni doono.")
    assert result.recognized
    assert result.expected_person == "3pl"
    assert "3pl" not in result.auxiliary_persons
    assert result.agrees is False


def test_ma_plus_affirmative_future_auxiliary_is_polarity_conflict():
    masculine = analyze_negative_future_auxiliary_agreement("Ninku ma cuni doonaa.")
    feminine = analyze_negative_future_auxiliary_agreement("Gabadhu ma cuni doontaa.")
    assert masculine.recognized and masculine.auxiliary_polarity == "affirmative"
    assert masculine.agrees is False
    assert feminine.recognized and feminine.auxiliary_polarity == "affirmative"
    assert feminine.agrees is False


def test_unknown_lookalike_negative_auxiliary_is_unjudged_not_guessed():
    result = analyze_negative_future_auxiliary_agreement("Ninku ma cuni doonoXYZ.")
    assert result.recognized
    assert result.auxiliary == "doonoXYZ"
    assert result.auxiliary_persons == ()
    assert result.agrees is None


def test_non_future_stem_does_not_trigger_negative_future_layer():
    assert analyze_negative_future_auxiliary_agreement("Ninku ma tijaabi doono.").recognized is False


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_reports_negative_future_gender_conflict_without_autofix():
    output = _run_checker("Gabadhu ma cuni doono.")
    assert "possible negative future auxiliary agreement conflict" in output
    assert "Expected 3sg_f" in output
    assert "Safe corrected text:\nGabadhu ma cuni doono." in output


def test_cli_uses_subject_aware_future_warning_instead_of_duplicate_generic_warning():
    output = _run_checker("Ninku ma cuni doonaa.")
    assert "possible negative future auxiliary agreement conflict" in output
    assert "possible negation-paradigm conflict" not in output
    assert "Safe corrected text:\nNinku ma cuni doonaa." in output


def test_cli_accepts_supported_negative_future_sentence():
    output = _run_checker("Macallimiintu ma cuni doonaan.")
    assert output == "No supported orthography or grammar findings found."
