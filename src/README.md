# Source code

Executable Python code for the Somali grammar foundation.

## Main responsibilities

- sentence agreement, focus, negation, tense, aspect, mood, noun, and clitic analysis;
- conservative morphology and vocabulary lookup;
- `numbers.py` — evidence-constrained cardinal numbers;
- `ordinals.py` — productive numeric `N-aad` notation plus exact reviewed written ordinals;
- `calendar_terms.py` — Gregorian months and Somali traditional seasons;
- `datetime_terms.py` — weekdays, full dates, relative days/time, and durations;
- `age.py` — reviewed numeric `N jir` age construction;
- `directions.py` — reviewed direction/location vocabulary;
- `measurements.py` — metric measurement expressions and documented Somali unit variants;
- `function_words.py` — grammar-aware high-frequency/function-word classification;
- regional-variant analysis.

## Conservative behavior

`numbers.py` does not invent arbitrary large-number phrases.

`ordinals.py` recognizes numeric forms such as `1aad` and `36-aad` productively, but it does not guess unseen written-out ordinal morphophonology.

`datetime_terms.py` does not yet generate clock-hour translations automatically; the project preference is Jigjiga/Hargeisa-style direct clock wording, while other regional conventions remain separately recognizable when evidenced.

`measurements.py` recognizes units and symbols without converting values or forcing one spelling where sources support variants.

`function_words.py` is deliberately **not** a stopword remover. Somali particles, clitics, focus markers, and connectives often carry essential grammar and are marked unsafe for blind deletion.

## Safety rule

Analyzer code should only make judgments that reviewed evidence supports. Unsupported forms, spellings, regional conventions, or sentence interpretations remain unknown/context-dependent rather than guessed.
