"""Conservative Somali connective subject-focus analysis.

Somali conjunction ``-na`` ('and') attaches to an early word in the second
clause. Source evidence explicitly supports ``ayaana = ayaa + -na`` and
``baana = baa + -na``. This first executable stage recognizes those two bare
focus+conjunction forms only when an overt comma or semicolon establishes a
preceding clause.

The analyzer removes only connective ``-na`` internally and delegates the
resulting ``SUBJECT + ayaa/baa + ...`` clause to the existing subject-focus
case and restrictive-agreement analyzers. It does not treat ``ayaana`` as
negative ``ayaan`` and does not infer clitic-bearing forms such as buuna/beyna.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.noun_subject_case import analyze_noun_subject_case
from src.subject_focus_agreement import analyze_subject_focus_agreement

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)
CLAUSE_BOUNDARY_RE = re.compile(r"[,;]")
CONNECTIVE_FOCUS_PARTICLES = {"ayaana": "ayaa", "baana": "baa"}


@dataclass(frozen=True)
class ConnectiveFocusAnalysis:
    recognized: bool
    subject: str | None = None
    particle: str | None = None
    base_particle: str | None = None
    conjunction: str | None = None
    predicate: str | None = None
    expected_person: str | None = None
    agreement_agrees: bool | None = None
    case_agrees: bool | None = None
    expected_subject_form: str | None = None
    normalized_clause: str | None = None
    boundary: str | None = None
    evidence: str | None = None
    rule_id: str = "GRAM-CONNFOCUS-001"
    note: str = ""


def _normalized_base_particle(surface: str) -> str | None:
    return CONNECTIVE_FOCUS_PARTICLES.get(surface.casefold())


def analyze_connective_subject_focus(sentence: str) -> ConnectiveFocusAnalysis:
    """Analyze reviewed second-clause ``SUBJECT + ayaana/baana + ...`` focus.

    A comma or semicolon is required in this first stage. This is intentionally
    narrower than Somali usage in general: ``-na`` itself can connect clauses
    without punctuation, but treating every standalone ayaana/baana as a full
    second clause would be unsafe before broader clause segmentation exists.
    """
    for boundary_match in CLAUSE_BOUNDARY_RE.finditer(sentence):
        tail = sentence[boundary_match.end() :].strip()
        tokens = TOKEN_RE.findall(tail)
        if len(tokens) < 3:
            continue

        subject, particle = tokens[0], tokens[1]
        base_particle = _normalized_base_particle(particle)
        if base_particle is None:
            continue

        normalized_clause = " ".join((subject, base_particle, *tokens[2:]))
        agreement = analyze_subject_focus_agreement(normalized_clause)
        case = analyze_noun_subject_case(normalized_clause)

        # This stage is specifically reviewed true subject focus. A connective
        # focus particle before an unreviewed/adverbial focus constituent is not
        # promoted merely because ayaana/baana is present.
        if not agreement.recognized and not case.recognized:
            continue

        predicate = agreement.predicate
        if predicate is None and len(tokens) >= 3:
            predicate = tokens[2]

        evidence_parts = ["source_backed_focus_plus_conjunction_na"]
        if agreement.evidence:
            evidence_parts.append(agreement.evidence)
        if case.recognized:
            evidence_parts.append("reviewed_subject_focus_case")

        return ConnectiveFocusAnalysis(
            recognized=True,
            subject=subject,
            particle=particle,
            base_particle=base_particle,
            conjunction="-na",
            predicate=predicate,
            expected_person=agreement.expected_person if agreement.recognized else None,
            agreement_agrees=agreement.agrees if agreement.recognized else None,
            case_agrees=case.agrees if case.recognized else None,
            expected_subject_form=(
                case.expected_subject_form if case.recognized else subject
            ),
            normalized_clause=normalized_clause,
            boundary=boundary_match.group(0),
            evidence="+".join(evidence_parts),
            note=(
                f"{particle} is analyzed as {base_particle} + connective -na ('and') in an "
                "overt second-clause context. Only -na is removed for analysis; subject-focus "
                "case and restrictive predicate agreement are inherited from the reviewed "
                f"{base_particle} construction. ayaana/baana are not negative-focus markers. "
                "No automatic rewrite."
            ),
        )

    return ConnectiveFocusAnalysis(
        recognized=False,
        note=(
            "No overt second-clause reviewed ayaana/baana true-subject-focus frame was found. "
            "Standalone connective forms and other -na attachments remain context-dependent."
        ),
    )
