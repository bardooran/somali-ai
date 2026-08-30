import json
import subprocess
import sys
from pathlib import Path

from src.jussive_mood import analyze_jussive_mood


RULE_PATH = Path("rules/grammar/jussive_mood_agreement.jsonl")


def test_jussive_rule_is_review_only():
    records = [
        json.loads(line)
        for line in RULE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 1
    assert records[0]["id"] == "GRAM-JUSS-001"
    assert records[0]["autofix"] is False


def test_ha_pair_disambiguates_third_person_gender_and_number():
    masculine = analyze_jussive_mood("ha cuno")
    feminine = analyze_jussive_mood("ha cunto")
    plural = analyze_jussive_mood("ha cuneen")

    assert set(masculine.marker_persons) == {"3sg_m", "3sg_f", "3pl"}
    assert masculine.persons == ("3sg_m",)
    assert feminine.persons == ("3sg_f",)
    assert plural.persons == ("3pl",)
    assert all(result.agrees is True for result in (masculine, feminine, plural))


def test_first_and_second_person_affirmative_jussive_pairs():
    first_singular = analyze_jussive_mood("an cuno")
    first_plural_a = analyze_jussive_mood("an cunno")
    first_plural_b = analyze_jussive_mood("aynu cunno")
    second_singular = analyze_jussive_mood("ad cunto")
    second_plural = analyze_jussive_mood("ad cunteen")

    assert first_singular.persons == ("1sg",)
    assert first_plural_a.persons == ("1pl",)
    assert first_plural_b.persons == ("1pl",)
    assert second_singular.persons == ("2sg",)
    assert second_plural.persons == ("2pl",)
    assert all(
        result.agrees is True
        for result in (
            first_singular,
            first_plural_a,
            first_plural_b,
            second_singular,
            second_plural,
        )
    )


def test_negative_third_person_alternatives_are_preserved():
    masculine_a = analyze_jussive_mood("yaanu cunin")
    masculine_b = analyze_jussive_mood("yuusan cunin")
    feminine_plural_a = analyze_jussive_mood("yaanay cunin")
    feminine_plural_b = analyze_jussive_mood("yaysan cunin")

    assert masculine_a.persons == ("3sg_m",)
    assert masculine_b.persons == ("3sg_m",)
    assert set(feminine_plural_a.persons) == {"3sg_f", "3pl"}
    assert set(feminine_plural_b.persons) == {"3sg_f", "3pl"}
    assert all(
        result.agrees is True
        for result in (masculine_a, masculine_b, feminine_plural_a, feminine_plural_b)
    )
    assert all(
        result.person_neutralized is True
        for result in (masculine_a, masculine_b, feminine_plural_a, feminine_plural_b)
    )


def test_negative_first_and_second_person_syncretism_is_preserved():
    first = analyze_jussive_mood("yaanan cunin")
    second = analyze_jussive_mood("yaanad cunin")
    first_plural = analyze_jussive_mood("yaynu cunin")

    assert set(first.persons) == {"1sg", "1pl"}
    assert set(second.persons) == {"2sg", "2pl"}
    assert first_plural.persons == ("1pl",)
    assert first.agrees is True
    assert second.agrees is True
    assert first_plural.agrees is True


def test_known_person_mismatches_are_review_conflicts():
    assert analyze_jussive_mood("ha cunteen").agrees is False
    assert analyze_jussive_mood("ad cuneen").agrees is False
    assert analyze_jussive_mood("an cunto").agrees is False


def test_polarity_mismatches_are_review_conflicts():
    negative_marker_affirmative_verb = analyze_jussive_mood("yaanu cuno")
    affirmative_marker_negative_verb = analyze_jussive_mood("ha cunin")
    assert negative_marker_affirmative_verb.recognized
    assert negative_marker_affirmative_verb.agrees is False
    assert set(negative_marker_affirmative_verb.marker_polarities) == {"negative"}
    assert set(negative_marker_affirmative_verb.verb_polarities) == {"affirmative"}
    assert affirmative_marker_negative_verb.recognized
    assert affirmative_marker_negative_verb.agrees is False


def test_unknown_verb_after_known_jussive_marker_is_unjudged_not_guessed():
    result = analyze_jussive_mood("ha tijaabxyz")
    assert result.recognized
    assert result.agrees is None
    assert result.verb == "tijaabxyz"


def test_main_clause_markers_are_not_treated_as_hab_talo():
    assert analyze_jussive_mood("wuu cuno").recognized is False
    assert analyze_jussive_mood("way cunto").recognized is False


def _run_checker(text: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", text],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_reports_jussive_person_conflict_without_autofix():
    output = _run_checker("Ha cunteen")
    assert "possible hab talo marker/verb conflict" in output
    assert "Safe corrected text:\nHa cunteen" in output


def test_cli_reports_jussive_polarity_conflict_without_autofix():
    output = _run_checker("Yaanu cuno")
    assert "possible hab talo marker/verb conflict" in output
    assert "Safe corrected text:\nYaanu cuno" in output


def test_cli_accepts_reviewed_negative_jussive_pair():
    output = _run_checker("Yaysan cunin")
    assert output == "No supported orthography or grammar findings found."
