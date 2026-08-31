"""Conservative Somali Language Standard rule candidate extractor.

The extractor is intentionally limited to audited SLS-authored specification
files. It does not import descriptive resource books/dictionaries and never
promotes records into project grammar automatically.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator

SOURCE_PROJECT = "Somali Language Standard (SLS)"
SOURCE_REPOSITORY = "goobolabs/somali-language-standard"
SOURCE_LICENSE = "CC-BY-4.0 (SLS-authored linguistic content)"
STATUS = "external_candidate_unreviewed"

GRAMMAR_PATHS = tuple(
    f"spec/grammar/{number:04d}-{slug}.md"
    for number, slug in (
        (10, "parts-of-speech"),
        (11, "noun-morphology-gender-plurals"),
        (12, "verb-system-tense-aspect-mood"),
        (13, "pronouns"),
        (14, "sentence-structure-word-order"),
        (15, "negation"),
        (16, "question-formation"),
        (17, "common-mistakes"),
        (18, "somali-grammar-standard"),
    )
)

ORTHOGRAPHY_PATHS = (
    "spec/orthography/0001-alphabet.md",
    "spec/orthography/0002-spelling-rules.md",
    "spec/orthography/0003-capitalization.md",
    "spec/orthography/0004-punctuation.md",
)

AUDITED_SOURCE_PATHS = frozenset(GRAMMAR_PATHS + ORTHOGRAPHY_PATHS)
_RULE_START_RE = re.compile(r"^- \*\*(?P<rule_id>[A-Z0-9-]+)\.\*\*\s*(?P<body>.*)$")
_FRONTMATTER_RE = re.compile(r"^(?P<key>[A-Za-z_][A-Za-z0-9_-]*):\s*(?P<value>.*)$")


@dataclass(frozen=True)
class RuleCandidate:
    rule_id: str
    statement: str
    document_id: str | None
    sls_id: str | None
    lifecycle_status: str | None
    version: str | None
    source_project: str
    source_repository: str
    source_commit: str
    source_path: str
    source_line: int
    source_license: str
    source_lineage_note: str
    status: str
    promotion_allowed: bool


def _clean_yaml_scalar(value: str) -> str:
    value = value.strip()
    if value.startswith(('"', "'")) and value.endswith(value[0]) and len(value) >= 2:
        return value[1:-1]
    if value in {"", "null", "~"}:
        return ""
    return value


def _frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    result: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = _FRONTMATTER_RE.match(line)
        if match:
            result[match.group("key")] = _clean_yaml_scalar(match.group("value"))
    return result


def parse_spec_rules(
    text: str,
    *,
    source_path: str,
    source_commit: str,
) -> Iterator[RuleCandidate]:
    """Extract numbered normative/proposed rules from one allowlisted SLS spec."""

    if source_path not in AUDITED_SOURCE_PATHS:
        raise ValueError(f"source path is not allowlisted: {source_path}")
    if not source_commit.strip():
        raise ValueError("source_commit is required for provenance")

    meta = _frontmatter(text)
    lines = text.splitlines()
    current_id: str | None = None
    current_line = 0
    current_parts: list[str] = []

    def emit_current() -> RuleCandidate | None:
        if current_id is None:
            return None
        statement = " ".join(part.strip() for part in current_parts if part.strip())
        return RuleCandidate(
            rule_id=current_id,
            statement=statement,
            document_id=meta.get("id") or None,
            sls_id=meta.get("sls_id") or None,
            lifecycle_status=meta.get("status") or None,
            version=meta.get("version") or meta.get("standard_version") or None,
            source_project=SOURCE_PROJECT,
            source_repository=SOURCE_REPOSITORY,
            source_commit=source_commit,
            source_path=source_path,
            source_line=current_line,
            source_license=SOURCE_LICENSE,
            source_lineage_note=(
                "SLS editorial/specification layer; trace underlying resource family before "
                "counting as independent linguistic confirmation"
            ),
            status=STATUS,
            promotion_allowed=False,
        )

    for line_number, line in enumerate(lines, start=1):
        match = _RULE_START_RE.match(line)
        if match:
            previous = emit_current()
            if previous is not None:
                yield previous
            current_id = match.group("rule_id")
            current_line = line_number
            current_parts = [match.group("body")]
            continue

        if current_id is None:
            continue

        stripped = line.strip()
        if not stripped:
            previous = emit_current()
            if previous is not None:
                yield previous
            current_id = None
            current_line = 0
            current_parts = []
            continue

        # Wrapped Markdown rule bullets are indented. Stop at another structural
        # boundary rather than accidentally absorbing examples or headings.
        if stripped.startswith(("#", "|", "- **")):
            previous = emit_current()
            if previous is not None:
                yield previous
            current_id = None
            current_line = 0
            current_parts = []
            continue

        current_parts.append(stripped)

    final = emit_current()
    if final is not None:
        yield final


def extract_checkout(
    checkout: Path,
    *,
    source_commit: str,
    sections: Iterable[str] | None = None,
) -> list[RuleCandidate]:
    requested = set(sections or ("grammar", "orthography"))
    unknown = requested - {"grammar", "orthography"}
    if unknown:
        raise ValueError(f"unknown SLS sections: {sorted(unknown)}")

    paths: list[str] = []
    if "grammar" in requested:
        paths.extend(GRAMMAR_PATHS)
    if "orthography" in requested:
        paths.extend(ORTHOGRAPHY_PATHS)

    records: list[RuleCandidate] = []
    for relative_path in paths:
        path = checkout / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"missing audited SLS specification: {path}")
        records.extend(
            parse_spec_rules(
                path.read_text(encoding="utf-8-sig"),
                source_path=relative_path,
                source_commit=source_commit,
            )
        )
    return records


def write_jsonl(records: Iterable[RuleCandidate], output: Path) -> int:
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
        description="Extract unreviewed rule candidates from audited SLS specification files."
    )
    parser.add_argument("checkout", type=Path, help="Path to a local SLS checkout")
    parser.add_argument("--source-commit", required=True, help="Exact SLS commit SHA")
    parser.add_argument("--output", type=Path, required=True, help="Output JSONL path")
    parser.add_argument(
        "--section",
        action="append",
        choices=("grammar", "orthography"),
        dest="sections",
        help="Limit extraction to one section; may be repeated",
    )
    args = parser.parse_args()

    records = extract_checkout(
        args.checkout,
        source_commit=args.source_commit,
        sections=args.sections,
    )
    count = write_jsonl(records, args.output)
    print(f"wrote {count} unreviewed SLS rule candidates to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
