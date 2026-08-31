import subprocess
import sys

from src.vocabulary import lookup_word
from src.morphology_candidates import analyze_surface_form
from src.noun_subject_case import analyze_noun_subject_case


NEW_SUBJECT_FORMS = (
    "dugsigu",
    "magaaladu",
    "eygu",
    "naagtu",
    "miisku",
    "albaabku",
)


def test_new_subject_forms_remain_outside_exact_vocabulary_but_work_in_grammar_context():
    """Grammar can generalize sentence role without inventing dictionary lemmas."""
    sentences = (
        "Dugsigu wuu weyn yahay.",
        "Magaaladu way qurux badan tahay.",
        "Eygu wuu ordayaa.",
        "Naagtu way shaqaynaysaa.",
        "Miisku wuu jabay.",
        "Albaabku wuu xiran yahay.",
    )
    for form in NEW_SUBJECT_FORMS:
        result = lookup_word(form)
        assert result.known is False
        assert analyze_surface_form(form) == ()
    for sentence in sentences:
        analysis = analyze_noun_subject_case(sentence)
        assert analysis.recognized
        assert analysis.agrees is True


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


def test_checker_now_distinguishes_buug_subject_case_pair():
    correct = _run_checker("Buuggu wuu fiicanyahay.")
    wrong = _run_checker("Buugga wuu fiicanyahay.")
    assert "possible definite-noun subject-case conflict" not in correct
    assert "possible definite-noun subject-case conflict" in wrong
    assert "'Buuggu'" in wrong


def test_checker_now_distinguishes_gabadh_subject_case_pair():
    correct = _run_checker("Gabadhu way fiicantahay.")
    wrong = _run_checker("Gabadha way fiicantahay.")
    assert "possible definite-noun subject-case conflict" not in correct
    assert "possible definite-noun subject-case conflict" in wrong
    assert "'Gabadhu'" in wrong
    # Orthography may separately expand the valid contraction way -> waa ay;
    # that behavior is independent from noun subject-case analysis.


def test_focus_construction_is_not_collapsed_into_subject_u_form():
    analysis = analyze_noun_subject_case("Libaaxa ayaa eryanayaa.")
    assert analysis.recognized is False
