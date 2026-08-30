import subprocess
import sys

from src.dependent_mood import analyze_dependent_mood
from src.future_auxiliary_agreement import analyze_future_auxiliary_agreement
from src.jussive_mood import analyze_jussive_mood
from src.morphology_candidates import analyze_surface_form
from src.negative_finite_agreement import analyze_negative_finite_agreement
from src.negative_future_auxiliary_agreement import analyze_negative_future_auxiliary_agreement
from src.noun_number_verb_agreement import analyze_noun_number_verb_agreement
from src.noun_singular_verb_agreement import analyze_noun_singular_verb_agreement
from src.reviewed_finite_verb import analyze_reviewed_finite_verb


def test_aqaan_present_paradigm_is_exact_and_prefix_changing():
    expected = {
        "aqaan": {"1sg"},
        "taqaan": {"2sg", "3sg_f"},
        "yaqaan": {"3sg_m"},
        "naqaan": {"1pl"},
        "taqaaniin": {"2pl"},
        "yaqaaniin": {"3pl"},
    }
    for surface, persons in expected.items():
        analysis = analyze_reviewed_finite_verb(surface)
        assert analysis.recognized
        assert analysis.lemmas == ("aqaan",)
        assert set(analysis.persons) == persons


def test_aqaan_present_agreement_uses_exact_person_not_suffix_guessing():
    masculine = analyze_noun_singular_verb_agreement("Ninku wuu yaqaan.")
    feminine = analyze_noun_singular_verb_agreement("Gabadhu way taqaan.")
    plural = analyze_noun_number_verb_agreement("Macallimiintu way yaqaaniin.")

    assert masculine.recognized and masculine.agrees is True
    assert masculine.verb_lemmas == ("aqaan",)
    assert feminine.recognized and feminine.agrees is True
    assert plural.recognized and plural.agrees is True

    wrong_m = analyze_noun_singular_verb_agreement("Ninku wuu taqaan.")
    wrong_f = analyze_noun_singular_verb_agreement("Gabadhu way yaqaan.")
    wrong_pl = analyze_noun_number_verb_agreement("Macallimiintu way yaqaan.")
    assert wrong_m.recognized and wrong_m.agrees is False
    assert wrong_f.recognized and wrong_f.agrees is False
    assert wrong_pl.recognized and wrong_pl.agrees is False


def test_aqaan_source_past_paradigm_preserves_prefix_alternation():
    expected = {
        "iqiin": {"1sg"},
        "tiqiin": {"2sg", "3sg_f"},
        "yiqiin": {"3sg_m"},
        "niqiin": {"1pl"},
        "tiqiineen": {"2pl"},
        "yiqiineen": {"3pl"},
    }
    for surface, persons in expected.items():
        analysis = analyze_reviewed_finite_verb(surface)
        assert analysis.recognized
        assert analysis.lemmas == ("aqaan",)
        assert set(analysis.persons) == persons
        assert "tagto" in analysis.tense_aspects

    assert analyze_noun_singular_verb_agreement("Ninku wuu yiqiin.").agrees is True
    assert analyze_noun_singular_verb_agreement("Gabadhu way tiqiin.").agrees is True
    assert analyze_noun_number_verb_agreement("Macallimiintu way yiqiineen.").agrees is True
    assert analyze_noun_singular_verb_agreement("Ninku wuu tiqiin.").agrees is False
    assert analyze_noun_number_verb_agreement("Macallimiintu way tiqiineen.").agrees is False


def test_aqaan_negative_present_keeps_same_surface_but_uses_ma_context():
    masculine = analyze_negative_finite_agreement("Ninku ma yaqaan.")
    feminine = analyze_negative_finite_agreement("Gabadhu ma taqaan.")
    plural = analyze_negative_finite_agreement("Macallimiintu ma yaqaaniin.")

    assert masculine.recognized and masculine.polarity == "negative" and masculine.agrees is True
    assert feminine.recognized and feminine.polarity == "negative" and feminine.agrees is True
    assert plural.recognized and plural.polarity == "negative" and plural.agrees is True

    wrong_m = analyze_negative_finite_agreement("Ninku ma taqaan.")
    wrong_f = analyze_negative_finite_agreement("Gabadhu ma yaqaan.")
    wrong_pl = analyze_negative_finite_agreement("Macallimiintu ma yaqaan.")
    assert wrong_m.recognized and wrong_m.agrees is False
    assert wrong_f.recognized and wrong_f.agrees is False
    assert wrong_pl.recognized and wrong_pl.agrees is False


