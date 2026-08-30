# Somali lexical knowledge

This directory stores structured lexical evidence for future Somali language features, including vocabulary learning, semantic search, and a future Contexto-style game.

## Important separation

Grammar rules belong under `rules/` and executable grammar logic under `src/`.

Lexical records here are evidence about words and meanings. They are not automatically grammar rules and are not automatically trusted as correction targets.

## English meanings

The current Qaamuuska Af-Soomaaliga source is a Somali explanatory dictionary. Its definitions are Somali, not an English translation dictionary. Therefore English glosses must be stored separately with their own provenance. Never label an English gloss as coming from the Qaamuus unless the source actually provides it.

## Suggested record fields

- `lemma`: Somali headword
- `pos`: part of speech when supported
- `gender`: grammatical gender when supported
- `transitivity`: verb valency when supported
- `conjugation`: verb class when supported
- `somali_definition`: short structured/paraphrased Somali meaning evidence
- `english_gloss`: English meaning from a separately identified source or reviewed translation
- `variants`: documented spelling/lexical variants
- `semantic_tags`: broad meaning categories for later semantic/game use
- `source`: provenance identifier
- `source_location`: page/entry/section when available
- `status`: descriptive, provisional, native_reviewed, context_required, etc.

## Copyright/provenance policy

We extract linguistic facts and structured knowledge. We do not reproduce entire copyrighted dictionaries or books. Definitions should be represented as concise facts/paraphrases where appropriate, with provenance retained.
