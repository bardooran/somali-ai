#!/usr/bin/env python3
"""Run the current Somali orthography and conservative grammar checker."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from src.checker import check_file
from src.focus_particle import scan_focus_particle_clitics
from src.future_auxiliary_agreement import analyze_future_auxiliary_agreement
from src.negation import analyze_ma_plus_verb
from src.negative_finite_agreement import analyze_negative_finite_agreement
from src.negative_future_auxiliary_agreement import (
    analyze_negative_future_auxiliary_agreement,
)
from src.noun_gender_agreement import analyze_noun_gender_agreement
from src.noun_number_verb_agreement import analyze_noun_number_verb_agreement
from src.noun_singular_verb_agreement import analyze_noun_singular_verb_agreement
from src.noun_subject_case import analyze_noun_subject_case
from src.object_agreement import analyze_object_agreement
from src.past_habitual_auxiliary_agreement import analyze_past_habitual_auxiliary_agreement
from src.predicate_sentence import scan_predicate_agreement
from src.reviewed_sentence_agreement import analyze_reviewed_sentence_agreement
from src.role_aware_sentences import analyze_role_aware_sentence
from src.sentence_agreement import scan_sentence_agreement


DEFAULT_RULES = Path("rules/orthography")


def _scan_negation_conflicts(text: str):
    """Return review-only conflicts for exact documented ``ma + verb`` spans."""
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

    negative_finite_agreement = analyze_negative_finite_agreement(args.text)
    negative_finite_conflict = (
        negative_finite_agreement.recognized
        and negative_finite_agreement.agrees is False
    )
    if negative_finite_conflict:
        negation_conflicts = [
            result
            for result in negation_conflicts
            if result.paradigm not in {"present_general", "present_ongoing", "past_simple"}
        ]

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

    noun_singular_verb_agreement = analyze_noun_singular_verb_agreement(args.text)
    noun_singular_verb_conflict = (
        noun_singular_verb_agreement.recognized
        and noun_singular_verb_agreement.agrees is False
    )

    past_habitual_auxiliary_agreement = analyze_past_habitual_auxiliary_agreement(args.text)
    past_habitual_auxiliary_conflict = (
        past_habitual_auxiliary_agreement.recognized
        and past_habitual_auxiliary_agreement.agrees is False
    )

    future_auxiliary_agreement = analyze_future_auxiliary_agreement(args.text)
    future_auxiliary_conflict = (
        future_auxiliary_agreement.recognized
        and future_auxiliary_agreement.agrees is False
    )

    negative_future_auxiliary_agreement = analyze_negative_future_auxiliary_agreement(
        args.text
    )
    negative_future_auxiliary_conflict = (
        negative_future_auxiliary_agreement.recognized
        and negative_future_auxiliary_agreement.agrees is False
    )
    if negative_future_auxiliary_agreement.recognized:
        negation_conflicts = [
            result for result in negation_conflicts if result.paradigm != "future"
        ]

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
        and not noun_singular_verb_conflict
        and not past_habitual_auxiliary_conflict
        and not future_auxiliary_conflict
        and not negative_future_auxiliary_conflict
        and not negative_finite_conflict
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
        or noun_singular_verb_conflict
        or past_habitual_auxiliary_conflict
        or future_auxiliary_conflict
        or negative_future_auxiliary_conflict
        or negative_finite_conflict
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

        if negative_finite_conflict:
            persons = ", ".join(negative_finite_agreement.verb_persons)
            polarity = negative_finite_agreement.polarity or "unknown"
            print(
                f"- [REVIEW] {negative_finite_agreement.subject!r} + ma + "
                f"{negative_finite_agreement.verb!r}: possible negative finite subject/verb "
                f"agreement conflict; the reviewed form has polarity {polarity!r} and "
                f"person(s): {persons or 'none'}. Expected {negative_finite_agreement.expected_person}. "
                "Negative morphology is paradigm-specific; no automatic rewrite. "
                f"({negative_finite_agreement.rule_id})"
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
                + (f" {noun_gender_agreement.number}" if noun_gender_agreement.number else "")
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

        if noun_singular_verb_conflict:
            persons = ", ".join(noun_singular_verb_agreement.verb_persons)
            print(
                f"- [REVIEW] {noun_singular_verb_agreement.subject!r} + "
                f"{noun_singular_verb_agreement.verb!r}: possible singular noun-subject/finite-verb "
                f"agreement conflict; subject is reviewed as {noun_singular_verb_agreement.subject_gender} "
                f"singular, while the exact reviewed verb analysis has person(s): {persons}. "
                f"Expected {noun_singular_verb_agreement.expected_person}. "
                "Unknown verbs are not guessed; no automatic rewrite. "
                f"({noun_singular_verb_agreement.rule_id})"
            )

        if past_habitual_auxiliary_conflict:
            persons = ", ".join(past_habitual_auxiliary_agreement.auxiliary_persons)
            print(
                f"- [REVIEW] {past_habitual_auxiliary_agreement.subject!r} + "
                f"{past_habitual_auxiliary_agreement.habitual_stem!r} "
                f"{past_habitual_auxiliary_agreement.auxiliary!r}: possible past habitual "
                f"auxiliary agreement conflict; the reviewed auxiliary has person(s): "
                f"{persons or 'none'}. Expected {past_habitual_auxiliary_agreement.expected_person}. "
                "The habitual stem is non-finite and agreement is carried by the auxiliary; "
                "no automatic rewrite. "
                f"({past_habitual_auxiliary_agreement.rule_id})"
            )

        if future_auxiliary_conflict:
            persons = ", ".join(future_auxiliary_agreement.auxiliary_persons)
            print(
                f"- [REVIEW] {future_auxiliary_agreement.subject!r} + "
                f"{future_auxiliary_agreement.future_stem!r} {future_auxiliary_agreement.auxiliary!r}: "
                f"possible future auxiliary agreement conflict; the reviewed future auxiliary "
                f"has person(s): {persons}. Expected {future_auxiliary_agreement.expected_person}. "
                "The future stem is non-finite and does not carry this agreement; "
                "no automatic rewrite. "
                f"({future_auxiliary_agreement.rule_id})"
            )

        if negative_future_auxiliary_conflict:
            persons = ", ".join(negative_future_auxiliary_agreement.auxiliary_persons)
            polarity = negative_future_auxiliary_agreement.auxiliary_polarity or "unknown"
            print(
                f"- [REVIEW] {negative_future_auxiliary_agreement.subject!r} + ma + "
                f"{negative_future_auxiliary_agreement.future_stem!r} "
                f"{negative_future_auxiliary_agreement.auxiliary!r}: possible negative future "
                f"auxiliary agreement conflict; the reviewed auxiliary analysis has polarity "
                f"{polarity!r} and person(s): {persons or 'none'}. "
                f"Expected {negative_future_auxiliary_agreement.expected_person}. "
                "Under ma, the reviewed negative future auxiliary morphology is required; "
                "no automatic rewrite. "
                f"({negative_future_auxiliary_agreement.rule_id})"
            )

    print("\nSafe corrected text:")
    print(corrected)


if __name__ == "__main__":
    main()