def test_aqaan_past_negative_aqoon_is_person_neutralized():
    for sentence in (
        "Ninku ma aqoon.",
        "Gabadhu ma aqoon.",
        "Macallimiintu ma aqoon.",
        "Ninku ma aqoonin.",
        "Gabadhu ma aqoonin.",
        "Macallimiintu ma aqoonin.",
    ):
        result = analyze_negative_finite_agreement(sentence)
        assert result.recognized
        assert result.verb_lemma == "aqaan"
        assert result.person_neutralized is True
        assert result.agrees is True


def test_aqoon_future_uses_generic_future_auxiliary_engine():
    masculine = analyze_future_auxiliary_agreement("Ninku wuu aqoon doonaa.")
    feminine = analyze_future_auxiliary_agreement("Gabadhu way aqoon doontaa.")
    plural = analyze_future_auxiliary_agreement("Macallimiintu way aqoon doonaan.")

    assert masculine.recognized and masculine.future_lemma == "aqaan" and masculine.agrees is True
    assert feminine.recognized and feminine.future_lemma == "aqaan" and feminine.agrees is True
    assert plural.recognized and plural.future_lemma == "aqaan" and plural.agrees is True

    assert analyze_future_auxiliary_agreement("Ninku wuu aqoon doontaa.").agrees is False
    assert analyze_future_auxiliary_agreement("Gabadhu way aqoon doonaa.").agrees is False
    assert analyze_future_auxiliary_agreement("Macallimiintu way aqoon doonaa.").agrees is False


def test_aqoon_negative_future_reuses_same_reviewed_stem():
    masculine = analyze_negative_future_auxiliary_agreement("Ninku ma aqoon doono.")
    feminine = analyze_negative_future_auxiliary_agreement("Gabadhu ma aqoon doonto.")
    plural = analyze_negative_future_auxiliary_agreement("Macallimiintu ma aqoon doonaan.")

    assert masculine.recognized and masculine.future_lemma == "aqaan" and masculine.agrees is True
    assert feminine.recognized and feminine.future_lemma == "aqaan" and feminine.agrees is True
    assert plural.recognized and plural.future_lemma == "aqaan" and plural.agrees is True


def test_aqaan_dependent_pairs_are_exact_and_contextual():
    masculine = analyze_dependent_mood("uu yaqaanno")
    feminine = analyze_dependent_mood("ay taqaanno")
    plural = analyze_dependent_mood("ay yaqaanaan")

    assert masculine.recognized and masculine.lemma == "aqaan" and masculine.persons == ("3sg_m",) and masculine.agrees is True
    assert feminine.recognized and feminine.lemma == "aqaan" and feminine.persons == ("3sg_f",) and feminine.agrees is True
    assert plural.recognized and plural.lemma == "aqaan" and plural.persons == ("3pl",) and plural.agrees is True

    mismatch = analyze_dependent_mood("uu taqaanno")
    assert mismatch.recognized and mismatch.agrees is False


def test_aqaan_hab_talo_pairs_are_exact_and_preserve_source_marker():
    masculine = analyze_jussive_mood("ha yaqaanno")
    feminine = analyze_jussive_mood("ha taqaanno")
    plural = analyze_jussive_mood("ay yaqaanaan")

    assert masculine.recognized and masculine.lemma == "aqaan" and masculine.persons == ("3sg_m",) and masculine.agrees is True
    assert feminine.recognized and feminine.lemma == "aqaan" and feminine.persons == ("3sg_f",) and feminine.agrees is True
    assert plural.recognized and plural.lemma == "aqaan" and plural.persons == ("3pl",) and plural.agrees is True

    mismatch = analyze_jussive_mood("ha aqaanno")
    assert mismatch.recognized and mismatch.agrees is False


def test_unknown_aqaan_lookalikes_are_not_generated():
    assert analyze_reviewed_finite_verb("yaqaanXYZ").recognized is False
    assert analyze_surface_form("yiqiinXYZ") == ()
    assert analyze_future_auxiliary_agreement("Ninku wuu aqooXYZ doonaa.").recognized is False


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_accepts_aqaan_present_and_person_neutral_past_negative():
    assert _run_checker("Ninku wuu yaqaan.") == "No supported orthography or grammar findings found."
    assert _run_checker("Gabadhu way taqaan.") == "No supported orthography or grammar findings found."
    assert _run_checker("Macallimiintu ma aqoon.") == "No supported orthography or grammar findings found."


def test_cli_reports_aqaan_present_person_conflict_review_only():
    output = _run_checker("Gabadhu way yaqaan.")
    assert "possible singular noun-subject/finite-verb agreement conflict" in output
    assert "Safe corrected text:\nGabadhu way yaqaan." in output
