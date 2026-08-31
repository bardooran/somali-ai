# Repository Map

This page explains the **Somali AI** repository in plain English.

## Main data flow

```text
source / native review / real Somali text
                 ↓
candidate + reviewed evidence
                 ↓
   provenance / conflict checking
                 ↓
 Somali language foundation
(grammar, morphology, vocabulary,
 variants, corpus, QA, analyzers)
                 ↓
     knowledge retrieval
                 ↓
 general reasoning model
                 ↓
 Somali-first generation
                 ↓
 conservative response checker
                 ↓
         final answer
```

A source example does not automatically become an autocorrection rule, and an imported candidate does not automatically become trusted Somali knowledge.

## Root

### `README.md`
Main overview of Somali AI.

### `somali_ai.py`
Terminal launcher for the conversational Somali AI.

### `somali_ai_web.py`
Local browser-chat launcher.

### `check.py`
Command-line grammar/orthography checker subsystem. It calls analyzers from `src/`.

The root should stay small. Large datasets do not belong here.

## `src/` — executable code

Python code that powers Somali analysis and the assistant.

### `src/assistant/`
The conversational AI layer:

- `pipeline.py` — end-to-end assistant orchestration and conversation history;
- `retrieval.py` — searches reviewed and candidate Somali knowledge;
- `prompts.py` — Somali-first behavior, dialect preference, uncertainty, runtime context;
- `model.py` — reasoning-model adapters;
- `web.py` — dependency-free local browser chat;
- `evaluation.py` / `eval.py` — assistant capability evaluation tooling;
- `types.py` — shared assistant data structures.

### Other `src/` modules
Somali language analyzers, including:

- agreement and focus analyzers;
- negation and tense/mood analyzers;
- noun/case and morphology analyzers;
- number, date/time, direction, measurement, and ordinal modules;
- `vocabulary.py` for reviewed word lookup.

**Use `src/` for:** executable code.

**Do not use it for:** raw source material or large word/text datasets.

## `rules/` — machine-readable trusted language behavior

### `rules/grammar/`
Sentence grammar: agreement, focus, clitics, negation, questions, possession, clause patterns, moods, and related constructions.

### `rules/morphology/`
Reviewed patterns describing word forms and paradigms.

### `rules/orthography/`
Spelling and writing rules that may support safe deterministic corrections.

### `rules/variants/`
Supported regional forms and project output preferences. A regional difference is not automatically a grammar error.

The assistant currently uses conservative orthography/variant rules for automatic output fixing; broader grammar rules remain analysis evidence unless safe correction is justified.

## `data/` — Somali knowledge, corpora, candidates, and QA

### `data/vocabulary/`
Reviewed word information: headwords, word classes, gender, meaning notes, variants, and source provenance.

### `data/morphology/`
Reviewed surface forms, paradigms, exact stems, irregular forms, and source/native-reviewed morphology.

### `data/imported/`
Provenance-rich external candidate material.

Current major layers include:

- `data/imported/giellalt/lexical_candidates.jsonl` — external noun/verb/numeral candidates;
- `data/imported/giellalt/grammar_candidates.jsonl` — external pronoun/adposition/function-particle candidates;
- `data/imported/sls/rule_candidates.jsonl` — SLS grammar/orthography candidates;
- SomNLP source/audit scaffolding for corpus QA workflows.

Imported records are **not trusted automatically**. They remain non-promoting until reviewed.

### `data/corpus/`
Collections of real Somali text.

Current local corpus material includes Somali proverbs for research/stress-testing. External SomNLP material is kept source-separated rather than bulk-dumped into this repository.

### `data/qa/`
Independent/holdout examples used to find false positives, false negatives, rule conflicts, unsafe judgments, and assistant capability gaps.

Important: QA/holdout data is intentionally not part of the assistant's default knowledge-retrieval roots, to reduce evaluation leakage.

### `data/sources/`
Structured evidence extracted from linguistic sources.

This is different from top-level `sources/`, which contains human-readable notes.

## `tools/importers/` — controlled external-source ingestion

Importers turn audited external projects into provenance-rich candidate records.

Current importers include GiellaLT lexical/grammar extraction, SLS rule extraction, and SomNLP QA/corpus scaffolding.

The import workflow follows:

```text
external source
      ↓
allowlisted extractor
      ↓
provenance-rich candidate
      ↓
non-promoting storage
      ↓
review / cross-source validation
      ↓
trusted project data only if justified
```

## `.github/workflows/`

### `tests.yml`
Runs the full automated test suite.

### `refresh-external-candidates.yml`
Checks out the audited external mirrors, rebuilds candidate datasets, verifies they remain non-promoting, runs the full project tests, and only then commits refreshed candidate data.

## `tests/` — automated quality control

Tests cover both the language foundation and the assistant layer.

Where relevant they should include:

1. supported/correct examples;
2. clearly incompatible examples;
3. ambiguous/context-dependent cases;
4. unknown forms that must not be guessed;
5. unseen holdout/generalization examples;
6. regressions;
7. assistant retrieval, prompt, history, API-shape, and response-checking behavior.

## `sources/` — source notes for humans

Notes about external resources such as GiellaLT, SLS, SomNLP, Lexin, and linguistic references: what they contain, licensing/provenance cautions, and how Somali AI uses them.

## `docs/` — project documentation

- `STATUS.md` — fastest answer to **Where are we?**
- `REPO_MAP.md` — this repository map;
- `SOMALI_AI_V0_1.md` — conversational assistant architecture and usage;
- `DECISIONS.md` — important project and language decisions;
- `GRAMMAR_ANALYSIS.md` — longer grammar analysis notes;
- `VOCABULARY_SCHEMA.md` — vocabulary structure;
- `CLEANUP_AUDIT.md` — structural cleanup history.

## Cleanup labels

When a confusing file is found, classify it before changing it:

- **KEEP** — useful and correctly located;
- **RENAME** — useful but confusingly named;
- **MOVE** — useful but in the wrong folder;
- **MERGE** — duplicate material that should have one maintained home;
- **DEPRECATE** — temporarily retained for compatibility;
- **DELETE** — confirmed unused and containing no unique evidence.

## Safety checklist before deleting/moving

1. check code imports and hard-coded paths;
2. check tests;
3. check whether the file contains unique language evidence;
4. preserve provenance during migration;
5. run automated tests after structural changes;
6. update this map when responsibilities change.

The goal is simple: every folder and file should have an obvious purpose inside the larger Somali AI system.
