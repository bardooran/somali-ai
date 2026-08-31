"""Conservative Somali connective waxaa-family focus analysis.

Three exact connective surfaces currently have independent source support:

- ``waxaana = waxaa + -na``: person-neutral focus particle plus connective.
- ``waxayna = waxay + -na``: cleft focus carrying reviewed ``ay`` subject
  compatibility (3sg feminine / 3pl) plus connective.
- ``waxaadna = waxaad + -na``: cleft focus carrying reviewed ``aad`` subject
  compatibility (2sg / 2pl) plus connective.

These forms are not generated from one another. Source evidence supports
sentence-initial/discourse-linking use and describes ``-na`` as a conjunction
between main clauses attached to the first phrase of the second clause. The
executable layer therefore recognizes an exact reviewed form at input start,
after overt clause/sentence punctuation, or in one narrowly licensed
unpunctuated configuration: immediately after an exact reviewed finite verb.
For clitic-bearing forms, agreement is checked only against an exact reviewed
finite verb on the right. Unknown predicates remain unjudged, antecedents are
not inferred, and no automatic rewrite is performed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.reviewed_finite_verb import analyze_reviewed_finite_verb

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)
CLAUSE_BOUNDARY_RE = re.compile(r"[,;.!?]")
CONNECTIVE_WAXAA_CLITICS = {
    "waxayna": ("waxay", "ay", ("3sg_f", "3pl")),
    "waxaadna": ("waxaad", "aad", ("2sg", "2pl")),
}
REVIEWED_CONNECTIVE_SURFACES = {"waxaana", *CONNECTIVE_WAXAA_CLITICS}
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
    evidence: str | None = None
    rule_id: str = "GRAM-CONNWAXAA-001"
    note: str = ""


def _analyze_clitic_connective(
    particle: str,
    tokens: list[str],
    boundary: str,
) -> ConnectiveWaxaaFocusAnalysis | None:
    profile = CONNECTIVE_WAXAA_CLITICS.get(particle.casefold())
    if profile is None or len(tokens) < 2:
        return None

    base_focus_subject_form, subject_clitic, subject_persons = profile
    verb_candidates = tokens[1 : 1 + MAX_FINITE_GAP + 1]

    for verb in verb_candidates:
        finite = analyze_reviewed_finite_verb(verb)
        if not finite.recognized:
            continue

        agrees = any(person in finite.persons for person in subject_persons)
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
            evidence=(
                "source_backed_waxaa_focus_subject_clitic_plus_conjunction_na"
                "+sentence_or_clause_initial_distribution"
                "+exact_reviewed_finite_morphology"
            ),
            rule_id="GRAM-CONNWAXAA-006",
            note=(
                f"{particle} is an independently reviewed waxaa-family connective focus "
                f"form based on {base_focus_subject_form}, carrying subject clitic "
                f"{subject_clitic}, plus connective -na ('and'). Its clause-initial "
                "position is source-backed. Agreement is checked only between its encoded "
                "reviewed subject person(s) and an exact reviewed finite verb. No prior "
                "discourse antecedent, unseen verb form, punctuation rewrite, or automatic "
                "correction is inferred."
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
        evidence=(
            "source_backed_waxaa_focus_subject_clitic_plus_conjunction_na"
            "+sentence_or_clause_initial_distribution"
            "+unreviewed_predicate"
        ),
        rule_id="GRAM-CONNWAXAA-005",
        note=(
            f"{particle} is an independently reviewed waxaa-family connective focus form "
            "in a licensed clause-initial position, but no exact reviewed finite verb was "
            "found in the local predicate window. Agreement remains unjudged; no prior "
            "discourse antecedent, punctuation repair, or verb form is guessed."
        ),
    )


def _analyze_boundary_tokens(
    tokens: list[str],
    boundary: str,
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

    return _analyze_clitic_connective(particle, tokens, boundary)


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

        tail_tokens = [match.group(0) for match in token_matches[index:]]
        return _analyze_boundary_tokens(
            tail_tokens,
            REVIEWED_LEFT_FINITE_BOUNDARY,
        )

    return None


def analyze_connective_waxaa_focus(sentence: str) -> ConnectiveWaxaaFocusAnalysis:
    """Analyze exact reviewed clause-initial waxaa-family connectives.

    ``waxaana`` is person-neutral. ``waxayna`` and ``waxaadna`` carry exact
    reviewed subject-clitic person sets and may therefore be checked against
    exact reviewed finite morphology. Exact reviewed forms may occur at input
    start, immediately after explicit comma/semicolon/sentence punctuation, or
    immediately after an exact reviewed finite verb in the narrow unpunctuated
    configuration. This function does not reconstruct preceding discourse and
    is not a productive morphology or punctuation generator.
    """
    stripped = sentence.lstrip()
    if stripped:
        first_match = TOKEN_RE.match(stripped)
        if first_match is not None:
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
        result = _analyze_boundary_tokens(tokens, boundary_match.group(0))
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
