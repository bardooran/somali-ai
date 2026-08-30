"""Conservative noun-number to finite-verb agreement analysis.

This layer only judges a sentence when two independent pieces of reviewed
evidence are available:

1. the explicit noun subject is analyzed as plural by native review or reviewed
   noun morphology; and
2. the finite verb surface has an exact reviewed morphology analysis with
   person information.

Unknown noun number, unknown verbs, and non-finite forms remain unjudged. This
keeps the analyzer from inventing productive verb suffix rules before they are
validated across more Somali paradigms.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.morphology_candidates import MorphologyCandidate, analyze_surface_form
from src.noun_gender_agreement import infer_subject_number
from src.noun_subject_case import PERSONAL_PRONOUN_FORMS

TOKEN_RE = re.compile(r"[^\W\d_]+", flags=re.UNICODE)
STATEMENT_CLITICS = {"wuu", "way"}
MAX_VERB_GAP = 3
FINITE_ANALYSIS_TYPES = {"finite_verb", "native_reviewed_finite_verb_surface"}


@dataclass(frozen=True)
class NounNumberVerbAgreementAnalysis:
    recognized: bool
    subject: str | None = None
    subject_number: str | None = None
    number_evidence: str | None = None
    clitic: str | None = None
    verb: str | None = None
    verb_persons: tuple[str, ...] = ()
    agrees: bool | None = None
    expected_person: str | None = None
    rule_id: str = "GRAM-NNUMVERB-001"
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


def analyze_noun_number_verb_agreement(sentence: str) -> NounNumberVerbAgreementAnalysis:
    """Check reviewed plural noun subjects against reviewed finite verb person.

    Current scope is an explicit ``<noun> wuu/way ... <verb>`` statement. The
    verb may occur within a short local window after the clitic. A reviewed 3pl
    analysis is accepted. A reviewed verb whose available persons exclude 3pl
    is a review-only conflict. If the verb has no reviewed person analysis, the
    sentence remains unjudged.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 3:
        return NounNumberVerbAgreementAnalysis(recognized=False)

    for index in range(len(tokens) - 2):
        subject = tokens[index]
        clitic = tokens[index + 1]
        if subject.casefold() in PERSONAL_PRONOUN_FORMS:
            continue
        if clitic.casefold() not in STATEMENT_CLITICS:
            continue

        number, number_evidence = infer_subject_number(subject)
        if number != "plural":
            continue

        upper = min(len(tokens), index + 2 + MAX_VERB_GAP)
        for verb in tokens[index + 2 : upper]:
            persons = _reviewed_verb_persons(verb)
            if not persons:
                continue

            agrees = "3pl" in persons
            return NounNumberVerbAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_number="plural",
                number_evidence=number_evidence,
                clitic=clitic,
                verb=verb,
                verb_persons=persons,
                agrees=agrees,
                expected_person="3pl",
                note=(
                    "The noun subject has reviewed plural-number evidence and the "
                    "verb has an exact reviewed finite-person analysis. No suffix-only "
                    "verb inference or automatic rewrite is used."
                ),
            )

        return NounNumberVerbAgreementAnalysis(
            recognized=True,
            subject=subject,
            subject_number="plural",
            number_evidence=number_evidence,
            clitic=clitic,
            agrees=None,
            expected_person="3pl",
            note=(
                "Plural subject recognized, but no exact reviewed finite verb person "
                "was found in the local window; verb agreement remains unjudged."
            ),
        )

    return NounNumberVerbAgreementAnalysis(recognized=False)
