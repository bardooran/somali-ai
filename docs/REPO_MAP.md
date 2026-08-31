# Repository Map

This document explains what each major part of the repository is for and, just as importantly, what it is **not** for.

The project intentionally separates evidence, rules, executable analyzers, and tests.

## Data flow

```text
source / native review
        ↓
reviewed evidence (`data/`, `sources/`, decision notes)
        ↓
machine-readable linguistic rule (`rules/`)
        ↓
executable analyzer (`src/`)
        ↓
checker (`check.py`)
        ↓
behavior tests + independent QA (`tests/`, `data/qa/`)
```

A file appearing earlier in this flow does not automatically authorize a correction later in the flow.

## Root files

### `README.md`

Public overview of the project: purpose, current state, principles, major coverage, and navigation.

**Keep this current.** It should never say the project is only planning if executable grammar already exists.

### `check.py`

Current command-line entry point and grammar-check orchestration layer.

It calls multiple analyzers from `src/` and combines safe orthography behavior with conservative grammar analysis.

Do not turn this into the location for large linguistic datasets. New grammar logic should normally live in `src/` with machine-readable evidence in `rules/` or `data/`.

## `src/` — executable grammar engine

Python modules that analyze Somali text and implement behavior supported by the project’s rules and reviewed evidence.

Examples include agreement, focus, connectives, negation, future, dependent mood, noun case, clitic roles, and related sentence analysis.

**Purpose:** executable logic.

**Not for:** raw source notes, copied linguistic reference material, or unreviewed word lists.

Long term, this directory may be reorganized into a normal installable Python package such as `src/somali_grammar/`, but that refactor should happen only when it can be done without disrupting active grammar work.

## `rules/` — machine-readable linguistic rules

### `rules/grammar/`

Sentence-level grammar evidence and constraints: agreement, focus, clitics, negation, noun case, questions, connectives, possession, moods, and related constructions.

A record may be descriptive, provisional, or context-required. Presence in this folder does **not** mean automatic correction is safe.

### `rules/morphology/`

Structured reference patterns for noun and verb morphology.

This layer is conservative. Reviewed surface forms and documented paradigms may be analyzed, but the engine must not manufacture unseen forms by blind suffix rules.

### `rules/orthography/`

Rules that may support safe spelling/orthographic findings and corrections.

This is the main location for deterministic text-rewrite rules.

### `rules/variants/`

Supported lexical, spelling, or regional variation where alternatives should be represented separately from grammatical error.

## `data/` — reviewed evidence datasets

### `data/morphology/`

Reviewed surface forms, paradigms, exact stems, native-reviewed forms, and source-derived morphology evidence used by morphology/analyzer code.

These records should retain provenance and should be more explicit than guessed generative rules.

### `data/lexical/`

Reviewed lexical information and source-derived word-level data that does not belong directly in a grammar-rule file.

### `data/qa/`

Independent or holdout examples used to challenge the grammar engine.

A holdout file should not be quietly reused as the source from which its target rule is invented. The value of holdout QA is that it tests generalization and false-positive/false-negative behavior.

### `data/sources/`

Structured source-derived datasets or source artifacts that are useful to processing/evidence pipelines.

This is different from the top-level `sources/` directory, which is for human-readable source notes.

## `tests/` — automated executable tests

Tests verify behavior of the checker and individual analyzers.

The suite includes ordinary unit/integration behavior, agreement tests, verb-class tests, irregular-form generalization tests, regression probes, and CLI checks.

Tests should cover at least four classes when relevant:

1. correct/positive examples;
2. incorrect/negative examples;
3. ambiguous/context-required examples;
4. unknown/unsupported forms that must not be guessed.

A test should not be treated as linguistic evidence by itself. The linguistic claim should have a source or reviewed evidence record.

## `sources/` — human-readable external source notes

Short documentation about external linguistic resources, their role, limitations, and how project data derived from them should be interpreted.

Examples currently include SLS and Lexin notes.

This folder is for humans. Structured imported records should live under `data/`.

## `docs/` — project documentation and decisions

### `docs/STATUS.md`

The current coverage dashboard. This is the fastest answer to **“Where are we?”**

### `docs/REPO_MAP.md`

This file. It explains where things belong.

### `docs/DECISIONS.md`

Chronological project decisions, including source conflicts, native review, regional-profile choices, and safety constraints.

This file is important historical evidence. Do not casually delete old decisions; when a decision changes, document the newer decision as superseding the old one.

### `docs/GRAMMAR_ANALYSIS.md`

Longer linguistic and implementation analysis that does not fit cleanly into a machine-readable rule.

### `docs/LEXICON_SCHEMA.md`

Defines the intended shape and interpretation of lexical records.

## `lexicon/` — legacy/sample area under audit

The current `lexicon/samples.jsonl` is a small early sample file.

The repository now has a more developed `data/lexical/` layer, so this directory should be treated as **under audit** rather than as the primary lexical architecture.

Do not delete it until we confirm no code, tests, documentation, or unique evidence depends on it. If it is truly obsolete, migrate any unique records to `data/lexical/` and then remove the legacy directory in a separate cleanup change.

## File-status labels for future cleanup

When reviewing an unclear file, classify it before changing anything:

- **KEEP** — active and correctly located.
- **RENAME** — useful but misleadingly named.
- **MOVE** — useful but in the wrong layer/folder.
- **MERGE** — duplicates another maintained source of truth.
- **DEPRECATE** — still needed temporarily but should not receive new data.
- **DELETE** — confirmed unused, duplicated, and containing no unique linguistic evidence.

## Safe cleanup checklist

Before moving, merging, or deleting a file:

1. search imports and code references;
2. search tests and fixtures;
3. check whether it contains unique reviewed linguistic evidence;
4. check whether a newer file is truly equivalent;
5. preserve provenance when migrating records;
6. run the relevant test suite after the change;
7. update `README.md`, `STATUS.md`, or this map if responsibilities change.

The goal is not to make the repository artificially small. The goal is to make every retained file have a clear purpose.
