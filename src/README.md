# Source Code

Executable Python code for the Somali grammar engine.

This directory contains analyzers and shared logic that turn reviewed rules/evidence into conservative grammar behavior.

## Responsibilities

Modules here may:

- load reviewed linguistic records;
- analyze agreement, focus, clitics, negation, moods, noun forms, and clause constructions;
- return structured known/unknown/context-required results;
- support the main `check.py` command-line checker.

## What does not belong here

Do not store raw linguistic source notes, large copied paradigms, or unreviewed word lists directly in Python when they can be represented as data under `rules/` or `data/`.

The preferred flow is:

```text
reviewed evidence → machine-readable rule/data → analyzer code → tests
```

## Conservative analyzer rule

An analyzer should not claim a form is valid merely because a suffix pattern could produce it. If the project has not reviewed enough evidence to generalize, return unknown or context-required.

## Future structure

The current flat module layout is active and should remain stable during rapid grammar development. A later behavior-neutral refactor may create an installable package such as `src/somali_grammar/` and group modules by grammar domain.
