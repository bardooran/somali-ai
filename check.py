#!/usr/bin/env python3
"""Run the current Somali orthography and conservative grammar checker."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from src.checker import check_file
from src.focus_particle import scan_focus_particle_clitics
from src.negation import analyze_ma_plus_verb
from src.object_agreement import analyze_object_agreement
from src.predicate_sentence import scan_predicate_agreement
from src.reviewed_sentence_agreement import analyze_reviewed_sentence_agreement
from src.sentence_agreement import scan_sentence_agreement


DEFAULT_RULES = Path("rules/orthography")


def _scan_negation_conflicts(text: str):
    """Return review-only conflicts for exact documented ``ma + verb`` spans.

    The scanner is deliberately narrow. It considers short ``ma`` spans up to
    three following tokens so documented multiword forms such as ``ma cuni
    doono`` can be recognized, but unknown constructions remain unjudged.
    """
    tokens = re.findall(r"[^\W\d_]+", text, flags=re.UNICODE)
    conflicts = []
    for index, token in enumerate(tokens):
        if token.casefold() != "ma":
            continue
        for width in range(1, min(3, len(tokens) - index - 1) + 1):
            candidate = " ".join(tokens[index : index + width + 1])
            result = analyze_ma_plus_verb(candidate)
            if result.known and result.agrees_with_documented_pair is False:
                conflicts.append(result)
                break
            if result.known and result.agrees_with_documented_pair is True:
                break
    return conflicts


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
    negation_conflicts = _scan_negation_conflicts(args.text)
    predicate_conflicts = scan_predicate_agreement(args.text)
    reviewed_sentence_agreement = analyze_reviewed_sentence_agreement(args.text)
    reviewed_sentence_conflict = (
        reviewed_sentence_agreement.recognized
        and reviewed_sentence_agreement.agrees is False
    )

    if (
        not findings
        and not agreement_findings
        and not focus_findings
        and not object_agreement_conflict
        and not negation_conflicts
        and not predicate_conflicts
        and not reviewed_sentence_conflict
    ):
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

    if (
        agreement_findings
        or focus_findings
        or object_agreement_conflict
        or negation_conflicts
        or predicate_conflicts
        or reviewed_sentence_conflict
    ):
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

        for result in negation_conflicts:
            print(
                f"- [REVIEW] {result.input_form!r}: possible negation-paradigm conflict; "
                f"documented negative form for this paradigm: {result.paired_form!r}. "
                "Review required; no automatic rewrite."
            )

        for finding in predicate_conflicts:
            print(
                f"- [REVIEW] {finding.subject!r} + {finding.copula!r}: "
                f"possible predicate/copula agreement conflict; reviewed copula for this subject is "
                f"{finding.expected_copula!r}. Review required; no automatic rewrite."
            )

        if reviewed_sentence_conflict:
            expected = ", ".join(reviewed_sentence_agreement.expected_forms)
            print(
                f"- [REVIEW] {reviewed_sentence_agreement.subject!r} + "
                f"{reviewed_sentence_agreement.verb!r}: possible reviewed second-person-plural "
                f"agreement conflict; current reviewed Idinku waad forms include: {expected}. "
                "Review required; no automatic rewrite."
            )

    print("\nSafe corrected text:")
    print(corrected)


if __name__ == "__main__":
    main()
