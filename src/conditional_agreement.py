"""Conservative agreement analysis for the reviewed Somali conditional paradigm.

The current executable scope is intentionally narrow and source-bound:

* affirmative: ``<noun> wuu/way cuni lahaa/lahayd/...``
* negative: ``<noun> ma cuneen/cunteen/cunneen``

The cited CUN table has irregular/syncretic negative conditional forms, so this
module never derives a negative conditional from affirmative morphology or from
suffixes. Exact reviewed surfaces only.
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
class ConditionalAgreementAnalysis:
    recognized: bool
    subject: str | None = None
    subject_number: str | None = None
    subject_gender: str | None = None
    construction: str | None = None
    clitic: str | None = None
    conditional_stem: str | None = None
    verb_or_auxiliary: str | None = None
    polarity: str | None = None
    persons: tuple[str, ...] = ()
    expected_person: str | None = None
    agrees: bool | None = None
    mood: str | None = None
    rule_id: str = "GRAM-COND-001"
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


def _conditional_stem(form: str) -> MorphologyCandidate | None:
    for candidate in analyze_surface_form(form):
        if (
            candidate.analysis_type == "conditional_stem"
            and candidate.features.get("possible_use") == "conditional_with_auxiliary"
        ):
            return candidate
    return None


def _affirmative_auxiliary(form: str) -> MorphologyCandidate | None:
    for candidate in analyze_surface_form(form):
        if (
            candidate.analysis_type == "conditional_auxiliary"
            and candidate.features.get("construction") == "conditional"
            and candidate.features.get("polarity") == "affirmative"
        ):
            return candidate
    return None


def _negative_conditional(form: str) -> MorphologyCandidate | None:
    for candidate in analyze_surface_form(form):
        if (
            candidate.analysis_type == "negative_conditional_finite"
            and candidate.features.get("construction") == "negative_conditional"
            and candidate.features.get("polarity") == "negative"
        ):
            return candidate
    return None


def analyze_conditional_agreement(sentence: str) -> ConditionalAgreementAnalysis:
    """Analyze exact reviewed noun-subject conditional constructions.

    Unknown auxiliaries/forms remain unjudged. Negative conditional person
    ambiguity is preserved exactly as represented in the source-backed data.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 3:
        return ConditionalAgreementAnalysis(recognized=False)

    for index, subject in enumerate(tokens):
        if subject.casefold() in PERSONAL_PRONOUN_FORMS:
            continue
        expected_person, number, gender = _expected_person(subject)
        if expected_person is None:
            continue

        # Negative conditional: <noun> ma <negative-conditional-form>
        if index + 2 < len(tokens) and tokens[index + 1].casefold() == "ma":
            following = tokens[index + 2]
            negative = _negative_conditional(following)
            if negative is not None:
                persons = _candidate_persons(negative)
                return ConditionalAgreementAnalysis(
                    recognized=True,
                    subject=subject,
                    subject_number=number,
                    subject_gender=gender,
                    construction="negative_conditional",
                    verb_or_auxiliary=following,
                    polarity="negative",
                    persons=persons,
                    expected_person=expected_person,
                    agrees=expected_person in persons,
                    mood="shardiley",
                    rule_id="GRAM-COND-NEG-001",
                    note=(
                        "Exact reviewed negative conditional morphology is used. "
                        "Syncretic person values are preserved; no ordinary-past or suffix rule is substituted."
                    ),
                )

            # ma + cuni + affirmative conditional auxiliary is a polarity conflict.
            stem_candidate = _conditional_stem(following)
            if stem_candidate is not None and index + 3 < len(tokens):
                auxiliary = tokens[index + 3]
                affirmative_aux = _affirmative_auxiliary(auxiliary)
                if affirmative_aux is not None:
                    return ConditionalAgreementAnalysis(
                        recognized=True,
                        subject=subject,
                        subject_number=number,
                        subject_gender=gender,
                        construction="negative_conditional",
                        conditional_stem=following,
                        verb_or_auxiliary=auxiliary,
                        polarity="affirmative",
                        persons=_candidate_persons(affirmative_aux),
                        expected_person=expected_person,
                        agrees=False,
                        mood="shardiley",
                        rule_id="GRAM-COND-NEG-001",
                        note=(
                            "An exact reviewed affirmative conditional auxiliary appears after ma. "
                            "The cited negative conditional is a separate irregular paradigm; no automatic rewrite."
                        ),
                    )
                return ConditionalAgreementAnalysis(
                    recognized=True,
                    subject=subject,
                    subject_number=number,
                    subject_gender=gender,
                    construction="negative_conditional",
                    conditional_stem=following,
                    verb_or_auxiliary=auxiliary,
                    expected_person=expected_person,
                    agrees=None,
                    mood="shardiley",
                    rule_id="GRAM-COND-NEG-001",
                    note="Reviewed conditional stem found after ma, but the following form is not an exact reviewed conditional auxiliary.",
                )

        # Affirmative conditional: <noun> wuu/way cuni <conditional-auxiliary>
        if (
            index + 3 < len(tokens)
            and tokens[index + 1].casefold() in STATEMENT_CLITICS
        ):
            clitic = tokens[index + 1]
            stem = tokens[index + 2]
            stem_candidate = _conditional_stem(stem)
            if stem_candidate is None:
                continue
            auxiliary = tokens[index + 3]
            aux_candidate = _affirmative_auxiliary(auxiliary)
            if aux_candidate is None:
                return ConditionalAgreementAnalysis(
                    recognized=True,
                    subject=subject,
                    subject_number=number,
                    subject_gender=gender,
                    construction="affirmative_conditional",
                    clitic=clitic,
                    conditional_stem=stem,
                    verb_or_auxiliary=auxiliary,
                    polarity="affirmative",
                    expected_person=expected_person,
                    agrees=None,
                    mood="shardiley",
                    rule_id="GRAM-COND-AFF-001",
                    note="Reviewed conditional stem found, but the following auxiliary is not an exact reviewed affirmative conditional auxiliary.",
                )
            persons = _candidate_persons(aux_candidate)
            return ConditionalAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_number=number,
                subject_gender=gender,
                construction="affirmative_conditional",
                clitic=clitic,
                conditional_stem=stem,
                verb_or_auxiliary=auxiliary,
                polarity="affirmative",
                persons=persons,
                expected_person=expected_person,
                agrees=expected_person in persons,
                mood="shardiley",
                rule_id="GRAM-COND-AFF-001",
                note=(
                    "Agreement is read from the exact reviewed conditional auxiliary. "
                    "The cuni stem is non-finite; no suffix-only inference is used."
                ),
            )

    return ConditionalAgreementAnalysis(recognized=False)
