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
    evidence: str | None = None
    rule_id: str = "GRAM-CONNSTAT-001"
    note: str = ""


def analyze_connective_statement(sentence: str) -> ConnectiveStatementAnalysis:
    """Analyze reviewed second-clause connective statement forms.

    The connective form must be the first lexical token after an overt comma or
    semicolon. ``waana`` requires following predicate/clause material but does
    not encode a subject person, so no finite-agreement judgment is derived from
    it. For ``wuuna``/``wayna``, up to four intervening lexical tokens may
    precede an exact reviewed finite verb; if none is found, the connective form
    remains recognized but agreement is unjudged.
    """
    for boundary_match in CLAUSE_BOUNDARY_RE.finditer(sentence):
        tail = sentence[boundary_match.end() :].strip()
        tokens = TOKEN_RE.findall(tail)
        if len(tokens) < 2:
            continue

        particle = tokens[0]
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
                evidence="source_backed_declarative_particle_plus_conjunction_na+person_neutral_surface",
                rule_id="GRAM-CONNSTAT-005",
                note=(
                    f"{particle} is the reviewed person-neutral connective declarative form "
                    f"{base_particle} + -na ('and/so'). The form contains no short subject "
                    "pronoun, so no subject person, antecedent, or finite-verb agreement is "
                    "inferred from it. No automatic rewrite."
                ),
            )

        profile = CONNECTIVE_STATEMENT_CLITICS.get(particle.casefold())
        if profile is None:
            continue

        base_statement_clitic, subject_persons = profile
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
                evidence="source_backed_statement_subject_clitic_plus_conjunction_na+exact_reviewed_finite_morphology",
                rule_id="GRAM-CONNSTAT-003",
                note=(
                    f"{particle} is a reviewed connective statement form based on "
                    f"{base_statement_clitic} plus connective -na ('and'). Agreement is checked "
                    "only between the subject person(s) encoded by that exact form and an exact "
                    "reviewed finite verb. The antecedent is not inferred and no automatic "
                    "rewrite is used."
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
            evidence="source_backed_statement_subject_clitic_plus_conjunction_na+unreviewed_predicate",
            rule_id="GRAM-CONNSTAT-001",
            note=(
                f"{particle} is a reviewed connective statement form, but no exact reviewed "
                "finite verb was found in the local predicate window. Agreement remains "
                "unjudged; no verb form or antecedent is guessed."
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
