# Data

Reviewed evidence datasets used by the Somali grammar foundation.

This directory stores linguistic material that supports analysis and evaluation. It is deliberately separate from executable Python code and from machine-readable correction rules.

## Folders

- `morphology/` — reviewed surface forms, paradigms, exact stems, irregular forms, and native-reviewed morphology.
- `lexical/` — reviewed word-level lexical evidence.
- `qa/` — independent or holdout examples used to stress-test the engine.
- `sources/` — structured source-derived datasets or artifacts used by evidence pipelines.

## Evidence rule

Every imported or reviewed fact should retain enough provenance to answer:

- Where did this form or claim come from?
- Was it externally sourced, native-reviewed, or both?
- Is it descriptive, provisional, context-sensitive, or promoted into executable behavior?

## QA rule

Holdout QA should remain genuinely useful as an independent challenge set. Do not silently use the same holdout examples to invent the rule they are meant to test.

## Safety rule

Data can document a real Somali form without authorizing automatic correction. Promotion into executable grammar behavior requires separate validation and tests.
