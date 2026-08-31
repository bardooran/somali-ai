"""Conservative morphology candidate lookup for reviewed Somali surface forms.

This module intentionally does not perform open-ended suffix stripping. It only
returns analyses for surface forms stored in reviewed morphology datasets. That
gives the word analyzer a safe bridge from inflected or derived surface forms
to candidate lemmas while broader morphology remains under validation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

REVIEWED_NOUN_FORMS_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_noun_forms.jsonl"
)
REVIEWED_PLURAL_DEFINITE_FORMS_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_plural_definite_forms.jsonl"
)
REVIEWED_VERB_FORMS_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_verb_forms.jsonl"
)
REVIEWED_VERB_LEMMAS_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_verb_lemmas.jsonl"
)
REVIEWED_HEADWORD_MORPHOLOGY_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_headword_morphology.jsonl"
)
REVIEWED_COMPETITION_HEADWORDS_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_competition_headwords.jsonl"
)
REVIEWED_DHEH_EXPANSION_FORMS_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_dheh_expansion_forms.jsonl"
)
REVIEWED_IMOW_FORMS_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_imow_forms.jsonl"
)
REVIEWED_AQAAN_FORMS_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_aqaan_forms.jsonl"
)
REVIEWED_AAL_YAAL_FORMS_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_aal_yaal_forms.jsonl"
)
REVIEWED_AHAW_FORMS_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_ahaw_forms.jsonl"
)
REVIEWED_LEEYAHAY_FORMS_PATH = Path(
    "data/morphology/gothenburg_reviewed_leeyahay_forms.jsonl"
)
REVIEWED_FOCUS_EXAMPLE_FORMS_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_focus_example_forms.jsonl"
)
REVIEWED_VERB_CLASS_FORMS_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_verb_class_forms.jsonl"
)
REVIEWED_CLASS1_PAST_FORMS_PATH = Path(
    "data/morphology/qaamuus_corpus_reviewed_class1_past_forms.jsonl"
)
REVIEWED_CLASS2_3_PAST_FORMS_PATH = Path(
    "data/morphology/qaamuus_corpus_reviewed_class2_3_past_forms.jsonl"
)
REVIEWED_FUTURE_AUXILIARY_FORMS_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_future_auxiliary_forms.jsonl"
)
REVIEWED_NEGATIVE_FOCUS_AUXILIARY_FORMS_PATH = Path(
    "data/morphology/gothenburg_reviewed_negative_focus_auxiliaries.jsonl"
)
REVIEWED_NEGATIVE_FINITE_FORMS_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_negative_finite_forms.jsonl"
)
REVIEWED_PAST_ASPECT_FORMS_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_past_aspect_forms.jsonl"
)
REVIEWED_PAST_HABITUAL_STEMS_PATH = Path(
    "data/morphology/gothenburg_reviewed_past_habitual_stems.jsonl"
)
REVIEWED_CONDITIONAL_FORMS_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_conditional_forms.jsonl"
)
REVIEWED_IMPERATIVE_FORMS_PATH = Path(
    "data/morphology/qaamuus_2012_reviewed_imperative_forms.jsonl"
)
NATIVE_REVIEW_MAYDH_FORMS_PATH = Path(
    "data/morphology/native_review_jigjiga_maydh_forms.jsonl"
)
NATIVE_REVIEW_DERIVATIONAL_FORMS_PATH = Path(
    "data/morphology/native_review_jigjiga_derivational_forms.jsonl"
)
DEFAULT_MORPHOLOGY_PATHS = (
    REVIEWED_NOUN_FORMS_PATH,
    REVIEWED_PLURAL_DEFINITE_FORMS_PATH,
    REVIEWED_VERB_FORMS_PATH,
    REVIEWED_VERB_LEMMAS_PATH,
    REVIEWED_HEADWORD_MORPHOLOGY_PATH,
    REVIEWED_COMPETITION_HEADWORDS_PATH,
    REVIEWED_DHEH_EXPANSION_FORMS_PATH,
    REVIEWED_IMOW_FORMS_PATH,
    REVIEWED_AQAAN_FORMS_PATH,
    REVIEWED_AAL_YAAL_FORMS_PATH,
    REVIEWED_AHAW_FORMS_PATH,
    REVIEWED_LEEYAHAY_FORMS_PATH,
    REVIEWED_FOCUS_EXAMPLE_FORMS_PATH,
    REVIEWED_VERB_CLASS_FORMS_PATH,
    REVIEWED_CLASS1_PAST_FORMS_PATH,
    REVIEWED_CLASS2_3_PAST_FORMS_PATH,
    REVIEWED_FUTURE_AUXILIARY_FORMS_PATH,
    REVIEWED_NEGATIVE_FOCUS_AUXILIARY_FORMS_PATH,
    REVIEWED_NEGATIVE_FINITE_FORMS_PATH,
    REVIEWED_PAST_ASPECT_FORMS_PATH,
    REVIEWED_PAST_HABITUAL_STEMS_PATH,
    REVIEWED_CONDITIONAL_FORMS_PATH,
    REVIEWED_IMPERATIVE_FORMS_PATH,
    NATIVE_REVIEW_MAYDH_FORMS_PATH,
    NATIVE_REVIEW_DERIVATIONAL_FORMS_PATH,
)


@dataclass(frozen=True)
class MorphologyCandidate:
    surface: str
    lemma: str
    record_id: str
    analysis_type: str
    segmentation: str
    features: dict
    evidence_type: str
    source: str
    status: str
    executable: bool
    note: str
    raw: dict


def _load_jsonl(path: str | Path) -> list[dict]:
    records: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def _to_candidate(record: dict) -> MorphologyCandidate:
    return MorphologyCandidate(
        surface=record["surface"],
        lemma=record["lemma"],
        record_id=record.get("id", ""),
        analysis_type=record.get("analysis_type", ""),
        segmentation=record.get("segmentation", ""),
        features=dict(record.get("features", {})),
        evidence_type=record.get("evidence_type", ""),
        source=record.get("source", ""),
        status=record.get("status", ""),
        executable=bool(record.get("executable", False)),
        note=record.get("note", ""),
        raw=record,
    )


def _default_records() -> list[dict]:
    records: list[dict] = []
    for path in DEFAULT_MORPHOLOGY_PATHS:
        records.extend(_load_jsonl(path))
    return records


def reviewed_candidates_for_lemma(
    lemma: str,
    analysis_type: str | None = None,
) -> tuple[MorphologyCandidate, ...]:
    """Return exact reviewed records for a lemma, optionally filtered by type.

    This is an evidence lookup, not a generator. It is used when one analyzer
    needs to confirm that a corresponding reviewed paradigm actually exists
    before judging a contextual form.
    """
    lemma_key = lemma.strip().casefold()
    result: list[MorphologyCandidate] = []
    for record in _default_records():
        if str(record.get("lemma", "")).casefold() != lemma_key:
            continue
        if analysis_type is not None and record.get("analysis_type") != analysis_type:
            continue
        result.append(_to_candidate(record))
    return tuple(result)


def analyze_surface_form(
    form: str,
    path: str | Path | None = None,
) -> tuple[MorphologyCandidate, ...]:
    """Return reviewed morphology candidates for an exact surface form.

    By default all reviewed morphology datasets are searched. ``path`` can
    restrict lookup to one explicit JSONL file for tests or research.

    Matching is case-insensitive, but no characters are removed, replaced, or
    normalized beyond Unicode-preserving Python ``casefold`` comparison. If a
    form is absent from the reviewed datasets, the function returns an empty
    tuple rather than guessing a lemma or derivation.
    """
    query = form.strip().casefold()
    records = _load_jsonl(path) if path is not None else _default_records()
    return tuple(
        _to_candidate(record)
        for record in records
        if record.get("surface", "").casefold() == query
    )
