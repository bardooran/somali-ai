"""Sentence-level wrapper around conservative Somali agreement analyzers.

The scanner is intentionally narrow. It considers reviewed independent subject
pronouns in a short local window, subject clitics only in anchored
``baa/ayaa/waa + clitic`` contexts, reviewed true subject-focus
``SUBJECT + baa/ayaa + ... + predicate`` frames, overt second-clause connective
subject focus ``SUBJECT + baana/ayaana + ... + predicate`` frames, reviewed
clitic-bearing connective focus ``... + buuna/beyna + ... + predicate`` frames,
clause-initial connective statement ``wuuna/wayna + ... + predicate`` frames,
and exact clitic-bearing waxaa-family connectives ``waxayna/waxaadna``.
Unknown verbs are ignored or left unjudged rather than treated as errors.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.agreement import analyze_pronoun_verb, _load_jsonl, PRONOUN_PATH, AGREEMENT_PATH
from src.connective_focus import analyze_connective_clitic_focus
from src.connective_statement import analyze_connective_statement
from src.connective_waxaa_focus import analyze_connective_waxaa_focus
from src.subject_focus_agreement import analyze_subject_focus_agreement


TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿʼ’'-]+", re.UNICODE)
MAX_TOKEN_GAP = 4
CLITIC_VERB_GAP = 2
SUBJECT_FOCUS_WINDOW = 7
CLITIC_ANCHORS = {"baa", "ayaa", "waa"}
SUBJECT_FOCUS_PARTICLES = {"baa", "ayaa"}
CONNECTIVE_SUBJECT_FOCUS_PARTICLES = {"ayaana": "ayaa", "baana": "baa"}


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


def _subject_focus_expected_forms(result) -> tuple[str, ...]:
    expected = result.expected_person or "reviewed subject person"
    evidence = result.evidence or ""
    if "restrictive_simple_past" in evidence:
        return (
            f"a reviewed {expected} predicate under restrictive focused-subject simple-past agreement",
        )
    if "restrictive_past_progressive" in evidence:
        return (
            f"a reviewed {expected} predicate under restrictive focused-subject past-progressive agreement",
        )
    if "restrictive_simple_present" in evidence:
        return (
            f"a reviewed {expected} predicate under restrictive focused-subject simple-present agreement",
        )
    if "restrictive_present_progressive" in evidence:
        return (
            f"a reviewed {expected} predicate under restrictive focused-subject present-progressive agreement",
        )
    if "restrictive_copular_present" in evidence:
        return (f"the reviewed reduced copular present form for focused-subject {expected}",)
    return (f"a reviewed {expected} predicate",)


def _append_subject_focus_result(
    findings: list[SentenceAgreementFinding],
    tokens: list[re.Match[str]],
    index: int,
    upper: int,
    result,
    note_prefix: str = "",
) -> None:
    if not result.recognized or result.agrees is not False or not result.predicate:
        return
    predicate_match = next(
        (
            match
            for match in tokens[index + 2 : upper]
            if match.group(0).casefold() == result.predicate.casefold()
        ),
        None,
    )
    if predicate_match is None:
        return
    findings.append(
        SentenceAgreementFinding(
            pronoun=tokens[index].group(0),
            verb=predicate_match.group(0),
            pronoun_start=tokens[index].start(),
            verb_start=predicate_match.start(),
            agrees=False,
            expected_forms=_subject_focus_expected_forms(result),
            note=note_prefix + result.note,
        )
    )


def _append_subject_focus_mismatches(
    findings: list[SentenceAgreementFinding],
    tokens: list[re.Match[str]],
) -> None:
    """Append reviewed bare baa/ayaa subject-focus conflicts."""
    for index in range(len(tokens) - 2):
        particle_match = tokens[index + 1]
        if particle_match.group(0).casefold() not in SUBJECT_FOCUS_PARTICLES:
            continue
        upper = min(len(tokens), index + SUBJECT_FOCUS_WINDOW)
        candidate = " ".join(match.group(0) for match in tokens[index:upper])
        result = analyze_subject_focus_agreement(candidate)
        _append_subject_focus_result(findings, tokens, index, upper, result)


def _has_overt_clause_boundary(
    text: str,
    tokens: list[re.Match[str]],
    subject_index: int,
) -> bool:
    if subject_index == 0:
        return False
    between = text[tokens[subject_index - 1].end() : tokens[subject_index].start()]
    return "," in between or ";" in between


def _append_connective_subject_focus_mismatches(
    findings: list[SentenceAgreementFinding],
    text: str,
    tokens: list[re.Match[str]],
) -> None:
    """Append overt second-clause baana/ayaana subject-focus conflicts.

    ``-na`` is removed only for internal analysis. This stage deliberately
    requires comma/semicolon evidence for the preceding clause instead of
    treating every standalone ayaana/baana as a complete connective clause.
    """
    for index in range(len(tokens) - 2):
        particle_surface = tokens[index + 1].group(0)
        base_particle = CONNECTIVE_SUBJECT_FOCUS_PARTICLES.get(
            particle_surface.casefold()
        )
        if base_particle is None or not _has_overt_clause_boundary(text, tokens, index):
            continue

        upper = min(len(tokens), index + SUBJECT_FOCUS_WINDOW)
        normalized_tokens = [tokens[index].group(0), base_particle]
        normalized_tokens.extend(match.group(0) for match in tokens[index + 2 : upper])
        result = analyze_subject_focus_agreement(" ".join(normalized_tokens))
        _append_subject_focus_result(
            findings,
            tokens,
            index,
            upper,
            result,
            note_prefix=(
                f"{particle_surface} is analyzed as {base_particle} + connective -na ('and') "
                "in an overt second clause. "
            ),
        )


def _append_connective_clitic_focus_mismatch(
    findings: list[SentenceAgreementFinding],
    text: str,
    tokens: list[re.Match[str]],
) -> None:
    """Append reviewed buuna/beyna subject-clitic/finite-verb conflicts."""
    result = analyze_connective_clitic_focus(text)
    if (
        not result.recognized
        or result.agreement_agrees is not False
        or not result.particle
        or not result.verb
    ):
        return

    particle_match = next(
        (
            match
            for match in tokens
            if match.group(0).casefold() == result.particle.casefold()
        ),
        None,
    )
    if particle_match is None:
        return
    verb_match = next(
        (
            match
            for match in tokens
            if match.start() > particle_match.end()
            and match.group(0).casefold() == result.verb.casefold()
        ),
        None,
    )
    if verb_match is None:
        return

    encoded = "/".join(result.subject_persons) or "reviewed subject person"
    findings.append(
        SentenceAgreementFinding(
            pronoun=particle_match.group(0),
            verb=verb_match.group(0),
            pronoun_start=particle_match.start(),
            verb_start=verb_match.start(),
            agrees=False,
            expected_forms=(
                f"a reviewed finite predicate compatible with connective focus clitic person(s) {encoded}",
            ),
            note=result.note,
        )
    )


def _append_connective_statement_mismatch(
    findings: list[SentenceAgreementFinding],
    text: str,
    tokens: list[re.Match[str]],
) -> None:
    """Append reviewed wuuna/wayna statement-clitic/finite-verb conflicts."""
    result = analyze_connective_statement(text)
    if (
        not result.recognized
        or result.agreement_agrees is not False
        or not result.particle
        or not result.verb
    ):
        return

    particle_match = next(
        (
            match
            for match in tokens
            if match.group(0).casefold() == result.particle.casefold()
        ),
        None,
    )
    if particle_match is None:
        return
    verb_match = next(
        (
            match
            for match in tokens
            if match.start() > particle_match.end()
            and match.group(0).casefold() == result.verb.casefold()
        ),
        None,
    )
    if verb_match is None:
        return

    encoded = "/".join(result.subject_persons) or "reviewed subject person"
    findings.append(
        SentenceAgreementFinding(
            pronoun=particle_match.group(0),
            verb=verb_match.group(0),
            pronoun_start=particle_match.start(),
            verb_start=verb_match.start(),
            agrees=False,
            expected_forms=(
                f"a reviewed finite predicate compatible with connective statement clitic person(s) {encoded}",
            ),
            note=result.note,
        )
    )


def _append_connective_waxaa_mismatch(
    findings: list[SentenceAgreementFinding],
    text: str,
    tokens: list[re.Match[str]],
) -> None:
    """Append exact waxayna/waxaadna subject-clitic/finite-verb conflicts."""
    result = analyze_connective_waxaa_focus(text)
    if (
        not result.recognized
        or result.agreement_agrees is not False
        or not result.particle
        or not result.verb
        or not result.subject_persons
    ):
        return

    particle_match = next(
        (
            match
            for match in tokens
            if match.group(0).casefold() == result.particle.casefold()
        ),
        None,
    )
    if particle_match is None:
        return
    verb_match = next(
        (
            match
            for match in tokens
            if match.start() > particle_match.end()
            and match.group(0).casefold() == result.verb.casefold()
        ),
        None,
    )
    if verb_match is None:
        return

    encoded = "/".join(result.subject_persons)
    findings.append(
        SentenceAgreementFinding(
            pronoun=particle_match.group(0),
            verb=verb_match.group(0),
            pronoun_start=particle_match.start(),
            verb_start=verb_match.start(),
            agrees=False,
            expected_forms=(
                f"a reviewed finite predicate compatible with connective waxaa-focus clitic person(s) {encoded}",
            ),
            note=result.note,
        )
    )


def scan_sentence_agreement(text: str) -> list[SentenceAgreementFinding]:
    """Find reviewed subject/verb agreement conflicts in conservative contexts.

    Independent subject pronouns are checked in a short local window. Subject
    clitics are checked only when immediately preceded by ``baa``, ``ayaa`` or
    ``waa``. A clitic check is skipped when an independent subject pronoun is
    already present in the nearby left context, preventing duplicate reports.

    Reviewed true subject-focus frames are also checked. Bare ``baa``/``ayaa``
    is licensed because the noun before it is the focused subject. In an overt
    second clause, ``baana``/``ayaana`` is normalized only to its base focus
    particle for the same restrictive agreement check. Reviewed ``buuna`` and
    ``beyna`` are instead treated as focus+subject-clitic+connective forms: only
    their encoded subject person is checked against exact finite morphology.
    Reviewed clause-initial ``wuuna``/``wayna`` are statement/declarative
    clitic+connective forms and are checked separately from focus. Exact
    ``waxayna``/``waxaadna`` are waxaa-family focus+subject-clitic connectives
    checked only against exact finite morphology, while person-neutral
    ``waxaana`` never creates an agreement finding. Unknown or unmodeled forms
    stay silent, and standalone connective forms remain context-dependent.
    """
    tokens = list(TOKEN_RE.finditer(text))
    pronouns = _known_subject_pronouns()
    subject_clitics = _known_subject_clitics()
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
            _append_mismatch(findings, token_match, candidate)
            break

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
    _append_connective_subject_focus_mismatches(findings, text, tokens)
    _append_connective_clitic_focus_mismatch(findings, text, tokens)
    _append_connective_statement_mismatch(findings, text, tokens)
    _append_connective_waxaa_mismatch(findings, text, tokens)
    return findings
