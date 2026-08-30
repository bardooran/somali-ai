"""Conservative affirmative past-habitual auxiliary agreement analysis."""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.morphology_candidates import MorphologyCandidate, analyze_surface_form
from src.noun_gender_agreement import infer_subject_gender, infer_subject_number
from src.noun_subject_case import PERSONAL_PRONOUN_FORMS

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)
STATEMENT_CLITICS = {"wuu", "way"}


@dataclass(frozen=True)
class PastHabitualAuxiliaryAgreementAnalysis:
    recognized: bool
    subject: str | None = None
    subject_number: str | None = None
    subject_gender: str | None = None
    clitic: str | None = None
    habitual_stem: str | None = None
    habitual_lemma: str | None = None
    auxiliary: str | None = None
    auxiliary_persons: tuple[str, ...] = ()
    expected_person: str | None = None
    agrees: bool | None = None
    tense_aspect: str | None = None
    rule_id: str = "GRAM-PAST-HAB-AUX-001"
    note: str = ""


def _habitual_stem_candidate(form: str) -> MorphologyCandidate | None:
    for candidate in analyze_surface_form(form):
        if (
            candidate.analysis_type == "past_habitual_stem"
            and candidate.features.get("possible_use") == "past_habitual_with_auxiliary"
        ):
            return candidate
    return None


def _auxiliary_persons(form: str) -> tuple[str, ...]:
    persons: list[str] = []
    for candidate in analyze_surface_form(form):
        if candidate.analysis_type != "past_habitual_auxiliary":
            continue
        if candidate.features.get("construction") != "past_habitual":
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


def analyze_past_habitual_auxiliary_agreement(sentence: str) -> PastHabitualAuxiliaryAgreementAnalysis:
    """Check ``<noun> wuu/way cuni jiray/jirtay/jireen`` from reviewed forms."""
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 4:
        return PastHabitualAuxiliaryAgreementAnalysis(recognized=False)

    for index in range(len(tokens) - 3):
        subject = tokens[index]
        clitic = tokens[index + 1]
        if subject.casefold() in PERSONAL_PRONOUN_FORMS:
            continue
        if clitic.casefold() not in STATEMENT_CLITICS:
            continue

        stem = tokens[index + 2]
        stem_candidate = _habitual_stem_candidate(stem)
        if stem_candidate is None:
            continue

        expected_person, number, gender = _expected_person(subject)
        auxiliary = tokens[index + 3]
        persons = _auxiliary_persons(auxiliary)
        if expected_person is None:
            return PastHabitualAuxiliaryAgreementAnalysis(
                recognized=True, subject=subject, subject_number=number,
                subject_gender=gender, clitic=clitic, habitual_stem=stem,
                habitual_lemma=stem_candidate.lemma, auxiliary=auxiliary,
                auxiliary_persons=persons, tense_aspect="tagto_caadaley",
                agrees=None, note="Reviewed habitual construction found, but subject person cannot be resolved safely."
            )
        if not persons:
            return PastHabitualAuxiliaryAgreementAnalysis(
                recognized=True, subject=subject, subject_number=number,
                subject_gender=gender, clitic=clitic, habitual_stem=stem,
                habitual_lemma=stem_candidate.lemma, auxiliary=auxiliary,
                expected_person=expected_person, tense_aspect="tagto_caadaley",
                agrees=None, note="Reviewed habitual stem found, but the following auxiliary is not an exact reviewed habitual auxiliary."
            )
        return PastHabitualAuxiliaryAgreementAnalysis(
            recognized=True, subject=subject, subject_number=number,
            subject_gender=gender, clitic=clitic, habitual_stem=stem,
            habitual_lemma=stem_candidate.lemma, auxiliary=auxiliary,
            auxiliary_persons=persons, expected_person=expected_person,
            agrees=expected_person in persons, tense_aspect="tagto_caadaley",
            note="Agreement is read from the exact reviewed habitual auxiliary; no suffix-only inference is used."
        )

    return PastHabitualAuxiliaryAgreementAnalysis(recognized=False)
