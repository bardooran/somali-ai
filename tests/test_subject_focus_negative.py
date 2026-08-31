import subprocess
import sys

from src.morphology_candidates import analyze_surface_form
from src.noun_subject_case import analyze_noun_subject_case
from src.subject_focus_negative import analyze_subject_focus_negative


NO_FINDINGS = "No supported orthography or grammar findings found."


def _run_checker(sentence: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", sentence],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_exact_published_cali_negative_focus_example_is_recognized_without_bax_paradigm():
    for sentence, marker in (("Cali baan bixin.", "baan"), ("Cali ayaan bixin.", "ayaan")):
        result = analyze_subject_focus_negative(sentence)
        assert result.recognized is True
        assert result.covered is True
        assert result.subject == "Cali"
        assert result.marker == marker
        assert result.predicate == "bixin"
        assert result.case_agrees is True
        assert result.marker_agrees is True
        assert result.orthographically_ambiguous is True
        assert result.temporal_scope == ("past",)
        assert "source_exact_cali_bixin" in (result.evidence or "")
    assert analyze_subject_focus_negative("Cali baan baxXYZ.").recognized is False
    assert analyze_subject_focus_negative("Cali baa bixin.").recognized is False


def test_unambiguous_person_neutral_simple_negative_is_reduced_subjunctive_under_focus():
    examples = (("Carruurta baan cunin.", "cunin"), ("Gabadha ayaan iman.", "iman"), ("Wiilka baan imanin.", "imanin"))
    for sentence, predicate in examples:
        result = analyze_subject_focus_negative(sentence)
        assert result.recognized is True
        assert result.covered is True
        assert result.predicate == predicate
        assert result.tense_aspect == "reduced_subjunctive_simple"
        assert result.temporal_scope == ("present", "past")
        assert result.case_agrees is True
        assert result.marker_agrees is True
        assert result.predicate_has_nonnegative_analysis is False
        assert "exact_person_neutral_reduced_subjunctive_simple" in (result.evidence or "")


def test_aqoon_surface_ambiguity_is_not_forced_without_negative_context():
    ambiguous = analyze_subject_focus_negative("Gabadha baan aqoon.")
    assert ambiguous.recognized is False
    assert ambiguous.predicate == "aqoon"
    assert ambiguous.predicate_has_nonnegative_analysis is True
    assert ambiguous.orthographically_ambiguous is True

    disambiguated = analyze_subject_focus_negative("Gabadha baan waxba aqoon.")
    assert disambiguated.recognized is True
    assert disambiguated.predicate == "aqoon"
    assert disambiguated.marker_agrees is True
    assert disambiguated.predicate_has_nonnegative_analysis is True
    assert disambiguated.negative_context_evidence == ("waxba",)


def test_temporal_context_does_not_change_the_reduced_simple_surface():
    for result in (
        analyze_subject_focus_negative("Carruurta baan maanta cunin."),
        analyze_subject_focus_negative("Carruurta baan shalay cunin."),
    ):
        assert result.recognized is True
        assert result.predicate == "cunin"
        assert result.tense_aspect == "reduced_subjunctive_simple"
        assert result.temporal_scope == ("present", "past")


def test_waxba_is_recorded_as_negative_context_without_assigning_a_new_role():
    result = analyze_subject_focus_negative("Carruurta baan maanta waxba cunin.")
    assert result.recognized is True
    assert result.marker_agrees is True
    assert result.predicate == "cunin"
    assert result.negative_context_evidence == ("waxba",)
    assert "negative_context_waxba" in (result.evidence or "")


def test_person_neutral_progressive_negative_is_reduced_subjunctive_present_or_past():
    for sentence, predicate in (
        ("Carruurta baan muus cunayn.", "cunayn"),
        ("Carruurta ayaan muus cunaynin.", "cunaynin"),
        ("Gabadha baan maanta imanayn.", "imanayn"),
        ("Gabadha ayaan shalay imanaynin.", "imanaynin"),
    ):
        result = analyze_subject_focus_negative(sentence)
        assert result.recognized is True
        assert result.covered is True
        assert result.predicate == predicate
        assert result.tense_aspect == "reduced_subjunctive_progressive"
        assert result.temporal_scope == ("present", "past")
        assert result.case_agrees is True
        assert result.marker_agrees is True


def test_exact_habitual_stem_plus_jirin_is_reduced_negative_focus_habitual():
    for sentence, predicate in (
        ("Carruurta baan cuni jirin.", "cuni jirin"),
        ("Gabadha ayaan imaan jirin.", "imaan jirin"),
        ("Carruurta baan maanta waxba cuni jirin.", "cuni jirin"),
    ):
        result = analyze_subject_focus_negative(sentence)
        assert result.recognized is True
        assert result.covered is True
        assert result.predicate == predicate
        assert result.tense_aspect == "reduced_subjunctive_habitual"
        assert result.temporal_scope == ("past_habitual",)
        assert result.marker_agrees is True
        assert result.case_agrees is True


def test_exact_future_stem_plus_doonin_is_reduced_negative_focus_future():
    candidates = analyze_surface_form("doonin")
    assert any(c.analysis_type == "negative_focus_future_auxiliary" for c in candidates)

    for sentence, predicate in (
        ("Carruurta baan cuni doonin.", "cuni doonin"),
        ("Gabadha ayaan imaan doonin.", "imaan doonin"),
        ("Carruurta baan berri waxba cuni doonin.", "cuni doonin"),
    ):
        result = analyze_subject_focus_negative(sentence)
        assert result.recognized is True
        assert result.covered is True
        assert result.predicate == predicate
        assert result.tense_aspect == "reduced_subjunctive_future"
        assert result.temporal_scope == ("future",)
        assert result.marker_agrees is True
        assert result.case_agrees is True


def test_compound_negative_focus_requires_exact_reviewed_stem_and_auxiliary():
    for sentence in (
        "Carruurta baan cunXYZ jirin.",
        "Carruurta baan imanXYZ doonin.",
        "Carruurta baan cuni jirXYZ.",
        "Carruurta baan cuni doonXYZ.",
    ):
        assert analyze_subject_focus_negative(sentence).recognized is False


def test_ordinary_future_auxiliaries_do_not_substitute_for_focus_reduced_doonin():
    for sentence in (
        "Carruurta baan cuni doono.",
        "Gabadha ayaan cuni doonto.",
        "Carruurta baan cuni doonaan.",
    ):
        assert analyze_subject_focus_negative(sentence).recognized is False


def test_bare_baa_ayaa_are_marker_conflicts_before_proven_reduced_negative_predicate():
    for sentence, marker, expected, predicate in (
        ("Carruurta baa maanta cunin.", "baa", "baan", "cunin"),
        ("Carruurta ayaa maanta waxba cunin.", "ayaa", "ayaan", "cunin"),
        ("Carruurta ayaa cuni jirin.", "ayaa", "ayaan", "cuni jirin"),
        ("Carruurta baa cuni doonin.", "baa", "baan", "cuni doonin"),
    ):
        result = analyze_subject_focus_negative(sentence)
        assert result.recognized is True
        assert result.covered is True
        assert result.marker == marker
        assert result.marker_agrees is False
        assert result.expected_marker == expected
        assert result.predicate == predicate
        assert result.case_agrees is True


def test_connective_ayaana_and_markerless_fragments_are_not_forced_into_negative_focus():
    for sentence in (
        "Carruurta ayaana maanta wax cunin.",
        "Carruurta maanta wax cunin.",
        "Carruurta ayaana cuni doonin.",
        "Carruurta cuni jirin.",
    ):
        assert analyze_subject_focus_negative(sentence).recognized is False


def test_negative_focus_disambiguation_makes_common_noun_absolute_case_judgeable():
    plural = analyze_subject_focus_negative("Carruurtu baan cuni doonin.")
    assert plural.recognized is True
    assert plural.case_agrees is False
    assert plural.expected_subject_form == "Carruurta"

    feminine = analyze_subject_focus_negative("Gabadhu ayaan imaan jirin.")
    assert feminine.recognized is True
    assert feminine.case_agrees is False
    assert feminine.expected_subject_form == "Gabadha"

    masculine = analyze_subject_focus_negative("Wiilku baan imanin.")
    assert masculine.recognized is True
    assert masculine.case_agrees is False
    assert masculine.expected_subject_form == "Wiilka"


def test_main_noun_case_analyzer_reuses_negative_focus_evidence():
    correct = analyze_noun_subject_case("Carruurta baan cuni doonin.")
    assert correct.recognized is True
    assert correct.marker == "baan"
    assert correct.agrees is True

    wrong = analyze_noun_subject_case("Carruurtu baan cuni jirin.")
    assert wrong.recognized is True
    assert wrong.marker == "baan"
    assert wrong.agrees is False
    assert wrong.expected_subject_form == "Carruurta"
    assert wrong.rule_id == "GRAM-SUBJFOCUS-NEG-003"


def test_baan_ayaan_are_not_globally_reinterpreted_as_negative():
    for sentence in (
        "Carruurta baan cunay.",
        "Carruurta baan cunaan.",
        "Carruurta ayaan cuneen.",
        "Carruurta baan cunXYZ.",
        "Muus baan cunay.",
    ):
        assert analyze_subject_focus_negative(sentence).recognized is False


def test_full_present_negative_forms_are_not_substituted_for_reduced_focus_forms():
    for sentence in ("Carruurta baan cuno.", "Carruurta baan cunayo.", "Carruurta baan cunaan."):
        assert analyze_subject_focus_negative(sentence).recognized is False


def test_cli_accepts_reviewed_negative_focus_and_reports_only_safe_case_conflict():
    for sentence in (
        "Cali baan bixin.",
        "Carruurta baan cunin.",
        "Carruurta baan maanta waxba cunin.",
        "Gabadha ayaan imanayn.",
        "Gabadha baan aqoon.",
        "Carruurta baan cuni jirin.",
        "Gabadha ayaan imaan doonin.",
    ):
        assert _run_checker(sentence) == NO_FINDINGS

    output = _run_checker("Carruurtu baan cuni doonin.")
    assert "possible definite-noun subject-case conflict" in output
    assert "reviewed subject-form candidate is 'Carruurta'" in output
    assert "GRAM-SUBJFOCUS-NEG-003" in output
    assert "Safe corrected text:\nCarruurtu baan cuni doonin." in output


def test_cli_reports_bare_positive_focus_marker_before_reduced_negative():
    for sentence, marker, expected in (
        ("Carruurta baa maanta cunin.", "baa", "baan"),
        ("Carruurta ayaa maanta waxba cunin.", "ayaa", "ayaan"),
        ("Carruurta ayaa cuni jirin.", "ayaa", "ayaan"),
        ("Carruurta baa cuni doonin.", "baa", "baan"),
    ):
        output = _run_checker(sentence)
        assert "possible negative subject-focus marker conflict" in output
        assert repr(marker) in output
        assert repr(expected) in output
        assert "GRAM-SUBJFOCUS-NEG-006" in output
        assert f"Safe corrected text:\n{sentence}" in output


def test_cli_leaves_connective_and_markerless_negative_fragments_unjudged():
    assert _run_checker("Carruurta ayaana maanta wax cunin.") == NO_FINDINGS
    assert _run_checker("Carruurta maanta wax cunin.") == NO_FINDINGS
    assert _run_checker("Carruurta ayaana cuni doonin.") == NO_FINDINGS


def test_existing_affirmative_focus_and_ordinary_subject_case_stay_separate():
    assert analyze_noun_subject_case("Wiilka ayaa yimid.").agrees is True
    assert analyze_noun_subject_case("Wiilku ayaa yimid.").agrees is False
    assert analyze_noun_subject_case("Wiilku wuu yimid.").agrees is True
    assert analyze_noun_subject_case("Wiilka wuu yimid.").agrees is False
