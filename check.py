#!/usr/bin/env python3
"""Run the current Somali orthography and conservative grammar checker."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.checker import check_file
from src.focus_particle import scan_focus_particle_clitics
from src.object_agreement import analyze_object_agreement
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
    agreement_findings = scan_sentence_agreement(args.text)
    focus_findings = scan_focus_particle_clitics(args.text)
    object_agreement = analyze_object_agreement(args.text)
    object_agreement_conflict = object_agreement.recognized and object_agreement.agrees is False

    if not findings and not agreement_findings and not focus_findings and not object_agreement_conflict:
        print("No supported orthography or grammar findings found.")
        return

    if findings:
        print("Orthography findings:")
        for finding in findings:
            label = "REVIEW" if finding.status in {"ambiguous", "context_required"} else "SUGGEST"
            print(
                f"- [{label}] {finding.matched_text!r} -> {finding.suggestion!r} "
                f"({finding.rule_id})"
            )

    if agreement_findings or focus_findings or object_agreement_conflict:
        if findings:
            print()
        print("Grammar findings:")

        for finding in agreement_findings:
            expected = ", ".join(finding.expected_forms)
            print(
                f"- [REVIEW] {finding.pronoun!r} + {finding.verb!r}: "
                f"possible subject-verb agreement conflict; reviewed forms for this subject include: {expected}"
            )

        for finding in focus_findings:
            print(
                f"- [REVIEW] {finding.subject!r} ... {finding.particle!r}: "
                f"possible missing subject clitic in a baa/ayaa focus construction "
                f"({finding.rule_id})"
            )

        if object_agreement_conflict:
            print(
                f"- [REVIEW] {object_agreement.subject!r} + {object_agreement.object_clitic!r} + "
                f"{object_agreement.verb!r}: possible subject-gender/verb agreement conflict; "
                f"{object_agreement.note} ({object_agreement.rule_id})"
            )

    print("\nSafe corrected text:")
    print(corrected)


if __name__ == "__main__":
    main()
