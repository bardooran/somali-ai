"""Conservative agreement analysis for reviewed Somali subject-focus clauses.

True subject focus is kept separate from non-subject/object focus. Proper names
are licensed only from exact reviewed profiles. Common nouns are licensed only
when their absolute focus form can be paired with an already reviewed ``-u``
subject form. Affirmative simple-past predicates are interpreted through the
source-backed restrictive/reduced focus paradigm; other tenses remain unjudged
unless an exact subject-focus sentence surface has been reviewed directly.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from src.noun_gender_agreement import REVIEWED_PLURAL_FORMS, REVIEWED_SINGULAR_FORMS
from src.noun_subject_case import expected_subject_form
from src.subject_focus_restrictive import analyze_subject_focus_restrictive

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


def _common_noun_profile(surface: str) -> tuple[str, str, str] | None:
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
        return "3pl", "GRAM-SUBJFOCUS-006", "reviewed_common_noun_plural_absolute_pair"
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

    Exact sentence-level subject-focus evidence has first priority. Otherwise,
    known simple-past finite surfaces are interpreted through the restrictive
    paradigm. Full ordinary finite agreement is never used as a fallback in
    subject focus, because reduced agreement can differ in person/number.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 3:
        return SubjectFocusAgreementAnalysis(recognized=False)

    subject, particle, predicate = tokens[0], tokens[1], tokens[2]
    particle_key = particle.casefold()

    profile = _subject_profiles().get(subject.casefold())
    subject_evidence = "exact_reviewed_subject_profile"
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
        expected_person, rule_id, subject_evidence = common

    # Exact native-reviewed subject-focus predicate surfaces outrank any broader
    # paradigm inference. This preserves examples such as Maryan baa qososhay
    # without deriving an unseen qos- paradigm.
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
                "person comes only from an exact native-reviewed subject-focus surface; no "
                "unseen paradigm is inferred."
            ),
        )

    restrictive = analyze_subject_focus_restrictive(predicate, expected_person)
    if restrictive.covered:
        return SubjectFocusAgreementAnalysis(
            recognized=True,
            subject=subject,
            particle=particle,
            predicate=predicate,
            expected_person=expected_person,
            predicate_persons=restrictive.contextual_persons,
            agrees=restrictive.agrees,
            evidence=f"{subject_evidence}+restrictive_simple_past_exact_morphology",
            rule_id=rule_id,
            note=(
                "Focused subjects use the reviewed restrictive/reduced simple-past paradigm. "
                "The predicate surface itself comes from exact reviewed finite morphology, but "
                "its person interpretation is contextual: 2sg, 2pl and 3pl use the ordinary "
                "3sg-masculine-shaped past form; 3sg feminine remains distinct. No automatic "
                "rewrite."
            ),
        )

    if restrictive.recognized:
        return SubjectFocusAgreementAnalysis(
            recognized=True,
            subject=subject,
            particle=particle,
            predicate=predicate,
            expected_person=expected_person,
            agrees=None,
            evidence=f"{subject_evidence}+restrictive_paradigm_not_yet_modeled_for_tense",
            rule_id=rule_id,
            note=(
                "The subject-focus frame and finite predicate are recognized, but this "
                "tense/aspect is outside the currently modeled restrictive paradigm. It is "
                "left unjudged instead of reusing ordinary full agreement."
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
            "reviewed finite or sentence-level evidence. It is left unjudged rather than guessed."
        ),
    )
