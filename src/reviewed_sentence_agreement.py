"""Conservative sentence-level agreement checks for native-reviewed patterns.

This module intentionally recognizes only a very small set of exact patterns
that have project-native review. It never rewrites text. Unknown or structurally
different sentences are left unjudged rather than guessed about.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewedSentenceAgreementResult:
    sentence: str
    recognized: bool
    agrees: bool | None
    pattern: str | None
    subject: str | None
    verb: str | None
    expected_forms: tuple[str, ...]
    note: str


IDINKU_WAAD_2PL_FORMS = (
    "timaaddeen",
    "tagteen",
    "cunteen",
    "aragteen",
    "shaqayseen",
)

# Forms that are strongly contrasted with reviewed 2pl examples in the same
# construction. This is deliberately finite; the analyzer is not a general
# Somali conjugator.
KNOWN_NON_2PL_FORMS = (
    "yimid",
    "tagay",
    "cunay",
    "cuntay",
    "arkaa",
    "arkayaa",
    "eryanayaa",
    "eryanaysaa",
)

_TOKEN_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)?", re.UNICODE)


def _tokens(sentence: str) -> list[str]:
    return [token.casefold() for token in _TOKEN_RE.findall(sentence)]


def analyze_reviewed_sentence_agreement(sentence: str) -> ReviewedSentenceAgreementResult:
    """Analyze exact native-reviewed sentence templates without autocorrection."""
    tokens = _tokens(sentence)

    if len(tokens) == 3 and tokens[0] == "idinku" and tokens[1] == "waad":
        verb = tokens[2]
        if verb in IDINKU_WAAD_2PL_FORMS:
            return ReviewedSentenceAgreementResult(
                sentence,
                True,
                True,
                "idinku_waad_2pl",
                "idinku",
                verb,
                IDINKU_WAAD_2PL_FORMS,
                "Matches the native-reviewed ordinary second-person-plural statement pattern.",
            )
        if verb in KNOWN_NON_2PL_FORMS:
            return ReviewedSentenceAgreementResult(
                sentence,
                True,
                False,
                "idinku_waad_2pl",
                "idinku",
                verb,
                IDINKU_WAAD_2PL_FORMS,
                "Known verb form conflicts with the reviewed Idinku waad second-person-plural pattern; review required.",
            )
        return ReviewedSentenceAgreementResult(
            sentence,
            True,
            None,
            "idinku_waad_2pl",
            "idinku",
            verb,
            IDINKU_WAAD_2PL_FORMS,
            "Sentence shape is recognized, but this verb is outside the currently reviewed 2pl forms.",
        )

    return ReviewedSentenceAgreementResult(
        sentence,
        False,
        None,
        None,
        None,
        None,
        (),
        "Sentence is outside the current native-reviewed executable templates.",
    )
