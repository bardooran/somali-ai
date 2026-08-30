#!/usr/bin/env python3
"""Run the current Somali orthography and conservative grammar checker."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from src.checker import check_file
from src.focus_particle import scan_focus_particle_clitics
from src.negation import analyze_ma_plus_verb
from src.noun_gender_agreement import analyze_noun_gender_agreement
from src.noun_number_verb_agreement import analyze_noun_number_verb_agreement
from src.noun_subject_case import analyze_noun_subject_case
from src.object_agreement import analyze_object_agreement
from src.predicate_sentence import scan_predicate_agreement
from src.reviewed_sentence_agreement import analyze_reviewed_sentence_agreement
from src.role_aware_sentences import analyze_role_aware_sentence
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
    role_aware = analyze_role_aware_sentence(args.text)
    role_aware_conflict = role_aware.recognized and role_aware.agrees is False
    negation_conflicts = _scan_negation_conflicts(args.text)

    noun_gender_agreement = analyze_noun_gender_agreement(args.text)
    noun_gender_clitic_conflict = (
        noun_gender_agreement.recognized
        and noun_gender_agreement.clitic_agrees is False
    )
    noun_gender_copula_conflict = (
        noun_gender_agreement.recognized
        and noun_gender_agreement.copula_agrees is False
    )

    noun_number_verb_agreement = analyze_noun_number_verb_agreement(args.text)
    noun_number_verb_conflict = (
        noun_number_verb_agreement.recognized
        and noun_number_verb_agreement.agrees is False
    )

    predicate_conflicts = scan_predicate_agreement(args.text)
    if (
        noun_gender_copula_conflict
        and noun_gender_agreement.subject
        and noun_gender_agreement.copula
    ):
        predicate_conflicts = [
            finding
            for finding in predicate_conflicts
            if not (
                finding.subject.casefold() == noun_gender_agreement.subject.casefold()
                and finding.copula.casefold() == noun_gender_agreement.copula.casefold()
            )
        ]

    reviewed_sentence_agreement = analyze_reviewed_sentence_agreement(args.text)
    reviewed_sentence_conflict = (
        reviewed_sentence_agreement.recognized
        and reviewed_sentence_agreement.agrees is False
    )
    noun_subject_case = analyze_noun_subject_case(args.text)
    noun_subject_case_conflict = (
        noun_subject_case.recognized and noun_subject_case.agrees is False
    )

    if (
        not findings
        and not agreement_findings
        and not focus_findings
        and not object_agreement_conflict
        and not role_aware_conflict
        and not negation_conflicts
        and not predicate_conflicts
        and not reviewed_sentence_conflict
        and not noun_subject_case_conflict
        and not noun_gender_clitic_conflict
        and not noun_gender_copula_conflict
        and not noun_number_verb_conflict
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
        or role_aware_conflict
        or negation_conflicts
        or predicate_conflicts
        or reviewed_sentence_conflict
        or noun_subject_case_conflict
        or noun_gender_clitic_conflict
        or noun_gender_copula_conflict
        or noun_number_verb_conflict
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

        # Avoid duplicate output for the same maydin/idin lion conflict. The
        # role-aware layer adds useful coverage for explicit na-object forms.
        if role_aware_conflict and not object_agreement_conflict:
            print(
                f"- [REVIEW] {role_aware.subject!r} + object {role_aware.object_clitic!r} + "
                f"{role_aware.verb!r}: possible role-aware subject/verb agreement conflict; "
                f"reviewed verb for this subject is {role_aware.expected_verb!r}. "
                "The object clitic does not control agreement; no automatic rewrite."
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

        if noun_subject_case_conflict:
            print(
                f"- [REVIEW] {noun_subject_case.noun_form!r} before "
                f"{noun_subject_case.marker!r}: possible definite-noun subject-case conflict; "
                f"reviewed subject-form candidate is {noun_subject_case.expected_subject_form!r}. "
                "Sentence role matters; no automatic rewrite. "
                f"({noun_subject_case.rule_id})"
            )

        if noun_gender_clitic_conflict:
            print(
                f"- [REVIEW] {noun_gender_agreement.subject!r} + "
                f"{noun_gender_agreement.clitic!r}: possible noun-subject gender/clitic "
                f"agreement conflict; subject is analyzed as {noun_gender_agreement.gender}"
                + (
                    f" {noun_gender_agreement.number}"
                    if noun_gender_agreement.number
                    else ""
                )
                + f" and the supported clitic is {noun_gender_agreement.expected_clitic!r}. "
                "Number and gender are analyzed separately; no automatic rewrite. "
                f"({noun_gender_agreement.rule_id})"
            )

        if noun_gender_copula_conflict:
            print(
                f"- [REVIEW] {noun_gender_agreement.subject!r} + "
                f"{noun_gender_agreement.copula!r}: possible noun-subject predicate/copula "
                f"agreement conflict; supported copula for this reviewed "
                f"{noun_gender_agreement.gender} singular subject is "
                f"{noun_gender_agreement.expected_copula!r}. No automatic rewrite. "
                f"({noun_gender_agreement.rule_id})"
            )

        if noun_number_verb_conflict:
            persons = ", ".join(noun_number_verb_agreement.verb_persons)
            print(
                f"- [REVIEW] {noun_number_verb_agreement.subject!r} + "
                f"{noun_number_verb_agreement.verb!r}: possible plural noun-subject/verb "
                f"agreement conflict; subject has reviewed plural number, but the exact "
                f"reviewed verb analysis has person(s): {persons}. Expected 3pl. "
                "Unknown verbs are not guessed; no automatic rewrite. "
                f"({noun_number_verb_agreement.rule_id})"
            )

    print("\nSafe corrected text:")
    print(corrected)


if __name__ == "__main__":
    main()
