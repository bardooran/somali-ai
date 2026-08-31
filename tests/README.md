# Tests

Automated tests for the Somali grammar checker, analyzers, morphology coverage, and regression behavior.

Tests are executable quality control. They are not a substitute for linguistic evidence.

## What tests should protect

When relevant, a grammar feature should be tested with:

1. **positive examples** — supported Somali that should be recognized;
2. **negative examples** — clearly incompatible forms or agreement patterns;
3. **ambiguous/context-required examples** — constructions the engine must not over-correct;
4. **unknown examples** — unsupported forms that must remain unguessed;
5. **holdout/generalization examples** — new examples not used to create the rule;
6. **regression examples** — behavior that previously broke and must stay fixed.

## Current organization

The test suite currently contains many top-level feature files plus `fixtures/` and `orthography/` subdirectories.

This is valid but is becoming large. A future cleanup may group tests into folders such as `grammar/`, `morphology/`, `integration/`, and `regression/`. That move should be performed only as a dedicated refactor with all test discovery verified afterward.

## Naming guideline

Prefer test names that identify the actual linguistic behavior, for example:

- `test_subject_focus_...`
- `test_negative_future_...`
- `test_class2_verb_...`
- `test_connective_waxaa_...`

Avoid vague names such as `test_new.py` or `test_misc.py`.

## Evidence rule

If a test asserts a new Somali linguistic fact, make sure the fact is also represented by reviewed evidence or a documented project decision. Do not make a sentence true merely because it appears in a test.
