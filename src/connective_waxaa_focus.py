"""Conservative Somali connective waxaa-family focus analysis.

Four exact connective surfaces currently have independent source support:

- ``waxaana = waxaa + -na``: person-neutral focus particle plus connective.
- ``wuxuuna = wuxuu + -na``: cleft focus carrying reviewed ``uu`` subject
  compatibility (3sg masculine) plus connective.
- ``waxayna = waxay + -na``: cleft focus carrying reviewed ``ay`` subject
  compatibility (3sg feminine / 3pl) plus connective.
- ``waxaadna = waxaad + -na``: cleft focus carrying reviewed ``aad`` subject
  compatibility (2sg / 2pl) plus connective.

These forms are not generated from one another. Source evidence supports
sentence-initial/discourse-linking use for the previously reviewed exact forms
and describes ``-na`` as a conjunction between main clauses attached to the
first phrase of the second clause. The executable layer recognizes an exact
reviewed form after overt clause/sentence punctuation or in one narrowly
licensed unpunctuated configuration: immediately after an exact reviewed finite
verb. Independently attested sentence-initial forms are also recognized at input
start.

The ``waxa/waxaa`` construction is a final-focus construction: focused lexical
material follows the verb. For clitic-bearing connectives, when an exact
reviewed finite verb is found, this analyzer records whether lexical material
actually follows that verb. A missing final-focus tail is a review condition,
not an automatic rewrite.

A separate discourse-safety signal compares the right connective subject clitic
with the nearest reviewed statement subject clitic in the preceding text. A
disjoint person set does not make the sentence ungrammatical: it means that a
subject change requires context and therefore must not be presented as a plain
same-subject continuation. Unknown predicates remain unjudged, antecedents are
not inferred, and no automatic correction is performed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.reviewed_finite_verb import analyze_reviewed_finite_verb

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)
CLAUSE_BOUNDARY_RE = re.compile(r"[,;.!?]")
CONNECTIVE_WAXAA_CLITICS = {
    "wuxuuna": ("wuxuu", "uu", ("3sg_m",)),
    "waxayna": ("waxay", "ay", ("3sg_f", "3pl")),
    "waxaadna": ("waxaad", "aad", ("2sg", "2pl")),
}
STATEMENT_SUBJECT_CLITICS = {
    "wuu": ("3sg_m",),
    "way": ("3sg_f", "3pl"),
    "waad": ("2sg", "2pl"),
}
REVIEWED_CONNECTIVE_SURFACES = {"waxaana", *CONNECTIVE_WAXAA_CLITICS}
INPUT_START_CONNECTIVE_SURFACES = {"waxaana", "wuxuuna", "waxayna", "waxaadna"}
MAX_FINITE_GAP = 4
INPUT_START_BOUNDARY = "input_start"
REVIEWED_LEFT_FINITE_BOUNDARY = "reviewed_left_finite"


@dataclass(frozen=True)
class ConnectiveWaxaaFocusAnalysis:
    recognized: bool
    particle: str | None = None
    base_focus_particle: str | None = None
    base_focus_subject_form: str | None = None
    subject_clitic: str | None = None
    conjunction: str | None = None
    following_material: tuple[str, ...] = ()
    boundary: str | None = None
    subject_persons: tuple[str, ...] = ()
    verb: str | None = None
    verb_lemmas: tuple[str, ...] = ()
    verb_persons: tuple[str, ...] = ()
    agreement_agrees: bool | None = None
    focus_material: tuple[str, ...] = ()
    focus_structure_agrees: bool | None = None
    left_subject_clitic: str | None = None
    left_subject_persons: tuple[str, ...] = ()
    same_subject_continuity_agrees: bool | None = None
    evidence: str | None = None
    rule_id: str = "GRAM-CONNWAXAA-001"
    focus_rule_id: str | None = None
    continuity_rule_id: str | None = None
    note: str = ""


def _nearest_left_subject_context(text: str) -> tuple[str | None, tuple[str, ...]]:
    """Return the nearest exact reviewed statement subject clitic on the left."""
    tokens = TOKEN_RE.findall(text)
    for token in reversed(tokens):
        persons = STATEMENT_SUBJECT_CLITICS.get(token.casefold())
        if persons is not None:
            return token, persons
    return None, ()


def _continuity_value(
    left_subject_persons: tuple[str, ...],
    right_subject_persons: tuple[str, ...],
) -> bool | None:
    if not left_subject_persons or not right_subject_persons:
        return None
    return any(person in right_subject_persons for person in left_subject_persons)


def _analyze_clitic_connective(
    particle: str,
    tokens: list[str],
    boundary: str,
    left_subject_clitic: str | None = None,
    left_subject_persons: tuple[str, ...] = (),
) -> ConnectiveWaxaaFocusAnalysis | None:
    profile = CONNECTIVE_WAXAA_CLITICS.get(particle.casefold())
    if profile is None or len(tokens) < 2:
        return None

    base_focus_subject_form, subject_clitic, subject_persons = profile
    continuity = _continuity_value(left_subject_persons, subject_persons)
    if continuity is True:
        continuity_note = (
            "The nearest reviewed left statement subject clitic is compatible with the "
            "right connective subject person set, so same-subject continuation is possible."
        )
    elif continuity is False:
        continuity_note = (
            "The nearest reviewed left statement subject clitic has a disjoint person set. "
            "A subject switch may be grammatical, but it is context-required and must not "
            "be presented as a plain same-subject continuation."
        )
    else:
        continuity_note = (
            "No reviewed left statement subject clitic was available for a safe continuity "
            "judgment; antecedent identity remains unjudged."
        )

    verb_candidates = tokens[1 : 1 + MAX_FINITE_GAP + 1]

    for verb_offset, verb in enumerate(verb_candidates, start=1):
        finite = analyze_reviewed_finite_verb(verb)
        if not finite.recognized:
            continue

        agrees = any(person in finite.persons for person in subject_persons)
        focus_material = tuple(tokens[verb_offset + 1 :])
        focus_structure_agrees = bool(focus_material)
        if focus_structure_agrees:
            focus_note = (
                "The reviewed waxa/waxaa final-focus pattern is structurally supported "
                "because lexical material follows the exact reviewed finite verb."
            )
            focus_evidence = "+reviewed_final_focus_tail"
        else:
            focus_note = (
                "The reviewed waxa/waxaa pattern normally places focused lexical material "
                "after the verb, but none follows this exact reviewed finite verb. Treat "
                "the focus structure as REVIEW; do not silently treat it as a neutral "
                "waa-family statement and do not autofix."
            )
            focus_evidence = "+missing_reviewed_final_focus_tail"

        return ConnectiveWaxaaFocusAnalysis(
            recognized=True,
            particle=particle,
            base_focus_particle="waxaa",
            base_focus_subject_form=base_focus_subject_form,
            subject_clitic=subject_clitic,
            conjunction="-na",
            following_material=tuple(tokens[1:]),
            boundary=boundary,
            subject_persons=subject_persons,
            verb=verb,
            verb_lemmas=finite.lemmas,
            verb_persons=finite.persons,
            agreement_agrees=agrees,
            focus_material=focus_material,
            focus_structure_agrees=focus_structure_agrees,
            left_subject_clitic=left_subject_clitic,
            left_subject_persons=left_subject_persons,
            same_subject_continuity_agrees=continuity,
            evidence=(
                "source_backed_waxaa_focus_subject_clitic_plus_conjunction_na"
                "+sentence_or_clause_initial_distribution"
                "+exact_reviewed_finite_morphology"
                f"{focus_evidence}"
            ),
            rule_id="GRAM-CONNWAXAA-006",
            focus_rule_id="GRAM-CONNWAXAA-009",
            continuity_rule_id="GRAM-CONNWAXAA-010",
            note=(
                f"{particle} is an independently reviewed waxaa-family connective focus "
                f"form based on {base_focus_subject_form}, carrying subject clitic "
                f"{subject_clitic}, plus connective -na ('and'). Agreement is checked only "
                "between its encoded reviewed subject person(s) and an exact reviewed "
                f"finite verb. {focus_note} {continuity_note} No unseen verb form, "
                "punctuation rewrite, or automatic correction is inferred."
            ),
        )

    return ConnectiveWaxaaFocusAnalysis(
        recognized=True,
        particle=particle,
        base_focus_particle="waxaa",
        base_focus_subject_form=base_focus_subject_form,
        subject_clitic=subject_clitic,
        conjunction="-na",
        following_material=tuple(tokens[1:]),
        boundary=boundary,
        subject_persons=subject_persons,
        verb=verb_candidates[0] if verb_candidates else None,
        agreement_agrees=None,
        focus_structure_agrees=None,
        left_subject_clitic=left_subject_clitic,
        left_subject_persons=left_subject_persons,
        same_subject_continuity_agrees=continuity,
        evidence=(
            "source_backed_waxaa_focus_subject_clitic_plus_conjunction_na"
            "+sentence_or_clause_initial_distribution"
            "+unreviewed_predicate"
        ),
        rule_id="GRAM-CONNWAXAA-005",
        focus_rule_id="GRAM-CONNWAXAA-009",
        continuity_rule_id="GRAM-CONNWAXAA-010",
        note=(
            f"{particle} is an independently reviewed waxaa-family connective focus form "
            "in a licensed clause-initial position, but no exact reviewed finite verb was "
            f"found in the local predicate window. Agreement and final-focus structure remain "
            f"unjudged. {continuity_note} No punctuation repair or verb form is guessed."
        ),
    )


def _analyze_boundary_tokens(
    tokens: list[str],
    boundary: str,
    left_subject_clitic: str | None = None,
    left_subject_persons: tuple[str, ...] = (),
) -> ConnectiveWaxaaFocusAnalysis | None:
    if not tokens:
        return None

    particle = tokens[0]
    if particle.casefold() == "waxaana":
        return ConnectiveWaxaaFocusAnalysis(
            recognized=True,
            particle=particle,
            base_focus_particle="waxaa",
            conjunction="-na",
            following_material=tuple(tokens[1:]),
            boundary=boundary,
            subject_persons=(),
            agreement_agrees=None,
            focus_structure_agrees=None,
            left_subject_clitic=left_subject_clitic,
            left_subject_persons=left_subject_persons,
            same_subject_continuity_agrees=None,
            evidence=(
                "source_backed_waxaa_focus_particle_plus_conjunction_na"
                "+sentence_or_clause_initial_distribution"
                "+person_neutral_particle"
            ),
            rule_id="GRAM-CONNWAXAA-001",
            note=(
                "waxaana is analyzed only as the reviewed focus particle waxaa plus "
                "connective -na ('and'). Its clause-initial position is source-backed, "
                "but the particle itself does not encode a subject person. No hidden "
                "uu/ay/aad, prior discourse antecedent, verb agreement, punctuation "
                "rewrite, or automatic correction is inferred."
            ),
        )

    return _analyze_clitic_connective(
        particle,
        tokens,
        boundary,
        left_subject_clitic=left_subject_clitic,
        left_subject_persons=left_subject_persons,
    )


def _analyze_unpunctuated_after_reviewed_finite(
    sentence: str,
) -> ConnectiveWaxaaFocusAnalysis | None:
    """License one narrow punctuation-free main-clause boundary.

    The connective must be an exact reviewed surface and must be the lexical
    token immediately after an exact reviewed finite verb. Only whitespace may
    intervene. The left verb is used solely as a conservative clause-boundary
    anchor; its subject, tense, and relation to the connective are not inferred.
    """
    token_matches = list(TOKEN_RE.finditer(sentence))
    for index in range(1, len(token_matches)):
        particle_match = token_matches[index]
        if particle_match.group(0).casefold() not in REVIEWED_CONNECTIVE_SURFACES:
            continue

        previous_match = token_matches[index - 1]
        between = sentence[previous_match.end() : particle_match.start()]
        if between.strip():
            continue

        left_finite = analyze_reviewed_finite_verb(previous_match.group(0))
        if not left_finite.recognized:
            continue

        left_subject_clitic, left_subject_persons = _nearest_left_subject_context(
            sentence[: particle_match.start()]
        )
        tail_tokens = [match.group(0) for match in token_matches[index:]]
        return _analyze_boundary_tokens(
            tail_tokens,
            REVIEWED_LEFT_FINITE_BOUNDARY,
            left_subject_clitic=left_subject_clitic,
            left_subject_persons=left_subject_persons,
        )

    return None


def analyze_connective_waxaa_focus(sentence: str) -> ConnectiveWaxaaFocusAnalysis:
    """Analyze exact reviewed clause-initial waxaa-family connectives.

    ``waxaana`` is person-neutral. ``wuxuuna``, ``waxayna`` and ``waxaadna``
    carry exact reviewed subject-clitic person sets and may therefore be checked
    against exact reviewed finite morphology. Independently attested exact forms
    may occur at input start; all reviewed forms may occur after explicit clause
    punctuation or immediately after an exact reviewed finite verb in the narrow
    unpunctuated configuration. This function does not reconstruct preceding
    discourse and is not a productive morphology or punctuation generator.
    """
    stripped = sentence.lstrip()
    if stripped:
        first_match = TOKEN_RE.match(stripped)
        if (
            first_match is not None
            and first_match.group(0).casefold() in INPUT_START_CONNECTIVE_SURFACES
        ):
            start_tokens = TOKEN_RE.findall(stripped)
            start_result = _analyze_boundary_tokens(
                start_tokens,
                INPUT_START_BOUNDARY,
            )
            if start_result is not None:
                return start_result

    for boundary_match in CLAUSE_BOUNDARY_RE.finditer(sentence):
        tail = sentence[boundary_match.end() :].strip()
        tokens = TOKEN_RE.findall(tail)
        left_subject_clitic, left_subject_persons = _nearest_left_subject_context(
            sentence[: boundary_match.start()]
        )
        result = _analyze_boundary_tokens(
            tokens,
            boundary_match.group(0),
            left_subject_clitic=left_subject_clitic,
            left_subject_persons=left_subject_persons,
        )
        if result is not None:
            return result

    unpunctuated_result = _analyze_unpunctuated_after_reviewed_finite(sentence)
    if unpunctuated_result is not None:
        return unpunctuated_result

    return ConnectiveWaxaaFocusAnalysis(
        recognized=False,
        note=(
            "No licensed clause-initial exact reviewed waxaa-family connective was found. "
            "Unpunctuated mid-sentence recognition additionally requires lexical adjacency "
            "to an exact reviewed finite left predicate. Unknown left predicates and "
            "predicted related connective surfaces remain unjudged."
        ),
    )
