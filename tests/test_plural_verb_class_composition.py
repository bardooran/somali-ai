"""Cross-class composition tests for plural noun + finite-verb agreement.

These sentences are new combinations of independently reviewed noun-number and
verb-person evidence. The checker must not need a memorized whole sentence, and
it still must not invent unknown verb forms.
"""

from src.morphology_candidates import analyze_surface_form
from src.noun_number_verb_agreement import analyze_noun_number_verb_agreement


# subject, accepted 3pl verb, rejected singular-compatible verb, optional tail
CROSS_CLASS_CASES = (
    ("miisasku", "jabeen", "jabay", ""),
    ("macallimiintu", "tageen", "tagay", ""),
    ("macallimiintu", "qoreen", "qoray", "warqadda"),
    ("macallimiintu", "adkeeyeen", "adkeeyay", "albaabka"),
    ("waddooyinku", "adkaadeen", "adkaaday", ""),
    ("daawooyinku", "yaraadeen", "yaraaday", ""),
)


def _sentence(subject: str, verb: str, tail: str) -> str:
    extra = f" {tail}" if tail else ""
    return f"{subject} way {verb}{extra}."


def test_cross_class_correct_verbs_have_reviewed_3pl_evidence():
    for _subject, correct, _wrong, _tail in CROSS_CLASS_CASES:
        candidates = analyze_surface_form(correct)
        assert candidates
        assert any(
            candidate.features.get("part_of_speech") == "verb"
            and candidate.features.get("person") == "3pl"
            for candidate in candidates
        )


def test_cross_class_negative_controls_exclude_3pl():
    for _subject, _correct, wrong, _tail in CROSS_CLASS_CASES:
        candidates = analyze_surface_form(wrong)
        assert candidates
        persons = set()
        for candidate in candidates:
            person = candidate.features.get("person")
            if isinstance(person, str):
                persons.add(person)
            persons.update(candidate.features.get("possible_persons", []))
        assert persons
        assert "3pl" not in persons


def test_plural_agreement_composes_across_class_i_ii_and_iii_verbs():
    for subject, correct, wrong, tail in CROSS_CLASS_CASES:
        accepted = analyze_noun_number_verb_agreement(_sentence(subject, correct, tail))
        rejected = analyze_noun_number_verb_agreement(_sentence(subject, wrong, tail))

        assert accepted.recognized
        assert accepted.subject_number == "plural"
        assert accepted.verb == correct
        assert accepted.verb_persons == ("3pl",)
        assert accepted.agrees is True

        assert rejected.recognized
        assert rejected.subject_number == "plural"
        assert rejected.verb == wrong
        assert "3pl" not in rejected.verb_persons
        assert rejected.agrees is False


def test_unknown_lookalike_verbs_still_remain_unjudged():
    # Similar-looking endings must not become a productive suffix guess.
    for subject in ("miisasku", "macallimiintu", "waddooyinku"):
        result = analyze_noun_number_verb_agreement(f"{subject} way tijaabeenxyz.")
        assert result.recognized
        assert result.verb is None
        assert result.agrees is None
