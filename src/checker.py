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


def check_text(text: str, rules: Iterable[Rule]) -> list[Finding]:
    """Run executable replacement rules and ignore reference-only rules."""
    findings: list[Finding] = []
    for rule in rules:
        if not rule.is_executable_replacement:
            continue
        assert rule.input is not None
        assert rule.preferred_written is not None
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
