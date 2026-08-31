# Vocabulary data

This folder stores reviewed Somali **word information**.

Use this folder for dictionary-style facts such as:

- the word itself (`lemma`);
- noun/verb/other word type;
- grammatical gender when a source gives it;
- concise Somali meaning notes;
- documented related words or variants;
- provenance showing where the information came from.

## Current files

- `qaamuus_2012_grammar_words.jsonl` — grammar-related reviewed vocabulary.
- `qaamuus_2012_everyday_words.jsonl` — ordinary reviewed vocabulary.
- `qaamuus_2012_everyday_verbs.jsonl` — reviewed everyday verbs.
- `qaamuus_2012_sample_entries.jsonl` — preserved early Qaamuus/SLS sample records.
- `somali_numbers.json` — reviewed cardinal numbers and constrained composition evidence.
- `somali_calendar_terms.jsonl` — Gregorian month names and Somali traditional seasons.
- `somali_datetime_terms.jsonl` — weekdays, relative days, time units, time-of-day words, and reviewed relative-time vocabulary.
- `somali_age_terms.jsonl` — age-related vocabulary used alongside the reviewed `N jir` construction.
- `somali_direction_terms.jsonl` — cardinal/intermediate directions and location/direction terms with context-sensitive senses marked explicitly.

Executable helpers live in `src/vocabulary.py`, `src/numbers.py`, `src/calendar_terms.py`, `src/datetime_terms.py`, `src/age.py`, and `src/directions.py`.

## Calendar and clock safety

Somali traditional seasons are **not mechanically identical** to Western spring/summer/autumn/winter. Their month alignment is approximate and region-sensitive.

Clock expressions are also kept conservative. Sources attest ordinary forms such as `afar saac` / `labadii iyo barka`, while other standard-Somali teaching material documents a traditional six-hour clock relationship. The project therefore does **not** automatically convert every 24-hour timestamp into a Somali clock phrase until the convention/context is specified.

## Relative-time safety

Reviewed executable forms include `shalay`, `maanta`, `berri`, `dorraad`, `saadambe`, and provisionally reviewed `saakuun`, plus constrained phrases such as `3 saacadood ka hor` and `6 bilood ka dib`.

Submitted forms such as `shalay-dambe` and `saakuunta` are stored as candidates but are not automatic generation/correction targets until stronger independent evidence establishes their exact role.

## Important separation

Vocabulary data is **not automatically a grammar correction rule**. A dictionary or submitted batch may establish that a form exists without proving every sentence-level use or translation.

Context-sensitive terms such as `kor`, `hore`, `bari`, `dhexe`, `horta`, and `dhallinyaro` must not be flattened into one English gloss when Somali context can change their function.

## Safety

Do not guess missing gender, word class, conjugation, meaning, spelling status, number composition, clock convention, or regional meaning from surface form alone. Preserve source evidence and leave unsupported information unknown.
