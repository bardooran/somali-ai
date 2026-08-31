# Source code

Executable Python code for the Somali grammar foundation.

## Main responsibilities

- sentence agreement analysis;
- focus and connective analysis;
- negation, tense, aspect, and mood analysis;
- noun gender/number/case analysis;
- object and clitic-role analysis;
- conservative morphology lookup;
- `vocabulary.py` for reviewed word lookup;
- `numbers.py` for evidence-constrained Somali cardinal-number analysis;
- regional-variant analysis.

`numbers.py` recognizes reviewed base numerals, the documented finite 11–99 composition system, and explicitly reviewed large-number expressions. It deliberately does not invent arbitrary large-number phrases from an unchecked productive rule.

## Separation rule

`src/` contains **code**, not raw linguistic source material.

Reviewed evidence belongs under `data/` or `rules/`. Human-readable source notes belong under `sources/` or `docs/`.

## Safety rule

Analyzer code should only make judgments that the reviewed evidence supports. Unsupported word forms, numeral expressions, or sentence interpretations should remain unknown or context-dependent rather than being guessed.

Long term this code may move into an installable `src/somali_grammar/` package, but that should be a dedicated behavior-neutral refactor.
