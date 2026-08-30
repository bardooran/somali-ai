"""Subject-aware agreement for reviewed Somali negative finite verbs.

This layer handles exact ``<noun> ma <negative finite verb>`` constructions.
It keeps negative morphology separate from affirmative morphology and preserves
person neutralization where the reviewed paradigm explicitly has it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.morphology_candidates import (
    MorphologyCandidate,
    analyze_surface_form,
    reviewed_candidates_for_lemma,
)
from src.noun_gender_agreement import infer_subject_gender, infer_subject_number
from src.noun_subject_case import PERSONAL_PRONOUN_FORMS
from src.reviewed_finite_verb import ReviewedFiniteVerbAnalysis, analyze_reviewed_finite_verb

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)


@dataclass(frozen=True)
class NegativeFiniteAgreementAnalysis:
    recognized: bool
    subject: str | None = None
    subject_number: str | None = None
    subject_gender: str | None = None
    verb: str | None = None
    verb_lemma: str | None = None
    verb_persons: tuple[str, ...] = ()
    tense_aspect: str | None = None
    polarity: str | None = None
    expected_person: str | None = None
    person_neutralized: bool = False
    agrees: bool | None = None
    rule_id: str = "GRAM-NEGFIN-001"
    note: str = ""


def _expected_person(subject: str) -> tuple[str | None, str | None, str | None]:
    number, _ = infer_subject_number(subject)
    gender, _ = infer_subject_gender(subject)
    if number == "plural":
        return "3pl", number, gender
    if number == "singular" and gender == "masculine":
        return "3sg_m", number, gender
    if number == "singular" and gender == "feminine":
        return "3sg_f", number, gender
    return None, number, gender


def _candidate_persons(candidate: MorphologyCandidate) -> tuple[str, ...]:
    person = candidate.features.get("person")
    if isinstance(person, str):
        return (person,)
    possible = candidate.features.get("possible_persons")
    if isinstance(possible, list):
        return tuple(str(item) for item in possible)
    return ()


def _negative_candidate(form: str) -> MorphologyCandidate | None:
    for candidate in analyze_surface_form(form):
        if candidate.analysis_type != "negative_finite_verb":
            continue
        features = candidate.features
        if features.get("construction_context") != "ma":
            continue
        if features.get("polarity") != "negative":
            continue
        return candidate
    return None


def _has_matching_reviewed_negative_paradigm(
    affirmative: ReviewedFiniteVerbAnalysis,
) -> bool:
    """Return true only when the same lemma and tense/aspect has negative evidence.

    A reviewed affirmative token after ``ma`` is not enough by itself to prove a
    polarity error. Some irregular paradigms have incomplete negative evidence.
    This guard prevents the checker from turning missing evidence into a rule.
    """
    affirmative_aspects = set(affirmative.tense_aspects)
    if not affirmative_aspects:
        return False

    for lemma in affirmative.lemmas:
        for candidate in reviewed_candidates_for_lemma(lemma, "negative_finite_verb"):
            negative_aspect = candidate.features.get("tense_aspect")
            if isinstance(negative_aspect, str) and negative_aspect in affirmative_aspects:
                return True
    return False


def analyze_negative_finite_agreement(sentence: str) -> NegativeFiniteAgreementAnalysis:
    """Check a reviewed noun subject against an exact ``ma + verb`` paradigm.

    If an exact negative finite form is found, person agreement is checked from
    its reviewed features. If the form is explicitly person-neutralized, it is
    accepted for any safely resolved third-person noun subject. If ``ma`` is
    followed by an exact reviewed affirmative finite form, a polarity conflict
    is reported only when a reviewed negative paradigm exists for the same lemma
    and tense/aspect. Otherwise the construction remains unjudged. Unknown forms
    are never generated or guessed.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 3:
        return NegativeFiniteAgreementAnalysis(recognized=False)

    for index in range(len(tokens) - 2):
        subject = tokens[index]
        if subject.casefold() in PERSONAL_PRONOUN_FORMS:
            continue
        if tokens[index + 1].casefold() != "ma":
            continue

        expected_person, number, gender = _expected_person(subject)
        if expected_person is None:
            continue

        verb = tokens[index + 2]
        candidate = _negative_candidate(verb)
        if candidate is not None:
            persons = _candidate_persons(candidate)
            neutralized = bool(candidate.features.get("person_neutralized", False))
            agrees = True if neutralized else expected_person in persons
            return NegativeFiniteAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_number=number,
                subject_gender=gender,
                verb=verb,
                verb_lemma=candidate.lemma,
                verb_persons=persons,
                tense_aspect=candidate.features.get("tense_aspect"),
                polarity="negative",
                expected_person=expected_person,
                person_neutralized=neutralized,
                agrees=agrees,
                note=(
                    "Exact reviewed negative morphology is used in ma context. "
                    + (
                        "This paradigm explicitly neutralizes person on the negative form."
                        if neutralized
                        else "Agreement is checked from the reviewed negative person features."
                    )
                ),
            )

        affirmative = analyze_reviewed_finite_verb(verb)
        if affirmative.recognized:
            matching_negative = _has_matching_reviewed_negative_paradigm(affirmative)
            return NegativeFiniteAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_number=number,
                subject_gender=gender,
                verb=verb,
                verb_lemma=affirmative.lemmas[0] if affirmative.lemmas else None,
                verb_persons=affirmative.persons,
                tense_aspect=affirmative.tense_aspects[0] if affirmative.tense_aspects else None,
                polarity="affirmative",
                expected_person=expected_person,
                agrees=False if matching_negative else None,
                note=(
                    "The token after ma is an exact reviewed affirmative finite form and a "
                    "reviewed negative paradigm exists for the same lemma and tense/aspect; "
                    "review required."
                    if matching_negative
                    else
                    "The token after ma is an exact reviewed affirmative finite form, but no "
                    "reviewed negative paradigm is available for the same lemma and tense/aspect. "
                    "The construction is left unjudged rather than treating missing evidence as an error."
                ),
            )

        return NegativeFiniteAgreementAnalysis(
            recognized=True,
            subject=subject,
            subject_number=number,
            subject_gender=gender,
            verb=verb,
            expected_person=expected_person,
            agrees=None,
            note="No exact reviewed negative or affirmative finite analysis was found; no form is guessed.",
        )

    return NegativeFiniteAgreementAnalysis(recognized=False)
