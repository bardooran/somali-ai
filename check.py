#!/usr/bin/env python3
"""Run the current Somali orthography and conservative grammar checker."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.checker import check_file
from src.sentence_agreement import scan_sentence_agreement


DEFAULT_RULES = Path("rules/orthography")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check Somali text using current project rules.")
    parser.add_argument("text", help="Somali text to check")
    parser.add_argument(
        "--rules",
        type=Path,
        default=DEFAULT_RULES,
        help="A JSONL rule file or a directory containing JSONL rule files.",
    )
    args = parser.parse_args()

    findings, corrected = check_file(args.text, args.rules)
    grammar_findings = scan_sentence_agreement(args.text)

    if not findings and not grammar_findings:
        print("No supported orthography or agreement findings found.")
        return

    if findings:
        print("Orthography findings:")
        for finding in findings:
            label = "REVIEW" if finding.status in {"ambiguous", "context_required"} else "SUGGEST"
            print(
                f"- [{label}] {finding.matched_text!r} -> {finding.suggestion!r} "
                f"({finding.rule_id})"
            )

    if grammar_findings:
        if findings:
            print()
        print("Grammar findings:")
        for finding in grammar_findings:
            expected = ", ".join(finding.expected_forms)
            print(
                f"- [REVIEW] {finding.pronoun!r} + {finding.verb!r}: "
                f"possible subject-verb agreement conflict; reviewed forms for this subject include: {expected}"
            )

    print("\nSafe corrected text:")
    print(corrected)


if __name__ == "__main__":
    main()
