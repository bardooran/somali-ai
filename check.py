#!/usr/bin/env python3
"""Run the current Somali orthography checker from the command line."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.checker import check_file


DEFAULT_RULES = Path("rules/orthography/contractions.jsonl")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check Somali text using current project rules.")
    parser.add_argument("text", help="Somali text to check")
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    args = parser.parse_args()

    findings, corrected = check_file(args.text, args.rules)

    if not findings:
        print("No matching rules found.")
        return

    print("Findings:")
    for finding in findings:
        label = "REVIEW" if finding.status == "ambiguous" else "SUGGEST"
        print(
            f"- [{label}] {finding.matched_text!r} -> {finding.suggestion!r} "
            f"({finding.rule_id})"
        )

    print("\nSafe corrected text:")
    print(corrected)


if __name__ == "__main__":
    main()
