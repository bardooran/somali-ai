import subprocess
import sys

from src.noun_number_verb_agreement import analyze_noun_number_verb_agreement
from src.reviewed_finite_verb import analyze_reviewed_finite_verb
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


def test_regular_simple_present_reduced_forms_are_contextual():
    plural = analyze_subject_focus_restrictive("cuna", "3pl")
    assert plural.recognized is True
    assert plural.covered is True
    assert plural.agrees is True
    assert plural.paradigm == "simple_present_short"
    assert "3pl" in plural.contextual_persons
    assert "cunaa" in plural.source_full_surfaces

    feminine = analyze_subject_focus_restrictive("cunta", "3sg_f")
    assert feminine.agrees is True
    assert feminine.paradigm == "simple_present_short"

    first_plural = analyze_subject_focus_restrictive("cunna", "1pl")
    assert first_plural.agrees is True
    assert first_plural.paradigm == "simple_present_short"

    assert analyze_subject_focus_restrictive("cunta", "3pl").agrees is False
    assert analyze_subject_focus_restrictive("cuna", "3sg_f").agrees is False


def test_regular_full_simple_present_is_wrong_only_inside_subject_focus():
    focused = analyze_subject_focus_agreement("Carruurta ayaa cunaan.")
    assert focused.recognized is True
    assert focused.expected_person == "3pl"
    assert focused.predicate == "cunaan"
    assert focused.agrees is False
    assert "restrictive_simple_present" in (focused.evidence or "")

    ordinary = analyze_noun_number_verb_agreement("Carruurtu way cunaan.")
    assert ordinary.recognized is True
    assert ordinary.agrees is True


def test_regular_subject_focus_simple_present_accepts_reduced_number_gender():
    assert analyze_subject_focus_agreement("Carruurta ayaa cuna.").agrees is True
    assert analyze_subject_focus_agreement("Wiilka ayaa cuna.").agrees is True
    assert analyze_subject_focus_agreement("Gabadha ayaa cunta.").agrees is True

    assert analyze_subject_focus_agreement("Gabadha ayaa cuna.").agrees is False
    assert analyze_subject_focus_agreement("Carruurta ayaa cunta.").agrees is False


def test_present_progressive_reduced_forms_are_contextual():
    plural = analyze_subject_focus_restrictive("cunaya", "3pl")
    assert plural.recognized is True
    assert plural.covered is True
    assert plural.agrees is True
    assert plural.paradigm == "present_progressive_short"
    assert "cunayaa" in plural.source_full_surfaces

    feminine = analyze_subject_focus_restrictive("cunaysa", "3sg_f")
    assert feminine.agrees is True

    first_plural = analyze_subject_focus_restrictive("cunayna", "1pl")
    assert first_plural.agrees is True

    assert analyze_subject_focus_restrictive("cunaya", "3sg_f").agrees is False
    assert analyze_subject_focus_restrictive("cunaysa", "3pl").agrees is False


def test_subject_focus_present_progressive_rejects_full_plural_form():
    reduced = analyze_subject_focus_agreement("Carruurta ayaa cunaya.")
    assert reduced.recognized is True
    assert reduced.expected_person == "3pl"
    assert reduced.predicate == "cunaya"
    assert reduced.agrees is True
    assert "restrictive_present_progressive" in (reduced.evidence or "")

    full = analyze_subject_focus_agreement("Carruurta ayaa cunayaan.")
    assert full.recognized is True
    assert full.predicate == "cunayaan"
    assert full.agrees is False

    assert analyze_subject_focus_agreement("Gabadha ayaa cunaysa.").agrees is True
    assert analyze_subject_focus_agreement("Gabadha ayaa cunaya.").agrees is False


