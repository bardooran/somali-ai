# Vocabulary data

This folder stores reviewed Somali **word information** and small evidence-backed language inventories.

## Current files

- `qaamuus_2012_grammar_words.jsonl` — grammar-related reviewed vocabulary.
- `qaamuus_2012_everyday_words.jsonl` — ordinary reviewed vocabulary.
- `qaamuus_2012_everyday_verbs.jsonl` — reviewed everyday verbs.
- `qaamuus_2012_sample_entries.jsonl` — preserved early Qaamuus/SLS sample records.
- `somali_numbers.json` — reviewed cardinal numbers and constrained composition evidence.
- `somali_ordinals.json` — reviewed written ordinals plus productive numeric `N-aad` notation.
- `somali_calendar_terms.jsonl` — Gregorian month names and Somali traditional seasons.
- `somali_datetime_terms.jsonl` — weekdays, relative days, time units, time-of-day words, and relative-time vocabulary.
- `somali_age_terms.jsonl` — age vocabulary used with the reviewed `N jir` construction.
- `somali_direction_terms.jsonl` — direction/location vocabulary with ambiguity preserved.
- `somali_measurement_terms.jsonl` — metric length, mass, volume, temperature, and distance terminology with documented spelling variants.
- `somali_function_words.json` — grammar-bearing high-frequency words; **not** a blind stopword-deletion list.

Executable helpers live in `src/`, including `numbers.py`, `ordinals.py`, `calendar_terms.py`, `datetime_terms.py`, `age.py`, `directions.py`, `measurements.py`, and `function_words.py`.

## Ordinal safety

Numeric notation such as `1aad`, `2aad`, and `36-aad` is treated as productive. Written-out ordinals such as `kowaad`, `saddexaad`, `afraad`, `siddeedaad`, and `tobnaad` are recognized from reviewed evidence. Unseen written-out ordinal morphology is not guessed.

`toddobaad` is explicitly context-sensitive because it can mean both **seventh** and **week**.

## Measurement safety

Documented spelling variation is preserved rather than blindly corrected. Examples include `kiiloomitir / kiilomitir / kiilo mitir` and `litir / liitar / litar / liitir`.

`25°C` is recognized as Celsius notation, but the submitted lexical form `Selsiyas` remains non-executable until stronger independent Somali evidence supports it. Current dictionary evidence also records `sentigreed` for Centigrade/Celsius.

## Function-word / stopword safety

Somali grammar-bearing forms such as `ayaa`, `waa`, `oo`, `ee`, `ku`, `ka`, `u`, `la`, `wuxuu`, and `waxay` are **not safe for blind stopword removal**. They carry focus, clause, clitic, agreement, or connective information.

Submitted `qof` and `dadka` are kept out of the function-word list because they are content words, and English `this` is not accepted as Somali.

## Calendar and clock safety

Somali traditional seasons are not mechanically identical to Western spring/summer/autumn/winter. Clock expressions are also convention-sensitive; automatic clock conversion should follow the project's Jigjiga/Hargeisa preference only after that convention is explicitly implemented and tested.

## General safety

Vocabulary evidence is **not automatically a grammar correction rule**. Preserve provenance, keep ambiguity/variation visible, and leave unsupported forms unknown rather than guessing.
