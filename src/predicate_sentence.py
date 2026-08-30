"""Sentence-level scanner for reviewed Somali predicate/copula agreement.

This module intentionally recognizes only exact reviewed subject forms and the
copulas ``yahay``/``tahay``. It reports conflicts for review and never rewrites
text automatically.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.predicate_agreement import analyze_predicate_agreement


@dataclass(frozen=True)
class PredicateSentenceFinding:
    subject: str
    copula: str
    expected_copula: str
    note: str


_TOKEN_RE = re.compile(r"[^\W\d_]+", flags=re.UNICODE)
_REVIEWED_SUBJECTS = {"ninku", "naagtu"}
_REVIEWED_COPULAS = {"yahay", "tahay"}


def scan_predicate_agreement(text: str) -> list[PredicateSentenceFinding]:
    """Find reviewed subject/copula conflicts in a sentence.

    A copula may be separated from the subject by predicate material, so the
    scanner looks forward within a small window. Unknown subjects and unknown
    copulas remain unjudged.
    """
    tokens = _TOKEN_RE.findall(text)
    findings: list[PredicateSentenceFinding] = []

    for index, token in enumerate(tokens):
        if token.casefold() not in _REVIEWED_SUBJECTS:
            continue

        for following in tokens[index + 1 : index + 7]:
            if following.casefold() not in _REVIEWED_COPULAS:
                continue
            result = analyze_predicate_agreement(token, following)
            if result.recognized and result.agrees is False and result.expected_copula:
                findings.append(
                    PredicateSentenceFinding(
                        token,
                        following,
                        result.expected_copula,
                        result.note,
                    )
                )
            break

    return findings
