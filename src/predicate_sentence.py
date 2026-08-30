"""Sentence-level scanner for reviewed Somali predicate/copula agreement.

The scanner delegates subject evidence to ``predicate_agreement`` and recognizes
the reviewed present copulas ``yahay``/``tahay``/``yihiin``. Unknown subjects
remain unjudged and no automatic rewrite is performed.
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
_REVIEWED_COPULAS = {"yahay", "tahay", "yihiin"}


def scan_predicate_agreement(text: str) -> list[PredicateSentenceFinding]:
    """Find reviewed subject/copula conflicts in a sentence.

    A copula may be separated from the subject by predicate material, so the
    scanner looks forward within a small window. Candidate subjects are judged
    only through the shared reviewed noun number/gender evidence.
    """
    tokens = _TOKEN_RE.findall(text)
    findings: list[PredicateSentenceFinding] = []

    for index, token in enumerate(tokens):
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
