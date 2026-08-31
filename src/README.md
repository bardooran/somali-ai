# Source code

Executable Python code for the Somali grammar foundation.

## Main responsibilities

- sentence agreement analysis;
- focus, negation, tense, aspect, mood, noun and clitic analysis;
- conservative morphology lookup;
- `vocabulary.py` for reviewed word lookup;
- `numbers.py` for evidence-constrained Somali cardinal numbers;
- `calendar_terms.py` for Gregorian months and Somali traditional seasons;
- `datetime_terms.py` for weekdays, full Gregorian date display, relative-day lookup, durations, and reviewed relative-time phrases;
- `age.py` for the reviewed numeric `N jir` age construction;
- `directions.py` for exact reviewed direction/location vocabulary;
- regional-variant analysis.

`numbers.py` does not invent arbitrary large-number phrases from an unchecked productive rule.

`calendar_terms.py` treats Somali seasons as region-sensitive and does not mechanically translate them into Western seasons.

`datetime_terms.py` deliberately does **not** generate clock-hour translations. Somali sources show different clock conventions, including direct hour wording and a documented traditional six-hour relationship, so the convention must be established before automatic clock conversion is safe.

`age.py` recognizes numeric `N jir` without guessing that broad social labels such as `dhallinyaro` equal one fixed age range.

`directions.py` preserves context-sensitive terms such as `bari`, `hore`, `kor`, `dhexe`, and `horta` instead of forcing one interpretation in every sentence.

## Separation rule

`src/` contains **code**, not raw linguistic source material. Reviewed evidence belongs under `data/` or `rules/`; human-readable source notes belong under `sources/` or `docs/`.

## Safety rule

Analyzer code should only make judgments that reviewed evidence supports. Unsupported word forms, numeral expressions, calendar spellings, clock conventions, regional meanings, or sentence interpretations remain unknown/context-dependent rather than guessed.
