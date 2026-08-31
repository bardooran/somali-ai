import subprocess
import sys

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
    for sentence, marker in (
        ("Cali baan bixin.", "baan"),
        ("Cali ayaan bixin.", "ayaan"),
    ):
        result = analyze_subject_focus_negative(sentence)
        assert result.recognized is True
        assert result.covered is True
        assert result.subject == "Cali"
        assert result.marker == marker
        assert result.predicate == "bixin"
        assert result.case_agrees is True
        assert result.temporal_scope == ("past",)
        assert "source_exact_cali_bixin" in (result.evidence or "")

    # A single source sentence does not license unseen BAX morphology.
    assert analyze_subject_focus_negative("Cali baan baxXYZ.").recognized is False


def test_person_neutral_simple_negative_is_reduced_subjunctive_present_or_past_under_focus():
    examples = (
        ("Carruurta baan cunin.", "cunin"),
        ("Gabadha ayaan iman.", "iman"),
        ("Wiilka baan imanin.", "imanin"),
        ("Gabadha baan aqoon.", "aqoon"),
    )
    for sentence, predicate in examples:
        result = analyze_subject_focus_negative(sentence)
        assert result.recognized is True
        assert result.covered is True
        assert result.predicate == predicate
        assert result.tense_aspect == "reduced_subjunctive_simple"
        assert result.temporal_scope == ("present", "past")
        assert result.case_agrees is True
        assert "exact_person_neutral_reduced_subjunctive_simple" in (result.evidence or "")


def test_temporal_context_does_not_change_the_reduced_simple_surface():
    present_context = analyze_subject_focus_negative("Carruurta baan maanta cunin.")
    past_context = analyze_subject_focus_negative("Carruurta baan shalay cunin.")

    for result in (present_context, past_context):
        assert result.recognized is True
        assert result.predicate == "cunin"
        assert result.tense_aspect == "reduced_subjunctive_simple"
        assert result.temporal_scope == ("present", "past")


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


def test_negative_focus_disambiguation_makes_common_noun_absolute_case_judgeable():
    plural = analyze_subject_focus_negative("Carruurtu baan cunin.")
    assert plural.recognized is True
    assert plural.case_agrees is False
    assert plural.expected_subject_form == "Carruurta"

    feminine = analyze_subject_focus_negative("Gabadhu ayaan iman.")
    assert feminine.recognized is True
    assert feminine.case_agrees is False
    assert feminine.expected_subject_form == "Gabadha"

    masculine = analyze_subject_focus_negative("Wiilku baan imanin.")
    assert masculine.recognized is True
    assert masculine.case_agrees is False
    assert masculine.expected_subject_form == "Wiilka"


def test_main_noun_case_analyzer_reuses_negative_focus_evidence():
    correct = analyze_noun_subject_case("Carruurta baan cunin.")
    assert correct.recognized is True
    assert correct.marker == "baan"
    assert correct.agrees is True

    wrong = analyze_noun_subject_case("Carruurtu baan cunin.")
    assert wrong.recognized is True
    assert wrong.marker == "baan"
    assert wrong.agrees is False
    assert wrong.expected_subject_form == "Carruurta"
    assert wrong.rule_id == "GRAM-SUBJFOCUS-NEG-003"


def test_baan_ayaan_are_not_globally_reinterpreted_as_negative():
    # Affirmative/full predicates do not prove a negative-subject-focus reading.
    for sentence in (
        "Carruurta baan cunay.",
        "Carruurta baan cunaan.",
        "Carruurta ayaan cuneen.",
        "Carruurta baan cunXYZ.",
        "Muus baan cunay.",
    ):
        assert analyze_subject_focus_negative(sentence).recognized is False


def test_full_present_negative_forms_are_not_substituted_for_reduced_focus_forms():
    # Present meaning under focus still uses the reduced subjunctive; ordinary
    # full ma-negative forms do not become valid merely because baan/ayaan occurs.
    for sentence in (
        "Carruurta baan cuno.",
        "Carruurta baan cunayo.",
        "Carruurta baan cunaan.",
    ):
        assert analyze_subject_focus_negative(sentence).recognized is False


def test_future_and_habitual_negative_focus_remain_separate_pending_stages():
    for sentence in (
        "Carruurta baan cuni doonin.",
        "Carruurta baan cuni jirin.",
    ):
        assert analyze_subject_focus_negative(sentence).recognized is False


def test_cli_accepts_reviewed_negative_focus_and_reports_only_safe_case_conflict():
    assert _run_checker("Cali baan bixin.") == NO_FINDINGS
    assert _run_checker("Carruurta baan cunin.") == NO_FINDINGS
    assert _run_checker("Carruurta baan maanta cunin.") == NO_FINDINGS
    assert _run_checker("Gabadha ayaan imanayn.") == NO_FINDINGS

    output = _run_checker("Carruurtu baan cunin.")
    assert "possible definite-noun subject-case conflict" in output
    assert "reviewed subject-form candidate is 'Carruurta'" in output
    assert "GRAM-SUBJFOCUS-NEG-003" in output
    assert "Safe corrected text:\nCarruurtu baan cunin." in output


def test_existing_affirmative_focus_and_ordinary_subject_case_stay_separate():
    assert analyze_noun_subject_case("Wiilka ayaa yimid.").agrees is True
    assert analyze_noun_subject_case("Wiilku ayaa yimid.").agrees is False
    assert analyze_noun_subject_case("Wiilku wuu yimid.").agrees is True
    assert analyze_noun_subject_case("Wiilka wuu yimid.").agrees is False