def test_imow_present_and_progressive_use_reduced_focus_forms():
    assert analyze_subject_focus_agreement("Carruurta ayaa yimaadda.").agrees is True
    assert analyze_subject_focus_agreement("Carruurta ayaa yimaaddaan.").agrees is False
    assert analyze_subject_focus_agreement("Gabadha ayaa timaadda.").agrees is True
    assert analyze_subject_focus_agreement("Gabadha ayaa yimaadda.").agrees is False

    assert analyze_subject_focus_agreement("Carruurta ayaa imanaya.").agrees is True
    assert analyze_subject_focus_agreement("Carruurta ayaa imanayaan.").agrees is False
    assert analyze_subject_focus_agreement("Gabadha ayaa imanaysa.").agrees is True


def test_aqaan_present_reuses_source_backed_reduced_surfaces_contextually():
    global_yqaan = analyze_reviewed_finite_verb("yaqaan")
    assert global_yqaan.recognized is True
    assert global_yqaan.persons == ("3sg_m",)

    focused_plural = analyze_subject_focus_restrictive("yaqaan", "3pl")
    assert focused_plural.covered is True
    assert focused_plural.agrees is True
    assert focused_plural.paradigm == "simple_present_irregular_reuse"

    assert analyze_subject_focus_agreement("Carruurta ayaa yaqaan.").agrees is True
    assert analyze_subject_focus_agreement("Carruurta ayaa yaqaaniin.").agrees is False
    assert analyze_subject_focus_agreement("Gabadha ayaa taqaan.").agrees is True


def test_aal_yaal_present_reuses_source_backed_reduced_surfaces_contextually():
    global_yaal = analyze_reviewed_finite_verb("yaal")
    assert global_yaal.recognized is True
    assert "3sg_m" in global_yaal.persons

    focused_plural = analyze_subject_focus_restrictive("yaal", "3pl")
    assert focused_plural.covered is True
    assert focused_plural.agrees is True
    assert focused_plural.paradigm == "simple_present_irregular_reuse"

    assert analyze_subject_focus_agreement("Baabuurta baa yaal.").agrees is True
    assert analyze_subject_focus_agreement("Baabuurta baa yaalliin.").agrees is False


def test_copular_present_focus_uses_invariant_ah():
    reduced = analyze_subject_focus_restrictive("ah", "3pl")
    assert reduced.recognized is True
    assert reduced.covered is True
    assert reduced.agrees is True
    assert reduced.paradigm == "copular_present_invariant"

    assert analyze_subject_focus_agreement("Gabadha ayaa macallin ah.").agrees is True
    assert analyze_subject_focus_agreement("Carruurta ayaa macallimiin ah.").agrees is True
    assert analyze_subject_focus_agreement("Gabadha ayaa macallin tahay.").agrees is False
    assert analyze_subject_focus_agreement("Carruurta ayaa macallimiin yihiin.").agrees is False


def test_contextual_short_present_forms_do_not_become_global_finite_forms():
    assert analyze_reviewed_finite_verb("cuna").recognized is False
    assert analyze_reviewed_finite_verb("cunaya").recognized is False
    assert analyze_reviewed_finite_verb("yimaadda").recognized is False

    assert analyze_reviewed_finite_verb("cunaa").recognized is True
    assert analyze_reviewed_finite_verb("cunayaa").recognized is True
    assert analyze_reviewed_finite_verb("yimaaddaa").recognized is True


def test_cli_accepts_reduced_present_and_reports_full_present_focus_forms():
    assert _run_checker("Carruurta ayaa cuna.") == NO_FINDINGS
    assert _run_checker("Carruurta ayaa cunaya.") == NO_FINDINGS

    output = _run_checker("Carruurta ayaa cunaan.")
    assert "possible subject-verb agreement conflict" in output
    assert "restrictive focused-subject simple-present agreement" in output
    assert "Safe corrected text:\nCarruurta ayaa cunaan." in output

    output = _run_checker("Carruurta ayaa cunayaan.")
    assert "possible subject-verb agreement conflict" in output
    assert "restrictive focused-subject present-progressive agreement" in output
    assert "Safe corrected text:\nCarruurta ayaa cunayaan." in output
