# Somali lexical knowledge

This directory stores structured lexical evidence for future Somali language features, including vocabulary learning, semantic search, a word analyzer, and a future Contexto-style game.

## Important separation

Grammar rules belong under `rules/` and executable grammar logic under `src/`.

Lexical records here are evidence about words and meanings. They are not automatically grammar rules and are not automatically trusted as correction targets.

Regional preference is stored separately under `rules/variants/`. A dictionary fact and a project-preferred Jigjiga form may point to each other, but they must retain separate provenance.

## Current reviewed Qaamuus datasets

- `qaamuus_2012_grammar_lexicon_seed.jsonl` — grammar terminology, function words, homographs useful to grammar analysis, and the first reviewed bridge records.
- `qaamuus_2012_everyday_lexicon_seed.jsonl` — ordinary vocabulary mined in coherent families. It is intentionally separate so the general lexicon can grow without turning the grammar seed into a catch-all file.

The default lookup prototype in `src/lexicon.py` searches both files while preserving every matching analysis.

## English meanings

The current Qaamuuska Af-Soomaaliga source is a Somali explanatory dictionary. Its definitions are Somali, not an English translation dictionary. Therefore English glosses must be stored separately with their own provenance. Never label an English gloss as coming from the Qaamuus unless the source actually provides it.

## Suggested record fields

- `lemma`: Somali headword
- `source_pos`: original part-of-speech/grammar code when supported
- `inflection_raw`: original inflection notation where present
- `gender`: grammatical gender when explicitly supported
- `transitivity`: verb valency when explicitly supported
- `conjugation`: verb class when explicitly supported
- `somali_definition_summary`: concise structured/paraphrased Somali meaning evidence
- `english_gloss`: English meaning from a separately identified source or reviewed translation
- `related_lemmas`: documented variants, synonyms, derivational relatives, or other source-linked words
- `domain`: broad lexical domain such as `naxwe`, `general_lexicon`, or `suugaan`
- `project_profile`: separate project preference metadata when needed
- `source`: provenance identifier
- `source_location`: page/entry/section when available
- `status`: descriptive, provisional, native_reviewed, context_required, etc.

## Copyright/provenance policy

We extract linguistic facts and structured knowledge. We do not reproduce entire copyrighted dictionaries or books. Definitions should be represented as concise facts/paraphrases where appropriate, with provenance retained.
