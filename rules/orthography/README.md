# Orthography rules

This directory contains machine-readable Somali writing rules used by the checker.

## Rule maturity

Rules must carry a status so the software does not treat uncertain linguistic guidance as settled fact.

- `provisional` — supported by a documented source, but still needs broader validation.
- `ambiguous` — the form can have more than one analysis/correction and must not be auto-fixed without context.
- `context_required` — evidence or interpretation depends on context, dialect, or conflicting sources; it must not be auto-fixed.
- `validated` — reserved for rules we have reviewed against multiple reliable sources and tests.

## Current principle

The checker separates **detection** from **automatic correction**. A form may be worth flagging without being safe to rewrite automatically.

## Accepted variants and source conflicts

When reliable project resources disagree on a spelling or form, we record the alternatives in `variants.jsonl` instead of silently choosing one. Variant records are reference data and are not executable replacements.

Examples currently under review include:

- `Jimce` / `Jimco` for Friday
- `Jannaayo` / `Janaayo` for January

These forms should remain untouched by automatic correction until broader linguistic validation gives us enough evidence to classify their usage.

## Orthography groups

Rules are kept in separate files by purpose:

- contractions
- spacing and word separation
- punctuation
- capitalization
- weekdays and months
- proper names
- accepted variants and dialect-sensitive forms

Every rule should include provenance and tests before it becomes part of automatic correction.
