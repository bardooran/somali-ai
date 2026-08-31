"""Conservative Somali connective waxaa-family focus analysis.

Three exact connective surfaces currently have independent source support:

- ``waxaana = waxaa + -na``: person-neutral focus particle plus connective.
- ``waxayna = waxay + -na``: cleft focus carrying reviewed ``ay`` subject
  compatibility (3sg feminine / 3pl) plus connective.
- ``waxaadna = waxaad + -na``: cleft focus carrying reviewed ``aad`` subject
  compatibility (2sg / 2pl) plus connective.

These forms are not generated from one another. The executable layer requires
an overt comma or semicolon and clause-initial placement in the second clause.
For clitic-bearing forms, agreement is checked only against an exact reviewed
finite verb. Unknown predicates remain unjudged, antecedents are not inferred,
and no automatic rewrite is performed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.reviewed_finite_verb import analyze_reviewed_finite_verb

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)
CLAUSE_BOUNDARY_RE = re.compile(r"[,;]")
CONNECTIVE_WAXAA_CLITICS = {
    "waxayna": ("waxay", "ay", ("3sg_f", "3pl")),
    "waxaadna": ("waxaad", "aad", ("2sg", "2pl")),
}
MAX_FINITE_GAP = 4


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
                "+exact_reviewed_finite_morphology"
            ),
            rule_id="GRAM-CONNWAXAA-006",
            note=(
                f"{particle} is an independently reviewed waxaa-family connective focus "
                f"form based on {base_focus_subject_form}, carrying subject clitic "
                f"{subject_clitic}, plus connective -na ('and'). Agreement is checked only "
                "between its encoded reviewed subject person(s) and an exact reviewed "
                "finite verb. No antecedent, unseen verb form, or automatic rewrite is "
                "inferred."
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
            "+unreviewed_predicate"
        ),
        rule_id="GRAM-CONNWAXAA-005",
        note=(
            f"{particle} is an independently reviewed waxaa-family connective focus form, "
            "but no exact reviewed finite verb was found in the local predicate window. "
            "Agreement remains unjudged; no verb form or antecedent is guessed."
        ),
    )


def analyze_connective_waxaa_focus(sentence: str) -> ConnectiveWaxaaFocusAnalysis:
    """Analyze exact reviewed second-clause waxaa-family connective forms.

    ``waxaana`` is person-neutral. ``waxayna`` and ``waxaadna`` carry exact
    reviewed subject-clitic person sets and may therefore be checked against
    exact reviewed finite morphology. This function is an exact-form recognizer,
    not a productive morphology generator.
    """
    for boundary_match in CLAUSE_BOUNDARY_RE.finditer(sentence):
        tail = sentence[boundary_match.end() :].strip()
        tokens = TOKEN_RE.findall(tail)
        if not tokens:
            continue

        particle = tokens[0]
        if particle.casefold() == "waxaana":
            return ConnectiveWaxaaFocusAnalysis(
                recognized=True,
                particle=particle,
                base_focus_particle="waxaa",
                conjunction="-na",
                following_material=tuple(tokens[1:]),
                boundary=boundary_match.group(0),
                subject_persons=(),
                agreement_agrees=None,
                evidence=(
                    "source_backed_waxaa_focus_particle_plus_conjunction_na"
                    "+person_neutral_particle"
                ),
                rule_id="GRAM-CONNWAXAA-001",
                note=(
                    "waxaana is analyzed only as the reviewed focus particle waxaa plus "
                    "connective -na ('and'). The particle itself does not encode a subject "
                    "person, so no hidden uu/ay/aad, antecedent, or verb agreement is "
                    "inferred. No automatic rewrite."
                ),
            )

        clitic_result = _analyze_clitic_connective(
            particle,
            tokens,
            boundary_match.group(0),
        )
        if clitic_result is not None:
            return clitic_result

    return ConnectiveWaxaaFocusAnalysis(
        recognized=False,
        note=(
            "No overt second-clause clause-initial exact reviewed waxaa-family connective "
            "was found. Sentence-initial/discourse-linking forms and predicted related "
            "surfaces remain context-dependent."
        ),
    )
