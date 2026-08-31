"""Competitive morphology measurement for Somali AI.

The purpose of this module is not to declare a winner from raw record counts.
It measures the gap between our reviewed executable/evidence-backed morphology
and the broader GiellaLT candidate inventory, while preserving the project's
strict no-guess policy.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator

from .morphology_candidates import DEFAULT_MORPHOLOGY_PATHS, analyze_surface_form


GIELLALT_CANDIDATES_PATH = Path("data/imported/giellalt/lexical_candidates.jsonl")
VOCABULARY_ROOT = Path("data/vocabulary")
GIELLALT_REPORTED_LEMMA_BASELINE = 14_500

# Deliberate sentinel/unknown probes. They test that the evidence-backed
# analyzer does not manufacture analyses for unseen forms.
SAFETY_PROBES = (
    "cunXYZ",
    "magacaanlaaqoon",
    "buugtayda",
    "adkeeyeenno",
)


@dataclass(frozen=True)
class MorphologyBacklogItem:
    lemma: str
    candidate_types: tuple[str, ...]
    reviewed_types: tuple[str, ...]
    vocabulary_statuses: tuple[str, ...]
    vocabulary_domains: tuple[str, ...]
    source_paths: tuple[str, ...]
    priority: float
    promotion_allowed: bool = False


@dataclass(frozen=True)
class MorphologyScorecard:
    reviewed_surface_count: int
    reviewed_lemma_count: int
    reviewed_feature_dimensions: tuple[str, ...]
    reviewed_ambiguous_surface_count: int
    giellalt_candidate_row_count: int
    giellalt_candidate_unique_lemma_count: int
    giellalt_candidate_unique_lemma_type_count: int
    giellalt_candidate_type_counts: dict[str, int]
    giellalt_unique_lemma_counts_by_type: dict[str, int]
    reviewed_giellalt_shared_lemma_count: int
    reviewed_giellalt_shared_lemma_type_count: int
    reviewed_giellalt_type_mismatch_lemma_count: int
    cross_source_backlog_count: int
    cross_source_backlog_analysis_count: int
    giellalt_only_lemma_count: int
    giellalt_reported_lemma_baseline: int
    reviewed_breadth_gap_to_reported_giellalt: int
    safety_probe_count: int
    safety_probe_guess_count: int
    safety_probe_guess_rate: float


def _read_jsonl(path: Path) -> Iterator[dict]:
    if not path.is_file():
        return
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                yield value


def _walk_dicts(value: object) -> Iterator[dict]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_dicts(child)


def _read_json_records(path: Path) -> Iterator[dict]:
    if path.suffix == ".jsonl":
        yield from _read_jsonl(path)
        return
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return
    yield from _walk_dicts(value)


def reviewed_morphology_records(
    paths: Iterable[Path] = DEFAULT_MORPHOLOGY_PATHS,
) -> tuple[dict, ...]:
    records: list[dict] = []
    for path in paths:
        records.extend(_read_jsonl(Path(path)))
    return tuple(records)


def giellalt_candidate_records(
    path: Path = GIELLALT_CANDIDATES_PATH,
) -> tuple[dict, ...]:
    return tuple(_read_jsonl(path))


def vocabulary_records(root: Path = VOCABULARY_ROOT) -> tuple[dict, ...]:
    records: list[dict] = []
    if not root.exists():
        return ()
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix in {".json", ".jsonl"}:
            records.extend(_read_json_records(path))
    return tuple(records)


def _normalized_lemma(record: dict) -> str:
    value = record.get("lemma", "")
    return value.casefold().strip() if isinstance(value, str) else ""


def _reviewed_lemma_set(records: Iterable[dict]) -> set[str]:
    return {lemma for record in records if (lemma := _normalized_lemma(record))}


def _reviewed_surface_set(records: Iterable[dict]) -> set[str]:
    result: set[str] = set()
    for record in records:
        value = record.get("surface", "")
        if isinstance(value, str) and value.strip():
            result.add(value.casefold().strip())
    return result


def _feature_dimensions(records: Iterable[dict]) -> set[str]:
    dimensions: set[str] = set()
    for record in records:
        features = record.get("features")
        if isinstance(features, dict):
            dimensions.update(str(key) for key in features)
    return dimensions


def _freeze(value: object) -> object:
    if isinstance(value, dict):
        return tuple(sorted((str(key), _freeze(child)) for key, child in value.items()))
    if isinstance(value, list):
        return tuple(_freeze(child) for child in value)
    if isinstance(value, set):
        return tuple(sorted(_freeze(child) for child in value))
    return value


_ANALYSIS_FEATURE_KEYS = (
    "part_of_speech",
    "gender",
    "noun_gender",
    "number",
    "definiteness",
    "conjugation_class",
    "person",
    "possible_persons",
    "tense_aspect",
    "mood",
    "polarity",
    "transitivity",
    "possible_transitivity",
    "source_pos",
    "morphology_type",
)


def _analysis_signature(record: dict) -> tuple[object, ...]:
    features = record.get("features")
    feature_dict = features if isinstance(features, dict) else {}
    selected = {
        key: feature_dict[key]
        for key in _ANALYSIS_FEATURE_KEYS
        if key in feature_dict
    }
    return (
        str(record.get("analysis_type", "")),
        record.get("homograph_index"),
        _normalized_lemma(record),
        _freeze(selected),
    )


def _ambiguous_surfaces(records: Iterable[dict]) -> set[str]:
    """Return surfaces with explicit or structurally distinct reviewed analyses.

    This counts both feature-level ambiguity (for example a finite form that can
    realize more than one person) and same-surface homographs such as noun/verb
    ``kor`` or masculine/feminine ``inan``. Duplicate evidence for the same
    analysis does not create ambiguity by itself.
    """

    signatures: dict[str, set[tuple[object, ...]]] = defaultdict(set)
    explicit: set[str] = set()

    for record in records:
        surface = record.get("surface")
        if not isinstance(surface, str) or not surface.strip():
            continue
        surface_key = surface.casefold().strip()
        signatures[surface_key].add(_analysis_signature(record))

        status = str(record.get("status", "")).casefold()
        features = record.get("features", {})
        possible = features.get("possible_persons") if isinstance(features, dict) else None
        if "ambiguous" in status or "context_required" in status:
            explicit.add(surface_key)
        elif isinstance(possible, list) and len(possible) > 1:
            explicit.add(surface_key)

    structural = {
        surface for surface, analyses in signatures.items() if len(analyses) > 1
    }
    return explicit | structural


def _coarse_reviewed_type(record: dict) -> str:
    features = record.get("features")
    if isinstance(features, dict):
        part_of_speech = str(features.get("part_of_speech", "")).casefold().strip()
        if part_of_speech in {"noun", "verb", "adjective", "numeral"}:
            return part_of_speech

    analysis_type = str(record.get("analysis_type", "")).casefold()
    for candidate_type in ("noun", "verb", "adjective", "numeral"):
        if candidate_type in analysis_type:
            return candidate_type
    return ""


def _reviewed_types_by_lemma(records: Iterable[dict]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = defaultdict(set)
    for record in records:
        lemma = _normalized_lemma(record)
        reviewed_type = _coarse_reviewed_type(record)
        if lemma and reviewed_type:
            result[lemma].add(reviewed_type)
    return result


def _candidate_sets(
    records: Iterable[dict],
) -> tuple[set[str], Counter, dict[str, set[str]], dict[str, set[str]]]:
    lemmas: set[str] = set()
    row_counts: Counter = Counter()
    by_type: dict[str, set[str]] = defaultdict(set)
    paths_by_lemma: dict[str, set[str]] = defaultdict(set)
    for record in records:
        lemma = _normalized_lemma(record)
        if not lemma:
            continue
        record_type = str(record.get("record_type", "unknown"))
        lemmas.add(lemma)
        row_counts[record_type] += 1
        by_type[record_type].add(lemma)
        path = record.get("source_path")
        if isinstance(path, str) and path:
            paths_by_lemma[lemma].add(path)
    return lemmas, row_counts, by_type, paths_by_lemma


def _vocabulary_by_lemma(records: Iterable[dict]) -> dict[str, list[dict]]:
    result: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        lemma = _normalized_lemma(record)
        if lemma:
            result[lemma].append(record)
    return result


def cross_source_backlog(
    *,
    reviewed: Iterable[dict] | None = None,
    giellalt: Iterable[dict] | None = None,
    vocabulary: Iterable[dict] | None = None,
) -> tuple[MorphologyBacklogItem, ...]:
    """Return source-supported GiellaLT analyses still awaiting review.

    The queue is lemma + candidate-type aware. Reviewing a noun sense therefore
    does not silently remove an unreviewed verb or adjective analysis for the
    same spelling. This is a prioritization queue only; it never authorizes
    automatic promotion or paradigm generation.
    """

    reviewed_records = (
        tuple(reviewed) if reviewed is not None else reviewed_morphology_records()
    )
    giellalt_records = (
        tuple(giellalt) if giellalt is not None else giellalt_candidate_records()
    )
    vocabulary_rows = (
        tuple(vocabulary) if vocabulary is not None else vocabulary_records()
    )

    candidate_lemmas, _, candidate_by_type, paths_by_lemma = _candidate_sets(
        giellalt_records
    )
    reviewed_types_by_lemma = _reviewed_types_by_lemma(reviewed_records)
    vocab_by_lemma = _vocabulary_by_lemma(vocabulary_rows)

    candidate_types_by_lemma: dict[str, set[str]] = defaultdict(set)
    for record_type, lemmas in candidate_by_type.items():
        for lemma in lemmas:
            candidate_types_by_lemma[lemma].add(record_type)

    items: list[MorphologyBacklogItem] = []
    for lemma in sorted(candidate_lemmas & set(vocab_by_lemma)):
        rows = vocab_by_lemma[lemma]
        reviewed_types = reviewed_types_by_lemma.get(lemma, set())
        outstanding_types = candidate_types_by_lemma[lemma] - reviewed_types
        if not outstanding_types:
            continue

        statuses = {
            str(row.get("status", "unspecified"))
            for row in rows
        }
        domains = {
            str(row.get("domain", "unspecified"))
            for row in rows
            if row.get("domain")
        }

        priority = 1.0
        if "everyday" in domains:
            priority += 3.0
        if "verb" in outstanding_types:
            priority += 2.0
        if "adjective" in outstanding_types:
            priority += 1.5
        if "noun" in outstanding_types:
            priority += 1.0
        if any("source_backed" in status for status in statuses):
            priority += 1.0

        items.append(
            MorphologyBacklogItem(
                lemma=lemma,
                candidate_types=tuple(sorted(outstanding_types)),
                reviewed_types=tuple(sorted(reviewed_types)),
                vocabulary_statuses=tuple(sorted(statuses)),
                vocabulary_domains=tuple(sorted(domains)),
                source_paths=tuple(sorted(paths_by_lemma[lemma])),
                priority=priority,
            )
        )

    items.sort(key=lambda item: (-item.priority, item.lemma))
    return tuple(items)


def build_scorecard() -> MorphologyScorecard:
    reviewed = reviewed_morphology_records()
    giellalt = giellalt_candidate_records()
    vocabulary = vocabulary_records()

    reviewed_lemmas = _reviewed_lemma_set(reviewed)
    reviewed_surfaces = _reviewed_surface_set(reviewed)
    reviewed_types_by_lemma = _reviewed_types_by_lemma(reviewed)
    candidate_lemmas, row_counts, by_type, _ = _candidate_sets(giellalt)
    vocab_lemmas = set(_vocabulary_by_lemma(vocabulary))
    backlog = cross_source_backlog(
        reviewed=reviewed,
        giellalt=giellalt,
        vocabulary=vocabulary,
    )

    candidate_pairs = {
        (lemma, record_type)
        for record_type, lemmas in by_type.items()
        for lemma in lemmas
    }
    reviewed_pairs = {
        (lemma, reviewed_type)
        for lemma, reviewed_types in reviewed_types_by_lemma.items()
        for reviewed_type in reviewed_types
    }
    candidate_types_by_lemma = {
        lemma: {
            record_type
            for record_type, lemmas in by_type.items()
            if lemma in lemmas
        }
        for lemma in candidate_lemmas
    }
    shared_lemmas = reviewed_lemmas & candidate_lemmas
    type_mismatch_lemmas = {
        lemma
        for lemma in shared_lemmas
        if not (
            reviewed_types_by_lemma.get(lemma, set())
            & candidate_types_by_lemma.get(lemma, set())
        )
    }

    guessed = sum(bool(analyze_surface_form(probe)) for probe in SAFETY_PROBES)
    probe_count = len(SAFETY_PROBES)

    return MorphologyScorecard(
        reviewed_surface_count=len(reviewed_surfaces),
        reviewed_lemma_count=len(reviewed_lemmas),
        reviewed_feature_dimensions=tuple(sorted(_feature_dimensions(reviewed))),
        reviewed_ambiguous_surface_count=len(_ambiguous_surfaces(reviewed)),
        giellalt_candidate_row_count=len(giellalt),
        giellalt_candidate_unique_lemma_count=len(candidate_lemmas),
        giellalt_candidate_unique_lemma_type_count=len(candidate_pairs),
        giellalt_candidate_type_counts=dict(sorted(row_counts.items())),
        giellalt_unique_lemma_counts_by_type={
            key: len(values) for key, values in sorted(by_type.items())
        },
        reviewed_giellalt_shared_lemma_count=len(shared_lemmas),
        reviewed_giellalt_shared_lemma_type_count=len(reviewed_pairs & candidate_pairs),
        reviewed_giellalt_type_mismatch_lemma_count=len(type_mismatch_lemmas),
        cross_source_backlog_count=len(backlog),
        cross_source_backlog_analysis_count=sum(
            len(item.candidate_types) for item in backlog
        ),
        giellalt_only_lemma_count=len(candidate_lemmas - reviewed_lemmas - vocab_lemmas),
        giellalt_reported_lemma_baseline=GIELLALT_REPORTED_LEMMA_BASELINE,
        reviewed_breadth_gap_to_reported_giellalt=max(
            GIELLALT_REPORTED_LEMMA_BASELINE - len(reviewed_lemmas), 0
        ),
        safety_probe_count=probe_count,
        safety_probe_guess_count=guessed,
        safety_probe_guess_rate=(guessed / probe_count) if probe_count else 0.0,
    )


def report(limit: int = 20) -> dict:
    scorecard = build_scorecard()
    backlog = cross_source_backlog()[: max(limit, 0)]
    return {
        "scorecard": asdict(scorecard),
        "backlog_preview": [asdict(item) for item in backlog],
        "interpretation": {
            "raw_counts_are_not_a_win": True,
            "external_candidates_auto_promote": False,
            "target": "exceed competitor breadth while preserving deeper reviewed features and near-zero unsafe guessing",
        },
    }


def main() -> int:
    print(json.dumps(report(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
