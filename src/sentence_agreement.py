"""Sentence-level wrapper around the conservative Somali agreement analyzer.

The scanner is intentionally narrow. It considers reviewed independent subject
pronouns in a short local window, plus subject clitics only in anchored
``baa/ayaa/waa + clitic`` contexts. Unknown verbs are ignored rather than
treated as errors.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.agreement import analyze_pronoun_verb, _load_jsonl, PRONOUN_PATH, AGREEMENT_PATH


TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿʼ’'-]+", re.UNICODE)
MAX_TOKEN_GAP = 4
CLITIC_VERB_GAP = 2
CLITIC_ANCHORS = {"baa", "ayaa", "waa"}


@dataclass(frozen=True)
class SentenceAgreementFinding:
    pronoun: str
    verb: str
    pronoun_start: int
    verb_start: int
    agrees: bool
    expected_forms: tuple[str, ...]
    note: str


def _known_subject_pronouns() -> set[str]:
    return {
        record["form"].casefold()
        for record in _load_jsonl(PRONOUN_PATH)
        if record.get("pronoun_type") == "independent"
        and "subject" in record.get("role", [])
    }


def _known_subject_clitics() -> set[str]:
    return {
        record["form"].casefold()
        for record in _load_jsonl(PRONOUN_PATH)
        if record.get("category") == "subject_clitic"
    }


def _known_agreement_verbs() -> set[str]:
    return {
        value.casefold()
        for record in _load_jsonl(AGREEMENT_PATH)
        for key, value in record.get("verb_example", {}).items()
        if key != "lemma" and isinstance(value, str) and " " not in value
    }


def _append_mismatch(
    findings: list[SentenceAgreementFinding],
    pronoun_match: re.Match[str],
    verb_match: re.Match[str],
) -> None:
    result = analyze_pronoun_verb(pronoun_match.group(0), verb_match.group(0))
    if result.agrees is not False:
        return
    findings.append(
        SentenceAgreementFinding(
            pronoun=pronoun_match.group(0),
            verb=verb_match.group(0),
            pronoun_start=pronoun_match.start(),
            verb_start=verb_match.start(),
            agrees=False,
            expected_forms=result.expected_forms,
            note=result.note,
        )
    )


def scan_sentence_agreement(text: str) -> list[SentenceAgreementFinding]:
    """Find reviewed pronoun/verb agreement conflicts in conservative contexts.

    Independent subject pronouns are checked in a short local window. Subject
    clitics are checked only when immediately preceded by ``baa``, ``ayaa`` or
    ``waa``. A clitic check is skipped when an independent subject pronoun is
    already present in the nearby left context, preventing duplicate reports.
    Matching pairs and unknown forms stay silent. No corrections are generated.
    """
    tokens = list(TOKEN_RE.finditer(text))
    pronouns = _known_subject_pronouns()
    subject_clitics = _known_subject_clitics()
    verbs = _known_agreement_verbs()
    findings: list[SentenceAgreementFinding] = []

    # Independent subject pronouns.
    for index, token_match in enumerate(tokens):
        pronoun = token_match.group(0)
        if pronoun.casefold() not in pronouns:
            continue

        upper = min(len(tokens), index + MAX_TOKEN_GAP + 2)
        for candidate in tokens[index + 1 : upper]:
            verb = candidate.group(0)
            if verb.casefold() not in verbs:
                continue
            _append_mismatch(findings, token_match, candidate)
            break

    # Anchored subject clitics. Bare ``ay`` and similar forms are deliberately
    # not scanned because they can be ambiguous outside a recognized context.
    for index, token_match in enumerate(tokens):
        clitic = token_match.group(0)
        if clitic.casefold() not in subject_clitics or index == 0:
            continue
        if tokens[index - 1].group(0).casefold() not in CLITIC_ANCHORS:
            continue

        left = max(0, index - MAX_TOKEN_GAP - 1)
        if any(token.group(0).casefold() in pronouns for token in tokens[left:index]):
            continue

        upper = min(len(tokens), index + CLITIC_VERB_GAP + 2)
        for candidate in tokens[index + 1 : upper]:
            if candidate.group(0).casefold() not in verbs:
                continue
            _append_mismatch(findings, token_match, candidate)
            break

    return findings
