import json
import subprocess
import sys
from pathlib import Path

from src.imperative import analyze_imperative
from src.morphology_candidates import analyze_surface_form
from src.reviewed_finite_verb import analyze_reviewed_finite_verb


RULE_PATH = Path("rules/grammar/imperative.jsonl")


def test_imperative_rule_is_review_only():
    records = [
        json.loads(line)
        for line in RULE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 1
    assert records[0]["id"] == "GRAM-IMP-001"
    assert records[0]["autofix"] is False


def test_negative_plural_imperative_is_exact_morphology_candidate():
    candidates = analyze_surface_form("cunina")
    imperative = [candidate for candidate in candidates if candidate.analysis_type == "imperative"]
    assert len(imperative) == 1
    assert imperative[0].lemma == "cun"
    assert imperative[0].features["mood"] == "imperative"
    assert imperative[0].features["person"] == "2pl"
    assert imperative[0].features["polarity"] == "negative"


def test_cun_affirmative_imperatives_preserve_number():
    singular = analyze_imperative("Cun.")
    plural = analyze_imperative("Cuna!")
    assert singular.recognized
    assert singular.lemma == "cun"
    assert singular.person == "2sg"
    assert singular.polarity == "affirmative"
    assert singular.context_required is False
    assert plural.recognized
    assert plural.person == "2pl"
    assert plural.polarity == "affirmative"


def test_cun_negative_imperatives_preserve_number():
    singular = analyze_imperative("Cunin!")
    plural = analyze_imperative("Cunina!")
    assert singular.recognized
    assert singular.person == "2sg"
    assert singular.polarity == "negative"
    assert singular.context_required is True
    assert plural.recognized
    assert plural.person == "2pl"
    assert plural.polarity == "negative"
    assert plural.context_required is False


def test_existing_irregular_affirmative_imperatives_are_reused():
    singular = analyze_imperative("Dheh.")
    plural = analyze_imperative("Dhaha.")
    assert singular.recognized and singular.lemma == "dheh"
    assert singular.person == "2sg"
    assert singular.polarity == "affirmative"
    assert plural.recognized and plural.lemma == "dheh"
    assert plural.person == "2pl"
    assert plural.polarity == "affirmative"


def test_cunin_in_other_negative_contexts_is_not_reclassified_as_imperative():
    assert analyze_imperative("Uusan cunin.").recognized is False
    assert analyze_imperative("Aysan cunin.").recognized is False
    assert analyze_imperative("Ma cunin.").recognized is False


def test_imperatives_remain_outside_ordinary_finite_verb_agreement():
    for surface in ("cun", "cuna", "cunin", "cunina", "dheh", "dhaha"):
        assert analyze_reviewed_finite_verb(surface).recognized is False


def test_unknown_clause_initial_surface_is_not_guessed_as_imperative():
    result = analyze_imperative("Tijaabxyz.")
    assert result.recognized is False
    assert result.surface == "Tijaabxyz"


def _run_checker(text: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", text],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_does_not_flag_reviewed_imperatives_as_grammar_errors():
    for text in ("Cun.", "Cuna.", "Cunin.", "Cunina.", "Dheh.", "Dhaha."):
        assert _run_checker(text) == "No supported orthography or grammar findings found."
