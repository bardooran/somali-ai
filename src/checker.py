"""Small rule-based Somali orthography checker.

This is intentionally conservative: rules that require context are reported
separately and are never auto-applied without enough evidence.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


WORD_BOUNDARY_TEMPLATE = r"(?<!\w){token}(?!\w)"
NON_AUTOFIX_STATUSES = {"ambiguous", "context_required"}


@dataclass(frozen=True)
class Rule:
    id: str
    category: str
    input: str
    preferred_written: str
    status: str
    source: str = ""
    note: str = ""


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


def load_rules(path: str | Path) -> list[Rule]:
    rules: list[Rule] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                item = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL on line {line_number}: {exc}") from exc
            rules.append(Rule(**item))
    return rules


def _iter_matches(text: str, token: str) -> Iterable[re.Match[str]]:
    pattern = WORD_BOUNDARY_TEMPLATE.format(token=re.escape(token))
    return re.finditer(pattern, text, flags=re.IGNORECASE)


def check_text(text: str, rules: Iterable[Rule]) -> list[Finding]:
    findings: list[Finding] = []
    for rule in rules:
        for match in _iter_matches(text, rule.input):
            findings.append(
                Finding(
                    rule_id=rule.id,
                    matched_text=match.group(0),
                    suggestion=rule.preferred_written,
                    start=match.start(),
                    end=match.end(),
                    status=rule.status,
                    category=rule.category,
                    note=rule.note,
                )
            )
    return sorted(findings, key=lambda item: (item.start, item.end, item.rule_id))


def apply_safe_fixes(text: str, findings: Iterable[Finding]) -> str:
    """Apply only findings that do not require contextual review.

    Replacements are applied from right to left so character offsets stay valid.
    """
    safe = [
        finding for finding in findings if finding.status not in NON_AUTOFIX_STATUSES
    ]
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
