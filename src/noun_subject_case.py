"""Context-limited Somali definite-noun subject-case analysis.

This module generalizes a reviewed pattern without turning it into a global
string replacement. In explicit subject constructions with third-person subject
clitics such as ``wuu`` and ``way``, reviewed definite noun surfaces ending in
article-like ``-a`` allomorphs are expected to use the corresponding ``-u``
subject surface. Focus constructions headed by ``ayaa``/``baa`` are outside this
rule and must not be rewritten.

The analyzer is review-only: it can flag a likely case conflict, but it never
autocorrects text and it does not claim a dictionary lemma for unseen nouns.
Personal pronouns are excluded because they have their own reviewed paradigm
and must not be analyzed as ordinary article-bearing nouns.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Somali apostrophe/glottal-mark spellings can occur inside or at the end of a
# lexical word (for example the source-backed noun bu'). Keep those marks inside
# a token instead of silently splitting the word before grammar analysis.
TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*['’]?", flags=re.UNICODE)

# Longest suffixes first so -sha/-shu are not swallowed by -ha/-hu.
NON_SUBJECT_TO_SUBJECT = (
    ("sha", "shu"),
    ("ka", "ku"),
    ("ga", "gu"),
    ("ha", "hu"),
    ("ta", "tu"),
    ("da", "du"),
)
SUBJECT_TO_NON_SUBJECT = tuple((subject, non_subject) for non_subject, subject in NON_SUBJECT_TO_SUBJECT)

# Start with the constructions directly reviewed in this project. Broader
# predicate/focus contexts can be added after targeted native review.
SUBJECT_CLITICS = {"wuu", "way"}
BLOCKED_FOCUS_MARKERS = {"ayaa", "baa"}

# Independent personal pronouns belong to the pronoun system rather than the
# ordinary definite-noun case rule. Include both common non-u and u surfaces so
# neither side is misclassified here.
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
    """Return a reviewed subject-surface candidate for an article-like noun.

    This function only maps the reviewed definite article surface families and
    does not attempt to derive a lemma.
    """
    folded = form.casefold()
    if folded in PERSONAL_PRONOUN_FORMS:
        return None
    for non_subject, subject in NON_SUBJECT_TO_SUBJECT:
        if folded.endswith(non_subject):
            return _replace_suffix_preserving_case(form, non_subject, subject)
    return None


def expected_non_subject_form(form: str) -> str | None:
    """Return the paired non-subject definite surface for a reviewed subject form."""
    folded = form.casefold()
    if folded in PERSONAL_PRONOUN_FORMS:
        return None
    for subject, non_subject in SUBJECT_TO_NON_SUBJECT:
        if folded.endswith(subject):
            return _replace_suffix_preserving_case(form, subject, non_subject)
    return None


def analyze_noun_subject_case(sentence: str) -> NounSubjectCaseAnalysis:
    """Analyze the first explicit noun + subject-clitic pair in ``sentence``.

    Adjacent ``<noun> wuu`` / ``<noun> way`` pairs are currently in scope. A
    noun already carrying a reviewed ``-u`` subject surface agrees. A paired
    ``-a`` surface is returned as a review-only conflict with the expected
    ``-u`` form. Personal pronouns and other contexts remain outside this rule.
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
        if marker_folded in BLOCKED_FOCUS_MARKERS:
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
