import json
import subprocess
import sys
from pathlib import Path

from src.dependent_mood import analyze_dependent_mood


RULE_PATH = Path("rules/grammar/dependent_mood_agreement.jsonl")


def test_dependent_rule_is_review_only():
    records = [
        json.loads(line)
        for line in RULE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 1
    assert records[0]["id"] == "GRAM-DEP-001"
    assert records[0]["autofix"] is False


def test_third_person_masculine_affirmative_dependent_pairs():
    present = analyze_dependent_mood("uu cuno")
    past = analyze_dependent_mood("uu cunay")
    assert present.recognized and present.agrees is True
    assert present.persons == ("3sg_m",)
    assert present.tense_aspects == ("joogto",)
    assert present.polarity == "affirmative"
    assert past.recognized and past.agrees is True
    assert past.persons == ("3sg_m",)
    assert past.tense_aspects == ("tagto",)


def test_ay_pair_disambiguates_feminine_singular_and_plural():
    feminine_present = analyze_dependent_mood("ay cunto")
    feminine_past = analyze_dependent_mood("ay cuntay")
    plural_present = analyze_dependent_mood("ay cunaan")
    plural_past = analyze_dependent_mood("ay cuneen")

    assert set(feminine_present.marker_persons) == {"3sg_f", "3pl"}
    assert feminine_present.persons == ("3sg_f",)
    assert feminine_past.persons == ("3sg_f",)
    assert plural_present.persons == ("3pl",)
    assert plural_past.persons == ("3pl",)
    assert all(
        result.agrees is True
        for result in (feminine_present, feminine_past, plural_present, plural_past)
    )


def test_known_affirmative_person_mismatches_are_review_conflicts():
    masculine_with_feminine = analyze_dependent_mood("uu cunto")
    feminine_or_plural_with_masculine = analyze_dependent_mood("ay cuno")
    feminine_or_plural_with_masculine_past = analyze_dependent_mood("ay cunay")
    assert masculine_with_feminine.recognized and masculine_with_feminine.agrees is False
    assert feminine_or_plural_with_masculine.recognized and feminine_or_plural_with_masculine.agrees is False
    assert feminine_or_plural_with_masculine_past.recognized and feminine_or_plural_with_masculine_past.agrees is False


def test_negative_third_person_markers_pair_with_person_neutral_cunin():
    masculine = analyze_dependent_mood("uusan cunin")
    feminine = analyze_dependent_mood("aysan cunin")
    plural = analyze_dependent_mood("ayan cunin")

    assert masculine.agrees is True and masculine.persons == ("3sg_m",)
    assert feminine.agrees is True and feminine.persons == ("3sg_f",)
    assert plural.agrees is True and plural.persons == ("3pl",)
    assert masculine.person_neutralized is True
    assert feminine.person_neutralized is True
    assert plural.person_neutralized is True
    assert set(masculine.tense_aspects) == {"joogto", "tagto"}


def test_negative_first_and_second_person_markers_preserve_syncretism():
    first = analyze_dependent_mood("aanan cunin")
    second = analyze_dependent_mood("aadan cunin")
    assert first.agrees is True
    assert set(first.persons) == {"1sg", "1pl"}
    assert second.agrees is True
    assert set(second.persons) == {"2sg", "2pl"}


def test_dependent_polarity_mismatches_are_conflicts():
    negative_marker_affirmative_verb = analyze_dependent_mood("uusan cuno")
    affirmative_marker_negative_verb = analyze_dependent_mood("uu cunin")
    assert negative_marker_affirmative_verb.recognized
    assert negative_marker_affirmative_verb.agrees is False
    assert set(negative_marker_affirmative_verb.marker_polarities) == {"negative"}
    assert set(negative_marker_affirmative_verb.verb_polarities) == {"affirmative"}
    assert affirmative_marker_negative_verb.recognized
    assert affirmative_marker_negative_verb.agrees is False


def test_unknown_verb_after_known_dependent_marker_is_unjudged_not_guessed():
    result = analyze_dependent_mood("uu tijaabxyz")
    assert result.recognized
    assert result.agrees is None
    assert result.verb == "tijaabxyz"


def test_main_clause_wuu_is_not_treated_as_dependent_uu():
    assert analyze_dependent_mood("wuu cuno").recognized is False


def _run_checker(text: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", text],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_reports_dependent_person_conflict_without_autofix():
    output = _run_checker("Uu cunto")
    assert "possible habka dhimman marker/verb conflict" in output
    assert "Safe corrected text:\nUu cunto" in output


def test_cli_reports_dependent_polarity_conflict_without_autofix():
    output = _run_checker("Uusan cuno")
    assert "possible habka dhimman marker/verb conflict" in output
    assert "Safe corrected text:\nUusan cuno" in output


def test_cli_accepts_reviewed_negative_dependent_pair():
    output = _run_checker("Aysan cunin")
    assert output == "No supported orthography or grammar findings found."
