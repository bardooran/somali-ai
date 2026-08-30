"""Conservative singular noun-to-finite-verb agreement analysis.

This layer combines independently reviewed noun gender/number evidence with
exact reviewed finite-verb person and tense/aspect analyses. It does not infer
productive verb suffix rules and does not rewrite text automatically.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.morphology_candidates import analyze_surface_form
from src.noun_gender_agreement import infer_subject_gender, infer_subject_number
from src.noun_subject_case import PERSONAL_PRONOUN_FORMS
from src.reviewed_finite_verb import analyze_reviewed_finite_verb

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)
STATEMENT_CLITICS = {"wuu", "way"}
MAX_VERB_GAP = 3


@dataclass(frozen=True)
class NounSingularVerbAgreementAnalysis:
    recognized: bool
    subject: str | None = None
    subject_gender: str | None = None
    subject_number: str | None = None
    clitic: str | None = None
    verb: str | None = None
    verb_lemmas: tuple[str, ...] = ()
    verb_persons: tuple[str, ...] = ()
    verb_tense_aspects: tuple[str, ...] = ()
    verb_conjugation_classes: tuple[str, ...] = ()
    expected_person: str | None = None
    agrees: bool | None = None
    rule_id: str = "GRAM-NSINGVERB-001"
    note: str = ""


def _is_reviewed_conditional_auxiliary_context(tokens: list[str], verb_index: int) -> bool:
    """Keep lexical leeyahay past readings out of reviewed conditional spans."""
    if verb_index <= 0:
        return False
    auxiliary = any(
        candidate.analysis_type == "conditional_auxiliary"
        and candidate.features.get("construction") == "conditional"
        for candidate in analyze_surface_form(tokens[verb_index])
    )
    if not auxiliary:
        return False
    return any(
        candidate.analysis_type == "conditional_stem"
        and candidate.features.get("possible_use") == "conditional_with_auxiliary"
        for candidate in analyze_surface_form(tokens[verb_index - 1])
    )


def analyze_noun_singular_verb_agreement(sentence: str) -> NounSingularVerbAgreementAnalysis:
    """Check singular noun gender against an exact reviewed finite verb form.

    Current scope is ``<noun> wuu/way ... <verb>``. Masculine singular subjects
    require a reviewed 3sg_m-compatible finite verb; feminine singular subjects
    require 3sg_f compatibility. Reviewed tense/aspect is carried through as a
    separate feature. Unknown and non-finite verb forms remain unjudged.

    A surface such as ``lahaa`` can be both lexical possessive past and a
    conditional auxiliary. When it immediately follows an exact reviewed
    conditional stem, this generic finite layer yields to the conditional
    analyzer instead of reinterpreting the auxiliary as lexical possession.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 3:
        return NounSingularVerbAgreementAnalysis(recognized=False)

    for index in range(len(tokens) - 2):
        subject = tokens[index]
        clitic = tokens[index + 1]
        if subject.casefold() in PERSONAL_PRONOUN_FORMS:
            continue
        if clitic.casefold() not in STATEMENT_CLITICS:
            continue

        number, number_evidence = infer_subject_number(subject)
        gender, gender_evidence = infer_subject_gender(subject)
        if number != "singular" or gender not in {"masculine", "feminine"}:
            continue

        expected_person = "3sg_m" if gender == "masculine" else "3sg_f"
        upper = min(len(tokens), index + 2 + MAX_VERB_GAP)
        for verb_index in range(index + 2, upper):
            verb = tokens[verb_index]
            if _is_reviewed_conditional_auxiliary_context(tokens, verb_index):
                continue
            verb_analysis = analyze_reviewed_finite_verb(verb)
            if not verb_analysis.recognized or not verb_analysis.persons:
                continue

            return NounSingularVerbAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_gender=gender,
                subject_number=number,
                clitic=clitic,
                verb=verb,
                verb_lemmas=verb_analysis.lemmas,
                verb_persons=verb_analysis.persons,
                verb_tense_aspects=verb_analysis.tense_aspects,
                verb_conjugation_classes=verb_analysis.conjugation_classes,
                expected_person=expected_person,
                agrees=expected_person in verb_analysis.persons,
                note=(
                    f"Gender evidence: {gender_evidence}. Number evidence: {number_evidence}. "
                    "The verb decision uses only exact reviewed finite morphology and keeps "
                    "person separate from tense/aspect; unknown forms are not guessed."
                ),
            )

        return NounSingularVerbAgreementAnalysis(
            recognized=True,
            subject=subject,
            subject_gender=gender,
            subject_number=number,
            clitic=clitic,
            expected_person=expected_person,
            agrees=None,
            note=(
                f"Gender evidence: {gender_evidence}. Number evidence: {number_evidence}. "
                "No exact reviewed finite lexical verb was found outside a more specific reviewed construction; agreement and tense/aspect remain unjudged here."
            ),
        )

    return NounSingularVerbAgreementAnalysis(recognized=False)
