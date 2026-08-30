"""Conservative Somali future auxiliary agreement analysis.

This layer recognizes only reviewed affirmative future constructions in which
an exact reviewed future stem is immediately followed by an exact reviewed
future auxiliary. The auxiliary carries person agreement. Unknown stems,
unknown auxiliaries, negative future forms, and other constructions remain
unjudged rather than being derived from suffixes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.morphology_candidates import MorphologyCandidate, analyze_surface_form
from src.noun_gender_agreement import infer_subject_gender, infer_subject_number
from src.noun_subject_case import PERSONAL_PRONOUN_FORMS

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)
STATEMENT_CLITICS = {"wuu", "way"}


@dataclass(frozen=True)
class FutureAuxiliaryAgreementAnalysis:
    recognized: bool
    subject: str | None = None
    subject_number: str | None = None
    subject_gender: str | None = None
    clitic: str | None = None
    future_stem: str | None = None
    future_lemma: str | None = None
    auxiliary: str | None = None
    auxiliary_persons: tuple[str, ...] = ()
    expected_person: str | None = None
    agrees: bool | None = None
    tense_aspect: str | None = None
    rule_id: str = "GRAM-FUT-AUX-001"
    note: str = ""


def _is_reviewed_future_stem(candidate: MorphologyCandidate) -> bool:
    features = candidate.features
    return (
        features.get("part_of_speech") == "verb"
        and (
            features.get("possible_use") == "future_with_auxiliary"
            or "future_with_auxiliary" in features.get("possible_functions", [])
        )
    )


def _future_stem_candidate(form: str) -> MorphologyCandidate | None:
    for candidate in analyze_surface_form(form):
        if _is_reviewed_future_stem(candidate):
            return candidate
    return None


def _auxiliary_persons(form: str) -> tuple[str, ...]:
    persons: list[str] = []
    for candidate in analyze_surface_form(form):
        if candidate.analysis_type != "future_auxiliary":
            continue
        if candidate.features.get("construction") != "future":
            continue
        person = candidate.features.get("person")
        if isinstance(person, str) and person not in persons:
            persons.append(person)
        possible = candidate.features.get("possible_persons")
        if isinstance(possible, list):
            for item in possible:
                value = str(item)
                if value not in persons:
                    persons.append(value)
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


def analyze_future_auxiliary_agreement(sentence: str) -> FutureAuxiliaryAgreementAnalysis:
    """Check reviewed noun subjects against affirmative future auxiliary person.

    Current executable scope is ``<noun> wuu/way <reviewed-future-stem> <aux>``.
    The future stem and auxiliary must both be exact reviewed forms. The stem is
    non-finite; agreement is carried by the auxiliary.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 4:
        return FutureAuxiliaryAgreementAnalysis(recognized=False)

    for index in range(len(tokens) - 3):
        subject = tokens[index]
        clitic = tokens[index + 1]
        if subject.casefold() in PERSONAL_PRONOUN_FORMS:
            continue
        if clitic.casefold() not in STATEMENT_CLITICS:
            continue

        stem = tokens[index + 2]
        stem_candidate = _future_stem_candidate(stem)
        if stem_candidate is None:
            continue

        expected_person, number, gender = _expected_person(subject)
        if expected_person is None:
            return FutureAuxiliaryAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_number=number,
                subject_gender=gender,
                clitic=clitic,
                future_stem=stem,
                future_lemma=stem_candidate.lemma,
                tense_aspect="timaaddo",
                agrees=None,
                note="Reviewed future stem found, but subject person cannot yet be resolved safely.",
            )

        auxiliary = tokens[index + 3]
        persons = _auxiliary_persons(auxiliary)
        if not persons:
            return FutureAuxiliaryAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_number=number,
                subject_gender=gender,
                clitic=clitic,
                future_stem=stem,
                future_lemma=stem_candidate.lemma,
                auxiliary=auxiliary,
                expected_person=expected_person,
                tense_aspect="timaaddo",
                agrees=None,
                note="Reviewed future stem found, but the following auxiliary is not an exact reviewed affirmative future auxiliary.",
            )

        return FutureAuxiliaryAgreementAnalysis(
            recognized=True,
            subject=subject,
            subject_number=number,
            subject_gender=gender,
            clitic=clitic,
            future_stem=stem,
            future_lemma=stem_candidate.lemma,
            auxiliary=auxiliary,
            auxiliary_persons=persons,
            expected_person=expected_person,
            agrees=expected_person in persons,
            tense_aspect="timaaddo",
            note=(
                "The future stem and auxiliary are exact reviewed source forms. "
                "Agreement is read from the auxiliary; no suffix-only future inference is used."
            ),
        )

    return FutureAuxiliaryAgreementAnalysis(recognized=False)
