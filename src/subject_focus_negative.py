"""Conservative Somali negative true-subject-focus analysis.

Negative subject focus differs from ordinary main-clause ``ma`` negation. The
embedded/subjunctive negative ``aan`` fuses with ``baa/ayaa`` and is written
``baan/ayaan``. Ordinary spelling can leave this ambiguous with non-subject
focus plus first-singular ``aan``, so the marker alone never selects a negative
reading.

Covered reduced-subjunctive constructions are evidence-driven:

* simple/progressive: exact reviewed person-neutral negative surfaces;
* habitual: exact reviewed habitual stem + exact negative auxiliary ``jirin``;
* future: exact reviewed future stem + exact focus-reduced auxiliary ``doonin``.

No stem or suffix is generated. Bare ``baa/ayaa`` before a proven reduced
negative construction is review-only marker conflict; ``ayaana`` and markerless
fragments remain outside this rule.
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
MAX_PREDICATE_GAP = 5
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
    labels = {REDUCED_LABELS[t] for t in source_tenses if t in REDUCED_LABELS}
    reduced_label = next(iter(labels)) if len(labels) == 1 else "reduced_subjunctive_negative"
    return reduced_label, ("present", "past"), "/".join(lemmas) or "reviewed verb"


def _has_nonnegative_verb_analysis(surface: str) -> bool:
    for candidate in analyze_surface_form(surface):
        features = candidate.features
        if features.get("part_of_speech") != "verb":
            continue
        if features.get("polarity") == "negative":
            continue
        return True
    return False


def _stem_license(surface: str, construction: str) -> tuple[str, str] | None:
    """Return exact lemma/evidence when a surface is reviewed for a compound stem use."""
    for candidate in analyze_surface_form(surface):
        features = candidate.features
        if features.get("part_of_speech") != "verb":
            continue
        if construction == "habitual":
            licensed = (
                candidate.analysis_type == "past_habitual_stem"
                or features.get("possible_use") == "past_habitual_with_auxiliary"
                or "habitual_past_with_jir" in features.get("possible_functions", [])
            )
        else:
            licensed = (
                candidate.analysis_type == "masdar_or_future_stem"
                or features.get("possible_use") == "future_with_auxiliary"
                or "future_with_auxiliary" in features.get("possible_functions", [])
            )
        if licensed:
            return candidate.lemma, candidate.record_id
    return None


def _reviewed_auxiliary(surface: str, construction: str) -> str | None:
    for candidate in analyze_surface_form(surface):
        features = candidate.features
        if features.get("part_of_speech") != "auxiliary":
            continue
        if construction == "habitual":
            if (
                candidate.analysis_type == "negative_past_habitual_auxiliary"
                and features.get("polarity") == "negative"
                and features.get("person_neutralized") is True
            ):
                return candidate.record_id
        elif (
            candidate.analysis_type == "negative_focus_future_auxiliary"
            and features.get("polarity") == "negative"
            and features.get("person_neutralized") is True
        ):
            return candidate.record_id
    return None


def _compound_negative_predicate(tokens: list[str]) -> tuple[str, str, tuple[str, ...], str] | None:
    """Return exact reviewed stem+auxiliary reduced construction from a token window."""
    for index in range(len(tokens) - 1):
        stem, auxiliary = tokens[index], tokens[index + 1]
        aux_folded = auxiliary.casefold()
        if aux_folded == "jirin":
            stem_info = _stem_license(stem, "habitual")
            aux_record = _reviewed_auxiliary(auxiliary, "habitual")
            if stem_info and aux_record:
                lemma, stem_record = stem_info
                evidence = f"{stem_record}+{aux_record}"
                return f"{stem} {auxiliary}", "reduced_subjunctive_habitual", ("past_habitual",), f"{lemma}:{evidence}"
        elif aux_folded == "doonin":
            stem_info = _stem_license(stem, "future")
            aux_record = _reviewed_auxiliary(auxiliary, "future")
            if stem_info and aux_record:
                lemma, stem_record = stem_info
                evidence = f"{stem_record}+{aux_record}"
                return f"{stem} {auxiliary}", "reduced_subjunctive_future", ("future",), f"{lemma}:{evidence}"
    return None


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
    return expected.capitalize() if marker and marker[0].isupper() else expected


def _covered_result(
    *,
    subject: str,
    marker: str,
    predicate: str,
    reduced_label: str,
    temporal_scope: tuple[str, ...],
    expected_surface: str,
    case_agrees: bool,
    subject_evidence: str,
    negative_context: tuple[str, ...],
    predicate_evidence: str,
    predicate_has_nonnegative_analysis: bool = False,
) -> SubjectFocusNegativeAnalysis:
    marker_is_negative = marker.casefold() in NEGATIVE_FOCUS_MARKERS
    expected_marker = _expected_negative_marker(marker)
    rule_id = "GRAM-SUBJFOCUS-NEG-001" if marker_is_negative else "GRAM-SUBJFOCUS-NEG-006"
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
        marker_agrees=marker_is_negative,
        expected_marker=expected_marker,
        orthographically_ambiguous=marker_is_negative,
        predicate_has_nonnegative_analysis=predicate_has_nonnegative_analysis,
        negative_context_evidence=negative_context,
        evidence=f"{subject_evidence}+{predicate_evidence}{context_label}",
        rule_id=rule_id,
        note=(
            f"Exact reviewed {reduced_label} evidence supports a negative subject-focus reading. "
            + (
                "The negative focus marker agrees. "
                if marker_is_negative
                else f"Bare {marker} lacks negative aan; review against {expected_marker}. "
            )
            + "The construction is person-neutral where documented; no automatic rewrite."
        ),
    )


def analyze_subject_focus_negative(sentence: str) -> SubjectFocusNegativeAnalysis:
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

    if marker_is_negative:
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
                    temporal_scope=("past",),
                    expected_subject_form=expected_surface,
                    case_agrees=case_agrees,
                    marker_agrees=True,
                    expected_marker=marker,
                    orthographically_ambiguous=True,
                    negative_context_evidence=negative_context,
                    evidence=f"{subject_evidence}+{exact_evidence}",
                    note="Exact published negative subject-focus example; no BAX paradigm is inferred.",
                )

    compound = _compound_negative_predicate(candidates)
    if compound is not None:
        predicate, reduced_label, temporal_scope, compound_evidence = compound
        return _covered_result(
            subject=subject,
            marker=marker,
            predicate=predicate,
            reduced_label=reduced_label,
            temporal_scope=temporal_scope,
            expected_surface=expected_surface,
            case_agrees=case_agrees,
            subject_evidence=subject_evidence,
            negative_context=negative_context,
            predicate_evidence=f"exact_compound_{compound_evidence}",
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
                note="Predicate and focus-marker spellings are both ambiguous; leave unjudged without independent negative context.",
            )
        return _covered_result(
            subject=subject,
            marker=marker,
            predicate=predicate,
            reduced_label=reduced_label,
            temporal_scope=temporal_scope,
            expected_surface=expected_surface,
            case_agrees=case_agrees,
            subject_evidence=subject_evidence,
            negative_context=negative_context,
            predicate_evidence=f"exact_person_neutral_{reduced_label}_{lemma}",
            predicate_has_nonnegative_analysis=has_nonnegative,
        )

    return SubjectFocusNegativeAnalysis(
        recognized=False,
        subject=subject,
        marker=marker,
        orthographically_ambiguous=marker_is_negative,
        note="Insufficient reviewed evidence for a negative true-subject-focus reading.",
    )
