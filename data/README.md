# Data

Reviewed evidence datasets used by the Somali grammar foundation.

This directory stores linguistic material that supports analysis and evaluation. It is separate from executable Python code and from machine-readable correction rules.

## Folders

- `vocabulary/` — reviewed information about Somali words: headwords, word classes, meanings, gender, and related source-backed facts.
- `morphology/` — reviewed word forms, paradigms, exact stems, irregular forms, and native-reviewed morphology.
- `corpus/` — collections of real Somali text used for research and stress-testing, including the maahmaahyo collection.
- `qa/` — independent or holdout examples used to challenge the engine.
- `sources/` — structured source-derived datasets used by evidence pipelines.

## Simple distinction

```text
vocabulary = information about words
morphology = how reviewed words change form
corpus     = real Somali text collections
qa         = examples used to test the engine
sources    = structured evidence extracted from sources
```

## Evidence rule

Every imported or reviewed fact should retain enough provenance to answer where it came from, how it was reviewed, and whether it is descriptive, provisional, context-sensitive, or executable.

## QA rule

Holdout QA should remain genuinely independent. Do not silently use the same holdout examples to invent the rule they are meant to test.

## Safety rule

Data can document a real Somali form or sentence without authorizing an automatic correction. Promotion into executable grammar behavior requires separate validation and tests.
