import subprocess
import sys

from src.lexicon import lookup_word
from src.morphology_candidates import analyze_surface_form


NEW_SUBJECT_FORMS = (
    "dugsigu",
    "magaaladu",
    "eygu",
    "naagtu",
    "miisku",
    "albaabku",
)


def test_new_subject_forms_are_not_yet_morphologically_generalized():
    """Diagnostic boundary: these native-reviewed subject forms are still unseen by the exact morphology layer."""
    for form in NEW_SUBJECT_FORMS:
        result = lookup_word(form)
        assert result.known is False
        assert analyze_surface_form(form) == ()


def test_known_controls_are_reached_by_the_live_repo():
    """Controls prove the probe is exercising the real reviewed morphology datasets."""
    expected_lemmas = {
        "buugga": "buug",
        "maydhayaa": "maydh",
        "jabsadayaal": "jabsadayaal",
    }
    for form, lemma in expected_lemmas.items():
        result = lookup_word(form)
        assert result.known
        assert any(candidate.lemma == lemma for candidate in result.morphology_candidates)


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_checker_does_not_yet_distinguish_buug_subject_case_pair():
    correct = _run_checker("Buuggu wuu fiicanyahay.")
    wrong = _run_checker("Buugga wuu fiicanyahay.")
    assert correct == "No supported orthography or grammar findings found."
    assert wrong == "No supported orthography or grammar findings found."


def test_checker_does_not_yet_distinguish_gabadh_subject_case_pair():
    correct = _run_checker("Gabadhu way fiicantahay.")
    wrong = _run_checker("Gabadha way fiicantahay.")
    assert correct == "No supported orthography or grammar findings found."
    assert wrong == "No supported orthography or grammar findings found."
