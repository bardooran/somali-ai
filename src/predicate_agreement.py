"""Conservative Somali predicate/copuIa agreement analysis.

Only exact subject/copula pairs backed by the current project evidence are
recognized. The analyzer never rewrites text automatically and leaves unknown
constructions unjudged.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PredicateAgreementResult:
    subject: str
    copula: str
    recognized: bool
    agrees: bool | None
    expected_copula: str | None
    note: str


_REVIEWED_SUBJECTS = {
    "ninku": "yahay",
    "naagtu": "tahay",
}


def analyze_predicate_agreement(subject: str, copula: str) -> PredicateAgreementResult:
    subject_norm = subject.casefold().strip()
    copula_norm = copula.casefold().strip()
    expected = _REVIEWED_SUBJECTS.get(subject_norm)

    if expected is None:
        return PredicateAgreementResult(
            subject,
            copula,
            False,
            None,
            None,
            "Subject form is outside the current reviewed predicate-agreement evidence.",
        )

    agrees = copula_norm == expected
    return PredicateAgreementResult(
        subject,
        copula,
        True,
        agrees,
        expected,
        (
            "Subject and predicate copula match the current reviewed gender evidence."
            if agrees
            else "Subject and predicate copula conflict within the current reviewed gender evidence; review required."
        ),
    )
