"""Conservative Somali predicate/copula agreement analysis.

Agreement is inferred only when the existing reviewed noun evidence safely
resolves subject number and, for singular subjects, grammatical gender. Unknown
subjects remain unjudged and no automatic rewrite is performed.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.noun_gender_agreement import infer_subject_gender, infer_subject_number


@dataclass(frozen=True)
class PredicateAgreementResult:
    subject: str
    copula: str
    recognized: bool
    agrees: bool | None
    expected_copula: str | None
    note: str


def analyze_predicate_agreement(subject: str, copula: str) -> PredicateAgreementResult:
    """Check reviewed noun evidence against the present copular paradigm.

    Reviewed plural subjects expect ``yihiin``. Reviewed singular masculine
    subjects expect ``yahay`` and reviewed singular feminine subjects expect
    ``tahay``. Number and gender are resolved by the shared noun-evidence layer;
    unresolved subjects are left unjudged rather than guessed from a copula.
    """
    number, number_evidence = infer_subject_number(subject)
    gender, gender_evidence = infer_subject_gender(subject)

    expected: str | None = None
    if number == "plural":
        expected = "yihiin"
    elif number == "singular" and gender == "masculine":
        expected = "yahay"
    elif number == "singular" and gender == "feminine":
        expected = "tahay"

    if expected is None:
        return PredicateAgreementResult(
            subject,
            copula,
            False,
            None,
            None,
            (
                "Subject number/gender is outside the safely reviewed predicate-agreement evidence. "
                f"Number evidence: {number_evidence}; gender evidence: {gender_evidence}."
            ),
        )

    agrees = copula.casefold().strip() == expected
    return PredicateAgreementResult(
        subject,
        copula,
        True,
        agrees,
        expected,
        (
            "Subject and present predicate copula match reviewed number/gender evidence."
            if agrees
            else "Subject and present predicate copula conflict with reviewed number/gender evidence; review required."
        ),
    )
