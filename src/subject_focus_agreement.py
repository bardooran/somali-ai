"""Conservative agreement analysis for reviewed Somali subject-focus clauses.

This module distinguishes true subject focus from the non-subject/object-focus
patterns handled elsewhere. Initial executable scope is exact reviewed evidence
for::

    Cali baa yimid.
    Maryan baa qososhay.

Bare ``baa`` is licensed because the noun immediately before it is itself the
focused subject. Proper-name person/gender is never guessed: only subjects
listed in the reviewed rule data are judged. Predicate agreement comes from the
shared exact finite-morphology bridge when available, with exact sentence-level
fallback evidence for reviewed surfaces such as ``qososhay``. No unseen forms
are derived and no automatic rewrite is produced.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from src.reviewed_finite_verb import analyze_reviewed_finite_verb

RULE_PATH = Path("rules/grammar/subject_focus_agreement.jsonl")
TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)


@dataclass(frozen=True)
class SubjectFocusAgreementAnalysis:
    recognized: bool
    subject: str | None = None
    particle: str | None = None
    predicate: str | None = None
    expected_person: str | None = None
    predicate_persons: tuple[str, ...] = ()
    agrees: bool | None = None
    evidence: str | None = None
    rule_id: str = "GRAM-SUBJFOCUS-001"
    note: str = ""


def _load_records() -> list[dict]:
    if not RULE_PATH.exists():
        return []
    return [
        json.loads(line)
        for line in RULE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _subject_profiles() -> dict[str, tuple[str, str]]:
    profiles: dict[str, tuple[str, str]] = {}
    for record in _load_records():
        if record.get("category") != "subject_focus_baa":
            continue
        subject = record.get("subject")
        person = record.get("subject_person")
        if isinstance(subject, str) and isinstance(person, str):
            profiles[subject.casefold()] = (person, record.get("id", "GRAM-SUBJFOCUS-001"))
    return profiles


def _reviewed_predicate_persons(surface: str) -> tuple[str, ...]:
    persons: list[str] = []
    for record in _load_records():
        if record.get("category") != "reviewed_subject_focus_predicate_surface":
            continue
        if str(record.get("surface", "")).casefold() != surface.casefold():
            continue
        person = record.get("person")
        if isinstance(person, str) and person not in persons:
            persons.append(person)
    return tuple(persons)


def analyze_subject_focus_agreement(sentence: str) -> SubjectFocusAgreementAnalysis:
    """Analyze exact reviewed ``FOCUSED_SUBJECT + baa + predicate`` agreement.

    Only an immediately adjacent reviewed proper-name subject plus bare ``baa``
    enters this rule. A known exact finite verb is checked through shared
    morphology; otherwise an exact reviewed sentence-level predicate surface may
    supply person evidence. Unknown predicates remain unjudged rather than being
    guessed.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 3:
        return SubjectFocusAgreementAnalysis(recognized=False)

    subject, particle, predicate = tokens[0], tokens[1], tokens[2]
    if particle.casefold() != "baa":
        return SubjectFocusAgreementAnalysis(recognized=False)

    profile = _subject_profiles().get(subject.casefold())
    if profile is None:
        return SubjectFocusAgreementAnalysis(recognized=False)
    expected_person, rule_id = profile

    finite = analyze_reviewed_finite_verb(predicate)
    if finite.recognized and finite.persons:
        agrees = expected_person in finite.persons
        return SubjectFocusAgreementAnalysis(
            recognized=True,
            subject=subject,
            particle=particle,
            predicate=predicate,
            expected_person=expected_person,
            predicate_persons=finite.persons,
            agrees=agrees,
            evidence="exact_reviewed_finite_morphology",
            rule_id=rule_id,
            note=(
                "The noun immediately before baa is the reviewed focused subject. Bare baa is "
                "licensed in this subject-focus structure; agreement is checked against exact "
                "reviewed finite morphology and no subject clitic is required by this rule."
            ),
        )

    reviewed_persons = _reviewed_predicate_persons(predicate)
    if reviewed_persons:
        agrees = expected_person in reviewed_persons
        return SubjectFocusAgreementAnalysis(
            recognized=True,
            subject=subject,
            particle=particle,
            predicate=predicate,
            expected_person=expected_person,
            predicate_persons=reviewed_persons,
            agrees=agrees,
            evidence="exact_native_reviewed_sentence_surface",
            rule_id=rule_id,
            note=(
                "The noun immediately before baa is the reviewed focused subject. Predicate "
                "person comes only from an exact native-reviewed sentence surface; no lemma or "
                "unseen paradigm is inferred."
            ),
        )

    return SubjectFocusAgreementAnalysis(
        recognized=True,
        subject=subject,
        particle=particle,
        predicate=predicate,
        expected_person=expected_person,
        agrees=None,
        evidence="predicate_unreviewed",
        rule_id=rule_id,
        note=(
            "The reviewed subject-focus frame is recognized, but the predicate lacks exact "
            "reviewed person evidence. It is left unjudged rather than guessed."
        ),
    )
