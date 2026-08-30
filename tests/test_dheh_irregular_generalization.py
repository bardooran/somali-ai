import subprocess
import sys

from src.future_auxiliary_agreement import analyze_future_auxiliary_agreement
from src.morphology_candidates import analyze_surface_form
from src.negative_future_auxiliary_agreement import analyze_negative_future_auxiliary_agreement
from src.negative_past_aspect_agreement import analyze_negative_past_aspect_agreement
from src.noun_number_verb_agreement import analyze_noun_number_verb_agreement
from src.noun_singular_verb_agreement import analyze_noun_singular_verb_agreement
from src.past_habitual_auxiliary_agreement import analyze_past_habitual_auxiliary_agreement
from src.reviewed_finite_verb import analyze_reviewed_finite_verb


def test_source_backed_missing_plural_dheh_forms_are_loaded():
    expected = {
        "tiraahdaan": "2pl",
        "yiraahdaan": "3pl",
        "tiraahdeen": "2pl",
        "yiraahdeen": "3pl",
    }
    for surface, person in expected.items():
        candidates = [
            candidate
            for candidate in analyze_surface_form(surface)
            if candidate.lemma == "dheh" and candidate.analysis_type == "finite_verb"
        ]
        assert candidates
        assert any(candidate.features.get("person") == person for candidate in candidates)


def test_irregular_present_finite_agreement_generalizes_to_noun_subjects():
    masculine = analyze_noun_singular_verb_agreement("Ninku wuu yiraahdaa.")
    feminine = analyze_noun_singular_verb_agreement("Gabadhu way tiraahdaa.")
    plural = analyze_noun_number_verb_agreement("Macallimiintu way yiraahdaan.")

    assert masculine.recognized and masculine.agrees is True
    assert masculine.verb_lemmas == ("dheh",)
    assert masculine.verb_persons == ("3sg_m",)

    assert feminine.recognized and feminine.agrees is True
    assert feminine.verb_lemmas == ("dheh",)
    assert set(feminine.verb_persons) == {"2sg", "3sg_f"}

    assert plural.recognized and plural.agrees is True
    assert plural.verb_lemmas == ("dheh",)
    assert plural.verb_persons == ("3pl",)


def test_irregular_present_rejects_wrong_person_without_suffix_guessing():
    masculine = analyze_noun_singular_verb_agreement("Ninku wuu tiraahdaa.")
    plural = analyze_noun_number_verb_agreement("Macallimiintu way tiraahdaan.")
    assert masculine.recognized and masculine.agrees is False
    assert plural.recognized and plural.agrees is False


def test_irregular_past_supports_preferred_jigjiga_forms_and_source_plural():
    masculine = analyze_noun_singular_verb_agreement("Ninku wuu yidhi.")
    feminine = analyze_noun_singular_verb_agreement("Gabadhu way tidhi.")
    plural = analyze_noun_number_verb_agreement("Macallimiintu way yiraahdeen.")

    assert masculine.recognized and masculine.agrees is True
    assert masculine.verb_lemmas == ("dheh",)
    assert feminine.recognized and feminine.agrees is True
    assert feminine.verb_lemmas == ("dheh",)
    assert plural.recognized and plural.agrees is True
    assert plural.verb_lemmas == ("dheh",)


def test_irregular_past_plural_rejects_second_person_plural_surface():
    result = analyze_noun_number_verb_agreement("Macallimiintu way tiraahdeen.")
    assert result.recognized
    assert result.verb_persons == ("2pl",)
    assert result.agrees is False


def test_standard_yiri_tiri_remain_recognized_alongside_preferred_yidhi_tidbi():
    masculine = analyze_reviewed_finite_verb("yiri")
    feminine = analyze_reviewed_finite_verb("tiri")
    preferred_m = analyze_reviewed_finite_verb("yidhi")
    preferred_f = analyze_reviewed_finite_verb("tidhi")
    assert masculine.recognized and masculine.lemmas == ("dheh",)
    assert feminine.recognized and feminine.lemmas == ("dheh",)
    assert preferred_m.recognized and preferred_m.lemmas == ("dheh",)
    assert preferred_f.recognized and preferred_f.lemmas == ("dheh",)


