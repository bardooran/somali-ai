# Somali Grammar

An evidence-based Somali language foundation for grammar checking, linguistic analysis, and future Somali-first AI evaluation.

The project currently focuses on building a conservative grammar engine: rules are added from reviewed linguistic evidence, tested against real Somali examples, and kept context-sensitive when the evidence does not support a safe automatic judgment.

## Project goals

1. Help Somali speakers improve written Somali.
2. Help learners understand Somali grammar through clear explanations and examples.
3. Build reviewed Somali morphology, syntax, lexical evidence, and QA datasets.
4. Create a strong language foundation that can later help train and evaluate Somali-first AI systems.

This repository does **not** train a large language model. The current work is the linguistic and rule-based foundation that can later support model training and evaluation.

## Current status

The repository is no longer only a planning project. It contains:

- an executable command-line checker in `check.py`;
- grammar analyzers under `src/`;
- machine-readable grammar, morphology, orthography, and variant rules under `rules/`;
- reviewed linguistic evidence and holdout QA datasets under `data/`;
- automated regression and generalization tests under `tests/`;
- documented project decisions and linguistic analysis under `docs/`;
- source notes under `sources/`.

See [`docs/STATUS.md`](docs/STATUS.md) for the current coverage dashboard and [`docs/REPO_MAP.md`](docs/REPO_MAP.md) for a map of the repository.

## Core safety principle

**Do not invent Somali grammar or morphology.**

A predicted word form is not accepted simply because it looks regular. The project prefers:

- source-backed forms over guessed forms;
- exact reviewed morphology over blind suffix generation;
- `context_required` or unknown results over unsafe corrections;
- recognition of supported regional variants instead of falsely marking them wrong.

## Evidence flow

```text
linguistic source / native review
            ↓
      reviewed evidence
            ↓
     grammar/morphology rule
            ↓
        analyzer code
            ↓
          checker
            ↓
   tests + independent QA
```

Evidence and executable behavior are deliberately separated. A source-backed observation does not automatically become an autocorrection rule.

## Repository layout

```text
somali-grammar/
├── check.py          # main command-line checker
├── src/              # executable grammar/analyzer code
├── rules/            # machine-readable linguistic rules
├── data/             # reviewed evidence and QA datasets
├── tests/            # automated behavior and regression tests
├── sources/          # human-readable external source notes
├── docs/             # project decisions, status, architecture notes
└── lexicon/          # small legacy/sample lexical area under audit
```

For detailed folder responsibilities, see [`docs/REPO_MAP.md`](docs/REPO_MAP.md).

## Current linguistic coverage

Current implemented or reviewed areas include:

- personal pronouns and subject clitics;
- subject–verb agreement;
- masculine/feminine and singular/plural agreement;
- noun subject forms and focus-sensitive case behavior;
- `baa` / `ayaa` focus constructions;
- object clitics such as `idin`;
- statement clitics such as `wuu`, `way`, `waan`, and `waad`;
- connective forms such as `wuuna`, `wayna`, and reviewed `wuxuuna` constructions;
- negation and negative agreement;
- future and negative-future auxiliary agreement;
- past, habitual, imperative, jussive, dependent, and conditional patterns;
- possession with `leeyahay`-type constructions;
- predicate/copula agreement;
- reviewed verb classes and irregular verb families;
- regional-variant handling with a Jigjiga-first preferred output profile.

Coverage is still incomplete. Unknown or insufficiently supported forms should remain unjudged rather than being guessed.

## Preferred Somali output profile

The current preferred generation/teaching profile is **Jigjiga Somali**, with strong compatibility with Northwestern/Hargeisa usage. Other supported Somali regional forms should remain recognized and should not be marked wrong solely because they differ regionally.

See [`docs/DECISIONS.md`](docs/DECISIONS.md) for the full decision history.

## Running the checker

```bash
python check.py "Somali text here"
```

The checker combines safe orthography corrections with conservative grammar analysis. Context-sensitive findings should be surfaced for review instead of automatically rewritten.

## Development rule

Before promoting a new grammar behavior:

1. collect trustworthy evidence;
2. record provenance;
3. separate morphology facts from sentence-context claims;
4. implement only what the evidence supports;
5. add positive, negative, ambiguous, and unknown tests;
6. test examples that were not used to create the rule;
7. keep unsupported cases unjudged.

## Documentation

- [`docs/STATUS.md`](docs/STATUS.md) — current project and coverage dashboard
- [`docs/REPO_MAP.md`](docs/REPO_MAP.md) — what every major folder is for
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — project decisions and reviewed language judgments
- [`docs/GRAMMAR_ANALYSIS.md`](docs/GRAMMAR_ANALYSIS.md) — grammar analysis notes
- [`docs/LEXICON_SCHEMA.md`](docs/LEXICON_SCHEMA.md) — lexical data schema
- [`rules/grammar/README.md`](rules/grammar/README.md) — grammar evidence-layer principles
- [`rules/morphology/README.md`](rules/morphology/README.md) — morphology evidence-layer principles
