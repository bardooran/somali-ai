"""Small rule-based Somali orthography checker.

The checker is intentionally conservative. The rule library may contain both
executable replacement rules and reference/context rules that are not yet safe
to apply automatically.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


WORD_BOUNDARY_TEMPLATE = r"(?<!\w){token}(?!\w)"
NON_AUTOFIX_STATUSES = {"ambiguous", "context_required"}
OPENING_SENTENCE_CHARS = set('"\'“‘([{')
SENTENCE_END_CHARS = set(".!?")


@dataclass(frozen=True)
class Rule:
    id: str
    category: str
    status: str
    source: str = ""
    note: str = ""
    input: str | None = None
    preferred_written: str | None = None
    target: str | None = None
    pattern: str | None = None
    preferred_pattern: str | None = None
    mark: str | None = None
    use: str | None = None
    forms: list[str] | None = None
    sources: list[str] | None = None

    @property
    def is_executable_replacement(self) -> bool:
        return bool(self.input and self.preferred_written)


@dataclass(frozen=True)
class Finding:
    rule_id: str
    matched_text: str
    suggestion: str
    start: int
    end: int
    status: str
    category: str
    note: str = ""


def _rule_files(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(path.glob("*.jsonl"))
    return [path]


def load_rules(path: str | Path) -> list[Rule]:
    """Load one JSONL rule file or every JSONL file in a rule directory."""
    rules: list[Rule] = []
    for rule_file in _rule_files(Path(path)):
        with rule_file.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    item = json.loads(stripped)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSONL in {rule_file} on line {line_number}: {exc}"
                    ) from exc
                try:
                    rules.append(Rule(**item))
                except TypeError as exc:
                    raise ValueError(
                        f"Invalid rule schema in {rule_file} on line {line_number}: {exc}"
                    ) from exc
    return rules


def _iter_matches(text: str, token: str) -> Iterable[re.Match[str]]:
    pattern = WORD_BOUNDARY_TEMPLATE.format(token=re.escape(token))
    return re.finditer(pattern, text, flags=re.IGNORECASE)


def _next_sentence_letter(text: str, start: int) -> int | None:
    """Return the next alphabetic character after whitespace/opening punctuation."""
    index = start
    while index < len(text):
        char = text[index]
        if char.isspace() or char in OPENING_SENTENCE_CHARS:
            index += 1
            continue
        return index if char.isalpha() else None
    return None


def _sentence_start_positions(text: str) -> list[int]:
    starts: list[int] = []
    first = _next_sentence_letter(text, 0)
    if first is not None:
        starts.append(first)

    for index, char in enumerate(text):
        if char not in SENTENCE_END_CHARS:
            continue
        next_letter = _next_sentence_letter(text, index + 1)
        if next_letter is not None and next_letter not in starts:
            starts.append(next_letter)
    return starts


def _capitalization_findings(text: str, rules: Iterable[Rule]) -> list[Finding]:
    sentence_rule = next(
        (
            rule
            for rule in rules
            if rule.category == "capitalization" and rule.target == "sentence_start"
        ),
        None,
    )
    if sentence_rule is None:
        return []

    findings: list[Finding] = []
    for position in _sentence_start_positions(text):
        char = text[position]
        if not char.islower():
            continue
        findings.append(
            Finding(
                rule_id=sentence_rule.id,
                matched_text=char,
                suggestion=char.upper(),
                start=position,
                end=position + 1,
                status=sentence_rule.status,
                category=sentence_rule.category,
                note=sentence_rule.note,
            )
        )
    return findings


def check_text(text: str, rules: Iterable[Rule]) -> list[Finding]:
    """Run supported orthography detectors while ignoring reference-only rules."""
    rule_list = list(rules)
    findings: list[Finding] = []

    for rule in rule_list:
        if not rule.is_executable_replacement:
            continue
        assert rule.input is not None
        assert rule.preferred_written is not None
        for match in _iter_matches(text, rule.input):
            matched_text = match.group(0)
            if matched_text == rule.preferred_written:
                continue
            findings.append(
                Finding(
                    rule_id=rule.id,
                    matched_text=matched_text,
                    suggestion=rule.preferred_written,
                    start=match.start(),
                    end=match.end(),
                    status=rule.status,
                    category=rule.category,
                    note=rule.note,
                )
            )

    findings.extend(_capitalization_findings(text, rule_list))
    return sorted(findings, key=lambda item: (item.start, item.end, item.rule_id))


def _overlaps(left: Finding, right: Finding) -> bool:
    return left.start < right.end and right.start < left.end


def _select_non_overlapping_fixes(findings: Iterable[Finding]) -> list[Finding]:
    """Choose deterministic safe edits, preferring the most specific span.

    A longer lexical correction supersedes a shorter detector finding that
    touches the same text. This prevents edits such as sentence-start
    capitalization and proper-name capitalization from being applied twice to
    the same characters.
    """
    safe = [
        finding for finding in findings if finding.status not in NON_AUTOFIX_STATUSES
    ]
    candidates = sorted(
        safe,
        key=lambda item: (-(item.end - item.start), item.start, item.rule_id),
    )
    selected: list[Finding] = []
    for candidate in candidates:
        if any(_overlaps(candidate, existing) for existing in selected):
            continue
        selected.append(candidate)
    return selected


def apply_safe_fixes(text: str, findings: Iterable[Finding]) -> str:
    """Apply only compatible findings that do not require contextual review.

    Overlapping edits are resolved first, then replacements are applied from
    right to left so character offsets stay valid.
    """
    safe = _select_non_overlapping_fixes(findings)
    result = text
    for finding in sorted(safe, key=lambda item: item.start, reverse=True):
        replacement = finding.suggestion
        if finding.matched_text[:1].isupper():
            replacement = replacement[:1].upper() + replacement[1:]
        result = result[: finding.start] + replacement + result[finding.end :]
    return result


def check_file(text: str, rule_path: str | Path) -> tuple[list[Finding], str]:
    rules = load_rules(rule_path)
    findings = check_text(text, rules)
    corrected = apply_safe_fixes(text, findings)
    return findings, corrected
