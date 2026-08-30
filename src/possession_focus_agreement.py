"""Conservative agreement analysis for focused Somali possession clauses.

Initial executable scope is deliberately narrow and source-backed::

    <reviewed noun subject> <1-4 focused tokens> buu/bay/ayuu/ayay <leeyahay finite form>

The explicit noun subject controls both the contracted focus/subject clitic and
the finite possession verb. Intervening focused material is never treated as
the agreement controller. Exact reviewed morphology only; no unseen forms are
derived and no automatic rewrite is produced.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.noun_gender_agreement import infer_subject_gender, infer_subject_number
from src.noun_subject_case import PERSONAL_PRONOUN_FORMS
from src.reviewed_finite_verb import analyze_reviewed_finite_verb

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)

# baa/ayaa + third-person short subject pronoun.
FOCUS_CLITIC_PERSONS = {
    "buu": ("3sg_m",),
    "ayuu": ("3sg_m",),
    "bay": ("3sg_f", "3pl"),
    "ayay": ("3sg_f", "3pl"),
}


@dataclass(frozen=True)
class PossessionFocusAgreementAnalysis:
    recognized: bool
    subject: str | None = None
    subject_number: str | None = None
    subject_gender: str | None = None
    focused_material: tuple[str, ...] = ()
    focus_clitic: str | None = None
    focus_clitic_persons: tuple[str, ...] = ()
    verb: str | None = None
    verb_persons: tuple[str, ...] = ()
    verb_tense_aspects: tuple[str, ...] = ()
    expected_person: str | None = None
    clitic_agrees: bool | None = None
    verb_agrees: bool | None = None
    agrees: bool | None = None
    rule_id: str = "GRAM-POSS-FOCUS-001"
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


def analyze_possession_focus_agreement(sentence: str) -> PossessionFocusAgreementAnalysis:
    """Analyze a reviewed noun-subject focused possession construction.

    At least one lexical token must occur between the explicit subject and the
    contracted focus clitic. This excludes subject-focus ``NOUN baa ...`` from
    the current rule. The finite verb must be an exact reviewed ``leeyahay``
    analysis for a full agreement judgment. An unknown following verb leaves
    the recognized focus frame unjudged rather than guessed.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 4:
        return PossessionFocusAgreementAnalysis(recognized=False)

    subject = tokens[0]
    if subject.casefold() in PERSONAL_PRONOUN_FORMS:
        return PossessionFocusAgreementAnalysis(recognized=False)

    expected_person, number, gender = _expected_person(subject)
    if expected_person is None:
        return PossessionFocusAgreementAnalysis(recognized=False)

    # Require 1-4 focused tokens after the subject, then a contracted focus
    # clitic, then an immediately following finite possessive verb.
    upper = min(len(tokens) - 1, 6)
    for clitic_index in range(2, upper):
        clitic = tokens[clitic_index]
        clitic_persons = FOCUS_CLITIC_PERSONS.get(clitic.casefold())
        if clitic_persons is None:
            continue

        verb = tokens[clitic_index + 1]
        verb_analysis = analyze_reviewed_finite_verb(verb)
        possession_reading = verb_analysis.recognized and "leeyahay" in verb_analysis.lemmas
        clitic_agrees = expected_person in clitic_persons

        if not possession_reading:
            return PossessionFocusAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_number=number,
                subject_gender=gender,
                focused_material=tuple(tokens[1:clitic_index]),
                focus_clitic=clitic,
                focus_clitic_persons=clitic_persons,
                verb=verb,
                expected_person=expected_person,
                clitic_agrees=clitic_agrees,
                verb_agrees=None,
                agrees=None,
                note=(
                    "Reviewed noun subject and contracted focus clitic found, but the immediately "
                    "following form is not an exact reviewed finite leeyahay form. The frame is "
                    "left unjudged and the intervening focused material does not control agreement."
                ),
            )

        verb_agrees = expected_person in verb_analysis.persons
        agrees = clitic_agrees and verb_agrees
        return PossessionFocusAgreementAnalysis(
            recognized=True,
            subject=subject,
            subject_number=number,
            subject_gender=gender,
            focused_material=tuple(tokens[1:clitic_index]),
            focus_clitic=clitic,
            focus_clitic_persons=clitic_persons,
            verb=verb,
            verb_persons=verb_analysis.persons,
            verb_tense_aspects=verb_analysis.tense_aspects,
            expected_person=expected_person,
            clitic_agrees=clitic_agrees,
            verb_agrees=verb_agrees,
            agrees=agrees,
            note=(
                "The explicit noun subject controls both the contracted focus/subject clitic and "
                "the exact reviewed leeyahay finite form. Focused material between them is not an "
                "agreement controller; no suffix-only inference or automatic rewrite is used."
            ),
        )

    return PossessionFocusAgreementAnalysis(recognized=False)
