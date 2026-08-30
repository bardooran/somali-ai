"""Conservative noun-subject gender and number agreement analysis.

The analyzer treats grammatical gender and number as separate facts. Strong
subject-surface suffixes can reveal gender, while singular/plural number must
come from explicit native review or reviewed morphology. This matters because
Somali noun plurals can change grammatical gender, and third-person plural
statements use the ay/way family regardless of singular gender.

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
# Keep Somali apostrophe/glottal-mark spellings (for example bu') inside one
# grammar token rather than splitting the lexical surface.
TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*['’]?", flags=re.UNICODE)

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


def _load_rule_record(rule_id: str) -> dict:
    if not RULE_PATH.exists():
        return {}
    for line in RULE_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("id") == rule_id:
            return record
    return {}


def _load_reviewed_singular_forms() -> dict[str, str]:
    record = _load_rule_record("GRAM-NGENDER-002")
    return {
        item["form"].casefold(): item["gender"]
        for item in record.get("forms", [])
    }


def _load_reviewed_plural_forms() -> set[str]:
    record = _load_rule_record("GRAM-NGENDER-006")
    return {
        item["form"].casefold()
        for item in record.get("forms", [])
        if item.get("form")
    }


REVIEWED_SINGULAR_FORMS = _load_reviewed_singular_forms()
REVIEWED_PLURAL_FORMS = _load_reviewed_plural_forms()


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
    """Infer number only from explicit review or reviewed paired morphology."""
    folded = form.casefold().strip()
    if folded in REVIEWED_SINGULAR_FORMS:
        return "singular", "native_reviewed_singular_subject"
    if folded in REVIEWED_PLURAL_FORMS:
        return "plural", "native_reviewed_plural_subject"

    paired = expected_non_subject_form(form)
    if paired is None:
        return None, "number_not_safely_inferable"

    candidates = analyze_surface_form(paired)
    numbers = {
        candidate.features.get("number")
        for candidate in candidates
        if candidate.features.get("number") in {"singular", "plural"}
    }
    if numbers == {"singular"}:
        return "singular", "paired_reviewed_morphology"
    if numbers == {"plural"}:
        return "plural", "paired_reviewed_morphology"

    return None, "number_not_safely_inferable"


def _find_singular_copula(tokens: list[str], subject_index: int) -> str | None:
    for token in tokens[subject_index + 2 : subject_index + 8]:
        if token.casefold() in SINGULAR_COPULAS:
            return token
    return None


def analyze_noun_gender_agreement(sentence: str) -> NounGenderAgreementAnalysis:
    """Analyze a noun subject followed by ``wuu``/``way``.

    Number takes priority for the statement clitic: reviewed plural subjects
    expect ``way``. For singular subjects, grammatical gender controls
    ``wuu``/``way`` and ``yahay``/``tahay``. If number is unknown, only the
    conclusions that are safe from gender alone are returned.
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
        number, number_evidence = infer_subject_number(subject)
        if gender is None and number is None:
            continue

        expected_clitic: str | None = None
        clitic_agrees: bool | None = None

        if number == "plural":
            expected_clitic = "way"
            clitic_agrees = clitic.casefold() == "way"
        elif number == "singular":
            if gender == "masculine":
                expected_clitic = "wuu"
                clitic_agrees = clitic.casefold() == "wuu"
            elif gender == "feminine":
                expected_clitic = "way"
                clitic_agrees = clitic.casefold() == "way"
        elif gender == "feminine":
            # With unknown number, both reviewed feminine singular and plural
            # statement patterns are compatible with way; wuu is not.
            expected_clitic = "way"
            clitic_agrees = clitic.casefold() == "way"

        copula = _find_singular_copula(tokens, index)
        expected_copula: str | None = None
        copula_agrees: bool | None = None
        if copula is not None and number == "singular" and gender is not None:
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
                f"Gender evidence: {gender_evidence}. Number evidence: {number_evidence}. "
                "Number and gender remain separate because Somali pluralization can change "
                "grammatical gender."
            ),
        )

    return NounGenderAgreementAnalysis(recognized=False)
