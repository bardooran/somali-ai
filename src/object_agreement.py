"""Conservative analyzer for reviewed Somali object-clitic agreement patterns.

This module only recognizes a small set of native-reviewed constructions. It
never rewrites text. Its purpose is to keep subject agreement separate from the
second-person-plural object clitic ``idin`` in examples such as
``Libaaxu maydin eryanayaa?``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ObjectAgreementResult:
    text: str
    recognized: bool
    subject: str | None
    subject_gender: str | None
    object_clitic: str | None
    verb: str | None
    agrees: bool | None
    rule_id: str | None
    note: str


_TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", re.UNICODE)


def _tokens(text: str) -> list[str]:
    return [token.casefold() for token in _TOKEN_RE.findall(text)]


def analyze_object_agreement(text: str) -> ObjectAgreementResult:
    """Analyze only the currently reviewed subject/object-agreement patterns.

    Bare ``maydin`` questions may have a discourse-given subject. For the
    native-reviewed ``cunayaa/cunaysaa`` contrast, the verb form itself provides
    masculine/feminine agreement evidence. Unknown verb forms remain unjudged.
    """
    tokens = _tokens(text)
    if not tokens:
        return ObjectAgreementResult(text, False, None, None, None, None, None, None, "No reviewed construction found.")

    object_present = "maydin" in tokens or "idin" in tokens
    if not object_present:
        return ObjectAgreementResult(text, False, None, None, None, None, None, None, "No reviewed second-person-plural object construction found.")

    if tokens[0] == "libaaxu":
        verb = next((token for token in reversed(tokens) if token.startswith("eryan")), None)
        agrees = None if verb is None else verb == "eryanayaa"
        return ObjectAgreementResult(
            text,
            True,
            "libaaxu",
            "masculine",
            "idin",
            verb,
            agrees,
            "GRAM-OBJAGR-003",
            "Masculine subject libaaxu controls eryanayaa; idin is the object.",
        )

    if tokens[0] == "libaaxadu":
        verb = next((token for token in reversed(tokens) if token.startswith("eryan")), None)
        agrees = None if verb is None else verb == "eryanaysaa"
        return ObjectAgreementResult(
            text,
            True,
            "libaaxadu",
            "feminine",
            "idin",
            verb,
            agrees,
            "GRAM-OBJAGR-004",
            "Feminine subject libaaxadu controls eryanaysaa; idin is the object.",
        )

    verb = tokens[-1] if tokens else None
    if verb == "cunaysaa":
        return ObjectAgreementResult(
            text,
            True,
            None,
            "feminine",
            "idin",
            verb,
            True,
            "GRAM-OBJAGR-002",
            "Reviewed bare maydin construction: cunaysaa carries feminine agreement for the understood subject; idin is the object.",
        )
    if verb == "cunayaa":
        return ObjectAgreementResult(
            text,
            True,
            None,
            "masculine",
            "idin",
            verb,
            True,
            "GRAM-OBJAGR-006",
            "Reviewed bare maydin construction: cunayaa carries masculine agreement for the understood subject; idin is the object.",
        )

    return ObjectAgreementResult(
        text,
        True,
        None,
        None,
        "idin",
        verb,
        None,
        "GRAM-OBJAGR-001",
        "Second-person-plural object is recognized, but the subject or verb agreement is outside the current reviewed executable patterns; no agreement judgment is made.",
    )
