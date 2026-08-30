import json
import subprocess
import sys
from pathlib import Path

from src.morphology_candidates import analyze_surface_form
from src.negative_past_aspect_agreement import analyze_negative_past_aspect_agreement
from src.reviewed_finite_verb import analyze_reviewed_finite_verb


RULE_PATH = Path("rules/grammar/negative_past_aspect_agreement.jsonl")


def test_rule_is_review_only():
    records = [
        json.loads(line)
        for line in RULE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert records
    assert all(record["autofix"] is False for record in records)


def test_negative_past_progressive_forms_are_exact_reviewed_and_person_neutralized():
    for surface in ("cunayn", "cunaynin"):
        candidates = [
            c for c in analyze_surface_form(surface)
            if c.analysis_type == "negative_past_progressive"
        ]
        assert candidates
        assert all(c.features.get("person_neutralized") is True for c in candidates)
        assert analyze_reviewed_finite_verb(surface).recognized is False


def test_negative_habitual_auxiliary_is_exact_reviewed_and_person_neutralized():
    candidates = [
        c for c in analyze_surface_form("jirin")
        if c.analysis_type == "negative_past_habitual_auxiliary"
    ]
    assert candidates
    assert all(c.features.get("person_neutralized") is True for c in candidates)
    assert analyze_reviewed_finite_verb("jirin").recognized is False


def test_negative_past_progressive_accepts_same_surface_across_subject_persons():
    masculine = analyze_negative_past_aspect_agreement("Ninku ma cunayn.")
    feminine = analyze_negative_past_aspect_agreement("Gabadhu ma cunayn.")
    plural = analyze_negative_past_aspect_agreement("Macallimiintu ma cunayn.")

    assert masculine.recognized and masculine.expected_person == "3sg_m"
    assert feminine.recognized and feminine.expected_person == "3sg_f"
    assert plural.recognized and plural.expected_person == "3pl"
    assert masculine.person_neutralized is True and masculine.agrees is True
    assert feminine.person_neutralized is True and feminine.agrees is True
    assert plural.person_neutralized is True and plural.agrees is True
    assert masculine.tense_aspect == "tagto_socota"


def test_negative_past_progressive_accepts_cunaynin_variant():
    for sentence in (
        "Ninku ma cunaynin.",
        "Gabadhu ma cunaynin.",
        "Macallimiintu ma cunaynin.",
    ):
        result = analyze_negative_past_aspect_agreement(sentence)
        assert result.recognized
        assert result.person_neutralized is True
        assert result.agrees is True


def test_ma_plus_affirmative_past_progressive_is_polarity_conflict():
    cases = (
        ("Ninku ma cunayay.", "3sg_m"),
        ("Gabadhu ma cunaysay.", "3sg_f"),
        ("Macallimiintu ma cunayeen.", "3pl"),
    )
    for sentence, expected in cases:
        result = analyze_negative_past_aspect_agreement(sentence)
        assert result.recognized
        assert result.construction == "negative_past_progressive"
        assert result.polarity == "affirmative"
        assert result.expected_person == expected
        assert result.agrees is False


def test_negative_past_habitual_accepts_jirin_across_subject_persons():
    cases = (
        ("Ninku ma cuni jirin.", "3sg_m"),
        ("Gabadhu ma cuni jirin.", "3sg_f"),
        ("Macallimiintu ma cuni jirin.", "3pl"),
    )
    for sentence, expected in cases:
        result = analyze_negative_past_aspect_agreement(sentence)
        assert result.recognized
        assert result.construction == "negative_past_habitual"
        assert result.stem == "cuni"
        assert result.verb_or_auxiliary == "jirin"
        assert result.expected_person == expected
        assert result.person_neutralized is True
        assert result.agrees is True
        assert result.tense_aspect == "tagto_caadaley"


def test_ma_plus_affirmative_habitual_auxiliary_is_polarity_conflict():
    cases = (
        "Ninku ma cuni jiray.",
        "Gabadhu ma cuni jirtay.",
        "Macallimiintu ma cuni jireen.",
    )
    for sentence in cases:
        result = analyze_negative_past_aspect_agreement(sentence)
        assert result.recognized
        assert result.construction == "negative_past_habitual"
        assert result.polarity == "affirmative"
        assert result.agrees is False


def test_unknown_past_progressive_lookalike_is_not_guessed():
    result = analyze_negative_past_aspect_agreement("Ninku ma cunaynXYZ.")
    assert result.recognized is False


def test_unknown_habitual_auxiliary_after_reviewed_stem_is_unjudged():
    result = analyze_negative_past_aspect_agreement("Ninku ma cuni jirinXYZ.")
    assert result.recognized
    assert result.verb_or_auxiliary == "jirinXYZ"
    assert result.agrees is None


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_accepts_person_neutralized_negative_past_aspects():
    for sentence in (
        "Ninku ma cunayn.",
        "Gabadhu ma cunaynin.",
        "Macallimiintu ma cuni jirin.",
    ):
        assert _run_checker(sentence) == "No supported orthography or grammar findings found."


def test_cli_reports_negative_past_progressive_polarity_conflict():
    output = _run_checker("Gabadhu ma cunaysay.")
    assert "possible negative past-aspect conflict" in output
    assert "tagto_socota" in output
    assert "Safe corrected text:\nGabadhu ma cunaysay." in output


def test_cli_prefers_specific_habitual_warning_over_generic_negation_warning():
    output = _run_checker("Ninku ma cuni jiray.")
    assert "possible negative past-aspect conflict" in output
    assert "possible negation-paradigm conflict" not in output
    assert "Safe corrected text:\nNinku ma cuni jiray." in output
