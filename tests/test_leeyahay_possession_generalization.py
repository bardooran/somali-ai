import subprocess
import sys

from src.conditional_agreement import analyze_conditional_agreement
from src.future_auxiliary_agreement import analyze_future_auxiliary_agreement
from src.imperative import analyze_imperative
from src.morphology_candidates import analyze_surface_form
from src.negative_finite_agreement import analyze_negative_finite_agreement
from src.noun_number_verb_agreement import analyze_noun_number_verb_agreement
from src.noun_singular_verb_agreement import analyze_noun_singular_verb_agreement
from src.reviewed_finite_verb import analyze_reviewed_finite_verb


def test_leeyahay_present_person_paradigm_is_exact():
    expected = {
        "leeyahay": {"1sg", "3sg_m"},
        "leedahay": {"2sg", "3sg_f"},
        "leenahay": {"1pl"},
        "leedihiin": {"2pl"},
        "leeyihiin": {"3pl"},
    }
    for surface, persons in expected.items():
        analysis = analyze_reviewed_finite_verb(surface)
        assert analysis.recognized
        assert analysis.lemmas == ("leeyahay",)
        assert set(analysis.persons) == persons
        assert "joogto" in analysis.tense_aspects


def test_leeyahay_present_noun_agreement_uses_exact_person():
    masculine = analyze_noun_singular_verb_agreement("Ninku wuu leeyahay guri.")
    feminine = analyze_noun_singular_verb_agreement("Gabadhu way leedahay guri.")
    plural = analyze_noun_number_verb_agreement("Macallimiintu way leeyihiin guri.")
    assert masculine.recognized and masculine.agrees is True
    assert feminine.recognized and feminine.agrees is True
    assert plural.recognized and plural.agrees is True

    assert analyze_noun_singular_verb_agreement("Ninku wuu leedahay guri.").agrees is False
    assert analyze_noun_singular_verb_agreement("Gabadhu way leeyahay guri.").agrees is False
    assert analyze_noun_number_verb_agreement("Macallimiintu way leedihiin guri.").agrees is False


def test_leeyahay_present_negative_third_person_syncretism():
    for sentence in (
        "Ninku ma laha guri.",
        "Gabadhu ma laha guri.",
        "Macallimiintu ma laha guri.",
    ):
        result = analyze_negative_finite_agreement(sentence)
        assert result.recognized
        assert result.verb_lemma == "leeyahay"
        assert result.polarity == "negative"
        assert set(result.verb_persons) == {"3sg_m", "3sg_f", "3pl"}
        assert result.person_neutralized is False
        assert result.agrees is True


def test_leeyahay_present_affirmative_under_ma_is_conflict_when_negative_evidence_exists():
    masculine = analyze_negative_finite_agreement("Ninku ma leeyahay guri.")
    feminine = analyze_negative_finite_agreement("Gabadhu ma leedahay guri.")
    plural = analyze_negative_finite_agreement("Macallimiintu ma leeyihiin guri.")
    for result in (masculine, feminine, plural):
        assert result.recognized
        assert result.verb_lemma == "leeyahay"
        assert result.polarity == "affirmative"
        assert result.agrees is False


def test_leeyahay_past_surfaces_are_finite_possession_forms():
    expected = {
        "lahaa": {"1sg", "3sg_m"},
        "lahayd": {"2sg", "3sg_f"},
        "lahayn": {"1pl"},
        "lahaydeen": {"2pl"},
        "lahaayeen": {"3pl"},
    }
    for surface, persons in expected.items():
        analysis = analyze_reviewed_finite_verb(surface)
        assert analysis.recognized
        assert "leeyahay" in analysis.lemmas
        assert set(analysis.persons) == persons
        assert "tagto" in analysis.tense_aspects


def test_leeyahay_past_noun_agreement():
    assert analyze_noun_singular_verb_agreement("Ninku wuu lahaa guri.").agrees is True
    assert analyze_noun_singular_verb_agreement("Gabadhu way lahayd guri.").agrees is True
    assert analyze_noun_number_verb_agreement("Macallimiintu way lahaayeen guri.").agrees is True

    assert analyze_noun_singular_verb_agreement("Ninku wuu lahayd guri.").agrees is False
    assert analyze_noun_singular_verb_agreement("Gabadhu way lahaa guri.").agrees is False
    assert analyze_noun_number_verb_agreement("Macallimiintu way lahaydeen guri.").agrees is False


def test_leeyahay_past_negative_lahayn_is_person_neutralized():
    for sentence in (
        "Ninku ma lahayn guri.",
        "Gabadhu ma lahayn guri.",
        "Macallimiintu ma lahayn guri.",
    ):
        result = analyze_negative_finite_agreement(sentence)
        assert result.recognized
        assert result.verb_lemma == "leeyahay"
        assert result.tense_aspect == "tagto"
        assert result.person_neutralized is True
        assert result.agrees is True


