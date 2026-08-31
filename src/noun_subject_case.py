"""Context-limited Somali definite-noun subject-case analysis.

Two reviewed contexts are distinguished:

* ordinary explicit subjects before ``wuu/way`` use the ``-u`` subject surface;
* noun subjects focused by bare ``baa/ayaa`` use the paired absolute/non-subject
  surface instead.

The focus branch is deliberately stricter than the ordinary suffix mapping: it
runs only for noun surfaces whose paired ``-u`` form already occurs in the
project's explicit reviewed singular/plural subject inventory. No unseen noun
pair is promoted to an executable grammar judgment.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*['’]?", flags=re.UNICODE)

NON_SUBJECT_TO_SUBJECT = (
    ("sha", "shu"),
    ("ka", "ku"),
    ("ga", "gu"),
    ("ha", "hu"),
    ("ta", "tu"),
    ("da", "du"),
)
SUBJECT_TO_NON_SUBJECT = tuple((subject, non_subject) for non_subject, subject in NON_SUBJECT_TO_SUBJECT)

SUBJECT_CLITICS = {"wuu", "way"}
FOCUS_MARKERS = {"ayaa", "baa"}
REVIEWED_NOUN_RULE_PATH = Path("rules/grammar/noun_subject_gender_agreement.jsonl")

PERSONAL_PRONOUN_FORMS = {
    "aniga", "anigu",
    "adiga", "adigu",
    "isaga", "isagu",
    "iyada", "iyadu",
    "annaga", "annagu",
    "innaga", "innagu",
    "idinka", "idinku",
    "iyaga", "iyagu",
}


@dataclass(frozen=True)
class NounSubjectCaseAnalysis:
    recognized: bool
    noun_form: str | None = None
    marker: str | None = None
    expected_subject_form: str | None = None
    agrees: bool | None = None
    rule_id: str = "GRAM-NSUBJ-001"
    note: str = ""


def _replace_suffix_preserving_case(form: str, source: str, target: str) -> str:
    if not form.casefold().endswith(source):
        return form
    return form[: len(form) - len(source)] + target


def expected_subject_form(form: str) -> str | None:
    """Return a reviewed-pattern ``-u`` subject-surface candidate."""
    folded = form.casefold()
    if folded in PERSONAL_PRONOUN_FORMS:
        return None
    for non_subject, subject in NON_SUBJECT_TO_SUBJECT:
        if folded.endswith(non_subject):
            return _replace_suffix_preserving_case(form, non_subject, subject)
    return None


def expected_non_subject_form(form: str) -> str | None:
    """Return the paired absolute/non-subject definite surface."""
    folded = form.casefold()
    if folded in PERSONAL_PRONOUN_FORMS:
        return None
    for subject, non_subject in SUBJECT_TO_NON_SUBJECT:
        if folded.endswith(subject):
            return _replace_suffix_preserving_case(form, subject, non_subject)
    return None


def _reviewed_subject_forms() -> set[str]:
    """Load only exact noun subject surfaces explicitly reviewed by the project."""
    if not REVIEWED_NOUN_RULE_PATH.exists():
        return set()
    reviewed: set[str] = set()
    for line in REVIEWED_NOUN_RULE_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("id") not in {"GRAM-NGENDER-002", "GRAM-NGENDER-006"}:
            continue
        for item in record.get("forms", []):
            form = item.get("form")
            if isinstance(form, str):
                reviewed.add(form.casefold())
    return reviewed


def _analyze_focus_case(noun: str, marker: str) -> NounSubjectCaseAnalysis | None:
    """Return an exact reviewed common-noun focus-case analysis when possible."""
    reviewed = _reviewed_subject_forms()
    noun_key = noun.casefold()

    # Exact reviewed ordinary subject surface used incorrectly in subject focus.
    if noun_key in reviewed:
        absolute = expected_non_subject_form(noun)
        if absolute is None:
            return None
        return NounSubjectCaseAnalysis(
            recognized=True,
            noun_form=noun,
            marker=marker,
            expected_subject_form=absolute,
            agrees=False,
            rule_id="GRAM-SUBJFOCUS-005",
            note=(
                "A common-noun subject focused by baa/ayaa uses its paired absolute/non-subject "
                "surface rather than the ordinary -u nominative subject surface. No automatic rewrite."
            ),
        )

    # Correct absolute focus surface must map back to an exact reviewed subject form.
    subject = expected_subject_form(noun)
    if subject is None or subject.casefold() not in reviewed:
        return None
    return NounSubjectCaseAnalysis(
        recognized=True,
        noun_form=noun,
        marker=marker,
        expected_subject_form=noun,
        agrees=True,
        rule_id="GRAM-SUBJFOCUS-005",
        note=(
            "Exact reviewed absolute/non-subject noun surface found before a subject-focus baa/ayaa particle."
        ),
    )


def analyze_noun_subject_case(sentence: str) -> NounSubjectCaseAnalysis:
    """Analyze reviewed noun case before ``wuu/way`` and bare ``baa/ayaa``.

    Ordinary ``<noun> wuu/way`` keeps the established ``-u`` subject rule.
    Adjacent ``<noun> baa/ayaa`` is treated as true noun subject focus only when
    the noun belongs to an exact reviewed subject/absolute pair. Proper names and
    unknown noun pairs remain outside this case analyzer.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 2:
        return NounSubjectCaseAnalysis(recognized=False)

    for index in range(len(tokens) - 1):
        noun = tokens[index]
        marker = tokens[index + 1]
        noun_folded = noun.casefold()
        marker_folded = marker.casefold()

        if noun_folded in PERSONAL_PRONOUN_FORMS:
            continue

        if marker_folded in FOCUS_MARKERS:
            focus = _analyze_focus_case(noun, marker)
            if focus is not None:
                return focus
            continue

        if marker_folded not in SUBJECT_CLITICS:
            continue

        non_subject = expected_non_subject_form(noun)
        if non_subject is not None:
            return NounSubjectCaseAnalysis(
                recognized=True,
                noun_form=noun,
                marker=marker,
                expected_subject_form=noun,
                agrees=True,
                note=(
                    "Reviewed -u definite noun subject surface found before an explicit "
                    "third-person subject clitic."
                ),
            )

        subject = expected_subject_form(noun)
        if subject is not None:
            return NounSubjectCaseAnalysis(
                recognized=True,
                noun_form=noun,
                marker=marker,
                expected_subject_form=subject,
                agrees=False,
                note=(
                    "In this reviewed explicit-subject construction, the definite noun "
                    "is expected to use its -u subject surface. No automatic rewrite."
                ),
            )

    return NounSubjectCaseAnalysis(recognized=False)
