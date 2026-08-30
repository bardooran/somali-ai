"""Conservative agreement analysis for fronted Somali object-focus clauses.

Executable scope is intentionally narrow and native-reviewed::

    FOCUSED_OBJECT + ayuu/ayay + REVIEWED_NOUN_SUBJECT + FINITE_CUN

The project explicitly reviewed ``Muus ayuu wiilku cunay``. In this order the
sentence-initial noun is the focused object, not the subject. The noun following
the contracted ``ayaa + uu/ay`` form controls both the contraction and the
finite verb. Exact reviewed morphology only; unknown forms and unsupported
lemmas remain unjudged.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.noun_gender_agreement import infer_subject_gender, infer_subject_number
from src.noun_subject_case import PERSONAL_PRONOUN_FORMS
from src.reviewed_finite_verb import analyze_reviewed_finite_verb

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)

FRONTED_FOCUS_CLITIC_PERSONS = {
    "ayuu": ("3sg_m",),
    "ayay": ("3sg_f", "3pl"),
}

# Object-first focus order is independently reviewed for cun in this project.
REVIEWED_FRONTED_OBJECT_LEMMAS = {"cun"}


@dataclass(frozen=True)
class FrontedObjectFocusAgreementAnalysis:
    recognized: bool
    focused_object: tuple[str, ...] = ()
    focus_clitic: str | None = None
    focus_clitic_persons: tuple[str, ...] = ()
    subject: str | None = None
    subject_number: str | None = None
    subject_gender: str | None = None
    verb: str | None = None
    verb_lemmas: tuple[str, ...] = ()
    verb_persons: tuple[str, ...] = ()
    expected_person: str | None = None
    clitic_agrees: bool | None = None
    verb_agrees: bool | None = None
    agrees: bool | None = None
    rule_id: str = "GRAM-OBJFOCUS-FRONT-001"
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


def analyze_fronted_object_focus_agreement(
    sentence: str,
) -> FrontedObjectFocusAgreementAnalysis:
    """Analyze reviewed object-first ``... ayuu/ayay SUBJECT VERB`` clauses.

    One to four lexical tokens may form the fronted focused object. The subject
    must immediately follow ``ayuu/ayay`` and the finite verb must immediately
    follow the subject in this first executable layer. This prevents the first
    noun from being treated as a subject merely because it is sentence-initial.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 4:
        return FrontedObjectFocusAgreementAnalysis(recognized=False)

    # Require 1-4 fronted object tokens, followed by ayuu/ayay, subject, verb.
    upper = min(4, len(tokens) - 3)
    for object_width in range(1, upper + 1):
        clitic_index = object_width
        clitic = tokens[clitic_index]
        clitic_persons = FRONTED_FOCUS_CLITIC_PERSONS.get(clitic.casefold())
        if clitic_persons is None:
            continue

        subject = tokens[clitic_index + 1]
        if subject.casefold() in PERSONAL_PRONOUN_FORMS:
            return FrontedObjectFocusAgreementAnalysis(recognized=False)

        expected_person, number, gender = _expected_person(subject)
        if expected_person is None:
            return FrontedObjectFocusAgreementAnalysis(recognized=False)

        verb = tokens[clitic_index + 2]
        finite = analyze_reviewed_finite_verb(verb)
        clitic_agrees = expected_person in clitic_persons
        focused = tuple(tokens[:clitic_index])

        if not finite.recognized:
            return FrontedObjectFocusAgreementAnalysis(
                recognized=True,
                focused_object=focused,
                focus_clitic=clitic,
                focus_clitic_persons=clitic_persons,
                subject=subject,
                subject_number=number,
                subject_gender=gender,
                verb=verb,
                expected_person=expected_person,
                clitic_agrees=clitic_agrees,
                agrees=None,
                note=(
                    "The fronted focus frame and reviewed noun subject are recognized, but the "
                    "following verb is not an exact reviewed finite form. Agreement remains "
                    "unjudged and no verb form is guessed."
                ),
            )

        licensed = tuple(
            lemma for lemma in finite.lemmas if lemma in REVIEWED_FRONTED_OBJECT_LEMMAS
        )
        if not licensed:
            return FrontedObjectFocusAgreementAnalysis(
                recognized=True,
                focused_object=focused,
                focus_clitic=clitic,
                focus_clitic_persons=clitic_persons,
                subject=subject,
                subject_number=number,
                subject_gender=gender,
                verb=verb,
                verb_lemmas=finite.lemmas,
                verb_persons=finite.persons,
                expected_person=expected_person,
                clitic_agrees=clitic_agrees,
                verb_agrees=None,
                agrees=None,
                note=(
                    "The verb is reviewed, but its lemma does not yet have independent evidence "
                    "for this object-first focus order. The focused constituent's role is not "
                    "generalized from word order alone."
                ),
            )

        verb_agrees = expected_person in finite.persons
        return FrontedObjectFocusAgreementAnalysis(
            recognized=True,
            focused_object=focused,
            focus_clitic=clitic,
            focus_clitic_persons=clitic_persons,
            subject=subject,
            subject_number=number,
            subject_gender=gender,
            verb=verb,
            verb_lemmas=licensed,
            verb_persons=finite.persons,
            expected_person=expected_person,
            clitic_agrees=clitic_agrees,
            verb_agrees=verb_agrees,
            agrees=clitic_agrees and verb_agrees,
            note=(
                "The noun after ayuu/ayay is the reviewed subject and controls both the focus "
                "contraction and the exact finite cun form. The sentence-initial focused object "
                "does not control agreement; no automatic rewrite is used."
            ),
        )

    return FrontedObjectFocusAgreementAnalysis(recognized=False)