def test_leeyahay_past_affirmative_under_ma_is_polarity_conflict():
    result = analyze_negative_finite_agreement("Ninku ma lahaa guri.")
    assert result.recognized
    assert result.verb_lemma == "leeyahay"
    assert result.tense_aspect == "tagto"
    assert result.polarity == "affirmative"
    assert result.agrees is False


def test_lahaa_family_preserves_multiple_reviewed_roles():
    lahaa_types = {candidate.analysis_type for candidate in analyze_surface_form("lahaa")}
    lahayn_types = {candidate.analysis_type for candidate in analyze_surface_form("lahayn")}
    lahaayeen_types = {candidate.analysis_type for candidate in analyze_surface_form("lahaayeen")}

    assert {"finite_verb", "conditional_auxiliary"} <= lahaa_types
    assert {"finite_verb", "negative_finite_verb", "conditional_auxiliary"} <= lahayn_types
    assert {"finite_verb", "conditional_auxiliary"} <= lahaayeen_types


def test_conditional_context_takes_precedence_over_possessive_past_reading():
    conditional = analyze_conditional_agreement("Gabadhu way cuni lahaa.")
    generic = analyze_noun_singular_verb_agreement("Gabadhu way cuni lahaa.")
    assert conditional.recognized and conditional.agrees is False
    assert generic.recognized and generic.agrees is None
    assert generic.verb is None

    plural_conditional = analyze_conditional_agreement("Macallimiintu way cuni lahaayeen.")
    plural_generic = analyze_noun_number_verb_agreement("Macallimiintu way cuni lahaayeen.")
    assert plural_conditional.recognized and plural_conditional.agrees is True
    assert plural_generic.recognized and plural_generic.agrees is None
    assert plural_generic.verb is None


def test_cross_validated_lahaayeen_supersedes_bad_parsed_surface():
    assert analyze_surface_form("lahaayeen")
    assert analyze_surface_form("lahayeen") == ()
    result = analyze_conditional_agreement("Macallimiintu way cuni lahaayeen.")
    assert result.recognized and result.agrees is True


def test_leeyahay_imperatives_are_exact():
    singular = analyze_imperative("Lahow!")
    plural = analyze_imperative("Lahaada!")
    assert singular.recognized and singular.lemma == "leeyahay" and singular.person == "2sg"
    assert plural.recognized and plural.lemma == "leeyahay" and plural.person == "2pl"


def test_lahaan_is_infinitive_only_in_this_stage_not_invented_future_stem():
    candidates = analyze_surface_form("lahaan")
    assert any(candidate.analysis_type == "masdar" for candidate in candidates)
    assert analyze_reviewed_finite_verb("lahaan").recognized is False
    assert analyze_future_auxiliary_agreement("Ninku wuu lahaan doonaa.").recognized is False


def test_unknown_leeyahay_lookalikes_are_not_generated():
    assert analyze_surface_form("leeyahayXYZ") == ()
    assert analyze_surface_form("lahaaXYZ") == ()
    assert analyze_surface_form("lahaayeenXYZ") == ()


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_accepts_reviewed_leeyahay_present_past_and_negative():
    for sentence in (
        "Ninku wuu leeyahay guri.",
        "Gabadhu way leedahay guri.",
        "Macallimiintu way leeyihiin guri.",
        "Ninku wuu lahaa guri.",
        "Gabadhu way lahayd guri.",
        "Macallimiintu way lahaayeen guri.",
        "Ninku ma laha guri.",
        "Gabadhu ma laha guri.",
        "Macallimiintu ma laha guri.",
        "Ninku ma lahayn guri.",
    ):
        assert _run_checker(sentence) == "No supported orthography or grammar findings found."


def test_cli_reports_possessive_person_conflict_without_autofix():
    output = _run_checker("Gabadhu way leeyahay guri.")
    assert "possible singular noun-subject/finite-verb agreement conflict" in output
    assert "Safe corrected text:\nGabadhu way leeyahay guri." in output


def test_cli_conditional_conflict_is_not_duplicated_as_possessive_finite_conflict():
    output = _run_checker("Gabadhu way cuni lahaa.")
    assert "possible conditional agreement conflict" in output
    assert "possible singular noun-subject/finite-verb agreement conflict" not in output


def test_cli_accepts_corrected_plural_conditional_surface():
    assert _run_checker("Macallimiintu way cuni lahaayeen.") == "No supported orthography or grammar findings found."
