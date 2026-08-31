"""Conservative Somali connective statement analysis.

This module is deliberately separate from connective focus. Source evidence
supports three exact declarative/statement forms with connective ``-na``:

- ``wuuna = waa + uu + -na`` -> encoded 3sg masculine subject
- ``wayna = way + -na`` -> reviewed ``way`` person compatibility (3sg feminine/3pl)
- ``waana = waa + -na`` -> declarative particle plus connective, with no subject
  person encoded in the form itself

The executable stage recognizes only clause-initial exact forms after an overt
comma or semicolon. ``wuuna``/``wayna`` may check their encoded subject person(s)
against exact reviewed finite morphology. ``waana`` is person-neutral: it is
recognized without inventing a hidden short subject pronoun or agreement value.

A separate discourse-safety signal compares the right connective subject clitic
with the nearest reviewed statement subject clitic in the preceding clause.
Overlapping person sets make same-subject continuation compatible; disjoint sets
mean that a subject switch needs context. A disjoint set is not itself a grammar
error because ``-na`` connects clauses and the two clauses need not be assigned
one hidden discourse subject. No antecedent is reconstructed and no rewrite is
performed.

No broader ``waa + clitic + -na`` paradigm is generated and no form is rewritten.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.reviewed_finite_verb import analyze_reviewed_finite_verb

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)
CLAUSE_BOUNDARY_RE = re.compile(r"[,;]")
CONNECTIVE_STATEMENT_CLITICS = {
    "wuuna": ("wuu", ("3sg_m",)),
    "wayna": ("way", ("3sg_f", "3pl")),
}
CONNECTIVE_STATEMENT_PARTICLES = {"waana": "waa"}
STATEMENT_SUBJECT_CLITICS = {
    "wuu": ("3sg_m",),
    "way": ("3sg_f", "3pl"),
    "waad": ("2sg", "2pl"),
}
MAX_FINITE_GAP = 4


@dataclass(frozen=True)
class ConnectiveStatementAnalysis:
    recognized: bool
    particle: str | None = None
    base_statement_clitic: str | None = None
    subject_persons: tuple[str, ...] = ()
    verb: str | None = None
    verb_lemmas: tuple[str, ...] = ()
    verb_persons: tuple[str, ...] = ()
    agreement_agrees: bool | None = None
    conjunction: str | None = None
    boundary: str | None = None
    left_subject_clitic: str | None = None
    left_subject_persons: tuple[str, ...] = ()
    same_subject_continuity_agrees: bool | None = None
    evidence: str | None = None
    rule_id: str = "GRAM-CONNSTAT-001"
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


def _continuity_note(continuity: bool | None) -> str:
    if continuity is True:
        return (
            "The nearest reviewed left statement subject clitic is compatible with the "
            "right connective subject person set, so same-subject continuation is possible."
        )
    if continuity is False:
        return (
            "The nearest reviewed left statement subject clitic has a disjoint person set. "
            "A subject switch may be grammatical, but it is context-required and must not "
            "be presented as a plain same-subject continuation."
        )
    return (
        "No reviewed left statement subject clitic was available for a safe continuity "
        "judgment; antecedent identity remains unjudged."
    )


def analyze_connective_statement(sentence: str) -> ConnectiveStatementAnalysis:
    """Analyze reviewed second-clause connective statement forms.

    The connective form must be the first lexical token after an overt comma or
    semicolon. ``waana`` requires following predicate/clause material but does
    not encode a subject person, so no finite-agreement or continuity judgment is
    derived from it. For ``wuuna``/``wayna``, up to four intervening lexical
    tokens may precede an exact reviewed finite verb; if none is found, local
    finite agreement remains unjudged. Subject continuity is a separate signal
    based only on independently reviewed left and right statement subject clitics.
    """
    for boundary_match in CLAUSE_BOUNDARY_RE.finditer(sentence):
        tail = sentence[boundary_match.end() :].strip()
        tokens = TOKEN_RE.findall(tail)
        if len(tokens) < 2:
            continue

        particle = tokens[0]
        left_subject_clitic, left_subject_persons = _nearest_left_subject_context(
            sentence[: boundary_match.start()]
        )
        base_particle = CONNECTIVE_STATEMENT_PARTICLES.get(particle.casefold())
        if base_particle is not None:
            return ConnectiveStatementAnalysis(
                recognized=True,
                particle=particle,
                base_statement_clitic=base_particle,
                subject_persons=(),
                agreement_agrees=None,
                conjunction="-na",
                boundary=boundary_match.group(0),
                left_subject_clitic=left_subject_clitic,
                left_subject_persons=left_subject_persons,
                same_subject_continuity_agrees=None,
                evidence="source_backed_declarative_particle_plus_conjunction_na+person_neutral_surface",
                rule_id="GRAM-CONNSTAT-005",
                note=(
                    f"{particle} is the reviewed person-neutral connective declarative form "
                    f"{base_particle} + -na ('and/so'). The form contains no short subject "
                    "pronoun, so no subject person, antecedent, finite-verb agreement, or "
                    "same-subject continuity value is inferred from it. No automatic rewrite."
                ),
            )

        profile = CONNECTIVE_STATEMENT_CLITICS.get(particle.casefold())
        if profile is None:
            continue

        base_statement_clitic, subject_persons = profile
        continuity = _continuity_value(left_subject_persons, subject_persons)
        continuity_note = _continuity_note(continuity)
        verb_candidates = tokens[1 : 1 + MAX_FINITE_GAP + 1]
        if not verb_candidates:
            continue

        for verb in verb_candidates:
            finite = analyze_reviewed_finite_verb(verb)
            if not finite.recognized:
                continue

            agrees = any(person in finite.persons for person in subject_persons)
            return ConnectiveStatementAnalysis(
                recognized=True,
                particle=particle,
                base_statement_clitic=base_statement_clitic,
                subject_persons=subject_persons,
                verb=verb,
                verb_lemmas=finite.lemmas,
                verb_persons=finite.persons,
                agreement_agrees=agrees,
                conjunction="-na",
                boundary=boundary_match.group(0),
                left_subject_clitic=left_subject_clitic,
                left_subject_persons=left_subject_persons,
                same_subject_continuity_agrees=continuity,
                evidence=(
                    "source_backed_statement_subject_clitic_plus_conjunction_na"
                    "+exact_reviewed_finite_morphology+reviewed_clause_subject_continuity"
                ),
                rule_id="GRAM-CONNSTAT-003",
                continuity_rule_id="GRAM-CONNSTAT-006",
                note=(
                    f"{particle} is a reviewed connective statement form based on "
                    f"{base_statement_clitic} plus connective -na ('and'). Agreement is checked "
                    "only between the subject person(s) encoded by that exact form and an exact "
                    f"reviewed finite verb. {continuity_note} No unseen verb form, antecedent "
                    "identity, or automatic rewrite is inferred."
                ),
            )

        return ConnectiveStatementAnalysis(
            recognized=True,
            particle=particle,
            base_statement_clitic=base_statement_clitic,
            subject_persons=subject_persons,
            verb=verb_candidates[0],
            agreement_agrees=None,
            conjunction="-na",
            boundary=boundary_match.group(0),
            left_subject_clitic=left_subject_clitic,
            left_subject_persons=left_subject_persons,
            same_subject_continuity_agrees=continuity,
            evidence=(
                "source_backed_statement_subject_clitic_plus_conjunction_na"
                "+unreviewed_predicate+reviewed_clause_subject_continuity"
            ),
            rule_id="GRAM-CONNSTAT-001",
            continuity_rule_id="GRAM-CONNSTAT-006",
            note=(
                f"{particle} is a reviewed connective statement form, but no exact reviewed "
                "finite verb was found in the local predicate window. Local finite agreement "
                f"remains unjudged. {continuity_note} No verb form or antecedent is guessed."
            ),
        )

    return ConnectiveStatementAnalysis(
        recognized=False,
        note=(
            "No overt second-clause clause-initial reviewed wuuna/wayna/waana statement frame "
            "was found. Standalone forms and predicted waa+clitic+na combinations remain "
            "context-dependent."
        ),
    )
