"""Build compact Tier-A natural Somali usage candidates from SomNLP downloads.

This importer is intentionally separate from grammar promotion. It converts
bounded raw Wikipedia / XL-Sum downloads into retrieval-friendly usage excerpts
with dataset-level provenance and per-source licensing. Appearance in these
sources is evidence of use, not proof that a construction is grammatically
correct or preferred by Somali AI.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator

STATUS = "external_natural_usage_unreviewed"
SOURCE_PROJECT = "SomNLP-Corpus"
SOURCE_REPOSITORY = "goobolabs/SomNLP-Corpus"
SPACE_RE = re.compile(r"\s+")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
WORD_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)?", flags=re.UNICODE)


@dataclass(frozen=True)
class UsageSource:
    dataset: str
    dataset_config: str
    dataset_url: str
    source_license: str
    evidence_role: str


SOURCES: dict[str, UsageSource] = {
    "wikipedia": UsageSource(
        dataset="wikimedia/wikipedia",
        dataset_config="20231101.so",
        dataset_url="https://huggingface.co/datasets/wikimedia/wikipedia",
        source_license="CC-BY-SA-4.0",
        evidence_role="edited_native_use_attestation",
    ),
    "xlsum": UsageSource(
        dataset="csebuetnlp/xlsum",
        dataset_config="somali",
        dataset_url="https://huggingface.co/datasets/csebuetnlp/xlsum",
        source_license="CC-BY-4.0",
        evidence_role="edited_news_summary_attestation",
    ),
}


@dataclass(frozen=True)
class NaturalUsageCandidate:
    usage_id: str
    text: str
    source: str
    dataset: str
    dataset_config: str
    dataset_url: str
    source_license: str
    source_project: str
    source_repository: str
    source_commit: str
    source_row: int
    content_hash: str
    provenance_precision: str
    evidence_tier: str
    evidence_role: str
    status: str
    promotion_allowed: bool
    correctness_inference_allowed: bool


def normalize_text(text: str) -> str:
    return SPACE_RE.sub(" ", text).strip()


def word_count(text: str) -> int:
    return sum(1 for _ in WORD_RE.finditer(text))


def bounded_excerpt(
    text: str,
    *,
    minimum_words: int = 8,
    maximum_words: int = 100,
) -> str | None:
    """Return a compact natural-language excerpt without inventing new text."""

    cleaned = normalize_text(text)
    if not cleaned or "\x00" in cleaned:
        return None
    if word_count(cleaned) < minimum_words:
        return None

    if word_count(cleaned) <= maximum_words:
        return cleaned

    selected: list[str] = []
    selected_words = 0
    for sentence in SENTENCE_SPLIT_RE.split(cleaned):
        sentence = sentence.strip()
        if not sentence:
            continue
        count = word_count(sentence)
        if not selected and count > maximum_words:
            words = sentence.split()
            return " ".join(words[:maximum_words]).strip()
        if selected_words + count > maximum_words:
            break
        selected.append(sentence)
        selected_words += count
        if selected_words >= minimum_words:
            break

    excerpt = " ".join(selected).strip()
    return excerpt if word_count(excerpt) >= minimum_words else None


def iter_raw_usage_candidates(
    lines: Iterable[str],
    *,
    source: str,
    source_commit: str,
    minimum_words: int = 8,
    maximum_words: int = 100,
) -> Iterator[NaturalUsageCandidate]:
    if source not in SOURCES:
        raise ValueError(f"unsupported Tier-A source: {source}")
    if not source_commit.strip():
        raise ValueError("source_commit is required for provenance")
    if minimum_words < 1 or maximum_words < minimum_words:
        raise ValueError("invalid word bounds")

    policy = SOURCES[source]
    seen: set[str] = set()

    for source_row, raw_line in enumerate(lines, start=1):
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON on source row {source_row}: {exc.msg}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"source row {source_row} must be a JSON object")

        raw_text = record.get("text")
        if not isinstance(raw_text, str):
            raise ValueError(f"source row {source_row} is missing string text")
        excerpt = bounded_excerpt(
            raw_text,
            minimum_words=minimum_words,
            maximum_words=maximum_words,
        )
        if excerpt is None:
            continue

        digest = hashlib.sha256(excerpt.casefold().encode("utf-8")).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        usage_id = f"{source}:{digest[:20]}"

        yield NaturalUsageCandidate(
            usage_id=usage_id,
            text=excerpt,
            source=source,
            dataset=policy.dataset,
            dataset_config=policy.dataset_config,
            dataset_url=policy.dataset_url,
            source_license=policy.source_license,
            source_project=SOURCE_PROJECT,
            source_repository=SOURCE_REPOSITORY,
            source_commit=source_commit,
            source_row=source_row,
            content_hash=f"sha256:{digest}",
            provenance_precision="pinned_dataset_snapshot+content_hash+source_row",
            evidence_tier="A",
            evidence_role=policy.evidence_role,
            status=STATUS,
            promotion_allowed=False,
            correctness_inference_allowed=False,
        )


def write_jsonl(records: Iterable[NaturalUsageCandidate], output: Path) -> int:
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
        description="Create bounded Tier-A Somali natural-usage candidates from a SomNLP raw JSONL download."
    )
    parser.add_argument("input", type=Path, help="Raw SomNLP JSONL containing text fields")
    parser.add_argument("--source", required=True, choices=sorted(SOURCES))
    parser.add_argument("--source-commit", required=True, help="Exact SomNLP commit SHA")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--minimum-words", type=int, default=8)
    parser.add_argument("--maximum-words", type=int, default=100)
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8-sig") as handle:
        records = iter_raw_usage_candidates(
            handle,
            source=args.source,
            source_commit=args.source_commit,
            minimum_words=args.minimum_words,
            maximum_words=args.maximum_words,
        )
        count = write_jsonl(records, args.output)

    if count == 0:
        raise SystemExit("no usable Tier-A natural-language records were produced")
    print(f"wrote {count} {args.source} natural-usage candidates to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
