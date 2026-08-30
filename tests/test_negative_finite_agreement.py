import json
import subprocess
import sys
from pathlib import Path

from src.morphology_candidates import analyze_surface_form
from src.negative_finite_agreement import analyze_negative_finite_agreement
from src.reviewed_finite_verb import analyze_reviewed_finite_verb


RULE_PATH = Path("rules/grammar/negative_finite_agreement.jsonl")


def test_negative_finite_rule_is_review_only():
    records = [
        json.loads(line)
        for line in RULE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert records
    assert all(record["autofix"] is False for record in records)


def test_negative_forms_are_context_morphology_not_ordinary_affirmative_finite_forms():
    assert any(c.analysis_type == "negative_finite_verb" for c in analyze_surface_form("cuno"))
    assert any(c.analysis_type == "negative_finite_verb" for c in analyze_surface_form("cunto"))
    assert any(c.analysis_type == "negative_finite_verb" for c in analyze_surface_form("cunayo"))
    assert analyze_reviewed_finite_verb("cuno").recognized is False
    assert analyze_reviewed_finite_verb("cunto").recognized is False
    assert analyze_reviewed_finite_verb("cunayo").recognized is False


def test_shared_plural_surfaces_preserve_affirmative_negative_ambiguity():
    cunaan_types = {c.analysis_type for c in analyze_surface_form("cunaan")}
    cunayaan_types = {c.analysis_type for c in analyze_surface_form("cunayaan")}
    assert {"finite_verb", "negative_finite_verb"} <= cunaan_types
    assert {"finite_verb", "negative_finite_verb"} <= cunayaan_types


def test_present_general_negative_agreement_by_gender_and_number():
    masculine = analyze_negative_finite_agreement("Ninku ma cuno.")
    feminine = analyze_negative_finite_agreement("Gabadhu ma cunto.")
    plural = analyze_negative_finite_agreement("Macallimiintu ma cunaan.")

    assert masculine.recognized and masculine.expected_person == "3sg_m"
    assert masculine.tense_aspect == "joogto_caadaley"
    assert set(masculine.verb_persons) == {"1sg", "3sg_m"}
    assert masculine.agrees is True

    assert feminine.recognized and feminine.expected_person == "3sg_f"
    assert set(feminine.verb_persons) == {"2sg", "3sg_f"}
    assert feminine.agrees is True

    assert plural.recognized and plural.expected_person == "3pl"
    assert plural.verb_persons == ("3pl",)
    assert plural.agrees is True


def test_present_general_negative_rejects_wrong_person_forms():
    masculine = analyze_negative_finite_agreement("Ninku ma cunto.")
    feminine = analyze_negative_finite_agreement("Gabadhu ma cuno.")
    plural = analyze_negative_finite_agreement("Macallimiintu ma cuno.")
    assert masculine.agrees is False
    assert feminine.agrees is False
    assert plural.agrees is False


def test_progressive_negative_agreement_by_gender_and_number():
    masculine = analyze_negative_finite_agreement("Ninku ma cunayo.")
    feminine = analyze_negative_finite_agreement("Gabadhu ma cunayso.")
    plural = analyze_negative_finite_agreement("Macallimiintu ma cunayaan.")

    assert masculine.tense_aspect == "joogto_socota" and masculine.agrees is True
    assert feminine.tense_aspect == "joogto_socota" and feminine.agrees is True
    assert plural.tense_aspect == "joogto_socota" and plural.agrees is True


def test_progressive_negative_rejects_wrong_person_forms():
    assert analyze_negative_finite_agreement("Ninku ma cunayso.").agrees is False
    assert analyze_negative_finite_agreement("Gabadhu ma cunayo.").agrees is False
    assert analyze_negative_finite_agreement("Macallimiintu ma cunayo.").agrees is False


def test_simple_past_negative_is_explicitly_person_neutralized():
    for sentence, expected in (
        ("Ninku ma cunin.", "3sg_m"),
        ("Gabadhu ma cunin.", "3sg_f"),
        ("Macallimiintu ma cunin.", "3pl"),
    ):
        result = analyze_negative_finite_agreement(sentence)
        assert result.recognized
        assert result.tense_aspect == "tagto"
        assert result.expected_person == expected
        assert result.person_neutralized is True
        assert result.agrees is True


def test_ma_plus_affirmative_form_is_polarity_conflict():
    present = analyze_negative_finite_agreement("Ninku ma cunaa.")
    progressive = analyze_negative_finite_agreement("Gabadhu ma cunaysaa.")
    past = analyze_negative_finite_agreement("Ninku ma cunay.")
    for result in (present, progressive, past):
        assert result.recognized
        assert result.polarity == "affirmative"
        assert result.agrees is False


def test_unknown_negative_lookalike_is_unjudged_not_guessed():
    result = analyze_negative_finite_agreement("Ninku ma cunoXYZ.")
    assert result.recognized
    assert result.verb == "cunoXYZ"
    assert result.verb_persons == ()
    assert result.agrees is None


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_reports_negative_finite_gender_conflict_without_autofix():
    output = _run_checker("Gabadhu ma cuno.")
    assert "possible negative finite subject/verb agreement conflict" in output
    assert "Expected 3sg_f" in output
    assert "Safe corrected text:\nGabadhu ma cuno." in output


def test_cli_uses_subject_aware_warning_instead_of_duplicate_generic_negation_warning():
    output = _run_checker("Ninku ma cunaa.")
    assert "possible negative finite subject/verb agreement conflict" in output
    assert "possible negation-paradigm conflict" not in output
    assert "Safe corrected text:\nNinku ma cunaa." in output


def test_cli_accepts_person_neutralized_past_negative():
    output = _run_checker("Gabadhu ma cunin.")
    assert output == "No supported orthography or grammar findings found."
