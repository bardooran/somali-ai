"""Contextual restrictive agreement for Somali focused subjects.

Focused subjects marked by bare ``baa``/``ayaa`` do not use the ordinary full
finite agreement paradigm. This module keeps that reduced agreement strictly
contextual: reduced person values and shortened present surfaces are never added
to global morphology.

Implemented source-backed scopes:
- affirmative simple past: the reduced paradigm reuses reviewed full-paradigm
  surfaces but collapses person distinctions;
- affirmative simple present: reviewed finite paradigms ending in ``-aa`` may
  supply contextual short-``-a`` reduced forms; reviewed AQAAN and AAL/YAAL
  paradigms instead reuse their explicitly sourced present surfaces;
- affirmative present progressive: reviewed finite ``-aa`` surfaces supply the
  corresponding short-``-a`` reduced forms;
- affirmative past progressive: exact reviewed full past-progressive surfaces
  are reinterpreted through the same reduced person classes, while AQAAN,
  AAL/YAAL and AHAW/AH are explicitly excluded because the reviewed school
  grammar states that they do not have this form;
- copular AHAW/AH present: the source-backed reduced absolutive form is invariant
  ``ah``.

Unknown or unsupported surfaces stay unjudged rather than being guessed.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache

from src.morphology_candidates import DEFAULT_MORPHOLOGY_PATHS
from src.reviewed_finite_verb import FINITE_ANALYSIS_TYPES, analyze_reviewed_finite_verb

RESTRICTIVE_SOURCE_PERSON = {
    "1sg": "1sg",
    "2sg": "3sg_m",
    "3sg_m": "3sg_m",
    "3sg_f": "3sg_f",
    "1pl": "1pl",
    "2pl": "3sg_m",
    "3pl": "3sg_m",
}
DEFAULT_CONTEXTUAL_PERSONS = ("1sg", "2sg", "3sg_m", "2pl", "3pl")
FEMININE_CONTEXTUAL_PERSONS = ("3sg_f",)
FIRST_PLURAL_CONTEXTUAL_PERSONS = ("1pl",)
ALL_CONTEXTUAL_PERSONS = (
    "1sg",
    "2sg",
    "3sg_m",
    "3sg_f",
    "1pl",
    "2pl",
    "3pl",
)

SIMPLE_PAST_TENSE = "tagto"
PAST_PROGRESSIVE_TENSE = "tagto_socota"
SIMPLE_PRESENT_TENSE = "joogto_caadaley"
PRESENT_PROGRESSIVE_TENSE = "joogto_socota"
COPULAR_PRESENT_TENSE = "joogto"

# These source-backed irregular present paradigms reuse exact listed surfaces
# under reduced agreement. Their source datasets use different tense labels, so
# the pairing is explicit rather than normalized globally.
PRESENT_REUSE_TENSES = {
    "aqaan": {SIMPLE_PRESENT_TENSE},
    "aal/yaal": {COPULAR_PRESENT_TENSE},
}
PRESENT_REUSE_LEMMAS = set(PRESENT_REUSE_TENSES)
COPULAR_LEMMAS = {"ahaw/ah"}
SHORT_PRESENT_SKIP_DERIVED_1PL = {"imow", "dheh"}
PAST_PROGRESSIVE_EXCLUDED_LEMMAS = {"aqaan", "aal/yaal", "ahaw/ah"}


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
    paradigm: str | None = None
    source_full_surfaces: tuple[str, ...] = ()
    note: str = ""


def _contextual_persons(full_surface_persons: tuple[str, ...]) -> tuple[str, ...]:
    licensed: list[str] = []
    for person, source_person in RESTRICTIVE_SOURCE_PERSON.items():
        if source_person in full_surface_persons and person not in licensed:
            licensed.append(person)
    return tuple(licensed)


def _record_persons(record: dict) -> tuple[str, ...]:
    features = record.get("features", {})
    person = features.get("person")
    if isinstance(person, str):
        return (person,)
    possible = features.get("possible_persons")
    if isinstance(possible, list):
        return tuple(str(item) for item in possible)
    return ()


def _is_affirmative_finite(record: dict) -> bool:
    features = record.get("features", {})
    return (
        record.get("analysis_type") in FINITE_ANALYSIS_TYPES
        and features.get("part_of_speech") == "verb"
        and features.get("polarity") == "affirmative"
    )


def _all_reviewed_records() -> tuple[dict, ...]:
    records: list[dict] = []
    for path in DEFAULT_MORPHOLOGY_PATHS:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    records.append(json.loads(stripped))
    return tuple(records)


def _append_unique(items: list[str], value: str) -> None:
    if value and value not in items:
        items.append(value)


def _derived_group(persons: tuple[str, ...], lemma: str, tense: str) -> tuple[str, ...]:
    if "3sg_m" in persons:
        return DEFAULT_CONTEXTUAL_PERSONS
    if "3sg_f" in persons:
        return FEMININE_CONTEXTUAL_PERSONS
    if "1pl" in persons:
        if tense == SIMPLE_PRESENT_TENSE and lemma in SHORT_PRESENT_SKIP_DERIVED_1PL:
            return ()
        return FIRST_PLURAL_CONTEXTUAL_PERSONS
    return ()


@lru_cache(maxsize=1)
def _short_present_index() -> dict[str, tuple[dict, ...]]:
    """Build focus-only short-``a`` present/progressive forms from exact evidence."""
    index: dict[str, list[dict]] = {}
    for record in _all_reviewed_records():
        if not _is_affirmative_finite(record):
            continue
        features = record.get("features", {})
        tense = features.get("tense_aspect")
        if tense not in {SIMPLE_PRESENT_TENSE, PRESENT_PROGRESSIVE_TENSE}:
            continue

        lemma = str(record.get("lemma", ""))
        if tense == SIMPLE_PRESENT_TENSE and lemma in PRESENT_REUSE_LEMMAS:
            continue
        if lemma in COPULAR_LEMMAS:
            continue

        full_surface = str(record.get("surface", ""))
        if not full_surface.casefold().endswith("aa"):
            continue

        persons = _record_persons(record)
        contextual = _derived_group(persons, lemma, tense)
        if not contextual:
            continue

        reduced_surface = full_surface[:-1]
        item = {
            "surface": reduced_surface,
            "lemma": lemma,
            "tense": tense,
            "full_surface": full_surface,
            "full_persons": persons,
            "contextual_persons": contextual,
        }
        index.setdefault(reduced_surface.casefold(), []).append(item)

    return {key: tuple(value) for key, value in index.items()}


def _analyze_short_present_surface(
    surface: str,
    expected_person: str,
) -> SubjectFocusRestrictiveAnalysis | None:
    entries = _short_present_index().get(surface.casefold(), ())
    if not entries:
        return None

    matching = [entry for entry in entries if expected_person in entry["contextual_persons"]]
    relevant = matching or list(entries)
    contextual: list[str] = []
    persons: list[str] = []
    lemmas: list[str] = []
    tenses: list[str] = []
    source_surfaces: list[str] = []
    for entry in relevant:
        for person in entry["contextual_persons"]:
            _append_unique(contextual, person)
        for person in entry["full_persons"]:
            _append_unique(persons, person)
        _append_unique(lemmas, entry["lemma"])
        _append_unique(tenses, entry["tense"])
        _append_unique(source_surfaces, entry["full_surface"])

    tense = tenses[0] if len(tenses) == 1 else None
    paradigm = (
        "simple_present_short"
        if tense == SIMPLE_PRESENT_TENSE
        else "present_progressive_short"
        if tense == PRESENT_PROGRESSIVE_TENSE
        else "present_short_contextual"
    )
    return SubjectFocusRestrictiveAnalysis(
        recognized=True,
        covered=True,
        surface=surface,
        expected_person=expected_person,
        restrictive_source_person=RESTRICTIVE_SOURCE_PERSON.get(expected_person),
        full_surface_persons=tuple(persons),
        contextual_persons=tuple(contextual),
        lemmas=tuple(lemmas),
        tense_aspects=tuple(tenses),
        agrees=bool(matching),
        paradigm=paradigm,
        source_full_surfaces=tuple(source_surfaces),
        note=(
            "The focused-subject reduced present form is licensed contextually from exact "
            "reviewed full finite morphology. The source-backed reduction shortens final "
            "-aa to -a and collapses agreement to default, 3sg-feminine, and 1pl classes. "
            "The reduced surface is not added to global morphology."
        ),
    )


def _finite_has_reuse_present(finite) -> bool:
    for lemma in finite.lemmas:
        allowed_tenses = PRESENT_REUSE_TENSES.get(lemma)
        if allowed_tenses and any(tense in allowed_tenses for tense in finite.tense_aspects):
            return True
    return False


def _analyze_special_present_surface(
    surface: str,
    expected_person: str,
) -> SubjectFocusRestrictiveAnalysis | None:
    key = surface.casefold()

    if key == "ah":
        return SubjectFocusRestrictiveAnalysis(
            recognized=True,
            covered=True,
            surface=surface,
            expected_person=expected_person,
            contextual_persons=ALL_CONTEXTUAL_PERSONS,
            lemmas=("ahaw/ah",),
            tense_aspects=(COPULAR_PRESENT_TENSE,),
            agrees=expected_person in ALL_CONTEXTUAL_PERSONS,
            paradigm="copular_present_invariant",
            note=(
                "Focused-subject copular present uses the source-backed invariant reduced "
                "absolutive form ah. This contextual form is kept separate from ordinary "
                "ahay/tahay/yahay/nahay/tihiin/yihiin agreement."
            ),
        )

    finite = analyze_reviewed_finite_verb(surface)
    if not finite.recognized or not _finite_has_reuse_present(finite):
        return None

    contextual = _contextual_persons(finite.persons)
    return SubjectFocusRestrictiveAnalysis(
        recognized=True,
        covered=True,
        surface=surface,
        expected_person=expected_person,
        restrictive_source_person=RESTRICTIVE_SOURCE_PERSON.get(expected_person),
        full_surface_persons=finite.persons,
        contextual_persons=contextual,
        lemmas=finite.lemmas,
        tense_aspects=finite.tense_aspects,
        agrees=expected_person in contextual,
        paradigm="simple_present_irregular_reuse",
        source_full_surfaces=(surface,),
        note=(
            "This source-backed irregular present paradigm reuses an exact reviewed surface "
            "under focused-subject reduced agreement. Person interpretation is contextual "
            "and does not alter the global lexical analysis."
        ),
    )


def _has_expected_short_form(lemma: str, tense: str, expected_person: str) -> bool:
    for entries in _short_present_index().values():
        for entry in entries:
            if (
                entry["lemma"] == lemma
                and entry["tense"] == tense
                and expected_person in entry["contextual_persons"]
            ):
                return True
    return False


def _past_progressive_supported(finite) -> bool:
    if PAST_PROGRESSIVE_TENSE not in finite.tense_aspects:
        return False
    return any(lemma not in PAST_PROGRESSIVE_EXCLUDED_LEMMAS for lemma in finite.lemmas)


def analyze_subject_focus_restrictive(
    surface: str,
    expected_person: str,
) -> SubjectFocusRestrictiveAnalysis:
    """Judge a predicate surface in a reviewed focused-subject context."""
    special = _analyze_special_present_surface(surface, expected_person)
    if special is not None:
        return special

    shortened = _analyze_short_present_surface(surface, expected_person)
    if shortened is not None:
        return shortened

    finite = analyze_reviewed_finite_verb(surface)
    if not finite.recognized:
        return SubjectFocusRestrictiveAnalysis(
            recognized=False,
            covered=False,
            surface=surface,
            expected_person=expected_person,
            note=(
                "No exact reviewed finite morphology or source-backed contextual reduced "
                "present surface exists for this form."
            ),
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

    if SIMPLE_PAST_TENSE in finite.tense_aspects:
        contextual = _contextual_persons(finite.persons)
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
            agrees=expected_person in contextual,
            paradigm="simple_past_reuse",
            source_full_surfaces=(surface,),
            note=(
                "Focused subjects use the source-backed restrictive simple-past mapping. "
                "The lexical surface remains exact reviewed morphology; only its person "
                "interpretation changes in focus context."
            ),
        )

    if _past_progressive_supported(finite):
        contextual = _contextual_persons(finite.persons)
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
            agrees=expected_person in contextual,
            paradigm="past_progressive_reuse",
            source_full_surfaces=(surface,),
            note=(
                "Focused subjects use the reviewed restrictive person classes in the past "
                "progressive while retaining exact main-clause past-progressive endings. "
                "The ordinary surface stays unchanged globally; only its person interpretation "
                "is reduced in true subject-focus context. AQAAN, AAL/YAAL and AHAW/AH are "
                "excluded because the reviewed grammar states that they do not have this form."
            ),
        )

    if (
        COPULAR_PRESENT_TENSE in finite.tense_aspects
        and any(lemma in COPULAR_LEMMAS for lemma in finite.lemmas)
    ):
        return SubjectFocusRestrictiveAnalysis(
            recognized=True,
            covered=True,
            surface=surface,
            expected_person=expected_person,
            restrictive_source_person=source_person,
            full_surface_persons=finite.persons,
            lemmas=finite.lemmas,
            tense_aspects=finite.tense_aspects,
            agrees=False,
            paradigm="copular_present_invariant",
            note=(
                "The ordinary copular present surface is not the focused-subject reduced form; "
                "the reviewed reduced absolutive form is invariant ah. No autofix is applied."
            ),
        )

    for tense in (SIMPLE_PRESENT_TENSE, PRESENT_PROGRESSIVE_TENSE):
        if tense not in finite.tense_aspects:
            continue
        if any(_has_expected_short_form(lemma, tense, expected_person) for lemma in finite.lemmas):
            return SubjectFocusRestrictiveAnalysis(
                recognized=True,
                covered=True,
                surface=surface,
                expected_person=expected_person,
                restrictive_source_person=source_person,
                full_surface_persons=finite.persons,
                lemmas=finite.lemmas,
                tense_aspects=finite.tense_aspects,
                agrees=False,
                paradigm=(
                    "simple_present_short"
                    if tense == SIMPLE_PRESENT_TENSE
                    else "present_progressive_short"
                ),
                note=(
                    "This is an ordinary full present/progressive finite surface. The exact "
                    "reviewed lemma has a source-backed focused-subject reduced counterpart, "
                    "so the full surface is a review-only agreement conflict in this context."
                ),
            )

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
            "The surface is exact reviewed finite morphology, but its tense/aspect or irregular "
            "paradigm is outside the currently modeled focused-subject restrictive coverage."
        ),
    )
