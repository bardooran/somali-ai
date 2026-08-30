import subprocess
import sys

from src.future_auxiliary_agreement import analyze_future_auxiliary_agreement
from src.morphology_candidates import analyze_surface_form
from src.negative_finite_agreement import analyze_negative_finite_agreement
from src.noun_number_verb_agreement import analyze_noun_number_verb_agreement
from src.noun_singular_verb_agreement import analyze_noun_singular_verb_agreement
from src.reviewed_finite_verb import analyze_reviewed_finite_verb


def test_aal_yaal_present_short_and_long_alternatives_are_exact():
    expected = {
        "aal": {"1sg"},
        "aallaa": {"1sg"},
        "taal": {"2sg", "3sg_f"},
        "taallaa": {"2sg", "3sg_f"},
        "yaal": {"3sg_m"},
        "yaallaa": {"3sg_m"},
        "naal": {"1pl"},
        "naallaa": {"1pl"},
        "taalliin": {"2pl"},
        "taallaan": {"2pl"},
        "yaalliin": {"3pl"},
        "yaallaan": {"3pl"},
    }
    for surface, persons in expected.items():
        analysis = analyze_reviewed_finite_verb(surface)
        assert analysis.recognized
        assert analysis.lemmas == ("aal/yaal",)
        assert set(analysis.persons) == persons


def test_aal_yaal_present_noun_agreement_uses_prefix_person():
    for sentence in ("Ninku wuu yaal.", "Ninku wuu yaallaa."):
        result = analyze_noun_singular_verb_agreement(sentence)
        assert result.recognized and result.agrees is True
        assert result.verb_lemmas == ("aal/yaal",)

    for sentence in ("Gabadhu way taal.", "Gabadhu way taallaa."):
        result = analyze_noun_singular_verb_agreement(sentence)
        assert result.recognized and result.agrees is True

    for sentence in ("Macallimiintu way yaalliin.", "Macallimiintu way yaallaan."):
        result = analyze_noun_number_verb_agreement(sentence)
        assert result.recognized and result.agrees is True

    assert analyze_noun_singular_verb_agreement("Ninku wuu taal.").agrees is False
    assert analyze_noun_singular_verb_agreement("Gabadhu way yaal.").agrees is False
    assert analyze_noun_number_verb_agreement("Macallimiintu way taalliin.").agrees is False


def test_aal_yaal_past_short_and_long_alternatives_are_exact():
    expected = {
        "iil": {"1sg"},
        "iillay": {"1sg"},
        "tiil": {"2sg", "3sg_f"},
        "tiillay": {"2sg", "3sg_f"},
        "yiil": {"3sg_m"},
        "yiillay": {"3sg_m"},
        "niil": {"1pl"},
        "niillay": {"1pl"},
        "tiilleen": {"2pl"},
        "yiilleen": {"3pl"},
    }
    for surface, persons in expected.items():
        analysis = analyze_reviewed_finite_verb(surface)
        assert analysis.recognized
        assert analysis.lemmas == ("aal/yaal",)
        assert set(analysis.persons) == persons
        assert "tagto" in analysis.tense_aspects


def test_aal_yaal_past_noun_agreement_generalizes_without_suffix_rules():
    for sentence in ("Ninku wuu yiil.", "Ninku wuu yiillay."):
        result = analyze_noun_singular_verb_agreement(sentence)
        assert result.recognized and result.agrees is True

    for sentence in ("Gabadhu way tiil.", "Gabadhu way tiillay."):
        result = analyze_noun_singular_verb_agreement(sentence)
        assert result.recognized and result.agrees is True

    plural = analyze_noun_number_verb_agreement("Macallimiintu way yiilleen.")
    assert plural.recognized and plural.agrees is True

    assert analyze_noun_singular_verb_agreement("Ninku wuu tiil.").agrees is False
    assert analyze_noun_singular_verb_agreement("Gabadhu way yiil.").agrees is False
    assert analyze_noun_number_verb_agreement("Macallimiintu way tiilleen.").agrees is False


def test_aal_yaal_past_negative_ool_is_person_neutralized():
    for sentence in (
        "Ninku ma ool.",
        "Gabadhu ma ool.",
        "Macallimiintu ma ool.",
        "Ninku ma oolin.",
        "Gabadhu ma oolin.",
        "Macallimiintu ma oolin.",
    ):
        result = analyze_negative_finite_agreement(sentence)
        assert result.recognized
        assert result.verb_lemma == "aal/yaal"
        assert result.tense_aspect == "tagto"
        assert result.person_neutralized is True
        assert result.agrees is True


def test_aal_yaal_past_affirmative_under_ma_is_polarity_conflict():
    result = analyze_negative_finite_agreement("Ninku ma yiil.")
    assert result.recognized
    assert result.verb_lemma == "aal/yaal"
    assert result.tense_aspect == "tagto"
    assert result.polarity == "affirmative"
    assert result.agrees is False


def test_aal_yaal_present_under_ma_is_unjudged_without_present_negative_evidence():
    masculine = analyze_negative_finite_agreement("Ninku ma yaal.")
    feminine = analyze_negative_finite_agreement("Gabadhu ma taal.")
    plural = analyze_negative_finite_agreement("Macallimiintu ma yaalliin.")

    for result in (masculine, feminine, plural):
        assert result.recognized
        assert result.verb_lemma == "aal/yaal"
        assert result.polarity == "affirmative"
        assert result.agrees is None
        assert "no reviewed negative paradigm" in result.note


def test_oolli_is_masdar_only_not_invented_future_stem():
    candidates = analyze_surface_form("oolli")
    assert any(candidate.lemma == "aal/yaal" and candidate.analysis_type == "masdar" for candidate in candidates)
    assert analyze_reviewed_finite_verb("oolli").recognized is False
    assert analyze_future_auxiliary_agreement("Ninku wuu oolli doonaa.").recognized is False


def test_unknown_aal_yaal_lookalikes_are_not_generated():
    assert analyze_surface_form("yaalXYZ") == ()
    assert analyze_reviewed_finite_verb("yiilXYZ").recognized is False
    assert analyze_surface_form("oolXYZ") == ()


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cli_accepts_aal_yaal_reviewed_present_and_past_negative():
    assert _run_checker("Ninku wuu yaal.") == "No supported orthography or grammar findings found."
    assert _run_checker("Gabadhu way taal.") == "No supported orthography or grammar findings found."
    assert _run_checker("Ninku ma ool.") == "No supported orthography or grammar findings found."


def test_cli_does_not_invent_present_negative_conflict_for_aal_yaal():
    assert _run_checker("Ninku ma yaal.") == "No supported orthography or grammar findings found."


def test_cli_reports_reviewed_past_polarity_conflict():
    output = _run_checker("Ninku ma yiil.")
    assert "possible negative finite subject/verb agreement conflict" in output
    assert "Safe corrected text:\nNinku ma yiil." in output
