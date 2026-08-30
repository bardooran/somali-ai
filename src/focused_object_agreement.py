"""Conservative agreement analysis for reviewed Somali object-focus clauses.

Executable scope is intentionally limited to lemmas with direct reviewed
object-focus evidence. The explicit noun subject controls the contracted
baa/ayaa + subject-pronoun form and the finite verb; focused object material
never controls agreement.

Current reviewed orders:
- subject-first: ``Wiilku muus buu cunay``
- object-first: ``Muus ayuu wiilku cunay``

Current subject-first licensed lemmas:
- cun: project native review
- arag: Qaamuus 2012 focus example ``Gabadhu Cali bay aragtay``

The object-first analyzer is narrower and currently licenses cun only. Other
focus frames are left unjudged. The specialized leeyahay possession-focus
analyzer owns possession clauses, so this module does not duplicate them.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.fronted_object_focus_agreement import analyze_fronted_object_focus_agreement
from src.noun_gender_agreement import infer_subject_gender, infer_subject_number
from src.noun_subject_case import PERSONAL_PRONOUN_FORMS
from src.reviewed_finite_verb import analyze_reviewed_finite_verb

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)

FOCUS_CLITIC_PERSONS = {
    "buu": ("3sg_m",),
    "ayuu": ("3sg_m",),
    "bay": ("3sg_f", "3pl"),
    "ayay": ("3sg_f", "3pl"),
}

# Do not generalize objecthood from focus syntax alone. Each lemma here has
# independent reviewed evidence that the focused constituent can be its object.
REVIEWED_OBJECT_FOCUS_LEMMAS = {"cun", "arag"}


@dataclass(frozen=True)
class FocusedObjectAgreementAnalysis:
    recognized: bool
    subject: str | None = None
    subject_number: str | None = None
    subject_gender: str | None = None
    focused_object: tuple[str, ...] = ()
    focus_clitic: str | None = None
    focus_clitic_persons: tuple[str, ...] = ()
    verb: str | None = None
    verb_lemmas: tuple[str, ...] = ()
    verb_persons: tuple[str, ...] = ()
    expected_person: str | None = None
    clitic_agrees: bool | None = None
    verb_agrees: bool | None = None
    agrees: bool | None = None
    rule_id: str = "GRAM-OBJFOCUS-001"
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


def _convert_fronted(sentence: str) -> FocusedObjectAgreementAnalysis | None:
    """Return the shared result shape when object-first focus is recognized."""
    fronted = analyze_fronted_object_focus_agreement(sentence)
    if not fronted.recognized:
        return None
    return FocusedObjectAgreementAnalysis(
        recognized=True,
        subject=fronted.subject,
        subject_number=fronted.subject_number,
        subject_gender=fronted.subject_gender,
        focused_object=fronted.focused_object,
        focus_clitic=fronted.focus_clitic,
        focus_clitic_persons=fronted.focus_clitic_persons,
        verb=fronted.verb,
        verb_lemmas=fronted.verb_lemmas,
        verb_persons=fronted.verb_persons,
        expected_person=fronted.expected_person,
        clitic_agrees=fronted.clitic_agrees,
        verb_agrees=fronted.verb_agrees,
        agrees=fronted.agrees,
        rule_id=fronted.rule_id,
        note=fronted.note,
    )


def analyze_focused_object_agreement(sentence: str) -> FocusedObjectAgreementAnalysis:
    """Analyze a reviewed Somali focused-object construction.

    Supported frames are currently::

        SUBJECT + 1-4 focused tokens + buu/bay/ayuu/ayay + FINITE_VERB
        1-4 focused tokens + ayuu/ayay + SUBJECT + FINITE_CUN

    The second frame is checked first because its sentence-initial noun is the
    object rather than the subject. A full judgment requires independently
    reviewed subject number/gender and exact reviewed finite morphology.
    Unknown or unsupported verbs are not guessed.
    """
    fronted = _convert_fronted(sentence)
    if fronted is not None:
        return fronted

    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 4:
        return FocusedObjectAgreementAnalysis(recognized=False)

    subject = tokens[0]
    if subject.casefold() in PERSONAL_PRONOUN_FORMS:
        return FocusedObjectAgreementAnalysis(recognized=False)

    expected_person, number, gender = _expected_person(subject)
    if expected_person is None:
        return FocusedObjectAgreementAnalysis(recognized=False)

    upper = min(len(tokens) - 1, 6)
    for clitic_index in range(2, upper):
        clitic = tokens[clitic_index]
        clitic_persons = FOCUS_CLITIC_PERSONS.get(clitic.casefold())
        if clitic_persons is None:
            continue

        focused = tuple(tokens[1:clitic_index])
        verb = tokens[clitic_index + 1]
        finite = analyze_reviewed_finite_verb(verb)
        clitic_agrees = expected_person in clitic_persons

        if not finite.recognized:
            return FocusedObjectAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_number=number,
                subject_gender=gender,
                focused_object=focused,
                focus_clitic=clitic,
                focus_clitic_persons=clitic_persons,
                verb=verb,
                expected_person=expected_person,
                clitic_agrees=clitic_agrees,
                agrees=None,
                note=(
                    "A reviewed noun subject and contracted focus clitic are present, but the "
                    "following verb is not an exact reviewed finite form. Object role and verb "
                    "agreement remain unjudged; no form is guessed."
                ),
            )

        # leeyahay focus is handled by the more specific possession analyzer.
        if "leeyahay" in finite.lemmas:
            return FocusedObjectAgreementAnalysis(recognized=False)

        licensed = tuple(
            lemma for lemma in finite.lemmas if lemma in REVIEWED_OBJECT_FOCUS_LEMMAS
        )
        if not licensed:
            return FocusedObjectAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_number=number,
                subject_gender=gender,
                focused_object=focused,
                focus_clitic=clitic,
                focus_clitic_persons=clitic_persons,
                verb=verb,
                verb_lemmas=finite.lemmas,
                verb_persons=finite.persons,
                expected_person=expected_person,
                clitic_agrees=clitic_agrees,
                verb_agrees=None,
                agrees=None,
                note=(
                    "The finite verb is reviewed, but this lemma does not yet have independent "
                    "object-focus evidence in the executable rule. The focused constituent's role "
                    "is therefore not guessed."
                ),
            )

        verb_agrees = expected_person in finite.persons
        return FocusedObjectAgreementAnalysis(
            recognized=True,
            subject=subject,
            subject_number=number,
            subject_gender=gender,
            focused_object=focused,
            focus_clitic=clitic,
            focus_clitic_persons=clitic_persons,
            verb=verb,
            verb_lemmas=licensed,
            verb_persons=finite.persons,
            expected_person=expected_person,
            clitic_agrees=clitic_agrees,
            verb_agrees=verb_agrees,
            agrees=clitic_agrees and verb_agrees,
            note=(
                "The explicit noun subject controls both the contracted focus/subject clitic and "
                "the exact reviewed finite verb. The intervening reviewed object-focus material "
                "does not control agreement; no automatic rewrite is used."
            ),
        )

    return FocusedObjectAgreementAnalysis(recognized=False)
