"""Conservative singular noun-to-finite-verb agreement analysis.

This layer combines independently reviewed noun gender/number evidence with
exact reviewed finite-verb person analyses. It does not infer productive verb
suffix rules and does not rewrite text automatically.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.morphology_candidates import MorphologyCandidate, analyze_surface_form
from src.noun_gender_agreement import infer_subject_gender, infer_subject_number
from src.noun_subject_case import PERSONAL_PRONOUN_FORMS

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)
STATEMENT_CLITICS = {"wuu", "way"}
MAX_VERB_GAP = 3
FINITE_ANALYSIS_TYPES = {"finite_verb", "native_reviewed_finite_verb_surface"}


@dataclass(frozen=True)
class NounSingularVerbAgreementAnalysis:
    recognized: bool
    subject: str | None = None
    subject_gender: str | None = None
    subject_number: str | None = None
    clitic: str | None = None
    verb: str | None = None
    verb_persons: tuple[str, ...] = ()
    expected_person: str | None = None
    agrees: bool | None = None
    rule_id: str = "GRAM-NSINGVERB-001"
    note: str = ""


def _finite_persons(candidate: MorphologyCandidate) -> tuple[str, ...]:
    if candidate.features.get("part_of_speech") != "verb":
        return ()
    if candidate.analysis_type not in FINITE_ANALYSIS_TYPES:
        return ()

    person = candidate.features.get("person")
    if isinstance(person, str):
        return (person,)

    possible = candidate.features.get("possible_persons")
    if isinstance(possible, list):
        return tuple(str(item) for item in possible)
    return ()


def _reviewed_verb_persons(form: str) -> tuple[str, ...]:
    persons: list[str] = []
    for candidate in analyze_surface_form(form):
        for person in _finite_persons(candidate):
            if person not in persons:
                persons.append(person)
    return tuple(persons)


def analyze_noun_singular_verb_agreement(sentence: str) -> NounSingularVerbAgreementAnalysis:
    """Check singular noun gender against an exact reviewed finite verb form.

    Current scope is ``<noun> wuu/way ... <verb>``. Masculine singular subjects
    require a reviewed 3sg_m-compatible finite verb; feminine singular subjects
    require 3sg_f compatibility. Unknown verb forms remain unjudged.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 3:
        return NounSingularVerbAgreementAnalysis(recognized=False)

    for index in range(len(tokens) - 2):
        subject = tokens[index]
        clitic = tokens[index + 1]
        if subject.casefold() in PERSONAL_PRONOUN_FORMS:
            continue
        if clitic.casefold() not in STATEMENT_CLITICS:
            continue

        number, number_evidence = infer_subject_number(subject)
        gender, gender_evidence = infer_subject_gender(subject)
        if number != "singular" or gender not in {"masculine", "feminine"}:
            continue

        expected_person = "3sg_m" if gender == "masculine" else "3sg_f"
        upper = min(len(tokens), index + 2 + MAX_VERB_GAP)
        for verb in tokens[index + 2 : upper]:
            persons = _reviewed_verb_persons(verb)
            if not persons:
                continue

            return NounSingularVerbAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_gender=gender,
                subject_number=number,
                clitic=clitic,
                verb=verb,
                verb_persons=persons,
                expected_person=expected_person,
                agrees=expected_person in persons,
                note=(
                    f"Gender evidence: {gender_evidence}. Number evidence: {number_evidence}. "
                    "The verb decision uses only exact reviewed finite-person morphology; "
                    "unknown forms are not guessed."
                ),
            )

        return NounSingularVerbAgreementAnalysis(
            recognized=True,
            subject=subject,
            subject_gender=gender,
            subject_number=number,
            clitic=clitic,
            expected_person=expected_person,
            agrees=None,
            note=(
                f"Gender evidence: {gender_evidence}. Number evidence: {number_evidence}. "
                "No exact reviewed finite verb person was found; agreement remains unjudged."
            ),
        )

    return NounSingularVerbAgreementAnalysis(recognized=False)
