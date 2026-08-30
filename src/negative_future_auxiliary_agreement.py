"""Conservative Somali negative-future auxiliary agreement analysis.

This layer recognizes only reviewed ``ma + future stem + future auxiliary``
constructions with an explicit noun subject. The future stem remains non-finite;
person agreement is carried by the auxiliary. Negative future morphology is
kept separate from the affirmative future paradigm because some persons use
different auxiliary surfaces while others are syncretic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.morphology_candidates import MorphologyCandidate, analyze_surface_form
from src.noun_gender_agreement import infer_subject_gender, infer_subject_number
from src.noun_subject_case import PERSONAL_PRONOUN_FORMS

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)


@dataclass(frozen=True)
class NegativeFutureAuxiliaryAgreementAnalysis:
    recognized: bool
    subject: str | None = None
    subject_number: str | None = None
    subject_gender: str | None = None
    negator: str | None = None
    future_stem: str | None = None
    future_lemma: str | None = None
    auxiliary: str | None = None
    auxiliary_persons: tuple[str, ...] = ()
    auxiliary_polarity: str | None = None
    expected_person: str | None = None
    agrees: bool | None = None
    tense_aspect: str | None = None
    rule_id: str = "GRAM-FUT-NEG-AUX-001"
    note: str = ""


def _is_reviewed_future_stem(candidate: MorphologyCandidate) -> bool:
    features = candidate.features
    possible_functions = features.get("possible_functions", [])
    return (
        features.get("part_of_speech") == "verb"
        and (
            features.get("possible_use") == "future_with_auxiliary"
            or (
                isinstance(possible_functions, list)
                and "future_with_auxiliary" in possible_functions
            )
        )
    )


def _future_stem_candidate(form: str) -> MorphologyCandidate | None:
    for candidate in analyze_surface_form(form):
        if _is_reviewed_future_stem(candidate):
            return candidate
    return None


def _candidate_persons(candidate: MorphologyCandidate) -> tuple[str, ...]:
    person = candidate.features.get("person")
    if isinstance(person, str):
        return (person,)
    possible = candidate.features.get("possible_persons")
    if isinstance(possible, list):
        return tuple(str(item) for item in possible)
    return ()


def _auxiliary_persons(form: str, analysis_type: str) -> tuple[str, ...]:
    persons: list[str] = []
    for candidate in analyze_surface_form(form):
        if candidate.analysis_type != analysis_type:
            continue
        if candidate.features.get("construction") != "future":
            continue
        for person in _candidate_persons(candidate):
            if person not in persons:
                persons.append(person)
    return tuple(persons)


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


def analyze_negative_future_auxiliary_agreement(
    sentence: str,
) -> NegativeFutureAuxiliaryAgreementAnalysis:
    """Check ``<noun> ma <future-stem> <negative-future-auxiliary>``.

    Exact negative auxiliary morphology is preferred. If the following token is
    instead an exact reviewed affirmative future auxiliary, the construction is
    recognized as a polarity conflict. Unknown auxiliary lookalikes remain
    unjudged rather than being derived from spelling.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 4:
        return NegativeFutureAuxiliaryAgreementAnalysis(recognized=False)

    for index in range(len(tokens) - 3):
        subject = tokens[index]
        negator = tokens[index + 1]
        if subject.casefold() in PERSONAL_PRONOUN_FORMS:
            continue
        if negator.casefold() != "ma":
            continue

        stem = tokens[index + 2]
        stem_candidate = _future_stem_candidate(stem)
        if stem_candidate is None:
            continue

        expected_person, number, gender = _expected_person(subject)
        auxiliary = tokens[index + 3]

        if expected_person is None:
            return NegativeFutureAuxiliaryAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_number=number,
                subject_gender=gender,
                negator=negator,
                future_stem=stem,
                future_lemma=stem_candidate.lemma,
                auxiliary=auxiliary,
                expected_person=None,
                tense_aspect="timaaddo",
                agrees=None,
                note="Reviewed negative-future frame found, but subject person cannot yet be resolved safely.",
            )

        negative_persons = _auxiliary_persons(auxiliary, "future_negative_auxiliary")
        if negative_persons:
            return NegativeFutureAuxiliaryAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_number=number,
                subject_gender=gender,
                negator=negator,
                future_stem=stem,
                future_lemma=stem_candidate.lemma,
                auxiliary=auxiliary,
                auxiliary_persons=negative_persons,
                auxiliary_polarity="negative",
                expected_person=expected_person,
                agrees=expected_person in negative_persons,
                tense_aspect="timaaddo",
                note=(
                    "The ma particle, future stem, and negative future auxiliary are exact reviewed source forms. "
                    "Agreement is read from the auxiliary; no suffix-only inference is used."
                ),
            )

        affirmative_persons = _auxiliary_persons(auxiliary, "future_auxiliary")
        if affirmative_persons:
            return NegativeFutureAuxiliaryAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_number=number,
                subject_gender=gender,
                negator=negator,
                future_stem=stem,
                future_lemma=stem_candidate.lemma,
                auxiliary=auxiliary,
                auxiliary_persons=affirmative_persons,
                auxiliary_polarity="affirmative",
                expected_person=expected_person,
                agrees=False,
                tense_aspect="timaaddo",
                note=(
                    "The sentence uses ma with an exact reviewed affirmative future auxiliary. "
                    "The reviewed negative future paradigm requires its negative auxiliary morphology; no automatic rewrite."
                ),
            )

        return NegativeFutureAuxiliaryAgreementAnalysis(
            recognized=True,
            subject=subject,
            subject_number=number,
            subject_gender=gender,
            negator=negator,
            future_stem=stem,
            future_lemma=stem_candidate.lemma,
            auxiliary=auxiliary,
            expected_person=expected_person,
            tense_aspect="timaaddo",
            agrees=None,
            note="Reviewed future stem found after ma, but the following auxiliary is not an exact reviewed future auxiliary.",
        )

    return NegativeFutureAuxiliaryAgreementAnalysis(recognized=False)
