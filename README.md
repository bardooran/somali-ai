# Somali Grammar

An evidence-based Somali language foundation for grammar checking, linguistic analysis, and future Somali-first AI evaluation.

The project is building a conservative grammar engine: rules come from reviewed evidence, are tested against real Somali, and remain unknown or context-dependent when the evidence does not support a safe judgment.

## Project goals

1. Help Somali speakers improve written Somali.
2. Help learners understand Somali grammar through clear explanations and examples.
3. Build reviewed Somali grammar, morphology, vocabulary, real-text corpora, and QA datasets.
4. Create a strong Somali language foundation that can later help train and evaluate Somali-first AI systems.

This repository does **not** train a large language model yet. It builds the language knowledge and evaluation foundation first.

## Current status

The repository contains:

- an executable checker in `check.py`;
- grammar and analysis code under `src/`;
- machine-readable rules under `rules/`;
- reviewed evidence under `data/`;
- vocabulary data under `data/vocabulary/`;
- real Somali text collections under `data/corpus/`;
- automated tests under `tests/`;
- project decisions and status documentation under `docs/`;
- human-readable source notes under `sources/`.

See [`docs/STATUS.md`](docs/STATUS.md) for **where the project is now** and [`docs/REPO_MAP.md`](docs/REPO_MAP.md) for **what every folder means**.

## Core safety principle

**Do not invent Somali grammar or word forms.**

The project prefers:

- source-backed forms over guessed forms;
- exact reviewed morphology over blind suffix generation;
- `context_required` or unknown results over unsafe corrections;
- supported regional variants over falsely marking a valid form wrong.

## How knowledge moves through the project

```text
source / native review / real Somali text
                 ↓
          reviewed evidence
                 ↓
        grammar or morphology rule
                 ↓
           analyzer code
                 ↓
              checker
                 ↓
       tests + independent QA
```

Evidence does not automatically become a correction rule.

## Repository layout

```text
somali-grammar/
├── README.md
├── check.py                 # main checker
│
├── src/                     # executable Python analysis code
│   └── vocabulary.py        # reviewed word lookup
│
├── rules/
│   ├── grammar/             # sentence grammar rules
│   ├── morphology/          # word-form patterns
│   ├── orthography/         # spelling/writing rules
│   └── variants/            # supported regional variants
│
├── data/
│   ├── vocabulary/          # reviewed word information
│   ├── morphology/          # reviewed word forms/paradigms
│   ├── corpus/              # real Somali text collections
│   ├── qa/                  # independent/holdout test data
│   └── sources/             # structured source evidence
│
├── tests/                   # automated tests
├── sources/                 # human-readable source notes
└── docs/                    # status, decisions, repo map, schemas
```

## Current linguistic coverage

Implemented or reviewed areas include:

- personal pronouns and subject clitics;
- subject–verb agreement;
- masculine/feminine and singular/plural agreement;
- noun subject forms and focus-sensitive case behavior;
- `baa` / `ayaa` focus constructions;
- object clitics such as `idin`;
- statement clitics such as `wuu`, `way`, `waan`, and `waad`;
- connective forms such as `wuuna`, `wayna`, and reviewed `wuxuuna` constructions;
- negation and negative agreement;
- future and negative-future auxiliaries;
- past, habitual, imperative, jussive, dependent, and conditional patterns;
- possession with `leeyahay`-type constructions;
- predicate/copula agreement;
- reviewed regular and irregular verb families;
- Jigjiga-first regional preference handling;
- source-backed vocabulary lookup;
- a Somali proverb corpus for research and stress-testing.

Coverage is still incomplete. Unsupported forms should remain unjudged rather than being guessed.

## Preferred Somali output profile

The preferred generation/teaching profile is **Jigjiga Somali**, with strong compatibility with Northwestern/Hargeisa usage. Other supported Somali regional forms remain valid and should not be marked wrong solely because they differ regionally.

See [`docs/DECISIONS.md`](docs/DECISIONS.md) for the decision history.

## Running the checker

```bash
python check.py "Somali text here"
```

## Development rule

Before promoting new grammar behavior:

1. collect trustworthy evidence;
2. record provenance;
3. keep word-form facts separate from sentence-context claims;
4. implement only what the evidence supports;
5. add positive, negative, ambiguous, and unknown tests;
6. test examples that were not used to create the rule;
7. keep unsupported cases unjudged.

## Documentation

- [`docs/STATUS.md`](docs/STATUS.md) — current project dashboard
- [`docs/REPO_MAP.md`](docs/REPO_MAP.md) — what every major folder/file is for
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — project decisions and reviewed language judgments
- [`docs/GRAMMAR_ANALYSIS.md`](docs/GRAMMAR_ANALYSIS.md) — grammar analysis notes
- [`docs/VOCABULARY_SCHEMA.md`](docs/VOCABULARY_SCHEMA.md) — vocabulary-data structure
- [`docs/CLEANUP_AUDIT.md`](docs/CLEANUP_AUDIT.md) — structural cleanup history
