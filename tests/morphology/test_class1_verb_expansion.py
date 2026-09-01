import subprocess
import sys

from src.vocabulary import lookup_word
from src.morphology_candidates import analyze_surface_form
from src.noun_number_verb_agreement import analyze_noun_number_verb_agreement


HEADWORDS = {
    "tag": (2, "f.g/mg1"),
    "qor": (None, "f.g1"),
    "xir": (2, "f.g1"),
    "jab": (3, "f.mg1"),
}


def test_everyday_class1_headwords_are_in_the_reviewed_vocabulary():
    for lemma, (homograph_index, source_pos) in HEADWORDS.items():
        result = lookup_word(lemma)
        assert result.known
        entries = [entry for entry in result.exact_entries if entry.source_pos == source_pos]
        assert entries
        assert any(entry.homograph_index == homograph_index for entry in entries)
        assert all(entry.raw.get("english_gloss") is None for entry in entries)


def test_new_class1_past_surfaces_link_to_expected_lemmas_and_persons():
    expected = {
        "tagay": ("tag", {"1sg", "3sg_m"}),
        "tagtay": ("tag", {"2sg", "3sg_f"}),
        "tageen": ("tag", {"3pl"}),
        "qoray": ("qor", {"1sg", "3sg_m"}),
        "qortay": ("qor", {"2sg", "3sg_f"}),
        "qoreen": ("qor", {"3pl"}),
        "xiray": ("xir", {"1sg", "3sg_m"}),
        "xirtay": ("xir", {"2sg", "3sg_f"}),
        "xireen": ("xir", {"3pl"}),
        "jabeen": ("jab", {"3pl"}),
    }
    for surface, (lemma, persons) in expected.items():
        candidates = analyze_surface_form(surface)
        assert candidates
        candidate = next(item for item in candidates if item.lemma == lemma)
        observed = set(candidate.features.get("possible_persons", []))
        if candidate.features.get("person"):
            observed.add(candidate.features["person"])
        assert observed == persons
        assert candidate.analysis_type == "finite_verb"


def test_plural_noun_agreement_generalizes_across_four_class1_lemmas():
    pairs = (
        ("Macallimiintu way tageen.", "Macallimiintu way tagay."),
        ("Macallimiintu way qoreen.", "Macallimiintu way qoray."),
        ("Macallimiintu way xireen.", "Macallimiintu way xiray."),
        ("Miisasku way jabeen.", "Miisasku way jabay."),
    )
    for correct, wrong in pairs:
        accepted = analyze_noun_number_verb_agreement(correct)
        rejected = analyze_noun_number_verb_agreement(wrong)
        assert accepted.recognized and accepted.agrees is True
        assert accepted.verb_persons == ("3pl",)
        assert rejected.recognized and rejected.agrees is False
        assert "3pl" not in rejected.verb_persons


def test_expansion_preserves_evidence_strength_difference():
    tageen = analyze_surface_form("tageen")[0]
    qoreen = analyze_surface_form("qoreen")[0]
    xireen = analyze_surface_form("xireen")[0]
    jabeen = analyze_surface_form("jabeen")[0]
    assert tageen.evidence_type == "explicit_source_sentence"
    assert qoreen.evidence_type == "qaamuus_class_pattern_plus_uploaded_corpus_attestation"
    assert xireen.evidence_type == "qaamuus_class_pattern_plus_uploaded_corpus_attestation"
    assert jabeen.evidence_type == "qaamuus_class_pattern_plus_uploaded_corpus_attestation"


def run_cli(text: str) -> str:
    completed = subprocess.run(
        [sys.executable, "check.py", text],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def test_live_cli_reports_cross_family_plural_verb_conflicts_without_rewriting():
    for text in (
        "Macallimiintu way tagay.",
        "Macallimiintu way qoray.",
        "Macallimiintu way xiray.",
        "Miisasku way jabay.",
    ):
        output = run_cli(text)
        assert "possible plural noun-subject/verb agreement conflict" in output
        assert "Expected 3pl." in output
        assert "Safe corrected text:" in output
        assert text in output


def test_live_cli_accepts_reviewed_class1_plural_forms():
    for text in (
        "Macallimiintu way tageen.",
        "Macallimiintu way qoreen.",
        "Macallimiintu way xireen.",
        "Miisasku way jabeen.",
    ):
        output = run_cli(text)
        assert "possible plural noun-subject/verb agreement conflict" not in output