def test_oran_future_uses_generic_future_auxiliary_engine():
    masculine = analyze_future_auxiliary_agreement("Ninku wuu oran doonaa.")
    feminine = analyze_future_auxiliary_agreement("Gabadhu way oran doontaa.")
    plural = analyze_future_auxiliary_agreement("Macallimiintu way oran doonaan.")

    assert masculine.recognized and masculine.future_lemma == "dheh" and masculine.agrees is True
    assert feminine.recognized and feminine.future_lemma == "dheh" and feminine.agrees is True
    assert plural.recognized and plural.future_lemma == "dheh" and plural.agrees is True


def test_oran_future_rejects_wrong_auxiliary_person():
    masculine = analyze_future_auxiliary_agreement("Ninku wuu oran doontaa.")
    feminine = analyze_future_auxiliary_agreement("Gabadhu way oran doonaa.")
    plural = analyze_future_auxiliary_agreement("Macallimiintu way oran doonaa.")
    assert masculine.recognized and masculine.agrees is False
    assert feminine.recognized and feminine.agrees is False
    assert plural.recognized and plural.agrees is False


def test_oran_negative_future_uses_same_reviewed_stem_without_cun_specific_code():
    masculine = analyze_negative_future_auxiliary_agreement("Ninku ma oran doono.")
    feminine = analyze_negative_future_auxiliary_agreement("Gabadhu ma oran doonto.")
    plural = analyze_negative_future_auxiliary_agreement("Macallimiintu ma oran doonaan.")

    assert masculine.recognized and masculine.future_lemma == "dheh" and masculine.agrees is True
    assert feminine.recognized and feminine.future_lemma == "dheh" and feminine.agrees is True
    assert plural.recognized and plural.future_lemma == "dheh" and plural.agrees is True


def test_oran_past_habitual_uses_generic_jir_auxiliary_engine():
    masculine = analyze_past_habitual_auxiliary_agreement("Ninku wuu oran jiray.")
    feminine = analyze_past_habitual_auxiliary_agreement("Gabadhu way oran jirtay.")
    plural = analyze_past_habitual_auxiliary_agreement("Macallimiintu way oran jireen.")

    assert masculine.recognized and masculine.habitual_lemma == "dheh" and masculine.agrees is True
    assert feminine.recognized and feminine.habitual_lemma == "dheh" and feminine.agrees is True
    assert plural.recognized and plural.habitual_lemma == "dheh" and plural.agrees is True


def test_oran_negative_past_habitual_preserves_person_neutral_jirin():
    masculine = analyze_negative_past_aspect_agreement("Ninku ma oran jirin.")
    feminine = analyze_negative_past_aspect_agreement("Gabadhu ma oran jirin.")
    plural = analyze_negative_past_aspect_agreement("Macallimiintu ma oran jirin.")

    for result in (masculine, feminine, plural):
        assert result.recognized
        assert result.construction == "negative_past_habitual"
        assert result.person_neutralized is True
        assert result.agrees is True


def test_unknown_dheh_lookalike_is_not_invented():
    assert analyze_reviewed_finite_verb("yiraahXYZ").recognized is False
    result = analyze_future_auxiliary_agreement("Ninku wuu orXYZ doonaa.")
    assert result.recognized is False


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_accepts_source_backed_dheh_present_plural():
    assert _run_checker("Macallimiintu way yiraahdaan.") == "No supported orthography or grammar findings found."


def test_cli_reports_dheh_future_auxiliary_conflict_review_only():
    output = _run_checker("Gabadhu way oran doonaa.")
    assert "possible future auxiliary agreement conflict" in output
    assert "Expected 3sg_f" in output
    assert "Safe corrected text:\nGabadhu way oran doonaa." in output


def test_cli_accepts_dheh_negative_habitual():
    assert _run_checker("Ninku ma oran jirin.") == "No supported orthography or grammar findings found."
