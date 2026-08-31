"""Contextual restrictive agreement for Somali focused subjects.

Focused subjects marked by bare ``baa``/``ayaa`` do not use the ordinary full
finite agreement paradigm. This module implements only the source-backed
restrictive mapping for affirmative simple past (``tagto``), reusing exact
reviewed finite morphology as lexical surface evidence.

Crucially, these contextual person values are *not* added to global morphology.
For example ``yimid`` may license a focused 3pl subject here, while ordinary
``Carruurtu way yimid`` must remain a 3pl agreement error outside focus.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.reviewed_finite_verb import analyze_reviewed_finite_verb

# Restrictive agreement maps the clause subject person to the person-class whose
# full-paradigm surface is reused in the restrictive paradigm. Initial scope is
# the simple affirmative past only. The mapping is source-backed and independent
# of verb suffix spelling.
RESTRICTIVE_SOURCE_PERSON = {
    "1sg": "1sg",
    "2sg": "3sg_m",
    "3sg_m": "3sg_m",
    "3sg_f": "3sg_f",
    "1pl": "1pl",
    "2pl": "3sg_m",
    "3pl": "3sg_m",
}
SUPPORTED_TENSE_ASPECTS = {"tagto"}


@dataclass(frozen=True)
class SubjectFocusRestrictiveAnalysis:
    recognized: bool
    covered: bool
    surface: str
    expected_person: str | None = None
    restrictive_source_person: str | None = None
    full_surface_persons: tuple[str, ...] = ()
    contextual_persons: tuple[str, ...] = ()
    lemmas: tuple[str, ...] = ()
    tense_aspects: tuple[str, ...] = ()
    agrees: bool | None = None
    note: str = ""


def _contextual_persons(full_surface_persons: tuple[str, ...]) -> tuple[str, ...]:
    licensed: list[str] = []
    for person, source_person in RESTRICTIVE_SOURCE_PERSON.items():
        if source_person in full_surface_persons and person not in licensed:
            licensed.append(person)
    return tuple(licensed)


def analyze_subject_focus_restrictive(
    surface: str,
    expected_person: str,
) -> SubjectFocusRestrictiveAnalysis:
    """Judge ``surface`` in the focused-subject restrictive simple-past context.

    Unknown surfaces and exact finite surfaces outside the currently modeled
    simple past remain uncovered rather than being forced through the ordinary
    paradigm. No new lexical surface is generated.
    """
    finite = analyze_reviewed_finite_verb(surface)
    if not finite.recognized:
        return SubjectFocusRestrictiveAnalysis(
            recognized=False,
            covered=False,
            surface=surface,
            expected_person=expected_person,
            note="No exact reviewed finite morphology exists for this surface.",
        )

    source_person = RESTRICTIVE_SOURCE_PERSON.get(expected_person)
    if source_person is None:
        return SubjectFocusRestrictiveAnalysis(
            recognized=True,
            covered=False,
            surface=surface,
            expected_person=expected_person,
            full_surface_persons=finite.persons,
            lemmas=finite.lemmas,
            tense_aspects=finite.tense_aspects,
            note="This subject person is outside the currently reviewed restrictive mapping.",
        )

    if not any(tense in SUPPORTED_TENSE_ASPECTS for tense in finite.tense_aspects):
        return SubjectFocusRestrictiveAnalysis(
            recognized=True,
            covered=False,
            surface=surface,
            expected_person=expected_person,
            restrictive_source_person=source_person,
            full_surface_persons=finite.persons,
            lemmas=finite.lemmas,
            tense_aspects=finite.tense_aspects,
            note=(
                "The surface is exact reviewed finite morphology, but its tense/aspect is "
                "outside the currently modeled focused-subject restrictive simple past."
            ),
        )

    contextual = _contextual_persons(finite.persons)
    agrees = expected_person in contextual
    return SubjectFocusRestrictiveAnalysis(
        recognized=True,
        covered=True,
        surface=surface,
        expected_person=expected_person,
        restrictive_source_person=source_person,
        full_surface_persons=finite.persons,
        contextual_persons=contextual,
        lemmas=finite.lemmas,
        tense_aspects=finite.tense_aspects,
        agrees=agrees,
        note=(
            "Focused subjects use the source-backed restrictive agreement mapping. "
            "The lexical surface itself must already exist in exact reviewed full-paradigm "
            "morphology; only its person interpretation is changed by focus context."
        ),
    )
