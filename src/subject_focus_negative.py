"""Conservative Somali negative true-subject-focus analysis.

Negative subject focus differs from ordinary main-clause ``ma`` negation. The
embedded/subjunctive negative ``aan`` fuses with ``baa/ayaa`` and is written
``baan/ayaan``. Those spellings are ambiguous with subject-clitic combinations
in other focus constructions, so this module never interprets the marker alone.
A negative-subject-focus reading requires an exact reviewed negative predicate.

Executable coverage is intentionally narrow:
- the exact published ``Cali baan bixin`` example (with source-supported
  ``ayaan`` particle equivalence);
- exact reviewed person-neutral negative simple-past and past-progressive verb
  surfaces already present in project morphology.

No negative surface is generated from suffixes and no present/future negative
focus paradigm is inferred.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from src.morphology_candidates import DEFAULT_MORPHOLOGY_PATHS
from src.noun_gender_agreement import REVIEWED_PLURAL_FORMS, REVIEWED_SINGULAR_FORMS

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)
NEGATIVE_FOCUS_MARKERS = {"baan", "ayaan"}
COVERED_TENSE_ASPECTS = {"tagto", "tagto_socota"}
MAX_PREDICATE_GAP = 4
SUBJECT_FOCUS_RULE_PATH = Path("rules/grammar/subject_focus_agreement.jsonl")

NON_SUBJECT_TO_SUBJECT = (
    ("sha", "shu"),
    ("ka", "ku"),
    ("ga", "gu"),
    ("ha", "hu"),
    ("ta", "tu"),
    ("da", "du"),
)
SUBJECT_TO_NON_SUBJECT = tuple((subject, non_subject) for non_subject, subject in NON_SUBJECT_TO_SUBJECT)

# Exact published negative-focus predicate evidence. This is sentence-level
# evidence only; it must not be used to invent a BAX paradigm.
EXACT_SOURCE_PREDICATES = {
    ("cali", "bixin"): "source_exact_cali_bixin",
}


@dataclass(frozen=True)
class SubjectFocusNegativeAnalysis:
    recognized: bool
    covered: bool = False
    subject: str | None = None
    marker: str | None = None
    predicate: str | None = None
    tense_aspect: str | None = None
    expected_subject_form: str | None = None
    case_agrees: bool | None = None
    evidence: str | None = None
    rule_id: str = "GRAM-SUBJFOCUS-NEG-001"
    note: str = ""


def _replace_suffix_preserving_case(form: str, source: str, target: str) -> str:
    if not form.casefold().endswith(source):
        return form
    return form[: len(form) - len(source)] + target


def _expected_subject_form(form: str) -> str | None:
    folded = form.casefold()
    for non_subject, subject in NON_SUBJECT_TO_SUBJECT:
        if folded.endswith(non_subject):
            return _replace_suffix_preserving_case(form, non_subject, subject)
    return None


def _expected_non_subject_form(form: str) -> str | None:
    folded = form.casefold()
    for subject, non_subject in SUBJECT_TO_NON_SUBJECT:
        if folded.endswith(subject):
            return _replace_suffix_preserving_case(form, subject, non_subject)
    return None


def _reviewed_proper_subjects() -> set[str]:
    if not SUBJECT_FOCUS_RULE_PATH.exists():
        return set()
    subjects: set[str] = set()
    for line in SUBJECT_FOCUS_RULE_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("category") not in {"subject_focus_particle", "subject_focus_baa"}:
            continue
        subject = record.get("subject")
        if isinstance(subject, str):
            subjects.add(subject.casefold())
    return subjects


def _is_reviewed_common_subject(surface: str) -> bool:
    folded = surface.casefold()
    return folded in REVIEWED_SINGULAR_FORMS or folded in REVIEWED_PLURAL_FORMS


def _subject_case_profile(surface: str) -> tuple[bool, str, str] | None:
    """Return ``(case_agrees, expected_surface, evidence)`` for reviewed subjects."""
    folded = surface.casefold()
    if folded in _reviewed_proper_subjects():
        return True, surface, "exact_reviewed_proper_subject"

    # Wrong ordinary nominative/subject form used under focus.
    if _is_reviewed_common_subject(surface):
        absolute = _expected_non_subject_form(surface)
        if absolute is None:
            return None
        return False, absolute, "reviewed_common_noun_wrong_focus_case"

    # Correct absolute form must map back to an exact reviewed subject surface.
    nominative = _expected_subject_form(surface)
    if nominative is None or not _is_reviewed_common_subject(nominative):
        return None
    return True, surface, "reviewed_common_noun_absolute_pair"


def _record_is_covered_negative(record: dict) -> bool:
    features = record.get("features", {})
    return (
        features.get("part_of_speech") == "verb"
        and features.get("polarity") == "negative"
        and features.get("person_neutralized") is True
        and features.get("tense_aspect") in COVERED_TENSE_ASPECTS
    )


@lru_cache(maxsize=1)
def _covered_negative_index() -> dict[str, tuple[dict, ...]]:
    index: dict[str, list[dict]] = {}
    for path in DEFAULT_MORPHOLOGY_PATHS:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            if not _record_is_covered_negative(record):
                continue
            surface = record.get("surface")
            if isinstance(surface, str):
                index.setdefault(surface.casefold(), []).append(record)
    return {key: tuple(records) for key, records in index.items()}


def _negative_predicate(surface: str) -> tuple[str, str] | None:
    records = _covered_negative_index().get(surface.casefold(), ())
    if not records:
        return None
    tenses: list[str] = []
    lemmas: list[str] = []
    for record in records:
        features = record.get("features", {})
        tense = features.get("tense_aspect")
        lemma = record.get("lemma")
        if isinstance(tense, str) and tense not in tenses:
            tenses.append(tense)
        if isinstance(lemma, str) and lemma not in lemmas:
            lemmas.append(lemma)
    tense_label = tenses[0] if len(tenses) == 1 else "reviewed_past_negative"
    lemma_label = "/".join(lemmas) if lemmas else "reviewed verb"
    return tense_label, lemma_label


def analyze_subject_focus_negative(sentence: str) -> SubjectFocusNegativeAnalysis:
    """Analyze exact reviewed ``SUBJECT + baan/ayaan + ... + NEG`` focus clauses.

    Because ``baan/ayaan`` are orthographically ambiguous, the function returns
    ``recognized=False`` unless the predicate independently proves the negative
    reading. For common nouns, the ordinary ``-u`` subject surface is then a
    review-only case conflict; the paired absolute surface is required.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 3:
        return SubjectFocusNegativeAnalysis(recognized=False)

    subject, marker = tokens[0], tokens[1]
    if marker.casefold() not in NEGATIVE_FOCUS_MARKERS:
        return SubjectFocusNegativeAnalysis(recognized=False)

    case_profile = _subject_case_profile(subject)
    if case_profile is None:
        return SubjectFocusNegativeAnalysis(recognized=False)
    case_agrees, expected_surface, subject_evidence = case_profile

    candidates = tokens[2 : 2 + MAX_PREDICATE_GAP + 1]
    for predicate in candidates:
        exact_key = (subject.casefold(), predicate.casefold())
        exact_evidence = EXACT_SOURCE_PREDICATES.get(exact_key)
        if exact_evidence is not None:
            return SubjectFocusNegativeAnalysis(
                recognized=True,
                covered=True,
                subject=subject,
                marker=marker,
                predicate=predicate,
                tense_aspect="source_exact_negative",
                expected_subject_form=expected_surface,
                case_agrees=case_agrees,
                evidence=f"{subject_evidence}+{exact_evidence}",
                note=(
                    "Exact published negative subject-focus example. The fused marker is "
                    "baa/ayaa + negative aan, not ordinary ma. No BAX paradigm is inferred "
                    "from this single surface."
                ),
            )

        negative = _negative_predicate(predicate)
        if negative is None:
            continue
        tense, lemma = negative
        return SubjectFocusNegativeAnalysis(
            recognized=True,
            covered=True,
            subject=subject,
            marker=marker,
            predicate=predicate,
            tense_aspect=tense,
            expected_subject_form=expected_surface,
            case_agrees=case_agrees,
            evidence=f"{subject_evidence}+exact_person_neutral_negative_{tense}",
            note=(
                f"The predicate is an exact reviewed person-neutral negative {tense} surface "
                f"for {lemma}. This independently disambiguates {marker} as negative subject "
                "focus. Common-noun focused subjects use the absolute case. No automatic rewrite."
            ),
        )

    # The marker alone is too ambiguous to license a negative-focus analysis.
    return SubjectFocusNegativeAnalysis(
        recognized=False,
        subject=subject,
        marker=marker,
        note=(
            "baan/ayaan is orthographically ambiguous outside a reviewed negative predicate "
            "context, so the project leaves this clause unjudged."
        ),
    )
