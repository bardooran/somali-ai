"""Conservative Somali connective ``waxaana`` focus-particle analysis.

Source evidence explicitly analyzes ``waxaana`` as ``waxaa + -na`` where
``waxaa`` is a focus particle and ``-na`` is connective 'and'. This module
therefore keeps ``waxaana`` separate from declarative ``waana``, statement
clitics ``wuuna/wayna``, and the ``baa/ayaa`` connective-focus families.

The first executable stage recognizes only exact clause-initial ``waxaana``
after an overt comma or semicolon. The form itself does not encode subject
person, so no hidden subject clitic, antecedent, or finite-verb agreement is
inferred and no automatic rewrite is performed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)
CLAUSE_BOUNDARY_RE = re.compile(r"[,;]")


@dataclass(frozen=True)
class ConnectiveWaxaaFocusAnalysis:
    recognized: bool
    particle: str | None = None
    base_focus_particle: str | None = None
    conjunction: str | None = None
    following_material: tuple[str, ...] = ()
    boundary: str | None = None
    subject_persons: tuple[str, ...] = ()
    agreement_agrees: bool | None = None
    evidence: str | None = None
    rule_id: str = "GRAM-CONNWAXAA-001"
    note: str = ""


def analyze_connective_waxaa_focus(sentence: str) -> ConnectiveWaxaaFocusAnalysis:
    """Recognize reviewed second-clause ``waxaana = waxaa + -na``.

    This is an exact-form recognizer, not a productive morphology rule. A comma
    or semicolon must establish a preceding clause and ``waxaana`` must be the
    first lexical token after that boundary. Because the reviewed form contains
    no subject clitic, agreement remains unjudged by this layer.
    """
    for boundary_match in CLAUSE_BOUNDARY_RE.finditer(sentence):
        tail = sentence[boundary_match.end() :].strip()
        tokens = TOKEN_RE.findall(tail)
        if not tokens or tokens[0].casefold() != "waxaana":
            continue

        return ConnectiveWaxaaFocusAnalysis(
            recognized=True,
            particle=tokens[0],
            base_focus_particle="waxaa",
            conjunction="-na",
            following_material=tuple(tokens[1:]),
            boundary=boundary_match.group(0),
            subject_persons=(),
            agreement_agrees=None,
            evidence="source_backed_waxaa_focus_particle_plus_conjunction_na+person_neutral_particle",
            rule_id="GRAM-CONNWAXAA-001",
            note=(
                "waxaana is analyzed only as the reviewed focus particle waxaa plus "
                "connective -na ('and'). The particle itself does not encode a subject "
                "person, so no hidden uu/ay, antecedent, or verb agreement is inferred. "
                "No automatic rewrite."
            ),
        )

    return ConnectiveWaxaaFocusAnalysis(
        recognized=False,
        note=(
            "No overt second-clause clause-initial exact waxaana frame was found. "
            "Sentence-initial/discourse-linking waxaana and predicted related forms remain "
            "context-dependent."
        ),
    )
