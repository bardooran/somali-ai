"""Conservative Somali connective focus analysis.

Somali conjunction ``-na`` ('and') can attach to a focus marker in the second
of two conjoined clauses. The executable scope is deliberately split by role:

- ``ayaana = ayaa + -na`` and ``baana = baa + -na`` are modeled only for
  reviewed true subject focus and delegate to the existing restrictive
  subject-focus case/agreement analyzers.
- ``buuna = b=uu=na`` and lexical ``beyna`` are modeled as focus markers that
  already contain a subject clitic. For these forms we check only whether the
  encoded subject person is compatible with an exact reviewed finite verb.

All executable connective forms require an overt comma or semicolon establishing
a preceding clause. The checker never generates an unattested clitic+``-na``
paradigm, never infers the antecedent of the subject clitic, and never rewrites a
connective focus form automatically.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.noun_subject_case import analyze_noun_subject_case
from src.reviewed_finite_verb import analyze_reviewed_finite_verb
from src.subject_focus_agreement import analyze_subject_focus_agreement

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)
CLAUSE_BOUNDARY_RE = re.compile(r"[,;]")
CONNECTIVE_FOCUS_PARTICLES = {"ayaana": "ayaa", "baana": "baa"}
CONNECTIVE_FOCUS_CLITICS = {
    "buuna": ("buu", ("3sg_m",)),
    "beyna": ("bay", ("3sg_f", "3pl")),
}
MAX_FINITE_GAP = 4


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


@dataclass(frozen=True)
class ConnectiveCliticFocusAnalysis:
    recognized: bool
    focused_phrase: tuple[str, ...] = ()
    particle: str | None = None
    base_focus_clitic: str | None = None
    subject_persons: tuple[str, ...] = ()
    verb: str | None = None
    verb_lemmas: tuple[str, ...] = ()
    verb_persons: tuple[str, ...] = ()
    agreement_agrees: bool | None = None
    conjunction: str | None = None
    boundary: str | None = None
    evidence: str | None = None
    rule_id: str = "GRAM-CONNFOCUS-006"
    note: str = ""


def _normalized_base_particle(surface: str) -> str | None:
    return CONNECTIVE_FOCUS_PARTICLES.get(surface.casefold())


def analyze_connective_subject_focus(sentence: str) -> ConnectiveFocusAnalysis:
    """Analyze reviewed second-clause ``SUBJECT + ayaana/baana + ...`` focus.

    A comma or semicolon is required. This is intentionally narrower than Somali
    usage in general: ``-na`` itself can connect clauses without punctuation, but
    treating every standalone ayaana/baana as a complete second clause would be
    unsafe before broader clause segmentation exists.
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

        # This path is specifically reviewed true subject focus. A connective
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


def analyze_connective_clitic_focus(sentence: str) -> ConnectiveCliticFocusAnalysis:
    """Analyze reviewed second-clause focus with ``buuna`` or ``beyna``.

    Supported shape::

        preceding clause ,|; FOCUSED_PHRASE + buuna/beyna + ... + FINITE_VERB

    One to four tokens may make up the pre-clitic focused phrase, and up to four
    intervening tokens may precede the finite verb. The function does not assign
    a semantic role to that focused phrase. It checks only the subject person
    already encoded by the reviewed focus clitic against exact finite morphology.
    """
    for boundary_match in CLAUSE_BOUNDARY_RE.finditer(sentence):
        tail = sentence[boundary_match.end() :].strip()
        tokens = TOKEN_RE.findall(tail)
        if len(tokens) < 3:
            continue

        max_clitic_index = min(len(tokens) - 1, 5)
        for clitic_index in range(1, max_clitic_index):
            particle = tokens[clitic_index]
            profile = CONNECTIVE_FOCUS_CLITICS.get(particle.casefold())
            if profile is None:
                continue

            base_focus_clitic, subject_persons = profile
            focused_phrase = tuple(tokens[:clitic_index])
            verb_candidates = tokens[
                clitic_index + 1 : clitic_index + 1 + MAX_FINITE_GAP + 1
            ]
            if not verb_candidates:
                continue

            for verb in verb_candidates:
                finite = analyze_reviewed_finite_verb(verb)
                if not finite.recognized:
                    continue

                agrees = any(person in finite.persons for person in subject_persons)
                return ConnectiveCliticFocusAnalysis(
                    recognized=True,
                    focused_phrase=focused_phrase,
                    particle=particle,
                    base_focus_clitic=base_focus_clitic,
                    subject_persons=subject_persons,
                    verb=verb,
                    verb_lemmas=finite.lemmas,
                    verb_persons=finite.persons,
                    agreement_agrees=agrees,
                    conjunction="-na",
                    boundary=boundary_match.group(0),
                    evidence="source_backed_focus_subject_clitic_plus_conjunction_na+exact_reviewed_finite_morphology",
                    rule_id="GRAM-CONNFOCUS-007",
                    note=(
                        f"{particle} is a reviewed connective focus form whose base subject-clitic "
                        f"focus form is {base_focus_clitic}; only connective -na is removed "
                        "conceptually. Agreement is checked between the encoded subject person(s) "
                        "and an exact reviewed finite verb. The antecedent and semantic role of the "
                        "focused phrase are not inferred. No automatic rewrite."
                    ),
                )

            # The connective form itself is reviewed, but the following predicate
            # is not. Preserve recognition without guessing verb morphology.
            return ConnectiveCliticFocusAnalysis(
                recognized=True,
                focused_phrase=focused_phrase,
                particle=particle,
                base_focus_clitic=base_focus_clitic,
                subject_persons=subject_persons,
                verb=verb_candidates[0],
                agreement_agrees=None,
                conjunction="-na",
                boundary=boundary_match.group(0),
                evidence="source_backed_focus_subject_clitic_plus_conjunction_na+unreviewed_predicate",
                rule_id="GRAM-CONNFOCUS-006",
                note=(
                    f"{particle} is a reviewed connective focus form, but no exact reviewed finite "
                    "verb was found in the local predicate window. Agreement remains unjudged; no "
                    "verb form or antecedent is guessed."
                ),
            )

    return ConnectiveCliticFocusAnalysis(
        recognized=False,
        note=(
            "No overt second-clause reviewed buuna/beyna focus frame was found. Standalone forms "
            "and predicted clitic+na combinations remain context-dependent."
        ),
    )
