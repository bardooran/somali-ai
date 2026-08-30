"""Conservative negative past-progressive and past-habitual analysis.

The reviewed CUN paradigm neutralizes person in both negative constructions:
``ma cunayn/cunaynin`` for past progressive and ``ma cuni jirin`` for habitual
past. This layer preserves that neutralization instead of inventing gender or
number distinctions that the source does not show.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.morphology_candidates import MorphologyCandidate, analyze_surface_form
from src.noun_gender_agreement import infer_subject_gender, infer_subject_number
from src.noun_subject_case import PERSONAL_PRONOUN_FORMS

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)


@dataclass(frozen=True)
class NegativePastAspectAgreementAnalysis:
    recognized: bool
    subject: str | None = None
    subject_number: str | None = None
    subject_gender: str | None = None
    construction: str | None = None
    stem: str | None = None
    verb_or_auxiliary: str | None = None
    polarity: str | None = None
    persons: tuple[str, ...] = ()
    person_neutralized: bool = False
    expected_person: str | None = None
    agrees: bool | None = None
    tense_aspect: str | None = None
    rule_id: str = "GRAM-NEG-PASTASP-001"
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
    persons: list[str] = []
    person = candidate.features.get("person")
    if isinstance(person, str):
        persons.append(person)
    possible = candidate.features.get("possible_persons")
    if isinstance(possible, list):
        for item in possible:
            value = str(item)
            if value not in persons:
                persons.append(value)
    return tuple(persons)


def _find_candidate(form: str, analysis_type: str) -> MorphologyCandidate | None:
    for candidate in analyze_surface_form(form):
        if candidate.analysis_type == analysis_type:
            return candidate
    return None


def _find_affirmative_past_progressive(form: str) -> MorphologyCandidate | None:
    for candidate in analyze_surface_form(form):
        if (
            candidate.analysis_type == "finite_verb"
            and candidate.features.get("tense_aspect") == "tagto_socota"
            and candidate.features.get("polarity") == "affirmative"
        ):
            return candidate
    return None


def _past_habitual_stem(form: str) -> MorphologyCandidate | None:
    for candidate in analyze_surface_form(form):
        if (
            candidate.analysis_type == "past_habitual_stem"
            and candidate.features.get("possible_use") == "past_habitual_with_auxiliary"
        ):
            return candidate
    return None


def _affirmative_habitual_auxiliary(form: str) -> MorphologyCandidate | None:
    for candidate in analyze_surface_form(form):
        if (
            candidate.analysis_type == "past_habitual_auxiliary"
            and candidate.features.get("construction") == "past_habitual"
            and candidate.features.get("polarity") == "affirmative"
        ):
            return candidate
    return None


def analyze_negative_past_aspect_agreement(sentence: str) -> NegativePastAspectAgreementAnalysis:
    """Analyze reviewed noun-subject negative past aspect constructions.

    Supported patterns are ``<noun> ma <past-progressive-form>`` and
    ``<noun> ma <habitual-stem> <habitual-auxiliary>``. Exact reviewed forms
    only; unseen suffix lookalikes remain unjudged.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 3:
        return NegativePastAspectAgreementAnalysis(recognized=False)

    for index in range(len(tokens) - 2):
        subject = tokens[index]
        if subject.casefold() in PERSONAL_PRONOUN_FORMS:
            continue
        if tokens[index + 1].casefold() != "ma":
            continue

        expected_person, number, gender = _expected_person(subject)
        form = tokens[index + 2]

        negative_progressive = _find_candidate(form, "negative_past_progressive")
        if negative_progressive is not None:
            persons = _candidate_persons(negative_progressive)
            neutralized = bool(negative_progressive.features.get("person_neutralized"))
            agrees = True if neutralized else (
                expected_person in persons if expected_person is not None else None
            )
            return NegativePastAspectAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_number=number,
                subject_gender=gender,
                construction="negative_past_progressive",
                verb_or_auxiliary=form,
                polarity="negative",
                persons=persons,
                person_neutralized=neutralized,
                expected_person=expected_person,
                agrees=agrees,
                tense_aspect="tagto_socota",
                note=(
                    "The reviewed negative past-progressive form neutralizes person; "
                    "the same surface is licensed across the cited subject persons."
                ),
            )

        affirmative_progressive = _find_affirmative_past_progressive(form)
        if affirmative_progressive is not None:
            return NegativePastAspectAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_number=number,
                subject_gender=gender,
                construction="negative_past_progressive",
                verb_or_auxiliary=form,
                polarity="affirmative",
                persons=_candidate_persons(affirmative_progressive),
                expected_person=expected_person,
                agrees=False,
                tense_aspect="tagto_socota",
                note=(
                    "An exact reviewed affirmative past-progressive form appears after ma; "
                    "the cited negative paradigm uses cunayn/cunaynin instead."
                ),
            )

        stem_candidate = _past_habitual_stem(form)
        if stem_candidate is None or index + 3 >= len(tokens):
            continue

        auxiliary = tokens[index + 3]
        negative_aux = _find_candidate(auxiliary, "negative_past_habitual_auxiliary")
        if negative_aux is not None:
            persons = _candidate_persons(negative_aux)
            neutralized = bool(negative_aux.features.get("person_neutralized"))
            agrees = True if neutralized else (
                expected_person in persons if expected_person is not None else None
            )
            return NegativePastAspectAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_number=number,
                subject_gender=gender,
                construction="negative_past_habitual",
                stem=form,
                verb_or_auxiliary=auxiliary,
                polarity="negative",
                persons=persons,
                person_neutralized=neutralized,
                expected_person=expected_person,
                agrees=agrees,
                tense_aspect="tagto_caadaley",
                note=(
                    "The reviewed negative habitual auxiliary jirin is person-neutral "
                    "across the cited paradigm."
                ),
            )

        affirmative_aux = _affirmative_habitual_auxiliary(auxiliary)
        if affirmative_aux is not None:
            return NegativePastAspectAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_number=number,
                subject_gender=gender,
                construction="negative_past_habitual",
                stem=form,
                verb_or_auxiliary=auxiliary,
                polarity="affirmative",
                persons=_candidate_persons(affirmative_aux),
                expected_person=expected_person,
                agrees=False,
                tense_aspect="tagto_caadaley",
                note=(
                    "An exact reviewed affirmative habitual auxiliary appears after ma; "
                    "the cited negative habitual construction uses jirin."
                ),
            )

        return NegativePastAspectAgreementAnalysis(
            recognized=True,
            subject=subject,
            subject_number=number,
            subject_gender=gender,
            construction="negative_past_habitual",
            stem=form,
            verb_or_auxiliary=auxiliary,
            expected_person=expected_person,
            agrees=None,
            tense_aspect="tagto_caadaley",
            note="Reviewed habitual stem found, but the following auxiliary is not an exact reviewed form.",
        )

    return NegativePastAspectAgreementAnalysis(recognized=False)
