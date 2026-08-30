# Morphology reference layer

This directory stores source-backed Somali morphological evidence separately from executable orthography corrections.

The records here describe patterns such as noun gender, singular/plural behavior, gender polarity, verb classes, inflection, and reviewed aspect contrasts. They are **not** automatically applied by the checker.

## Status

`descriptive` means the record faithfully represents a reviewed source claim, but the project has not yet promoted it into a deterministic correction rule.

`provisional` means the pattern has useful evidence, including project native-speaker review where recorded, but still needs broader cross-source validation before it can be treated as a general rule.

`context_required` means the construction is real project evidence but interpretation depends on context, contraction/particle analysis, discourse, or an unresolved source conflict.

A morphology pattern can become executable only after we know:

1. how to identify the relevant lemma/class reliably;
2. what exceptions exist;
3. whether dialect or lexical variation affects the rule;
4. whether another trusted source agrees or provides needed qualifications; and
5. how to test the rule against real Somali sentences without creating false corrections.

## Current data

`noun_plural_patterns.jsonl` contains the noun plural classes and gender behavior described in SLS `resources/sarfe/01-magacyada.md`, including masculine L1–L6 classes and four feminine plural patterns.

`verb_conjugation_samples.jsonl` contains descriptive verb-class, tense/aspect, and negation samples from SLS `resources/sarfe/02-falalka.md`.

`verb_aspect_arag.jsonl` stores native-reviewed `arag` aspect contrasts independently from object-clitic parsing. It preserves pairs such as `arkaa` / `arkayaa`, `aragtaa` / `arkaysaa`, and `ma arko` / `ma arkayo`, plus the reviewed fact that both `Maydin arkaa?` and `Maan idin arkaa?` can be valid first-person constructions in project evidence. These records are not autocorrection rules.

One important noun property is **gender polarity**: several noun classes change grammatical gender between singular and plural. This means a future grammar checker cannot determine agreement by simply assigning one permanent gender to a lemma.
