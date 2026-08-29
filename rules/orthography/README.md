# Orthography rules

This directory contains machine-readable Somali writing rules used by the checker.

## Rule maturity

Rules must carry a status so the software does not treat uncertain linguistic guidance as settled fact.

- `provisional` — supported by a documented source, but still needs broader validation.
- `ambiguous` — the form can have more than one analysis/correction and must not be auto-fixed without context.
- `validated` — reserved for rules we have reviewed against multiple reliable sources and tests.

## Current principle

The checker separates **detection** from **automatic correction**. A form may be worth flagging without being safe to rewrite automatically.

## Next orthography groups

We will add new groups separately rather than mixing them into contractions:

- spacing and word separation
- punctuation
- capitalization
- accepted variants and dialect-sensitive forms

Every rule should include provenance and tests before it becomes part of automatic correction.
