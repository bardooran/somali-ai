"""Exact reviewed common-noun case checking for Somali subject focus.

Focused noun subjects before bare ``baa``/``ayaa`` use the absolute/non-subject
noun surface rather than the ordinary ``-u`` nominative subject surface. This
module only judges noun pairs already explicitly reviewed elsewhere in the
project; it does not generalize suffix replacement to unseen nouns.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.noun_gender_agreement import REVIEWED_PLURAL_FORMS, REVIEWED_SINGULAR_FORMS
from src.noun_subject_case import expected_non_subject_form, expected_subject_form

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)
FOCUS_PARTICLES = {"baa", "ayaa"}


@dataclass(frozen=True)
class SubjectFocusNounCaseAnalysis:
    recognized: bool
    noun_form: str | None = None
    particle: str | None = None
    paired_subject_form: str | None = None
    expected_focus_form: str | None = None
    agrees: bool | None = None
    rule_id: str = "GRAM-SUBJFOCUS-005"
    note: str = ""


def _is_exact_reviewed_subject(form: str) -> bool:
    folded = form.casefold()
    return folded in REVIEWED_SINGULAR_FORMS or folded in REVIEWED_PLURAL_FORMS


def analyze_subject_focus_noun_case(sentence: str) -> SubjectFocusNounCaseAnalysis:
    """Check the first adjacent ``noun + baa/ayaa`` reviewed common-noun pair."""
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 2:
        return SubjectFocusNounCaseAnalysis(recognized=False)

    for index in range(len(tokens) - 1):
        noun = tokens[index]
        particle = tokens[index + 1]
        if particle.casefold() not in FOCUS_PARTICLES:
            continue

        # Wrong focus case: an exact reviewed -u subject form appears before
        # baa/ayaa. Only exact reviewed noun surfaces enter this branch.
        if _is_exact_reviewed_subject(noun):
            absolute = expected_non_subject_form(noun)
            if absolute is None:
                continue
            return SubjectFocusNounCaseAnalysis(
                recognized=True,
                noun_form=noun,
                particle=particle,
                paired_subject_form=noun,
                expected_focus_form=absolute,
                agrees=False,
                note=(
                    "A focused common-noun subject before baa/ayaa uses its reviewed "
                    "absolute/non-subject surface rather than the ordinary -u subject surface. "
                    "No automatic rewrite."
                ),
            )

        # Correct focus case: map the absolute form back to a subject form and
        # require that paired subject form to be in our exact reviewed inventory.
        subject = expected_subject_form(noun)
        if subject is None or not _is_exact_reviewed_subject(subject):
            continue
        return SubjectFocusNounCaseAnalysis(
            recognized=True,
            noun_form=noun,
            particle=particle,
            paired_subject_form=subject,
            expected_focus_form=noun,
            agrees=True,
            note=(
                "Reviewed absolute/non-subject noun surface found in a subject-focus "
                "baa/ayaa construction."
            ),
        )

    return SubjectFocusNounCaseAnalysis(recognized=False)
