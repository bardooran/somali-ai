#!/usr/bin/env python3
"""Run the current Somali orthography checker from the command line."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.checker import check_file


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

    if not findings:
        print("No executable matching rules found.")
        return

    print("Findings:")
    for finding in findings:
        label = "REVIEW" if finding.status in {"ambiguous", "context_required"} else "SUGGEST"
        print(
            f"- [{label}] {finding.matched_text!r} -> {finding.suggestion!r} "
            f"({finding.rule_id})"
        )

    print("\nSafe corrected text:")
    print(corrected)


if __name__ == "__main__":
    main()
