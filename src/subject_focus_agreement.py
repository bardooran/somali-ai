"""Conservative agreement analysis for reviewed Somali subject-focus clauses.

True subject focus is kept separate from non-subject/object focus. Proper names
are licensed only from exact reviewed profiles. Common nouns are licensed only
when their absolute focus form can be paired with an already reviewed ``-u``
subject form. Focused plurals are recognized but left unjudged until the
restrictive/reduced focus-verb paradigm is modeled explicitly.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from src.noun_gender_agreement import REVIEWED_PLURAL_FORMS, REVIEWED_SINGULAR_FORMS
from src.noun_subject_case import expected_subject_form
from src.reviewed_finite_verb import analyze_reviewed_finite_verb

RULE_PATH = Path("rules/grammar/subject_focus_agreement.jsonl")
TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)
FOCUS_PARTICLES = {"baa", "ayaa"}


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


def _subject_profiles() -> dict[str, tuple[str, str, tuple[str, ...]]]:
    profiles: dict[str, tuple[str, str, tuple[str, ...]]] = {}
    for record in _load_records():
        if record.get("category") not in {"subject_focus_particle", "subject_focus_baa"}:
            continue
        subject = record.get("subject")
        person = record.get("subject_person")
        particles = record.get("focus_particles")
        if not isinstance(particles, list):
            legacy_particle = record.get("focus_particle")
            particles = [legacy_particle] if isinstance(legacy_particle, str) else []
        normalized_particles = tuple(
            particle.casefold() for particle in particles if isinstance(particle, str)
        )
        if isinstance(subject, str) and isinstance(person, str) and normalized_particles:
            profiles[subject.casefold()] = (
                person,
                record.get("id", "GRAM-SUBJFOCUS-001"),
                normalized_particles,
            )
    return profiles


def _common_noun_profile(surface: str) -> tuple[str | None, str, str] | None:
    """Map an absolute focus form to exact reviewed subject evidence only."""
    reviewed_subject = expected_subject_form(surface)
    if reviewed_subject is None:
        return None
    folded = reviewed_subject.casefold()

    gender = REVIEWED_SINGULAR_FORMS.get(folded)
    if gender == "masculine":
        return "3sg_m", "GRAM-SUBJFOCUS-005", "reviewed_common_noun_absolute_pair"
    if gender == "feminine":
        return "3sg_f", "GRAM-SUBJFOCUS-005", "reviewed_common_noun_absolute_pair"
    if folded in REVIEWED_PLURAL_FORMS:
        return None, "GRAM-SUBJFOCUS-006", "plural_focus_restrictive_paradigm_pending"
    return None


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
    """Analyze reviewed ``FOCUSED_SUBJECT + baa/ayaa + predicate`` agreement.

    Proper names require an exact rule profile. Common nouns require an absolute
    form whose paired ``-u`` subject surface is already explicitly reviewed.
    Singular common nouns can therefore reuse exact 3sg masculine/feminine
    finite morphology. Reviewed plurals are recognized but left unjudged because
    focused subjects use a restrictive verb paradigm that is not modeled yet.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 3:
        return SubjectFocusAgreementAnalysis(recognized=False)

    subject, particle, predicate = tokens[0], tokens[1], tokens[2]
    particle_key = particle.casefold()

    profile = _subject_profiles().get(subject.casefold())
    evidence = "exact_reviewed_subject_profile"
    if profile is not None:
        expected_person, rule_id, allowed_particles = profile
        if particle_key not in allowed_particles:
            return SubjectFocusAgreementAnalysis(recognized=False)
    else:
        if particle_key not in FOCUS_PARTICLES:
            return SubjectFocusAgreementAnalysis(recognized=False)
        common = _common_noun_profile(subject)
        if common is None:
            return SubjectFocusAgreementAnalysis(recognized=False)
        expected_person, rule_id, evidence = common
        if expected_person is None:
            return SubjectFocusAgreementAnalysis(
                recognized=True,
                subject=subject,
                particle=particle,
                predicate=predicate,
                expected_person=None,
                agrees=None,
                evidence=evidence,
                rule_id=rule_id,
                note=(
                    "The common-noun focused subject is linked to exact reviewed plural noun "
                    "evidence, but focused subjects use a restrictive/reduced verb paradigm. "
                    "Plural predicate agreement is therefore left unjudged until that paradigm "
                    "is modeled explicitly."
                ),
            )

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
            evidence=(
                "exact_reviewed_finite_morphology"
                if evidence == "exact_reviewed_subject_profile"
                else f"{evidence}+exact_reviewed_finite_morphology"
            ),
            rule_id=rule_id,
            note=(
                "The noun immediately before bare baa/ayaa is the focused subject. Common-noun "
                "focus uses the reviewed absolute/non-subject noun surface, while predicate "
                "agreement is checked only against exact reviewed finite morphology."
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
                "The noun immediately before bare baa/ayaa is the focused subject. Predicate "
                "person comes only from an exact native-reviewed surface; no unseen paradigm is "
                "inferred."
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
