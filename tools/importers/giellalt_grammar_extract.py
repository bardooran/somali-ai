"""Conservative GiellaLT Somali grammatical-word candidate extractor.

This is separate from the bulk noun/verb/numeral extractor because the audited
pronoun, focus/subjunction, and adposition sources use tagged lexc entries. Every
record remains external evidence only and requires project review before any
checker/generator behavior can be promoted.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator

SOURCE_PROJECT = "GiellaLT lang-som"
SOURCE_REPOSITORY = "giellalt/lang-som"
SOURCE_LICENSE = "repository LGPL-3.0; verify per-file notices before redistribution"
STATUS = "external_candidate_unreviewed"

AUDITED_SOURCE_PATHS = {
    "src/fst/morphology/stems/pronouns.lexc": "pronoun",
    "src/fst/morphology/stems/subjunctions.lexc": "function_particle",
    "src/fst/morphology/stems/adpositions.lexc": "adposition",
}

UNSAFE_MARKERS = (
    "+Err/",
    "+Use/NG",
    "+Use/-Spell",
    "+Use/Marg",
    "+Sty/TODO",
    "+TODO",
)

_GLOSS_RE = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')


@dataclass(frozen=True)
class GrammarCandidate:
    lemma: str
    record_type: str
    raw_lexical_token: str
    surface_pattern: str | None
    continuation: str | None
    gloss: str | None
    source_project: str
    source_repository: str
    source_commit: str
    source_path: str
    source_line: int
    source_license: str
    status: str
    promotion_allowed: bool
    usage_requires_review: bool


def _strip_comment(line: str) -> str:
    return line.split("!", 1)[0].strip()


def _parse_code(code: str) -> tuple[str, str | None, str | None] | None:
    """Return lexical token, continuation, gloss for a simple lexc entry."""

    if ";" not in code:
        return None
    before_semicolon = code.split(";", 1)[0].strip()
    if not before_semicolon:
        return None
    tokens = before_semicolon.split()
    if not tokens:
        return None
    raw_token = tokens[0]
    if raw_token.startswith(("+", "@", "%", "LEXICON")):
        return None
    continuation = tokens[1] if len(tokens) > 1 and not tokens[1].startswith('"') else None
    gloss_match = _GLOSS_RE.search(before_semicolon)
    gloss = gloss_match.group(1) if gloss_match else None
    return raw_token, continuation, gloss


def parse_grammar_candidates(
    text: str,
    *,
    source_path: str,
    source_commit: str,
) -> Iterator[GrammarCandidate]:
    if source_path not in AUDITED_SOURCE_PATHS:
        raise ValueError(f"source path is not allowlisted: {source_path}")
    if not source_commit.strip():
        raise ValueError("source_commit is required for provenance")

    record_type = AUDITED_SOURCE_PATHS[source_path]
    seen: set[tuple[str, str, int]] = set()

    for line_number, original in enumerate(text.splitlines(), start=1):
        code = _strip_comment(original)
        if not code or code.startswith("LEXICON ") or any(marker in code for marker in UNSAFE_MARKERS):
            continue
        parsed = _parse_code(code)
        if parsed is None:
            continue
        raw_token, continuation, gloss = parsed

        lexical_side, separator, surface = raw_token.partition(":")
        lemma = lexical_side.split("+", 1)[0].split("#", 1)[0].strip()
        if not lemma or lemma in {"0", "%0"}:
            continue
        # Lexc metacharacter-only entries are infrastructure, not words.
        if any(char in lemma for char in ("@", "{", "}")):
            continue

        key = (lemma, raw_token, line_number)
        if key in seen:
            continue
        seen.add(key)
        yield GrammarCandidate(
            lemma=lemma,
            record_type=record_type,
            raw_lexical_token=raw_token,
            surface_pattern=surface if separator else None,
            continuation=continuation,
            gloss=gloss,
            source_project=SOURCE_PROJECT,
            source_repository=SOURCE_REPOSITORY,
            source_commit=source_commit,
            source_path=source_path,
            source_line=line_number,
            source_license=SOURCE_LICENSE,
            status=STATUS,
            promotion_allowed=False,
            usage_requires_review=True,
        )


def extract_checkout(
    checkout: Path,
    *,
    source_commit: str,
    kinds: Iterable[str] | None = None,
) -> list[GrammarCandidate]:
    requested = set(kinds or AUDITED_SOURCE_PATHS.values())
    unknown = requested - set(AUDITED_SOURCE_PATHS.values())
    if unknown:
        raise ValueError(f"unknown grammatical candidate kinds: {sorted(unknown)}")

    records: list[GrammarCandidate] = []
    for relative_path, record_type in AUDITED_SOURCE_PATHS.items():
        if record_type not in requested:
            continue
        path = checkout / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"missing audited GiellaLT source file: {path}")
        records.extend(
            parse_grammar_candidates(
                path.read_text(encoding="utf-8-sig"),
                source_path=relative_path,
                source_commit=source_commit,
            )
        )
    return records


def write_jsonl(records: Iterable[GrammarCandidate], output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(asdict(record), ensure_ascii=False, sort_keys=True))
            handle.write("\n")
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract audited GiellaLT grammatical-word candidates")
    parser.add_argument("checkout", type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--kind",
        action="append",
        choices=sorted(set(AUDITED_SOURCE_PATHS.values())),
        dest="kinds",
    )
    args = parser.parse_args()
    records = extract_checkout(args.checkout, source_commit=args.source_commit, kinds=args.kinds)
    count = write_jsonl(records, args.output)
    print(f"wrote {count} unreviewed GiellaLT grammatical candidates to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
