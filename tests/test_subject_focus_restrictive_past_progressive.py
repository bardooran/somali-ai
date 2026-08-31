import subprocess
import sys

from src.focused_object_agreement import analyze_focused_object_agreement
from src.noun_number_verb_agreement import analyze_noun_number_verb_agreement
from src.subject_focus_agreement import analyze_subject_focus_agreement
from src.subject_focus_restrictive import analyze_subject_focus_restrictive


NO_FINDINGS = "No supported orthography or grammar findings found."


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_cun_past_progressive_uses_restrictive_person_classes():
    default = analyze_subject_focus_restrictive("cunayay", "3pl")
    assert default.recognized is True
    assert default.covered is True
    assert default.agrees is True
    assert default.paradigm == "past_progressive_reuse"
    assert "3pl" in default.contextual_persons
    assert "3sg_m" in default.full_surface_persons

    feminine = analyze_subject_focus_restrictive("cunaysay", "3sg_f")
    assert feminine.covered is True
    assert feminine.agrees is True

    first_plural = analyze_subject_focus_restrictive("cunaynay", "1pl")
    assert first_plural.covered is True
    assert first_plural.agrees is True


def test_full_plural_cun_past_progressive_is_not_restrictive_plural():
    result = analyze_subject_focus_restrictive("cunayeen", "3pl")
    assert result.recognized is True
    assert result.covered is True
    assert result.full_surface_persons == ("3pl",)
    assert result.agrees is False


def test_imow_past_progressive_uses_same_restrictive_classes():
    reduced_plural = analyze_subject_focus_restrictive("imanayay", "3pl")
    assert reduced_plural.recognized is True
    assert reduced_plural.covered is True
    assert reduced_plural.agrees is True
    assert reduced_plural.paradigm == "past_progressive_reuse"

    feminine = analyze_subject_focus_restrictive("imanaysay", "3sg_f")
    assert feminine.covered is True
    assert feminine.agrees is True

    first_plural = analyze_subject_focus_restrictive("imanaynay", "1pl")
    assert first_plural.covered is True
    assert first_plural.agrees is True

    full_plural = analyze_subject_focus_restrictive("imanayeen", "3pl")
    assert full_plural.covered is True
    assert full_plural.agrees is False


def test_subject_focus_sentence_layer_uses_restrictive_past_progressive():
    for sentence in (
        "Carruurta ayaa imanayay.",
        "Carruurta baa cunayay.",
        "Carruurta ayaa muus cunayay.",
        "Gabadha ayaa imanaysay.",
        "Gabadha baa cunaysay.",
    ):
        result = analyze_subject_focus_agreement(sentence)
        assert result.recognized is True
        assert result.agrees is True
        assert "restrictive_past_progressive" in (result.evidence or "")


def test_subject_focus_past_progressive_rejects_full_plural_and_gender_mismatch():
    for sentence in (
        "Carruurta ayaa imanayeen.",
        "Carruurta baa cunayeen.",
        "Gabadha ayaa imanayay.",
        "Gabadha baa cunayay.",
    ):
        result = analyze_subject_focus_agreement(sentence)
        assert result.recognized is True
        assert result.agrees is False
        assert "restrictive_past_progressive" in (result.evidence or "")


def test_past_progressive_restrictive_values_do_not_leak_into_ordinary_plural():
    ordinary_imow = analyze_noun_number_verb_agreement("Carruurtu way imanayeen.")
    assert ordinary_imow.recognized is True
    assert ordinary_imow.agrees is True

    reduced_imow = analyze_noun_number_verb_agreement("Carruurtu way imanayay.")
    assert reduced_imow.recognized is True
    assert reduced_imow.agrees is False

    ordinary_cun = analyze_noun_number_verb_agreement("Carruurtu way cunayeen.")
    assert ordinary_cun.recognized is True
    assert ordinary_cun.agrees is True

    reduced_cun = analyze_noun_number_verb_agreement("Carruurtu way cunayay.")
    assert reduced_cun.recognized is True
    assert reduced_cun.agrees is False


def test_past_progressive_restrictive_values_do_not_leak_into_object_focus():
    ordinary = analyze_focused_object_agreement("Carruurtu muus bay cunayeen.")
    assert ordinary.recognized is True
    assert ordinary.agrees is True

    reduced = analyze_focused_object_agreement("Carruurtu muus bay cunayay.")
    assert reduced.recognized is True
    assert reduced.agrees is False


def test_excluded_irregular_past_progressive_lookalike_is_not_inferred():
    result = analyze_subject_focus_agreement("Carruurta ayaa aqaanayay.")
    assert result.recognized is True
    assert result.agrees is None
    assert result.evidence == "predicate_unreviewed"


def test_cli_accepts_restrictive_past_progressive_and_reports_full_plural():
    assert _run_checker("Carruurta ayaa imanayay.") == NO_FINDINGS
    assert _run_checker("Carruurta ayaa muus cunayay.") == NO_FINDINGS
    assert _run_checker("Gabadha ayaa imanaysay.") == NO_FINDINGS

    output = _run_checker("Carruurta ayaa imanayeen.")
    assert "possible subject-verb agreement conflict" in output
    assert "restrictive focused-subject past-progressive agreement" in output
    assert "Safe corrected text:\nCarruurta ayaa imanayeen." in output

    output = _run_checker("Carruurta ayaa muus cunayeen.")
    assert "possible subject-verb agreement conflict" in output
    assert "restrictive focused-subject past-progressive agreement" in output
    assert "Safe corrected text:\nCarruurta ayaa muus cunayeen." in output
