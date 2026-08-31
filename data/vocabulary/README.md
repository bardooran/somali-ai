# Vocabulary data

This folder stores reviewed Somali **word information**.

Use this folder for dictionary-style facts such as:

- the word itself (`lemma`);
- noun/verb/other word type;
- grammatical gender when a source gives it;
- source part-of-speech codes;
- concise Somali meaning notes;
- documented related words or variants;
- provenance showing where the information came from.

## Current files

- `qaamuus_2012_grammar_words.jsonl` — words especially useful for grammar analysis, function words, and grammar-related entries.
- `qaamuus_2012_everyday_words.jsonl` — ordinary reviewed vocabulary.
- `qaamuus_2012_everyday_verbs.jsonl` — reviewed everyday verb entries.
- `qaamuus_2012_sample_entries.jsonl` — early Qaamuus/SLS sample records preserved from the old root `lexicon/` folder.
- `somali_numbers.json` — reviewed Somali cardinal-number vocabulary, 11–99 composition rules, exact reviewed large-number expressions, source notes, and submitted candidates that are deliberately not promoted without enough evidence.

The executable general word lookup is in `src/vocabulary.py`.
The conservative numeral analyzer is in `src/numbers.py`.

## Important separation

Vocabulary data is **not automatically a grammar correction rule**.

A dictionary may tell us that a word exists, its gender, or its grammatical category. Sentence grammar still needs construction-level evidence under `rules/` and executable logic under `src/`.

The number dataset follows the same rule: a submitted or source-attested form can be stored without becoming an automatic correction target. Unreviewed large-number compositions remain unknown rather than being generated freely.

Regional preferences stay separate under `rules/variants/` so a supported regional form is not incorrectly treated as a grammar error.

## Safety

Do not guess missing gender, word class, conjugation, meaning, spelling status, or number composition from surface form alone. Preserve source evidence and leave unsupported information unknown.
