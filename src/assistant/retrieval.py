"""Lightweight retrieval over the Somali language foundation.

The index deliberately excludes the large natural-text corpus and all holdout
QA. It searches reviewed project data and rules, compact imported candidate
layers, and bounded Tier-A natural-usage excerpts. External material is always
labelled lower-trust and is never treated as proof of correctness.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator


TOKEN_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)?", flags=re.UNICODE)
DEFAULT_ROOTS = (
    Path("data/vocabulary"),
    Path("data/morphology"),
    Path("rules/grammar"),
    Path("rules/morphology"),
    Path("rules/orthography"),
    Path("rules/variants"),
    Path("data/imported"),
    Path("data/usage"),
)
# Large natural corpora remain excluded by root. This ceiling is high enough for
# compact provenance-rich lexical and bounded natural-usage indexes.
MAX_INDEX_FILE_BYTES = 25_000_000
IDENTITY_KEYS = (
    "lemma",
    "form",
    "input",
    "preferred_written",
    "surface_pattern",
)


@dataclass(frozen=True)
class KnowledgeHit:
    path: str
    score: float
    trust: str
    status: str
    excerpt: str


@dataclass(frozen=True)
class _IndexedRecord:
    path: str
    searchable: str
    tokens: frozenset[str]
    exact_terms: frozenset[str]
    trust: str
    status: str
    excerpt: str


def _tokens(text: str) -> set[str]:
    return {match.group(0).casefold() for match in TOKEN_RE.finditer(text)}


def _flatten_strings(value: object) -> Iterator[str]:
    if isinstance(value, str):
        stripped = value.strip()
        if stripped:
            yield stripped
    elif isinstance(value, dict):
        for item in value.values():
            yield from _flatten_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _flatten_strings(item)


def _identity_terms(record: dict) -> frozenset[str]:
    terms: set[str] = set()
    for key in IDENTITY_KEYS:
        value = record.get(key)
        if not isinstance(value, str):
            continue
        folded = value.casefold().strip()
        if folded:
            terms.add(folded)
    return frozenset(terms)


def _records_from_json(path: Path) -> Iterator[dict]:
    if path.stat().st_size > MAX_INDEX_FILE_BYTES:
        return
    try:
        if path.suffix == ".jsonl":
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
            return

        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return

    if isinstance(value, dict):
        yield value
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                yield item


def _trust_for(path: Path, record: dict) -> str:
    normalized = f"/{path.as_posix()}"
    status = str(record.get("status", "")).casefold()

    if "/usage/external/" in normalized or status.startswith("external_natural_usage"):
        return "external_usage"
    if "/imported/" in normalized:
        return "external_candidate"
    if status in {"provisional", "candidate", "context_required", "ambiguous"}:
        return "reviewed_cautious"
    return "reviewed"


def _excerpt(record: dict, maximum: int = 520) -> str:
    preferred_keys = (
        "lemma",
        "form",
        "input",
        "preferred_written",
        "rule",
        "statement",
        "title",
        "somali_definition_summary",
        "note",
        "example",
        "examples",
        "text",
    )
    parts: list[str] = []
    for key in preferred_keys:
        if key in record:
            parts.extend(_flatten_strings(record[key]))
    if not parts:
        parts = list(_flatten_strings(record))
    joined = " | ".join(parts)
    return joined[:maximum]


class KnowledgeIndex:
    """In-memory lexical overlap index over project knowledge files."""

    def __init__(self, records: Iterable[_IndexedRecord] = ()) -> None:
        self._records = tuple(records)

    @classmethod
    def build(cls, roots: Iterable[str | Path] = DEFAULT_ROOTS) -> "KnowledgeIndex":
        indexed: list[_IndexedRecord] = []
        for root_value in roots:
            root = Path(root_value)
            if not root.exists():
                continue
            paths = [root] if root.is_file() else sorted(root.rglob("*"))
            for path in paths:
                if not path.is_file() or path.suffix not in {".json", ".jsonl"}:
                    continue
                for record in _records_from_json(path):
                    strings = list(_flatten_strings(record))
                    if not strings:
                        continue
                    searchable = " ".join(strings)
                    record_tokens = frozenset(_tokens(searchable))
                    if not record_tokens:
                        continue
                    indexed.append(
                        _IndexedRecord(
                            path=path.as_posix(),
                            searchable=searchable,
                            tokens=record_tokens,
                            exact_terms=_identity_terms(record),
                            trust=_trust_for(path, record),
                            status=str(record.get("status", "unspecified")),
                            excerpt=_excerpt(record),
                        )
                    )
        return cls(indexed)

    def search(self, query: str, limit: int = 8) -> tuple[KnowledgeHit, ...]:
        query_tokens = _tokens(query)
        if not query_tokens or limit <= 0:
            return ()

        folded_query = query.casefold().strip()
        hits: list[KnowledgeHit] = []
        for record in self._records:
            overlap = query_tokens & record.tokens
            if not overlap:
                continue

            score = float(len(overlap)) / max(len(query_tokens), 1)
            searchable_folded = record.searchable.casefold()
            if folded_query and folded_query in searchable_folded:
                score += 1.25

            if folded_query and folded_query in record.exact_terms:
                score += 1.00

            identity_token_matches = query_tokens & record.exact_terms
            if identity_token_matches:
                score += 0.85 * len(identity_token_matches)

            if record.trust == "reviewed":
                score += 0.20
            elif record.trust == "external_candidate":
                score -= 0.05
            elif record.trust == "external_usage":
                # Natural usage can improve context and phrasing, but it should
                # not beat a comparably relevant reviewed linguistic record.
                score -= 0.12

            hits.append(
                KnowledgeHit(
                    path=record.path,
                    score=score,
                    trust=record.trust,
                    status=record.status,
                    excerpt=record.excerpt,
                )
            )

        hits.sort(key=lambda hit: (-hit.score, hit.path, hit.excerpt))
        return tuple(hits[:limit])

    @property
    def record_count(self) -> int:
        return len(self._records)
