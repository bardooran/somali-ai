# Repository Cleanup Audit

This file tracks structural cleanup separately from linguistic development.

The cleanup rule is conservative: **do not delete, merge, rename, or move a file until we know what depends on it and whether it contains unique linguistic evidence.**

## Initial audit — 2026-08-31

| Location | Classification | Reason | Action |
|---|---|---|---|
| `README.md` | KEEP / REFRESHED | Main project overview was outdated | Rewritten to reflect executable grammar engine |
| `check.py` | KEEP | Current command-line entry point and analyzer orchestrator | No structural change now |
| `src/` | KEEP | Active executable grammar engine | Consider package reorganization only later |
| `rules/grammar/` | KEEP | Clear sentence-grammar rule layer | Continue using |
| `rules/morphology/` | KEEP | Clear morphology reference layer | Continue using |
| `rules/orthography/` | KEEP | Safe orthographic rule layer | Continue using |
| `rules/variants/` | KEEP | Needed to separate regional/lexical variation from errors | Continue using |
| `data/morphology/` | KEEP | Active reviewed morphology evidence | Continue using |
| `data/lexical/` | KEEP | Current developed lexical evidence area | Primary lexical-data location |
| `data/qa/` | KEEP | Independent/holdout QA layer | Expand |
| `data/sources/` | KEEP / CLARIFIED | Structured source-derived data; distinct from top-level `sources/` | Document distinction |
| `sources/` | KEEP / CLARIFIED | Human-readable source notes | Document distinction |
| `tests/` | KEEP / LATER REORGANIZE | Essential but increasingly flat/large | Group by domain only in dedicated refactor |
| `docs/DECISIONS.md` | KEEP | Important project decision history and native-review record | Never casually rewrite history |
| `docs/GRAMMAR_ANALYSIS.md` | KEEP | Useful linguistic/implementation analysis | Continue using |
| `docs/LEXICON_SCHEMA.md` | KEEP | Defines lexical record interpretation | Continue using |
| `lexicon/samples.jsonl` | AUDIT / POSSIBLE MOVE | Early sample file contains real SLS/Qaamuus lexical evidence, while `data/lexical/` is now the primary lexical layer | Check for unique records and references; migrate before any deletion |

## Changes completed in this cleanup stage

- Rewrote the root `README.md`.
- Added `docs/STATUS.md`.
- Added `docs/REPO_MAP.md`.
- Added `rules/README.md`.
- Added `data/README.md`.
- Added `tests/README.md`.
- Added `sources/README.md`.
- Added this cleanup audit.

## Deferred structural work

The following changes may improve the repository later, but should **not** be mixed into active grammar development without a dedicated refactor:

### Python package layout

Current:

```text
src/checker.py
src/agreement.py
src/...
```

Possible mature layout:

```text
src/somali_grammar/
    checker.py
    grammar/
    morphology/
    ...
```

Reason for deferral: moving active Python modules would require import changes across the checker and tests and creates unnecessary risk while grammar coverage is rapidly changing.

### Test-folder grouping

Possible future groups:

```text
tests/
    grammar/
    morphology/
    orthography/
    integration/
    regression/
```

Reason for deferral: the existing suite is active and working; grouping should be a behavior-neutral refactor with test discovery verified afterward.

### Legacy lexical sample migration

Before changing `lexicon/samples.jsonl`:

1. compare its records with `data/lexical/` datasets;
2. search code and test references;
3. preserve any unique source metadata or homonym distinctions;
4. migrate unique records to the current lexical schema;
5. run tests;
6. only then remove the legacy path if it is truly redundant.

## Cleanup principle

A clean repository is not one with the fewest files. It is one where every file has a known role, known provenance, and known relationship to executable behavior.
