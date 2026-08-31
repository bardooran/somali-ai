"""Conservative Somali connective waxaa-family focus analysis.

Three exact connective surfaces currently have independent source support:

- ``waxaana = waxaa + -na``: person-neutral focus particle plus connective.
- ``waxayna = waxay + -na``: cleft focus carrying reviewed ``ay`` subject
  compatibility (3sg feminine / 3pl) plus connective.
- ``waxaadna = waxaad + -na``: cleft focus carrying reviewed ``aad`` subject
  compatibility (2sg / 2pl) plus connective.

These forms are not generated from one another. Source evidence also supports
sentence-initial/discourse-linking use, so the executable layer recognizes an
exact reviewed form either at the left edge of the analyzed input or immediately
after overt clause/sentence punctuation. For clitic-bearing forms, agreement is
checked only against an exact reviewed finite verb. Unknown predicates remain
unjudged, antecedents are not inferred, and no automatic rewrite is performed.
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
MAX_FINITE_GAP = 4
INPUT_START_BOUNDARY = "input_start"


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
                f"{subject_clitic}, plus connective -na ('and'). Its sentence/clause-initial "
                "position is source-backed. Agreement is checked only between its encoded "
                "reviewed subject person(s) and an exact reviewed finite verb. No prior "
                "discourse antecedent, unseen verb form, or automatic rewrite is inferred."
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
            "in a licensed sentence/clause-initial position, but no exact reviewed finite "
            "verb was found in the local predicate window. Agreement remains unjudged; "
            "no prior discourse antecedent or verb form is guessed."
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
                "connective -na ('and'). Its sentence/clause-initial position is "
                "source-backed, but the particle itself does not encode a subject person. "
                "No hidden uu/ay/aad, prior discourse antecedent, verb agreement, or "
                "automatic rewrite is inferred."
            ),
        )

    return _analyze_clitic_connective(particle, tokens, boundary)


def analyze_connective_waxaa_focus(sentence: str) -> ConnectiveWaxaaFocusAnalysis:
    """Analyze exact reviewed sentence/clause-initial waxaa-family connectives.

    ``waxaana`` is person-neutral. ``waxayna`` and ``waxaadna`` carry exact
    reviewed subject-clitic person sets and may therefore be checked against
    exact reviewed finite morphology. Exact reviewed forms may occur at input
    start or immediately after explicit comma, semicolon, period, question mark,
    or exclamation mark. This function does not reconstruct preceding discourse
    and is not a productive morphology generator.
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

    return ConnectiveWaxaaFocusAnalysis(
        recognized=False,
        note=(
            "No sentence/clause-initial exact reviewed waxaa-family connective was found. "
            "Only independently reviewed surfaces are executable; predicted related forms "
            "remain unjudged."
        ),
    )
