# Rules

Machine-readable linguistic rules and reference constraints used by the Somali grammar project.

This directory is split by linguistic responsibility so that spelling, morphology, sentence grammar, and regional variation are not mixed together.

## Folders

- `grammar/` — sentence-level grammar, agreement, focus, clitics, negation, moods, case, possession, questions, and clause constructions.
- `morphology/` — noun and verb morphology patterns and reviewed reference forms.
- `orthography/` — safe spelling/orthographic rules, including rules that may support deterministic correction.
- `variants/` — supported regional or lexical variants that should not automatically be treated as grammatical errors.

## Important distinction

A machine-readable record is **not automatically an autocorrection rule**.

Grammar and morphology records may have statuses such as descriptive, provisional, or context-required. Automatic rewriting should be limited to behavior explicitly shown to be safe.

## Rule requirements

A new rule should normally have:

1. a clear linguistic claim;
2. provenance or reviewed evidence;
3. an explicit scope;
4. known limitations or context requirements;
5. executable tests when promoted into analyzer behavior.

Never create a general Somali paradigm from a single observed form.
