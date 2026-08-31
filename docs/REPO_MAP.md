# Repository Map

This page explains the repository in plain English.

## Data flow

```text
source / native review / real Somali text
                 ↓
          reviewed evidence
                 ↓
        grammar/morphology rules
                 ↓
          executable analyzers
                 ↓
               checker
                 ↓
          tests + holdout QA
```

A source example does not automatically become an autocorrection rule.

## Root

### `README.md`
Main overview of the project.

### `check.py`
Main command-line checker. It calls analyzers from `src/`.

The root should stay small. Large datasets do not belong here.

## `src/` — executable code

Python code that analyzes Somali text.

Examples:

- agreement analyzers;
- focus and connective analyzers;
- negation and tense/mood analyzers;
- noun/case analyzers;
- `vocabulary.py` for reviewed word lookup.

**Use this folder for:** code.

**Do not use it for:** raw source material or large word/text datasets.

## `rules/` — machine-readable language rules

### `rules/grammar/`
Sentence grammar: agreement, focus, clitics, negation, questions, possession, clause patterns, moods, and related constructions.

### `rules/morphology/`
Reviewed patterns describing word forms and paradigms.

### `rules/orthography/`
Spelling and writing rules that may support safe deterministic corrections.

### `rules/variants/`
Supported regional forms and project output preferences. A regional difference is not automatically a grammar error.

## `data/` — reviewed language data

### `data/vocabulary/`
Information about words: headwords, word classes, gender, meaning notes, variants, and source provenance.

Main files currently include:

- `qaamuus_2012_grammar_words.jsonl`
- `qaamuus_2012_everyday_words.jsonl`
- `qaamuus_2012_everyday_verbs.jsonl`
- `qaamuus_2012_sample_entries.jsonl`

The lookup code is `src/vocabulary.py`.

### `data/morphology/`
Reviewed surface forms, paradigms, exact stems, irregular forms, and source/native-reviewed morphology.

### `data/corpus/`
Collections of real Somali text.

Current corpus:

- `maahmaahyo.json` — roughly one thousand Somali proverbs.

Corpus material is useful for discovery and stress-testing, but a proverb is not automatically a normal modern grammar rule.

### `data/qa/`
Independent/holdout examples used to find false positives, false negatives, rule conflicts, and unsafe judgments.

### `data/sources/`
Structured evidence extracted from linguistic sources.

This is different from top-level `sources/`, which contains human-readable notes.

## `tests/` — automated quality control

Executable tests for checker behavior and language analyzers.

Tests should cover, where relevant:

1. supported/correct examples;
2. clearly incompatible examples;
3. ambiguous/context-dependent cases;
4. unknown forms that must not be guessed;
5. new holdout/generalization examples;
6. regressions.

## `sources/` — source notes for humans

Notes about external resources such as SLS and Lexin: what they contain, how trustworthy they are for a particular purpose, and how the project uses them.

## `docs/` — project documentation

- `STATUS.md` — fastest answer to **Where are we?**
- `REPO_MAP.md` — this repository map.
- `DECISIONS.md` — important project and language decisions.
- `GRAMMAR_ANALYSIS.md` — longer grammar analysis notes.
- `VOCABULARY_SCHEMA.md` — how word/vocabulary records are structured.
- `CLEANUP_AUDIT.md` — structural cleanup history.

## Cleanup labels

When a confusing file is found, classify it before changing it:

- **KEEP** — useful and correctly located.
- **RENAME** — useful but confusingly named.
- **MOVE** — useful but in the wrong folder.
- **MERGE** — duplicate material that should have one maintained home.
- **DEPRECATE** — temporarily retained for compatibility.
- **DELETE** — confirmed unused and containing no unique evidence.

## Safety checklist before deleting/moving

1. check code imports and hard-coded paths;
2. check tests;
3. check whether the file contains unique language evidence;
4. preserve provenance during migration;
5. run automated tests after structural changes;
6. update this map when responsibilities change.

The goal is simple: every folder and file should have an obvious purpose.
