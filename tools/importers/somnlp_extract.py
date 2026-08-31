"""Extract bounded QA/attestation candidates from a local SomNLP corpus.

This module is independently implemented for somali-grammar. It does not copy
SomNLP pipeline code and does not promote corpus text into trusted grammar.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator, TextIO

SOURCE_PROJECT = "SomNLP-Corpus"
SOURCE_REPOSITORY = "goobolabs/SomNLP-Corpus"
STATUS = "external_corpus_attestation_unreviewed"


@dataclass(frozen=True)
class SourcePolicy:
    tier: str
    evidence_role: str
    expected_license: str | None
    redistribution_resolved: bool


SOURCE_POLICIES: dict[str, SourcePolicy] = {
    "wikipedia": SourcePolicy("A", "edited_native_use_qa", "CC-BY-SA-4.0", True),
    "xlsum": SourcePolicy("A", "edited_news_qa", "CC-BY-4.0", True),
    "hplt": SourcePolicy("B", "broad_web_attestation", "CC0-1.0", True),
    "cc100": SourcePolicy("B", "broad_web_attestation", "CC-BY-SA-4.0", True),
    "mc4": SourcePolicy("B", "broad_web_attestation", "ODC-BY", True),
    "madlad": SourcePolicy("B", "broad_web_attestation", "ODC-BY", True),
    "opus": SourcePolicy("C", "parallel_translation_attestation", "CC0-1.0", True),
    "mt560": SourcePolicy("C", "parallel_translation_attestation", "CC-BY-4.0", True),
    "nllb": SourcePolicy("C", "parallel_translation_attestation", "ODC-BY", True),
    "quran": SourcePolicy("D", "specialized_religious_translation", None, False),
    "tanzil": SourcePolicy("D", "specialized_religious_translation", None, False),
    "quran-tanzil": SourcePolicy("D", "specialized_religious_translation", None, False),
}


@dataclass(frozen=True)
class CorpusAttestationCandidate:
    corpus_record_id: str
    text: str
    source: str
    source_license: str
    evidence_tier: str
    evidence_role: str
    source_project: str
    source_repository: str
    source_commit: str
    corpus_schema_version: int | None
    lang: str | None
    status: str
    promotion_allowed: bool
    correctness_inference_allowed: bool


def _require_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def parse_corpus_record(
    record: dict,
    *,
    source_commit: str,
    requested_sources: set[str] | None = None,
    allow_unresolved_license: bool = False,
) -> CorpusAttestationCandidate | None:
    """Validate one SomNLP processed record and return an unreviewed candidate.

    Non-kept records and records outside the requested source set return None.
    Malformed provenance/license metadata raises ValueError so silent provenance
    loss cannot enter a QA dataset.
    """

    if not source_commit.strip():
        raise ValueError("source_commit is required for provenance")

    quality = record.get("quality")
    if not isinstance(quality, dict):
        raise ValueError("quality metadata is required")
    disposition = quality.get("disposition")
    if disposition != "kept":
        return None

    provenance = record.get("provenance")
    if not isinstance(provenance, dict):
        raise ValueError("provenance metadata is required")
    source = _require_string(provenance.get("source"), "provenance.source")

    if requested_sources is not None and source not in requested_sources:
        return None

    policy = SOURCE_POLICIES.get(source)
    if policy is None:
        raise ValueError(f"unrecognized SomNLP source key: {source}")

    source_license = _require_string(record.get("license"), "license")
    if policy.expected_license is not None and source_license != policy.expected_license:
        raise ValueError(
            f"license mismatch for {source}: expected {policy.expected_license}, got {source_license}"
        )
    if not policy.redistribution_resolved and not allow_unresolved_license:
        return None

    corpus_record_id = _require_string(record.get("id"), "id")
    text = _require_string(record.get("text"), "text")
    lang_value = provenance.get("lang")
    lang = lang_value if isinstance(lang_value, str) and lang_value else None
    schema_version = record.get("schema_version")
    if schema_version is not None and not isinstance(schema_version, int):
        raise ValueError("schema_version must be an integer when present")

    return CorpusAttestationCandidate(
        corpus_record_id=corpus_record_id,
        text=text,
        source=source,
        source_license=source_license,
        evidence_tier=policy.tier,
        evidence_role=policy.evidence_role,
        source_project=SOURCE_PROJECT,
        source_repository=SOURCE_REPOSITORY,
        source_commit=source_commit,
        corpus_schema_version=schema_version,
        lang=lang,
        status=STATUS,
        promotion_allowed=False,
        correctness_inference_allowed=False,
    )


def iter_jsonl_candidates(
    handle: TextIO,
    *,
    source_commit: str,
    requested_sources: set[str],
    per_source_limit: int,
    allow_unresolved_license: bool = False,
) -> Iterator[CorpusAttestationCandidate]:
    """Stream a balanced, bounded candidate sample from processed JSONL."""

    if not requested_sources:
        raise ValueError("at least one requested source is required")
    unknown = requested_sources - SOURCE_POLICIES.keys()
    if unknown:
        raise ValueError(f"unknown requested SomNLP sources: {sorted(unknown)}")
    if per_source_limit < 1:
        raise ValueError("per_source_limit must be at least 1")

    counts = {source: 0 for source in requested_sources}
    for line_number, raw_line in enumerate(handle, start=1):
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSON on line {line_number}: {error.msg}") from error
        if not isinstance(record, dict):
            raise ValueError(f"JSON line {line_number} must be an object")

        candidate = parse_corpus_record(
            record,
            source_commit=source_commit,
            requested_sources=requested_sources,
            allow_unresolved_license=allow_unresolved_license,
        )
        if candidate is None:
            continue
        if counts[candidate.source] >= per_source_limit:
            continue

        counts[candidate.source] += 1
        yield candidate

        # Stop once every requested source has reached its quota. Unresolved
        # sources will normally never reach it unless explicitly enabled.
        active_sources = {
            source
            for source in requested_sources
            if SOURCE_POLICIES[source].redistribution_resolved or allow_unresolved_license
        }
        if active_sources and all(counts[source] >= per_source_limit for source in active_sources):
            break


def write_jsonl(records: Iterable[CorpusAttestationCandidate], output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(asdict(record), ensure_ascii=False, sort_keys=True))
            handle.write("\n")
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract bounded, unreviewed QA candidates from a local SomNLP processed corpus."
    )
    parser.add_argument("corpus", type=Path, help="Processed SomNLP CorpusRecord JSONL")
    parser.add_argument("--source-commit", required=True, help="Exact SomNLP source commit SHA")
    parser.add_argument("--output", type=Path, required=True, help="Output candidate JSONL")
    parser.add_argument(
        "--source",
        action="append",
        required=True,
        choices=sorted(SOURCE_POLICIES),
        dest="sources",
        help="Source registry key to sample; repeat for multiple source families",
    )
    parser.add_argument(
        "--per-source-limit",
        type=int,
        default=500,
        help="Maximum kept records emitted per requested source (default: 500)",
    )
    parser.add_argument(
        "--allow-unresolved-license",
        action="store_true",
        help="Allow specialized sources whose redistribution license is unresolved; off by default",
    )
    args = parser.parse_args()

    with args.corpus.open("r", encoding="utf-8-sig") as handle:
        records = iter_jsonl_candidates(
            handle,
            source_commit=args.source_commit,
            requested_sources=set(args.sources),
            per_source_limit=args.per_source_limit,
            allow_unresolved_license=args.allow_unresolved_license,
        )
        count = write_jsonl(records, args.output)

    print(f"wrote {count} unreviewed SomNLP corpus-attestation candidates to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
