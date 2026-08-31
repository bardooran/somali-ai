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


def test_imow_restrictive_past_reinterprets_exact_full_surfaces_contextually():
    plural_reduced = analyze_subject_focus_restrictive("yimid", "3pl")
    assert plural_reduced.recognized is True
    assert plural_reduced.covered is True
    assert plural_reduced.agrees is True
    assert "3pl" in plural_reduced.contextual_persons
    assert plural_reduced.full_surface_persons == ("3sg_m",)

    plural_full = analyze_subject_focus_restrictive("yimaadeen", "3pl")
    assert plural_full.recognized is True
    assert plural_full.covered is True
    assert plural_full.agrees is False
    assert "3pl" not in plural_full.contextual_persons


def test_imow_restrictive_past_preserves_feminine_and_no_final_d_variants():
    assert analyze_subject_focus_restrictive("timid", "3sg_f").agrees is True
    assert analyze_subject_focus_restrictive("timi", "3sg_f").agrees is True
    assert analyze_subject_focus_restrictive("yimid", "3sg_f").agrees is False
    assert analyze_subject_focus_restrictive("yimi", "3pl").agrees is True


def test_cun_restrictive_past_generalizes_from_exact_reviewed_morphology():
    plural_reduced = analyze_subject_focus_restrictive("cunay", "3pl")
    assert plural_reduced.recognized is True
    assert plural_reduced.covered is True
    assert plural_reduced.agrees is True
    assert "3pl" in plural_reduced.contextual_persons

    plural_full = analyze_subject_focus_restrictive("cuneen", "3pl")
    assert plural_full.recognized is True
    assert plural_full.covered is True
    assert plural_full.agrees is False

    assert analyze_subject_focus_restrictive("cuntay", "3sg_f").agrees is True


def test_focused_plural_common_noun_now_uses_restrictive_imow_past():
    reduced = analyze_subject_focus_agreement("Carruurta ayaa yimid.")
    assert reduced.recognized is True
    assert reduced.expected_person == "3pl"
    assert reduced.predicate == "yimid"
    assert reduced.agrees is True
    assert "restrictive_simple_past" in (reduced.evidence or "")

    full = analyze_subject_focus_agreement("Carruurta ayaa yimaadeen.")
    assert full.recognized is True
    assert full.expected_person == "3pl"
    assert full.predicate == "yimaadeen"
    assert full.agrees is False


def test_focused_plural_can_have_intervening_object_before_restrictive_verb():
    reduced = analyze_subject_focus_agreement("Carruurta ayaa muus cunay.")
    assert reduced.recognized is True
    assert reduced.expected_person == "3pl"
    assert reduced.predicate == "cunay"
    assert reduced.agrees is True

    full = analyze_subject_focus_agreement("Carruurta ayaa muus cuneen.")
    assert full.recognized is True
    assert full.predicate == "cuneen"
    assert full.agrees is False


def test_singular_subject_focus_still_uses_restrictive_past_correctly():
    assert analyze_subject_focus_agreement("Wiilka ayaa yimid.").agrees is True
    assert analyze_subject_focus_agreement("Gabadha ayaa timid.").agrees is True
    assert analyze_subject_focus_agreement("Wiilka ayaa timid.").agrees is False
    assert analyze_subject_focus_agreement("Gabadha ayaa yimid.").agrees is False


def test_exact_native_subject_focus_surface_still_outranks_general_paradigm():
    result = analyze_subject_focus_agreement("Maryan baa qososhay.")
    assert result.recognized is True
    assert result.agrees is True
    assert result.evidence == "exact_native_reviewed_sentence_surface"


def test_unmodeled_present_focus_is_not_judged_from_full_paradigm():
    plural = analyze_subject_focus_agreement("Carruurta ayaa yimaaddaan.")
    assert plural.recognized is True
    assert plural.agrees is None
    assert "not_yet_modeled" in (plural.evidence or "")

    singular = analyze_subject_focus_agreement("Wiilka ayaa yimaaddaa.")
    assert singular.recognized is True
    assert singular.agrees is None
    assert "not_yet_modeled" in (singular.evidence or "")


def test_restrictive_person_values_do_not_leak_into_ordinary_plural_agreement():
    ordinary_full = analyze_noun_number_verb_agreement("Carruurtu way yimaadeen.")
    assert ordinary_full.recognized is True
    assert ordinary_full.agrees is True

    ordinary_reduced = analyze_noun_number_verb_agreement("Carruurtu way yimid.")
    assert ordinary_reduced.recognized is True
    assert ordinary_reduced.agrees is False


def test_restrictive_person_values_do_not_leak_into_object_focus():
    ordinary_object_focus = analyze_focused_object_agreement("Carruurtu muus bay cuneen.")
    assert ordinary_object_focus.recognized is True
    assert ordinary_object_focus.agrees is True

    wrong_reduced_object_focus = analyze_focused_object_agreement("Carruurtu muus bay cunay.")
    assert wrong_reduced_object_focus.recognized is True
    assert wrong_reduced_object_focus.agrees is False


def test_cli_accepts_restrictive_plural_and_reports_full_plural_in_subject_focus():
    assert _run_checker("Carruurta ayaa yimid.") == NO_FINDINGS
    assert _run_checker("Carruurta ayaa muus cunay.") == NO_FINDINGS

    output = _run_checker("Carruurta ayaa yimaadeen.")
    assert "possible subject-verb agreement conflict" in output
    assert "restrictive focused-subject simple-past form licensed for 3pl" in output
    assert "Safe corrected text:\nCarruurta ayaa yimaadeen." in output

    output = _run_checker("Carruurta ayaa muus cuneen.")
    assert "possible subject-verb agreement conflict" in output
    assert "restrictive focused-subject simple-past form licensed for 3pl" in output
    assert "Safe corrected text:\nCarruurta ayaa muus cuneen." in output


def test_unknown_focus_predicate_stays_unjudged():
    result = analyze_subject_focus_agreement("Carruurta ayaa yimidXYZ.")
    assert result.recognized is True
    assert result.agrees is None
    assert result.evidence == "predicate_unreviewed"
