"""Sentence-level wrapper around conservative Somali agreement analyzers.

The scanner is intentionally narrow. It considers reviewed independent subject
pronouns in a short local window, subject clitics only in anchored
``baa/ayaa/waa + clitic`` contexts, and exact reviewed true subject-focus
``SUBJECT + baa/ayaa + predicate`` frames. Unknown verbs are ignored or left
unjudged rather than treated as errors.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.agreement import analyze_pronoun_verb, _load_jsonl, PRONOUN_PATH, AGREEMENT_PATH
from src.subject_focus_agreement import analyze_subject_focus_agreement


TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿʼ’'-]+", re.UNICODE)
MAX_TOKEN_GAP = 4
CLITIC_VERB_GAP = 2
CLITIC_ANCHORS = {"baa", "ayaa", "waa"}
SUBJECT_FOCUS_PARTICLES = {"baa", "ayaa"}


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


def _append_subject_focus_mismatches(
    findings: list[SentenceAgreementFinding],
    tokens: list[re.Match[str]],
) -> None:
    """Append exact reviewed true-subject-focus conflicts.

    The first noun in these frames is the focused subject itself, so bare ``baa``
    or bare ``ayaa`` is valid. This path only reports predicate-person conflicts
    from the dedicated exact-evidence analyzer; matching and unknown predicates
    stay silent.
    """
    for index in range(len(tokens) - 2):
        subject_match, particle_match, predicate_match = tokens[index : index + 3]
        if particle_match.group(0).casefold() not in SUBJECT_FOCUS_PARTICLES:
            continue
        candidate = " ".join(
            (subject_match.group(0), particle_match.group(0), predicate_match.group(0))
        )
        result = analyze_subject_focus_agreement(candidate)
        if not result.recognized or result.agrees is not False:
            continue
        expected = result.expected_person or "reviewed subject person"
        findings.append(
            SentenceAgreementFinding(
                pronoun=subject_match.group(0),
                verb=predicate_match.group(0),
                pronoun_start=subject_match.start(),
                verb_start=predicate_match.start(),
                agrees=False,
                expected_forms=(f"a reviewed {expected} predicate",),
                note=result.note,
            )
        )


def scan_sentence_agreement(text: str) -> list[SentenceAgreementFinding]:
    """Find reviewed subject/verb agreement conflicts in conservative contexts.

    Independent subject pronouns are checked in a short local window. Subject
    clitics are checked only when immediately preceded by ``baa``, ``ayaa`` or
    ``waa``. A clitic check is skipped when an independent subject pronoun is
    already present in the nearby left context, preventing duplicate reports.

    Exact reviewed true subject-focus frames are also checked. In those frames
    bare ``baa`` or bare ``ayaa`` is licensed because the noun before it is the
    focused subject; only predicate-person conflict is reportable. Matching pairs
    and unknown forms stay silent. No corrections are generated.
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

    _append_subject_focus_mismatches(findings, tokens)
    return findings
