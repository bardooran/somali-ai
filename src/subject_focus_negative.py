"""Conservative Somali negative true-subject-focus analysis.

Negative subject focus differs from ordinary main-clause ``ma`` negation. The
embedded/subjunctive negative ``aan`` fuses with ``baa/ayaa`` and is written
``baan/ayaan``. Ordinary Somali spelling does not encode the pitch distinction
that can separate negative ``baa + aan`` from non-subject-focus ``baa + 1sg aan``.
The marker alone is therefore never enough to choose a negative-subject-focus
reading.

When negation co-occurs with focus, Somali uses the reduced subjunctive. In the
simple and progressive aspects these reduced forms do not distinguish present
from past and do not distinguish person/number. The project reuses only exact
person-neutral negative morphology already independently reviewed.

A second safety check is important: if the same written predicate surface also
has a reviewed non-negative verb analysis, ``baan/ayaan`` plus that surface is
still orthographically ambiguous. The analyzer then requires either exact
sentence-level evidence or an independently reviewed negative-context item. At
present ``waxba`` is the only such executable context item.

Bare positive ``baa/ayaa`` before an exact covered reduced negative predicate is
recognized as a review-only marker conflict: true negative subject focus requires
``baan/ayaan``. No automatic rewrite is made. Connective forms such as ``ayaana``
and clauses without a focus marker remain outside this rule until separately
modeled.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from src.morphology_candidates import DEFAULT_MORPHOLOGY_PATHS, analyze_surface_form

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", flags=re.UNICODE)
NEGATIVE_FOCUS_MARKERS = {"baan", "ayaan"}
POSITIVE_TO_NEGATIVE_FOCUS = {"baa": "baan", "ayaa": "ayaan"}
ALL_REVIEWED_FOCUS_MARKERS = NEGATIVE_FOCUS_MARKERS | set(POSITIVE_TO_NEGATIVE_FOCUS)
NEGATIVE_CONTEXT_ITEMS = {"waxba"}
COVERED_SOURCE_TENSE_ASPECTS = {"tagto", "tagto_socota"}
REDUCED_LABELS = {
    "tagto": "reduced_subjunctive_simple",
    "tagto_socota": "reduced_subjunctive_progressive",
}
MAX_PREDICATE_GAP = 4
SUBJECT_FOCUS_RULE_PATH = Path("rules/grammar/subject_focus_agreement.jsonl")
REVIEWED_NOUN_RULE_PATH = Path("rules/grammar/noun_subject_gender_agreement.jsonl")

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
    temporal_scope: tuple[str, ...] = ()
    expected_subject_form: str | None = None
    case_agrees: bool | None = None
    marker_agrees: bool | None = None
    expected_marker: str | None = None
    orthographically_ambiguous: bool = False
    predicate_has_nonnegative_analysis: bool | None = None
    negative_context_evidence: tuple[str, ...] = ()
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


@lru_cache(maxsize=1)
def _reviewed_common_subjects() -> set[str]:
    """Load exact reviewed ``-u`` noun subject surfaces without importing agreement code."""
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


def _is_reviewed_common_subject(surface: str) -> bool:
    return surface.casefold() in _reviewed_common_subjects()


def _subject_case_profile(surface: str) -> tuple[bool, str, str] | None:
    """Return ``(case_agrees, expected_surface, evidence)`` for reviewed subjects."""
    folded = surface.casefold()
    if folded in _reviewed_proper_subjects():
        return True, surface, "exact_reviewed_proper_subject"

    if _is_reviewed_common_subject(surface):
        absolute = _expected_non_subject_form(surface)
        if absolute is None:
            return None
        return False, absolute, "reviewed_common_noun_wrong_focus_case"

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
        and features.get("tense_aspect") in COVERED_SOURCE_TENSE_ASPECTS
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


def _negative_predicate(surface: str) -> tuple[str, tuple[str, ...], str] | None:
    """Return reduced-subjunctive label, temporal scope, and lemma evidence."""
    records = _covered_negative_index().get(surface.casefold(), ())
    if not records:
        return None

    source_tenses: list[str] = []
    lemmas: list[str] = []
    for record in records:
        features = record.get("features", {})
        tense = features.get("tense_aspect")
        lemma = record.get("lemma")
        if isinstance(tense, str) and tense not in source_tenses:
            source_tenses.append(tense)
        if isinstance(lemma, str) and lemma not in lemmas:
            lemmas.append(lemma)

    reduced_labels = {REDUCED_LABELS[tense] for tense in source_tenses if tense in REDUCED_LABELS}
    if len(reduced_labels) == 1:
        reduced_label = next(iter(reduced_labels))
    else:
        reduced_label = "reduced_subjunctive_negative"
    lemma_label = "/".join(lemmas) if lemmas else "reviewed verb"
    return reduced_label, ("present", "past"), lemma_label


def _has_nonnegative_verb_analysis(surface: str) -> bool:
    """Return True when the same reviewed spelling also has a non-negative verb use."""
    for candidate in analyze_surface_form(surface):
        features = candidate.features
        if features.get("part_of_speech") != "verb":
            continue
        if features.get("polarity") == "negative":
            continue
        return True
    return False


def _negative_context_evidence(tokens: list[str]) -> tuple[str, ...]:
    found: list[str] = []
    for token in tokens:
        folded = token.casefold()
        if folded in NEGATIVE_CONTEXT_ITEMS and folded not in found:
            found.append(folded)
    return tuple(found)


def _expected_negative_marker(marker: str) -> str | None:
    folded = marker.casefold()
    if folded in NEGATIVE_FOCUS_MARKERS:
        return marker
    expected = POSITIVE_TO_NEGATIVE_FOCUS.get(folded)
    if expected is None:
        return None
    if marker and marker[0].isupper():
        return expected.capitalize()
    return expected


def analyze_subject_focus_negative(sentence: str) -> SubjectFocusNegativeAnalysis:
    """Analyze reviewed negative true-subject-focus clauses conservatively.

    ``baan/ayaan`` alone never proves negation. A covered reduced negative
    predicate can support the reading only if its spelling has no reviewed
    non-negative verb analysis, or if independent reviewed negative context
    (currently ``waxba``) resolves that polarity ambiguity. Exact published
    sentence evidence remains independently licensed.

    Bare ``baa/ayaa`` plus a covered reduced negative predicate is recognized as
    a review-only marker conflict. Connective ``ayaana`` and markerless strings
    are intentionally not folded into this rule.
    """
    tokens = TOKEN_RE.findall(sentence)
    if len(tokens) < 3:
        return SubjectFocusNegativeAnalysis(recognized=False)

    subject, marker = tokens[0], tokens[1]
    marker_folded = marker.casefold()
    if marker_folded not in ALL_REVIEWED_FOCUS_MARKERS:
        return SubjectFocusNegativeAnalysis(recognized=False)

    case_profile = _subject_case_profile(subject)
    if case_profile is None:
        return SubjectFocusNegativeAnalysis(recognized=False)
    case_agrees, expected_surface, subject_evidence = case_profile

    candidates = tokens[2 : 2 + MAX_PREDICATE_GAP + 1]
    negative_context = _negative_context_evidence(candidates)
    marker_is_negative = marker_folded in NEGATIVE_FOCUS_MARKERS

    # Preserve the exact published BAX example without deriving an unseen
    # paradigm. Positive baa/ayaa with bixin is not judged from this one example.
    if marker_is_negative:
        for predicate in candidates:
            exact_key = (subject.casefold(), predicate.casefold())
            exact_evidence = EXACT_SOURCE_PREDICATES.get(exact_key)
            if exact_evidence is None:
                continue
            return SubjectFocusNegativeAnalysis(
                recognized=True,
                covered=True,
                subject=subject,
                marker=marker,
                predicate=predicate,
                tense_aspect="source_exact_negative",
                temporal_scope=("past",),
                expected_subject_form=expected_surface,
                case_agrees=case_agrees,
                marker_agrees=True,
                expected_marker=marker,
                orthographically_ambiguous=True,
                predicate_has_nonnegative_analysis=None,
                negative_context_evidence=negative_context,
                evidence=f"{subject_evidence}+{exact_evidence}",
                note=(
                    "Exact published negative subject-focus example. The written fused marker is "
                    "orthographically ambiguous in general, but this exact sentence-level source "
                    "licenses the negative reading. No BAX paradigm is inferred."
                ),
            )

    for predicate in candidates:
        negative = _negative_predicate(predicate)
        if negative is None:
            continue

        reduced_label, temporal_scope, lemma = negative
        has_nonnegative = _has_nonnegative_verb_analysis(predicate)
        if has_nonnegative and not negative_context:
            return SubjectFocusNegativeAnalysis(
                recognized=False,
                subject=subject,
                marker=marker,
                predicate=predicate,
                tense_aspect=reduced_label,
                temporal_scope=temporal_scope,
                expected_subject_form=expected_surface,
                case_agrees=None,
                marker_agrees=None,
                expected_marker=_expected_negative_marker(marker),
                orthographically_ambiguous=True,
                predicate_has_nonnegative_analysis=True,
                evidence="reviewed_predicate_surface_has_negative_and_nonnegative_analyses",
                note=(
                    "The predicate spelling has both reviewed negative and non-negative verb analyses. "
                    "Because Somali writing also leaves baan/ayaan focus ambiguity unresolved, the "
                    "project keeps this sentence unjudged without independent negative context."
                ),
            )

        expected_marker = _expected_negative_marker(marker)
        marker_agrees = marker_is_negative
        rule_id = "GRAM-SUBJFOCUS-NEG-001" if marker_agrees else "GRAM-SUBJFOCUS-NEG-004"
        context_label = "+negative_context_" + "_".join(negative_context) if negative_context else ""
        return SubjectFocusNegativeAnalysis(
            recognized=True,
            covered=True,
            subject=subject,
            marker=marker,
            predicate=predicate,
            tense_aspect=reduced_label,
            temporal_scope=temporal_scope,
            expected_subject_form=expected_surface,
            case_agrees=case_agrees,
            marker_agrees=marker_agrees,
            expected_marker=expected_marker,
            orthographically_ambiguous=marker_is_negative,
            predicate_has_nonnegative_analysis=has_nonnegative,
            negative_context_evidence=negative_context,
            evidence=f"{subject_evidence}+exact_person_neutral_{reduced_label}{context_label}",
            rule_id=rule_id,
            note=(
                f"The predicate is an exact reviewed person-neutral {reduced_label} surface for {lemma}. "
                "Under negation plus focus, the reduced subjunctive does not distinguish present from "
                "past or person/number. "
                + (
                    f"Reviewed negative context ({', '.join(negative_context)}) supports the negative reading. "
                    if negative_context
                    else "The predicate has no competing reviewed non-negative verb analysis, so it supports the negative reading. "
                )
                + (
                    "The negative focus marker agrees with this reading. "
                    if marker_agrees
                    else f"Bare {marker} does not contain negative aan; review against {expected_marker}. "
                )
                + "Common-noun focused subjects use the absolute case. No automatic rewrite."
            ),
        )

    return SubjectFocusNegativeAnalysis(
        recognized=False,
        subject=subject,
        marker=marker,
        orthographically_ambiguous=marker_is_negative,
        note=(
            "The focus marker and surrounding predicate do not provide enough reviewed evidence for "
            "a negative true-subject-focus reading, so the project leaves this clause unjudged."
        ),
    )
