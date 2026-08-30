"""Sentence-level wrapper around the conservative Somali agreement analyzer.

The scanner is intentionally narrow. It only considers an independent subject
pronoun followed by a reviewed verb form within a short token window. Unknown
verbs are ignored rather than treated as errors.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.agreement import analyze_pronoun_verb, _load_jsonl, PRONOUN_PATH, AGREEMENT_PATH


TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿʼ’'-]+", re.UNICODE)
MAX_TOKEN_GAP = 4


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


def _known_agreement_verbs() -> set[str]:
    return {
        value.casefold()
        for record in _load_jsonl(AGREEMENT_PATH)
        for key, value in record.get("verb_example", {}).items()
        if key != "lemma" and isinstance(value, str) and " " not in value
    }


def scan_sentence_agreement(text: str) -> list[SentenceAgreementFinding]:
    """Find reviewed pronoun/verb agreement conflicts in simple local contexts.

    Only mismatches are returned. Matching pairs and unknown forms stay silent.
    This function does not generate corrections.
    """
    tokens = list(TOKEN_RE.finditer(text))
    pronouns = _known_subject_pronouns()
    verbs = _known_agreement_verbs()
    findings: list[SentenceAgreementFinding] = []

    for index, token_match in enumerate(tokens):
        pronoun = token_match.group(0)
        if pronoun.casefold() not in pronouns:
            continue

        upper = min(len(tokens), index + MAX_TOKEN_GAP + 2)
        for candidate in tokens[index + 1 : upper]:
            verb = candidate.group(0)
            if verb.casefold() not in verbs:
                continue
            result = analyze_pronoun_verb(pronoun, verb)
            if result.agrees is False:
                findings.append(
                    SentenceAgreementFinding(
                        pronoun=pronoun,
                        verb=verb,
                        pronoun_start=token_match.start(),
                        verb_start=candidate.start(),
                        agrees=False,
                        expected_forms=result.expected_forms,
                        note=result.note,
                    )
                )
            break

    return findings
