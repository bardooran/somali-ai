import subprocess
import sys

from src.vocabulary import lookup_word
from src.morphology_candidates import analyze_surface_form
from src.noun_number_verb_agreement import analyze_noun_number_verb_agreement


HEADWORDS = {
    "jabi": "f.g2",
    "adkee": "f.g2",
    "cidlee": "f.g2",
    "jabso": "f.g3",
    "adkow": "f.mg3",
    "yarow": "f.mg3",
}


def test_class2_and_3_headwords_are_in_reviewed_vocabulary():
    for lemma, source_pos in HEADWORDS.items():
        result = lookup_word(lemma)
        assert result.known
        assert any(entry.source_pos == source_pos for entry in result.exact_entries)
        assert all(entry.raw.get("english_gloss") is None for entry in result.exact_entries)


def _persons(surface: str) -> set[str]:
    persons: set[str] = set()
    for candidate in analyze_surface_form(surface):
        person = candidate.features.get("person")
        if isinstance(person, str):
            persons.add(person)
        possible = candidate.features.get("possible_persons")
        if isinstance(possible, list):
            persons.update(possible)
    return persons


def test_reviewed_class2_plural_past_forms_have_3pl_person():
    for surface in ("jabiyeen", "adkeeyeen", "cidleeyeen"):
        assert _persons(surface) == {"3pl"}


def test_reviewed_class3_plural_past_forms_have_3pl_person():
    for surface in ("yaraadeen", "adkaadeen", "jabsadeen"):
        assert _persons(surface) == {"3pl"}


def test_class2_singular_compatible_past_forms_exclude_3pl():
    expected = {
        "jabiyay": {"1sg", "3sg_m"},
        "adkeeyay": {"1sg", "3sg_m"},
        "cidleeyay": {"1sg", "3sg_m"},
    }
    for surface, persons in expected.items():
        assert _persons(surface) == persons
        assert "3pl" not in persons


def test_class3_singular_compatible_past_forms_exclude_3pl():
    expected = {
        "yaraaday": {"1sg", "3sg_m"},
        "adkaaday": {"1sg", "3sg_m"},
        "jabsaday": {"1sg", "3sg_m"},
    }
    for surface, persons in expected.items():
        assert _persons(surface) == persons
        assert "3pl" not in persons


def test_plural_noun_agreement_generalizes_into_class2():
    pairs = (
        ("Macallimiintu way jabiyeen albaabka.", "Macallimiintu way jabiyay albaabka."),
        ("Macallimiintu way adkeeyeen imtixaanka.", "Macallimiintu way adkeeyay imtixaanka."),
        ("Macallimiintu way cidleeyeen guriga.", "Macallimiintu way cidleeyay guriga."),
    )
    for correct, wrong in pairs:
        accepted = analyze_noun_number_verb_agreement(correct)
        rejected = analyze_noun_number_verb_agreement(wrong)
        assert accepted.recognized and accepted.agrees is True
        assert accepted.verb_persons == ("3pl",)
        assert rejected.recognized and rejected.agrees is False
        assert "3pl" not in rejected.verb_persons


def test_plural_noun_agreement_generalizes_into_class3():
    pairs = (
        ("Miisasku way yaraadeen.", "Miisasku way yaraaday."),
        ("Macallimiintu way adkaadeen.", "Macallimiintu way adkaaday."),
        ("Macallimiintu way jabsadeen tukaan.", "Macallimiintu way jabsaday tukaan."),
    )
    for correct, wrong in pairs:
        accepted = analyze_noun_number_verb_agreement(correct)
        rejected = analyze_noun_number_verb_agreement(wrong)
        assert accepted.recognized and accepted.agrees is True
        assert accepted.verb_persons == ("3pl",)
        assert rejected.recognized and rejected.agrees is False
        assert "3pl" not in rejected.verb_persons


def test_evidence_strength_is_preserved_per_surface():
    assert analyze_surface_form("adkeeyeen")[0].evidence_type == "explicit_source_sentence"
    assert analyze_surface_form("cidleeyeen")[0].evidence_type == "explicit_source_sentence"
    assert analyze_surface_form("yaraadeen")[0].evidence_type == "explicit_source_sentence"
    assert analyze_surface_form("jabiyeen")[0].evidence_type == "qaamuus_class_pattern_plus_uploaded_corpus_attestation"
    assert analyze_surface_form("adkaadeen")[0].evidence_type == "qaamuus_class_pattern_plus_uploaded_corpus_attestation"


def run_cli(text: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", text],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def test_live_cli_reports_class2_and_3_plural_conflicts_without_autofix():
    for text in (
        "Macallimiintu way adkeeyay imtixaanka.",
        "Macallimiintu way jabsaday tukaan.",
        "Miisasku way yaraaday.",
    ):
        output = run_cli(text)
        assert "possible plural noun-subject/verb agreement conflict" in output
        assert "Expected 3pl." in output
        assert "Safe corrected text:" in output
        assert text in output


def test_live_cli_accepts_reviewed_class2_and_3_plural_forms():
    for text in (
        "Macallimiintu way adkeeyeen imtixaanka.",
        "Macallimiintu way jabsadeen tukaan.",
        "Miisasku way yaraadeen.",
    ):
        output = run_cli(text)
        assert "possible plural noun-subject/verb agreement conflict" not in output
