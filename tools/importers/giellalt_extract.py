"""Conservative GiellaLT Somali lexical candidate extractor.

This tool does not promote anything into trusted project data. It reads a local
checkout of GiellaLT lang-som and emits provenance-rich JSONL candidate records
from a small allowlist of audited Somali stem files.
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
    "src/fst/morphology/stems/nouns.lexc": "noun",
    "src/fst/morphology/stems/verbs.lexc": "verb",
    "src/fst/morphology/stems/numerals.lexc": "numeral",
    "src/fst/morphology/stems/adjectives.lexc": "adjective",
}

# These markers indicate that an entry should not become a clean lexical
# candidate in this first pass. They can be studied separately later.
UNSAFE_MARKERS = (
    "+Err/Orth",
    "+Err/Lex",
    "+Use/NG",
    "+Use/-Spell",
    "+Use/Marg",
    "+Sty/TODO",
    "+TODO",
)

_ENTRY_RE = re.compile(
    r"^(?P<lexical>\S+)\s+(?P<continuation>[A-Za-z0-9_/@.+-]+)\s*;\s*$"
)


@dataclass(frozen=True)
class Candidate:
    lemma: str
    record_type: str
    continuation: str
    raw_lexical_token: str
    source_project: str
    source_repository: str
    source_commit: str
    source_path: str
    source_line: int
    source_license: str
    status: str
    promotion_allowed: bool


def _strip_comment(line: str) -> str:
    """Remove lexc comments for the simple stem-entry subset we import."""

    return line.split("!", 1)[0].strip()


def parse_lexc_candidates(
    text: str,
    *,
    source_path: str,
    source_commit: str,
) -> Iterator[Candidate]:
    """Yield clean unreviewed candidates from one audited GiellaLT stem file.

    The parser is intentionally narrow. It ignores lexicon declarations,
    redirects, tagged error/nonstandard forms, TODO entries, and complex lines
    that do not match the audited simple stem-entry shape.
    """

    if source_path not in AUDITED_SOURCE_PATHS:
        raise ValueError(f"source path is not allowlisted: {source_path}")
    if not source_commit.strip():
        raise ValueError("source_commit is required for provenance")

    record_type = AUDITED_SOURCE_PATHS[source_path]

    for line_number, original_line in enumerate(text.splitlines(), start=1):
        code = _strip_comment(original_line)
        if not code or code.startswith(("LEXICON ", "Multichar_Symbols")):
            continue
        if any(marker in code for marker in UNSAFE_MARKERS):
            continue

        match = _ENTRY_RE.match(code)
        if not match:
            continue

        raw_token = match.group("lexical")
        continuation = match.group("continuation")

        # Lexical source entries may encode a surface/stem alternation with ':';
        # the lemma is the lexical side before that alternation.
        lemma_token = raw_token.split(":", 1)[0]

        # This importer accepts plain lexical lemmas only. Tagged/fused entries
        # belong in separately reviewed parsers. This is particularly important
        # for the adjective file, whose irregular section contains explicit tags.
        if not lemma_token or "+" in lemma_token or lemma_token.startswith(("@", "%")):
            continue

        yield Candidate(
            lemma=lemma_token,
            record_type=record_type,
            continuation=continuation,
            raw_lexical_token=raw_token,
            source_project=SOURCE_PROJECT,
            source_repository=SOURCE_REPOSITORY,
            source_commit=source_commit,
            source_path=source_path,
            source_line=line_number,
            source_license=SOURCE_LICENSE,
            status=STATUS,
            promotion_allowed=False,
        )


def extract_checkout(
    checkout: Path,
    *,
    source_commit: str,
    kinds: Iterable[str] | None = None,
) -> list[Candidate]:
    """Extract candidates from audited files in a local GiellaLT checkout."""

    requested = set(kinds or AUDITED_SOURCE_PATHS.values())
    unknown = requested - set(AUDITED_SOURCE_PATHS.values())
    if unknown:
        raise ValueError(f"unknown candidate kinds: {sorted(unknown)}")

    records: list[Candidate] = []
    for relative_path, record_type in AUDITED_SOURCE_PATHS.items():
        if record_type not in requested:
            continue
        path = checkout / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"missing audited GiellaLT source file: {path}")
        records.extend(
            parse_lexc_candidates(
                path.read_text(encoding="utf-8-sig"),
                source_path=relative_path,
                source_commit=source_commit,
            )
        )
    return records


def write_jsonl(records: Iterable[Candidate], output: Path) -> int:
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
        description="Extract unreviewed lexical candidates from an audited GiellaLT checkout."
    )
    parser.add_argument("checkout", type=Path, help="Path to a local GiellaLT/lang-som checkout")
    parser.add_argument("--source-commit", required=True, help="Exact GiellaLT commit SHA")
    parser.add_argument("--output", type=Path, required=True, help="Output JSONL path")
    parser.add_argument(
        "--kind",
        action="append",
        choices=sorted(set(AUDITED_SOURCE_PATHS.values())),
        dest="kinds",
        help="Limit extraction to a candidate type; may be repeated",
    )
    args = parser.parse_args()

    records = extract_checkout(
        args.checkout,
        source_commit=args.source_commit,
        kinds=args.kinds,
    )
    count = write_jsonl(records, args.output)
    print(f"wrote {count} unreviewed GiellaLT candidates to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
