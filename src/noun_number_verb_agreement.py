"""Conservative noun-number to finite-verb agreement analysis.

This layer only judges a sentence when two independent pieces of reviewed
evidence are available:

1. the explicit noun subject is analyzed as plural by native review or reviewed
   noun morphology; and
2. the finite verb surface has an exact reviewed morphology analysis with
   person information.

Reviewed tense/aspect is carried through separately from person. Unknown noun
number, unknown verbs, and non-finite forms remain unjudged, so the analyzer
never invents productive verb suffix rules.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.morphology_candidates import analyze_surface_form
from src.noun_gender_agreement import infer_subject_number
from src.noun_subject_case import PERSONAL_PRONOUN_FORMS
from src.reviewed_finite_verb import analyze_reviewed_finite_verb

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)
STATEMENT_CLITICS = {"wuu", "way"}
MAX_VERB_GAP = 3


@dataclass(frozen=True)
class NounNumberVerbAgreementAnalysis:
    recognized: bool
    subject: str | None = None
    subject_number: str | None = None
    number_evidence: str | None = None
    clitic: str | None = None
    verb: str | None = None
    verb_lemmas: tuple[str, ...] = ()
    verb_persons: tuple[str, ...] = ()
    verb_tense_aspects: tuple[str, ...] = ()
    verb_conjugation_classes: tuple[str, ...] = ()
    agrees: bool | None = None
    expected_person: str | None = None
    rule_id: str = "GRAM-NNUMVERB-001"
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


def analyze_noun_number_verb_agreement(sentence: str) -> NounNumberVerbAgreementAnalysis:
    """Check reviewed plural noun subjects against reviewed finite verb person.

    Current scope is an explicit ``<noun> wuu/way ... <verb>`` statement. The
    verb may occur within a short local window after the clitic. A reviewed 3pl
    analysis is accepted. A reviewed verb whose available persons exclude 3pl
    is a review-only conflict. Tense/aspect is reported independently. If the
    verb has no exact reviewed finite analysis, the sentence remains unjudged.

    When a surface such as ``lahaayeen`` immediately follows a reviewed
    conditional stem, this generic finite layer yields to the conditional
    analyzer rather than reinterpreting the auxiliary as lexical possession.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 3:
        return NounNumberVerbAgreementAnalysis(recognized=False)

    for index in range(len(tokens) - 2):
        subject = tokens[index]
        clitic = tokens[index + 1]
        if subject.casefold() in PERSONAL_PRONOUN_FORMS:
            continue
        if clitic.casefold() not in STATEMENT_CLITICS:
            continue

        number, number_evidence = infer_subject_number(subject)
        if number != "plural":
            continue

        upper = min(len(tokens), index + 2 + MAX_VERB_GAP)
        for verb_index in range(index + 2, upper):
            verb = tokens[verb_index]
            if _is_reviewed_conditional_auxiliary_context(tokens, verb_index):
                continue
            verb_analysis = analyze_reviewed_finite_verb(verb)
            if not verb_analysis.recognized or not verb_analysis.persons:
                continue

            agrees = "3pl" in verb_analysis.persons
            return NounNumberVerbAgreementAnalysis(
                recognized=True,
                subject=subject,
                subject_number="plural",
                number_evidence=number_evidence,
                clitic=clitic,
                verb=verb,
                verb_lemmas=verb_analysis.lemmas,
                verb_persons=verb_analysis.persons,
                verb_tense_aspects=verb_analysis.tense_aspects,
                verb_conjugation_classes=verb_analysis.conjugation_classes,
                agrees=agrees,
                expected_person="3pl",
                note=(
                    "The noun subject has reviewed plural-number evidence and the verb has "
                    "an exact reviewed finite analysis. Person and tense/aspect are kept "
                    "separate; no suffix-only inference or automatic rewrite is used."
                ),
            )

        return NounNumberVerbAgreementAnalysis(
            recognized=True,
            subject=subject,
            subject_number="plural",
            number_evidence=number_evidence,
            clitic=clitic,
            agrees=None,
            expected_person="3pl",
            note=(
                "Plural subject recognized, but no exact reviewed finite lexical verb was found outside a more specific reviewed construction; verb agreement and tense/aspect remain unjudged here."
            ),
        )

    return NounNumberVerbAgreementAnalysis(recognized=False)
