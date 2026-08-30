"""Conservative analyzer for reviewed Somali object-clitic agreement patterns.

This module only recognizes a small set of native-reviewed constructions. It
never rewrites text. Its purpose is to keep subject agreement separate from
object clitics and to preserve reviewed role distinctions such as ``idin`` as
second-person-plural object.
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

    Bare ``maydin`` questions may have a discourse-given subject in some
    constructions. For the reviewed ``cunayaa/cunaysaa`` contrast, the verb
    form provides masculine/feminine agreement evidence. The reviewed ``arag``
    questions are kept construction-specific: ``Maydin arkaa/arkayaa?`` is a
    first-person-subject + second-person-plural-object pattern in project native
    review, while ``Maad i aragtaan?`` reverses those roles.
    """
    tokens = _tokens(text)
    if not tokens:
        return ObjectAgreementResult(text, False, None, None, None, None, None, None, "No reviewed construction found.")

    # Reviewed arag-family constructions. These are role analyses, not fixes.
    if tokens in (["maydin", "arkaa"], ["maydin", "arkayaa"]):
        verb = tokens[-1]
        return ObjectAgreementResult(
            text,
            True,
            "first_person_singular",
            None,
            "idin",
            verb,
            True,
            "GRAM-OBJAGR-007",
            "Native-reviewed arag construction: the speaker is the subject/seer and idin is the second-person-plural object. Arkaa and arkayaa are both valid; their aspect contrast is modeled separately from agreement.",
        )

    if tokens in (["maan", "idin", "arkaa"], ["maan", "idin", "arkayaa"]):
        verb = tokens[-1]
        return ObjectAgreementResult(
            text,
            True,
            "first_person_singular",
            None,
            "idin",
            verb,
            True,
            "GRAM-OBJAGR-007",
            "Native review accepts this expanded first-person question alongside the contracted maydin form; neither is normalized into the other.",
        )

    if tokens == ["maad", "i", "aragtaan"]:
        return ObjectAgreementResult(
            text,
            True,
            "second_person_plural",
            None,
            "i",
            "aragtaan",
            True,
            "GRAM-OBJAGR-008",
            "Native-reviewed role reversal: you-all are the subject/seers and i is the first-person-singular object.",
        )

    if tokens == ["ma", "is", "arkaysaan"]:
        return ObjectAgreementResult(
            text,
            True,
            "second_person_plural",
            None,
            "is",
            "arkaysaan",
            True,
            "GRAM-OBJAGR-009",
            "Native-reviewed reciprocal construction: is gives the reviewed each-other reading here.",
        )

    if tokens in (["ma", "la", "idin", "arkaa"], ["ma", "la", "idin", "arki", "karaa"]):
        verb = " ".join(tokens[-2:]) if tokens[-2:] == ["arki", "karaa"] else tokens[-1]
        return ObjectAgreementResult(
            text,
            True,
            "impersonal_la",
            None,
            "idin",
            verb,
            True,
            "GRAM-OBJAGR-010",
            "Native-reviewed impersonal la construction with idin as second-person-plural object. Arki karaa adds ability/possibility; no rewrite is proposed.",
        )

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
