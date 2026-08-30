import subprocess
import sys

from src.dependent_mood import analyze_dependent_mood
from src.future_auxiliary_agreement import analyze_future_auxiliary_agreement
from src.imperative import analyze_imperative
from src.morphology_candidates import analyze_surface_form
from src.negative_finite_agreement import analyze_negative_finite_agreement
from src.noun_number_verb_agreement import analyze_noun_number_verb_agreement
from src.noun_singular_verb_agreement import analyze_noun_singular_verb_agreement
from src.predicate_agreement import analyze_predicate_agreement
from src.predicate_sentence import scan_predicate_agreement
from src.reviewed_finite_verb import analyze_reviewed_finite_verb


def test_ahaw_present_copular_paradigm_is_exact():
    expected = {
        "ahay": {"1sg"},
        "tahay": {"2sg", "3sg_f"},
        "yahay": {"3sg_m"},
        "nahay": {"1pl"},
        "tihiin": {"2pl"},
        "yihiin": {"3pl"},
    }
    for surface, persons in expected.items():
        analysis = analyze_reviewed_finite_verb(surface)
        assert analysis.recognized
        assert analysis.lemmas == ("ahaw/ah",)
        assert set(analysis.persons) == persons


def test_present_copula_agrees_with_reviewed_noun_gender_and_number():
    assert analyze_predicate_agreement("Ninku", "yahay").agrees is True
    assert analyze_predicate_agreement("Meeshu", "tahay").agrees is True
    assert analyze_predicate_agreement("Macallimiintu", "yihiin").agrees is True

    masculine_wrong = analyze_predicate_agreement("Ninku", "tahay")
    feminine_wrong = analyze_predicate_agreement("Meeshu", "yahay")
    plural_wrong = analyze_predicate_agreement("Macallimiintu", "yahay")
    assert masculine_wrong.recognized and masculine_wrong.agrees is False
    assert feminine_wrong.recognized and feminine_wrong.agrees is False
    assert plural_wrong.recognized and plural_wrong.agrees is False
    assert plural_wrong.expected_copula == "yihiin"


def test_predicate_sentence_scanner_now_covers_reviewed_plural_and_meeshu():
    feminine = scan_predicate_agreement("Meeshu aad bay u weyn yahay.")
    plural = scan_predicate_agreement("Macallimiintu waa diyaar yahay.")
    assert any(item.subject == "Meeshu" and item.expected_copula == "tahay" for item in feminine)
    assert any(item.subject == "Macallimiintu" and item.expected_copula == "yihiin" for item in plural)


def test_ahaw_present_finite_forms_flow_through_shared_noun_verb_engine():
    assert analyze_noun_singular_verb_agreement("Ninku wuu yahay.").agrees is True
    assert analyze_noun_singular_verb_agreement("Gabadhu way tahay.").agrees is True
    assert analyze_noun_number_verb_agreement("Macallimiintu way yihiin.").agrees is True
    assert analyze_noun_singular_verb_agreement("Ninku wuu tahay.").agrees is False
    assert analyze_noun_number_verb_agreement("Macallimiintu way yahay.").agrees is False


def test_ma_aha_is_syncretic_for_reviewed_third_person_noun_subjects():
    for sentence in (
        "Ninku ma aha.",
        "Gabadhu ma aha.",
        "Macallimiintu ma aha.",
    ):
        result = analyze_negative_finite_agreement(sentence)
        assert result.recognized
        assert result.verb_lemma == "ahaw/ah"
        assert set(result.verb_persons) == {"3sg_m", "3sg_f", "3pl"}
        assert result.person_neutralized is False
        assert result.agrees is True


def test_affirmative_present_copula_under_ma_is_reviewed_polarity_conflict():
    masculine = analyze_negative_finite_agreement("Ninku ma yahay.")
    feminine = analyze_negative_finite_agreement("Gabadhu ma tahay.")
    plural = analyze_negative_finite_agreement("Macallimiintu ma yihiin.")
    for result in (masculine, feminine, plural):
        assert result.recognized
        assert result.verb_lemma == "ahaw/ah"
        assert result.polarity == "affirmative"
        assert result.agrees is False


def test_ahaw_past_paradigm_uses_shared_finite_agreement():
    assert analyze_noun_singular_verb_agreement("Ninku wuu ahaa.").agrees is True
    assert analyze_noun_singular_verb_agreement("Gabadhu way ahayd.").agrees is True
    assert analyze_noun_number_verb_agreement("Macallimiintu way ahaayeen.").agrees is True
    assert analyze_noun_singular_verb_agreement("Ninku wuu ahayd.").agrees is False
    assert analyze_noun_number_verb_agreement("Macallimiintu way ahaa.").agrees is False


def test_ahaan_future_uses_generic_future_auxiliary_engine():
    masculine = analyze_future_auxiliary_agreement("Ninku wuu ahaan doonaa.")
    feminine = analyze_future_auxiliary_agreement("Gabadhu way ahaan doontaa.")
    plural = analyze_future_auxiliary_agreement("Macallimiintu way ahaan doonaan.")
    assert masculine.recognized and masculine.future_lemma == "ahaw/ah" and masculine.agrees is True
    assert feminine.recognized and feminine.future_lemma == "ahaw/ah" and feminine.agrees is True
    assert plural.recognized and plural.future_lemma == "ahaw/ah" and plural.agrees is True
    assert analyze_future_auxiliary_agreement("Ninku wuu ahaan doontaa.").agrees is False


def test_ahaw_dependent_pairs_are_exact():
    masculine = analyze_dependent_mood("uu ahaado")
    feminine = analyze_dependent_mood("ay ahaato")
    plural = analyze_dependent_mood("ay ahaadaan")
    assert masculine.recognized and masculine.lemma == "ahaw/ah" and masculine.persons == ("3sg_m",) and masculine.agrees is True
    assert feminine.recognized and feminine.lemma == "ahaw/ah" and feminine.persons == ("3sg_f",) and feminine.agrees is True
    assert plural.recognized and plural.lemma == "ahaw/ah" and plural.persons == ("3pl",) and plural.agrees is True
    mismatch = analyze_dependent_mood("uu ahaato")
    assert mismatch.recognized and mismatch.agrees is False


def test_ahaw_imperatives_are_exact_and_person_distinct():
    singular = analyze_imperative("Ahaw!")
    plural = analyze_imperative("Ahaada!")
    assert singular.recognized and singular.lemma == "ahaw/ah" and singular.person == "2sg"
    assert plural.recognized and plural.lemma == "ahaw/ah" and plural.person == "2pl"


def test_unknown_ahaw_lookalikes_are_not_generated():
    assert analyze_surface_form("yahayXYZ") == ()
    assert analyze_reviewed_finite_verb("ahayXYZ").recognized is False
    assert analyze_future_auxiliary_agreement("Ninku wuu ahaanXYZ doonaa.").recognized is False


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_accepts_reviewed_ahaw_predicate_and_negative_forms():
    assert _run_checker("Meeshu way weyn tahay.") == "No supported orthography or grammar findings found."
    assert _run_checker("Macallimiintu waa diyaar yihiin.") == "No supported orthography or grammar findings found."
    assert _run_checker("Ninku ma aha.") == "No supported orthography or grammar findings found."


def test_cli_reports_plural_predicate_copula_conflict_review_only():
    output = _run_checker("Macallimiintu waa diyaar yahay.")
    assert "possible predicate/copula agreement conflict" in output
    assert "'yihiin'" in output
    assert "Safe corrected text:\nMacallimiintu waa diyaar yahay." in output
