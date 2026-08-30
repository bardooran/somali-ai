import json
import subprocess
import sys
from pathlib import Path

from src.noun_number_verb_agreement import analyze_noun_number_verb_agreement
from src.noun_singular_verb_agreement import analyze_noun_singular_verb_agreement
from src.past_habitual_auxiliary_agreement import analyze_past_habitual_auxiliary_agreement
from src.reviewed_finite_verb import analyze_reviewed_finite_verb


RULE_PATH = Path("rules/grammar/past_aspect_agreement.jsonl")


def test_past_aspect_rules_are_review_only():
    records = [json.loads(line) for line in RULE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert records
    assert all(record["autofix"] is False for record in records)


def test_past_progressive_forms_are_exact_reviewed_finite_morphology():
    masculine = analyze_reviewed_finite_verb("cunayay")
    feminine = analyze_reviewed_finite_verb("cunaysay")
    plural = analyze_reviewed_finite_verb("cunayeen")
    assert masculine.recognized and set(masculine.persons) == {"1sg", "3sg_m"}
    assert feminine.recognized and set(feminine.persons) == {"2sg", "3sg_f"}
    assert plural.recognized and plural.persons == ("3pl",)
    assert masculine.tense_aspects == ("tagto_socota",)
    assert feminine.tense_aspects == ("tagto_socota",)
    assert plural.tense_aspects == ("tagto_socota",)


def test_past_progressive_singular_gender_agreement():
    masculine_ok = analyze_noun_singular_verb_agreement("Ninku wuu cunayay.")
    masculine_bad = analyze_noun_singular_verb_agreement("Ninku wuu cunaysay.")
    feminine_ok = analyze_noun_singular_verb_agreement("Gabadhu way cunaysay.")
    feminine_bad = analyze_noun_singular_verb_agreement("Gabadhu way cunayay.")
    assert masculine_ok.agrees is True
    assert masculine_bad.agrees is False
    assert feminine_ok.agrees is True
    assert feminine_bad.agrees is False


def test_past_progressive_plural_agreement():
    correct = analyze_noun_number_verb_agreement("Macallimiintu way cunayeen.")
    wrong = analyze_noun_number_verb_agreement("Macallimiintu way cunayay.")
    assert correct.recognized and correct.agrees is True
    assert wrong.recognized and wrong.agrees is False


def test_habitual_auxiliary_is_not_an_ordinary_finite_verb():
    assert analyze_reviewed_finite_verb("jiray").recognized is False
    assert analyze_reviewed_finite_verb("jirtay").recognized is False
    assert analyze_reviewed_finite_verb("jireen").recognized is False


def test_past_habitual_masculine_and_feminine_agreement():
    masculine_ok = analyze_past_habitual_auxiliary_agreement("Ninku wuu cuni jiray.")
    masculine_bad = analyze_past_habitual_auxiliary_agreement("Ninku wuu cuni jirtay.")
    feminine_ok = analyze_past_habitual_auxiliary_agreement("Gabadhu way cuni jirtay.")
    feminine_bad = analyze_past_habitual_auxiliary_agreement("Gabadhu way cuni jiray.")
    assert masculine_ok.recognized and masculine_ok.expected_person == "3sg_m" and masculine_ok.agrees is True
    assert masculine_bad.agrees is False
    assert feminine_ok.recognized and feminine_ok.expected_person == "3sg_f" and feminine_ok.agrees is True
    assert feminine_bad.agrees is False


def test_past_habitual_plural_agreement():
    correct = analyze_past_habitual_auxiliary_agreement("Macallimiintu way cuni jireen.")
    wrong = analyze_past_habitual_auxiliary_agreement("Macallimiintu way cuni jiray.")
    assert correct.recognized and correct.expected_person == "3pl" and correct.agrees is True
    assert wrong.agrees is False


def test_unknown_habitual_auxiliary_is_unjudged_not_guessed():
    result = analyze_past_habitual_auxiliary_agreement("Ninku wuu cuni jirayXYZ.")
    assert result.recognized
    assert result.auxiliary_persons == ()
    assert result.agrees is None


def _run_checker(sentence: str) -> str:
    completed = subprocess.run([sys.executable, "check.py", sentence], check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def test_cli_reports_past_progressive_conflict_without_autofix():
    output = _run_checker("Gabadhu way cunayay.")
    assert "possible singular noun-subject/finite-verb agreement conflict" in output
    assert "Expected 3sg_f" in output
    assert "Safe corrected text:\nGabadhu way cunayay." in output


def test_cli_reports_past_habitual_auxiliary_conflict_without_autofix():
    output = _run_checker("Gabadhu way cuni jiray.")
    assert "possible past habitual auxiliary agreement conflict" in output
    assert "Expected 3sg_f" in output
    assert "Safe corrected text:\nGabadhu way cuni jiray." in output
