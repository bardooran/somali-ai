"""Conservative noun-subject gender agreement analysis.

The analyzer separates grammatical gender from number. Strong subject-surface
suffixes can reveal gender, but they do not always reveal singular/plural. A
third-person plural subject can also use ``way``. Therefore masculine subjects
are only required to use ``wuu`` when singular number has independent project
evidence. Feminine subject surfaces safely reject ``wuu`` because both 3sg
feminine and 3pl use the ay/way family in the current project evidence.

This layer is review-only and never rewrites text.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from src.morphology_candidates import analyze_surface_form
from src.noun_subject_case import PERSONAL_PRONOUN_FORMS, expected_non_subject_form

RULE_PATH = Path("rules/grammar/noun_subject_gender_agreement.jsonl")
TOKEN_RE = re.compile(r"[^\W\d_]+", flags=re.UNICODE)

# Surface signals whose consonant belongs to a sufficiently clear determiner
# family in the currently reviewed data. -hu/-u are intentionally excluded.
STRONG_GENDER_SUFFIXES = (
    ("shu", "feminine"),
    ("tu", "feminine"),
    ("du", "feminine"),
    ("ku", "masculine"),
    ("gu", "masculine"),
)

STATEMENT_CLITICS = {"wuu", "way"}
SINGULAR_COPULAS = {"yahay", "tahay"}


@dataclass(frozen=True)
class NounGenderAgreementAnalysis:
    recognized: bool
    subject: str | None = None
    gender: str | None = None
    number: str | None = None
    number_evidence: str | None = None
    clitic: str | None = None
    expected_clitic: str | None = None
    clitic_agrees: bool | None = None
    copula: str | None = None
    expected_copula: str | None = None
    copula_agrees: bool | None = None
    rule_id: str = "GRAM-NGENDER-001"
    note: str = ""


def _load_reviewed_singular_forms() -> dict[str, str]:
    if not RULE_PATH.exists():
        return {}
    for line in RULE_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("id") != "GRAM-NGENDER-002":
            continue
        return {
            item["form"].casefold(): item["gender"]
            for item in record.get("forms", [])
        }
    return {}


REVIEWED_SINGULAR_FORMS = _load_reviewed_singular_forms()


def infer_subject_gender(form: str) -> tuple[str | None, str]:
    """Return ``(gender, evidence)`` without guessing ambiguous surfaces."""
    folded = form.casefold().strip()
    if folded in PERSONAL_PRONOUN_FORMS:
        return None, "personal_pronoun_excluded"

    reviewed = REVIEWED_SINGULAR_FORMS.get(folded)
    if reviewed:
        return reviewed, "native_reviewed_singular_subject"

    for suffix, gender in STRONG_GENDER_SUFFIXES:
        if folded.endswith(suffix):
            return gender, f"strong_subject_suffix:{suffix}"

    return None, "gender_not_safely_inferable"


def infer_subject_number(form: str) -> tuple[str | None, str]:
    """Infer singular only from explicit review or stored singular morphology."""
    folded = form.casefold().strip()
    if folded in REVIEWED_SINGULAR_FORMS:
        return "singular", "native_reviewed_singular_subject"

    paired = expected_non_subject_form(form)
    if paired is None:
        return None, "number_not_safely_inferable"

    for candidate in analyze_surface_form(paired):
        if candidate.features.get("number") == "singular":
            return "singular", "paired_reviewed_morphology"

    return None, "number_not_safely_inferable"


def _find_singular_copula(tokens: list[str], subject_index: int) -> str | None:
    for token in tokens[subject_index + 2 : subject_index + 8]:
        if token.casefold() in SINGULAR_COPULAS:
            return token
    return None


def analyze_noun_gender_agreement(sentence: str) -> NounGenderAgreementAnalysis:
    """Analyze a noun subject followed by ``wuu``/``way``.

    Gender is inferred conservatively. Number is independent. The analyzer can
    therefore return a recognized construction while leaving a masculine
    ``way`` sequence unresolved if singularity is not known.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 2:
        return NounGenderAgreementAnalysis(recognized=False)

    for index in range(len(tokens) - 1):
        subject = tokens[index]
        clitic = tokens[index + 1]
        if clitic.casefold() not in STATEMENT_CLITICS:
            continue
        if subject.casefold() in PERSONAL_PRONOUN_FORMS:
            continue

        gender, gender_evidence = infer_subject_gender(subject)
        if gender is None:
            continue

        number, number_evidence = infer_subject_number(subject)
        expected_clitic: str | None = None
        clitic_agrees: bool | None = None

        if gender == "feminine":
            # Both reviewed 3sg feminine and 3pl statement patterns use ay/way;
            # wuu is therefore incompatible even when number is unknown.
            expected_clitic = "way"
            clitic_agrees = clitic.casefold() == "way"
        elif gender == "masculine" and number == "singular":
            expected_clitic = "wuu"
            clitic_agrees = clitic.casefold() == "wuu"

        copula = _find_singular_copula(tokens, index)
        expected_copula: str | None = None
        copula_agrees: bool | None = None
        if copula is not None and number == "singular":
            expected_copula = "yahay" if gender == "masculine" else "tahay"
            copula_agrees = copula.casefold() == expected_copula

        return NounGenderAgreementAnalysis(
            recognized=True,
            subject=subject,
            gender=gender,
            number=number,
            number_evidence=number_evidence,
            clitic=clitic,
            expected_clitic=expected_clitic,
            clitic_agrees=clitic_agrees,
            copula=copula,
            expected_copula=expected_copula,
            copula_agrees=copula_agrees,
            note=(
                f"Gender evidence: {gender_evidence}. Number is analyzed separately "
                "so plural ay/way patterns are not collapsed into singular gender agreement."
            ),
        )

    return NounGenderAgreementAnalysis(recognized=False)
