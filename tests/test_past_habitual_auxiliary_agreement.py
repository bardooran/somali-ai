import json
import subprocess
import sys
from pathlib import Path

from src.morphology_candidates import analyze_surface_form
from src.past_habitual_auxiliary_agreement import analyze_past_habitual_auxiliary_agreement


RULE_PATH = Path("rules/grammar/past_habitual_auxiliary_agreement.jsonl")


def test_past_habitual_rule_is_review_only():
    records = [
        json.loads(line)
        for line in RULE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert records
    assert all(record["autofix"] is False for record in records)


def test_iibsan_is_an_exact_reviewed_habitual_stem_for_iibso():
    candidates = [
        candidate
        for candidate in analyze_surface_form("iibsan")
        if candidate.analysis_type == "past_habitual_stem"
    ]
    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.lemma == "iibso"
    assert candidate.features["form"] == "infinitive"
    assert candidate.features["possible_use"] == "past_habitual_with_auxiliary"
    assert candidate.features["tense_aspect"] == "tagto_caadaley"


def test_raadin_is_exact_reviewed_class2_habitual_stem_for_raadi():
    candidates = [
        candidate
        for candidate in analyze_surface_form("raadin")
        if candidate.analysis_type == "past_habitual_stem"
    ]
    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.lemma == "raadi"
    assert candidate.features["conjugation_class"] == "II"
    assert candidate.features["form"] == "infinitive"
    assert candidate.features["possible_use"] == "past_habitual_with_auxiliary"
    assert candidate.features["tense_aspect"] == "tagto_caadaley"
    assert candidate.status == "source_backed_context_required"


def test_gothenburg_tone_marked_heesi_evidence_is_not_silently_normalized():
    assert not any(
        candidate.analysis_type == "past_habitual_stem"
        for candidate in analyze_surface_form("heesi")
    )


def test_masculine_singular_iibsan_habitual_auxiliary_agrees():
    result = analyze_past_habitual_auxiliary_agreement(
        "Ninku wuu iibsan jiray hilibka."
    )
    assert result.recognized
    assert result.habitual_stem == "iibsan"
    assert result.habitual_lemma == "iibso"
    assert result.subject_number == "singular"
    assert result.subject_gender == "masculine"
    assert result.expected_person == "3sg_m"
    assert set(result.auxiliary_persons) == {"1sg", "3sg_m"}
    assert result.tense_aspect == "tagto_caadaley"
    assert result.agrees is True


def test_masculine_singular_rejects_feminine_habitual_auxiliary():
    result = analyze_past_habitual_auxiliary_agreement(
        "Ninku wuu iibsan jirtay hilibka."
    )
    assert result.recognized
    assert result.expected_person == "3sg_m"
    assert set(result.auxiliary_persons) == {"2sg", "3sg_f"}
    assert result.agrees is False


def test_feminine_singular_iibsan_habitual_auxiliary_agrees():
    result = analyze_past_habitual_auxiliary_agreement(
        "Gabadhu way iibsan jirtay rootiga."
    )
    assert result.recognized
    assert result.subject_number == "singular"
    assert result.subject_gender == "feminine"
    assert result.expected_person == "3sg_f"
    assert set(result.auxiliary_persons) == {"2sg", "3sg_f"}
    assert result.agrees is True


def test_feminine_singular_rejects_masculine_habitual_auxiliary():
    result = analyze_past_habitual_auxiliary_agreement(
        "Gabadhu way iibsan jiray rootiga."
    )
    assert result.recognized
    assert result.expected_person == "3sg_f"
    assert set(result.auxiliary_persons) == {"1sg", "3sg_m"}
    assert result.agrees is False


def test_plural_iibsan_habitual_auxiliary_agrees():
    result = analyze_past_habitual_auxiliary_agreement(
        "Macallimiintu way iibsan jireen buugaagta."
    )
    assert result.recognized
    assert result.subject_number == "plural"
    assert result.expected_person == "3pl"
    assert result.auxiliary_persons == ("3pl",)
    assert result.agrees is True


def test_plural_rejects_singular_habitual_auxiliary():
    result = analyze_past_habitual_auxiliary_agreement(
        "Macallimiintu way iibsan jiray buugaagta."
    )
    assert result.recognized
    assert result.expected_person == "3pl"
    assert "3pl" not in result.auxiliary_persons
    assert result.agrees is False


def test_class2_raadin_masculine_habitual_agrees_on_new_sentence():
    result = analyze_past_habitual_auxiliary_agreement(
        "Ninku wuu raadin jiray shaqo."
    )
    assert result.recognized
    assert result.habitual_stem == "raadin"
    assert result.habitual_lemma == "raadi"
    assert result.expected_person == "3sg_m"
    assert set(result.auxiliary_persons) == {"1sg", "3sg_m"}
    assert result.agrees is True


def test_class2_raadin_feminine_rejects_masculine_auxiliary_on_new_sentence():
    result = analyze_past_habitual_auxiliary_agreement(
        "Gabadhu way raadin jiray buugga."
    )
    assert result.recognized
    assert result.habitual_lemma == "raadi"
    assert result.expected_person == "3sg_f"
    assert set(result.auxiliary_persons) == {"1sg", "3sg_m"}
    assert result.agrees is False


def test_class2_raadin_plural_habitual_agrees_on_new_sentence():
    result = analyze_past_habitual_auxiliary_agreement(
        "Macallimiintu way raadin jireen ardayda."
    )
    assert result.recognized
    assert result.habitual_lemma == "raadi"
    assert result.expected_person == "3pl"
    assert result.auxiliary_persons == ("3pl",)
    assert result.agrees is True


def test_class2_finite_past_raadiyay_is_not_reinterpreted_as_habitual_infinitive():
    result = analyze_past_habitual_auxiliary_agreement(
        "Ninku wuu raadiyay jiray shaqo."
    )
    assert result.recognized is False


def test_future_auxiliary_after_reviewed_iibsan_stem_is_left_unjudged_here():
    result = analyze_past_habitual_auxiliary_agreement(
        "Ninku wuu iibsan doonaa hilibka."
    )
    assert result.recognized
    assert result.auxiliary == "doonaa"
    assert result.auxiliary_persons == ()
    assert result.agrees is None


def test_reviewed_finite_past_cunay_is_not_guessed_as_habitual_stem():
    result = analyze_past_habitual_auxiliary_agreement("Ninku wuu cunay jiray.")
    assert result.recognized is False


def test_existing_cuni_habitual_analysis_is_preserved():
    result = analyze_past_habitual_auxiliary_agreement("Gabadhu way cuni jirtay.")
    assert result.recognized
    assert result.habitual_lemma == "cun"
    assert result.expected_person == "3sg_f"
    assert result.agrees is True


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_reports_iibsan_habitual_auxiliary_conflict_without_autofix():
    sentence = "Gabadhu way iibsan jiray rootiga."
    output = _run_checker(sentence)
    assert "possible past habitual auxiliary agreement conflict" in output
    assert "Expected 3sg_f" in output
    assert f"Safe corrected text:\n{sentence}" in output


def test_cli_reports_raadin_habitual_auxiliary_conflict_without_autofix():
    sentence = "Gabadhu way raadin jiray buugga."
    output = _run_checker(sentence)
    assert "possible past habitual auxiliary agreement conflict" in output
    assert "Expected 3sg_f" in output
    assert f"Safe corrected text:\n{sentence}" in output
