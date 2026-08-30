import json
import subprocess
import sys
from pathlib import Path

from src.conditional_agreement import analyze_conditional_agreement
from src.morphology_candidates import analyze_surface_form
from src.reviewed_finite_verb import analyze_reviewed_finite_verb


RULE_PATH = Path("rules/grammar/conditional_agreement.jsonl")


def test_conditional_rules_are_review_only():
    records = [
        json.loads(line)
        for line in RULE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert {record["id"] for record in records} == {
        "GRAM-COND-AFF-001",
        "GRAM-COND-NEG-001",
    }
    assert all(record["autofix"] is False for record in records)


def test_conditional_auxiliaries_share_surfaces_with_possessive_past():
    for surface in ("lahaa", "lahayd", "lahaayeen"):
        candidates = analyze_surface_form(surface)
        assert any(c.analysis_type == "conditional_auxiliary" for c in candidates)
        assert analyze_reviewed_finite_verb(surface).recognized is True
        assert "leeyahay" in analyze_reviewed_finite_verb(surface).lemmas

    # Cross-validation corrected the earlier parsed 3pl spelling.
    assert analyze_surface_form("lahayeen") == ()


def test_negative_conditional_surfaces_preserve_contextual_ambiguity():
    cuneen_types = {c.analysis_type for c in analyze_surface_form("cuneen")}
    cunteen_types = {c.analysis_type for c in analyze_surface_form("cunteen")}
    assert "negative_conditional_finite" in cuneen_types
    assert "negative_conditional_finite" in cunteen_types
    assert analyze_reviewed_finite_verb("cuneen").recognized is True
    assert analyze_reviewed_finite_verb("cunteen").recognized is True


def test_masculine_affirmative_conditional_agrees():
    result = analyze_conditional_agreement("Ninku wuu cuni lahaa.")
    assert result.recognized
    assert result.construction == "affirmative_conditional"
    assert result.subject_number == "singular"
    assert result.subject_gender == "masculine"
    assert result.conditional_stem == "cuni"
    assert result.verb_or_auxiliary == "lahaa"
    assert set(result.persons) == {"1sg", "3sg_m"}
    assert result.expected_person == "3sg_m"
    assert result.agrees is True


def test_masculine_affirmative_conditional_rejects_feminine_auxiliary():
    result = analyze_conditional_agreement("Ninku wuu cuni lahayd.")
    assert result.recognized
    assert result.expected_person == "3sg_m"
    assert set(result.persons) == {"2sg", "3sg_f"}
    assert result.agrees is False


def test_feminine_affirmative_conditional_agrees():
    result = analyze_conditional_agreement("Gabadhu way cuni lahayd.")
    assert result.recognized
    assert result.subject_number == "singular"
    assert result.subject_gender == "feminine"
    assert result.expected_person == "3sg_f"
    assert set(result.persons) == {"2sg", "3sg_f"}
    assert result.agrees is True


def test_plural_affirmative_conditional_agrees():
    result = analyze_conditional_agreement("Macallimiintu way cuni lahaayeen.")
    assert result.recognized
    assert result.subject_number == "plural"
    assert result.expected_person == "3pl"
    assert result.persons == ("3pl",)
    assert result.agrees is True


def test_plural_affirmative_conditional_rejects_singular_auxiliary():
    result = analyze_conditional_agreement("Macallimiintu way cuni lahaa.")
    assert result.recognized
    assert result.expected_person == "3pl"
    assert "3pl" not in result.persons
    assert result.agrees is False


def test_negative_conditional_uses_exact_source_person_mapping():
    masculine = analyze_conditional_agreement("Ninku ma cuneen.")
    feminine = analyze_conditional_agreement("Gabadhu ma cunteen.")
    plural = analyze_conditional_agreement("Macallimiintu ma cuneen.")

    assert masculine.recognized and masculine.polarity == "negative"
    assert masculine.expected_person == "3sg_m"
    assert set(masculine.persons) == {"1sg", "3sg_m", "3pl"}
    assert masculine.agrees is True

    assert feminine.recognized and feminine.polarity == "negative"
    assert feminine.expected_person == "3sg_f"
    assert set(feminine.persons) == {"2sg", "3sg_f", "2pl"}
    assert feminine.agrees is True

    assert plural.recognized and plural.polarity == "negative"
    assert plural.expected_person == "3pl"
    assert set(plural.persons) == {"1sg", "3sg_m", "3pl"}
    assert plural.agrees is True


def test_negative_conditional_rejects_wrong_exact_person_mapping():
    masculine = analyze_conditional_agreement("Ninku ma cunteen.")
    feminine = analyze_conditional_agreement("Gabadhu ma cuneen.")
    plural = analyze_conditional_agreement("Macallimiintu ma cunteen.")
    assert masculine.recognized and masculine.agrees is False
    assert feminine.recognized and feminine.agrees is False
    assert plural.recognized and plural.agrees is False


def test_ma_plus_affirmative_conditional_is_polarity_conflict():
    masculine = analyze_conditional_agreement("Ninku ma cuni lahaa.")
    feminine = analyze_conditional_agreement("Gabadhu ma cuni lahayd.")
    assert masculine.recognized
    assert masculine.construction == "negative_conditional"
    assert masculine.polarity == "affirmative"
    assert masculine.agrees is False
    assert feminine.recognized
    assert feminine.polarity == "affirmative"
    assert feminine.agrees is False


def test_unknown_conditional_auxiliary_is_unjudged_not_guessed():
    result = analyze_conditional_agreement("Ninku wuu cuni lahaaXYZ.")
    assert result.recognized
    assert result.verb_or_auxiliary == "lahaaXYZ"
    assert result.persons == ()
    assert result.agrees is None


def test_unknown_negative_conditional_is_not_guessed():
    result = analyze_conditional_agreement("Ninku ma cuneenXYZ.")
    assert result.recognized is False


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_reports_affirmative_conditional_agreement_conflict_without_autofix():
    output = _run_checker("Gabadhu way cuni lahaa.")
    assert "possible conditional agreement conflict" in output
    assert "Expected 3sg_f" in output
    assert "possible singular noun/finite-verb agreement conflict" not in output
    assert "Safe corrected text:\nGabadhu way cuni lahaa." in output


def test_cli_accepts_reviewed_negative_conditional_without_generic_negative_conflict():
    output = _run_checker("Ninku ma cuneen.")
    assert output == "No supported orthography or grammar findings found."


def test_cli_reports_negative_conditional_conflict_once():
    output = _run_checker("Gabadhu ma cuneen.")
    assert "possible negative conditional agreement conflict" in output
    assert "Expected 3sg_f" in output
    assert "possible negative finite subject/verb agreement conflict" not in output
    assert "Safe corrected text:\nGabadhu ma cuneen." in output


def test_cli_reports_ma_plus_affirmative_conditional_as_conditional_polarity_conflict():
    output = _run_checker("Ninku ma cuni lahaa.")
    assert "possible negative conditional agreement conflict" in output
    assert "polarity 'affirmative'" in output
    assert "Safe corrected text:\nNinku ma cuni lahaa." in output
