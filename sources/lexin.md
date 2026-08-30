# Lexin Swedish–Somali

Source repository: `sprakradet/lexin-json`

Primary Somali file: `lexin-entries-som.json`

## Role in this project

Lexin is used as bilingual lexical and usage evidence for Somali. It is not treated as a Somali morphology authority by default.

The verified JSON structure separates Swedish material under `BaseLang` from Somali material under `TargetLang`.

Useful Somali-side evidence can include:

- `Translation`
- `Comment`
- `Explanation`
- `Example`
- `Idiom`
- `Compound`
- `Synonym`

The top-level search indices may also contain `targetlang` and `targetlang-synonym` strings useful for lookup and candidate extraction.

## Critical parsing rule

Do not interpret `BaseLang.Type` or `BaseLang.Inflection` as Somali grammatical information. Those fields describe the Swedish entry.

For example, a Swedish noun may have Swedish inflection forms while its Somali translation appears only in `TargetLang.Translation`. The Somali translation must therefore be cross-checked against Somali-native sources such as SLS or GiellaLT before assigning Somali part-of-speech or morphology.

## Pipeline use

1. Extract Somali target-language strings with their Lexin entry ID and Swedish source lemma.
2. Preserve field type: translation, synonym, example, idiom, compound, comment, or explanation.
3. Normalize whitespace and obvious machine-format artifacts only; do not silently rewrite Somali spelling.
4. Cross-reference Somali tokens/phrases against SLS and GiellaLT where possible.
5. Use Lexin examples as usage/context evidence and learner examples after review.
6. Promote a Lexin-derived fact into an automatic grammar correction only when Somali grammatical evidence supports it.

## Provenance

Every extracted record should retain at least:

- Lexin entry ID / variant ID when available
- Swedish base lemma (`Value`)
- source field path (for example `TargetLang.Example`)
- Somali text
- source repository/file
- review status

This keeps bilingual dictionary evidence separate from normative grammar decisions.
