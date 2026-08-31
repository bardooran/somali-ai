# Somali vocabulary data schema

The grammar checker needs structured information about Somali words in addition to sentence rules and morphology.

## What belongs here

Vocabulary records describe source-backed word facts such as:

- headword / lemma;
- part of speech;
- grammatical gender when explicitly supported;
- source inflection notation;
- concise Somali meaning evidence;
- documented variants or related words;
- provenance and review status.

The first schema is based on the SLS `resources/qaamuus/` collection and reviewed material from `Qaamuuska Af-Soomaaliga` (Puglielli & Mansuur, 2012). Dictionary evidence is descriptive evidence; it is not automatically a final spelling or grammar authority.

## Example normalized record

```json
{
  "lemma": "Aabbe",
  "part_of_speech": "noun",
  "features": {
    "gender": "masculine"
  },
  "inflection_raw": "-bayaal, m.l/m.dh",
  "variants": ["aabbo"],
  "source": "SLS resources/qaamuus/22-a.md",
  "source_codes": ["m.l"],
  "status": "descriptive"
}
```

## Principles

1. Preserve the original headword and grammatical codes.
2. Keep original inflection notation as `inflection_raw` until it has a tested parser.
3. Decode only codes explicitly supported by the source.
4. Keep variants separate from automatic spelling corrections.
5. Never infer gender, number, tense, conjugation, or part of speech from spelling alone when the source does not state it.
6. Preserve homonym distinctions.
7. Record provenance for every imported word record.
8. Validate extracted records before grammar code relies on them.
9. Regional preference is not the same as grammatical validity.
10. Sense-sensitive variants remain context-dependent.
11. Lemmatization must stay evidence-constrained; do not strip suffixes from unseen words and assume the remainder is a valid lemma.
12. Irregular verbs must be stored explicitly rather than forced through a regular template.

## Common Qaamuus/SLS codes

| Code | Meaning |
| --- | --- |
| `m` | noun |
| `f` | verb |
| `s` | adjective / attributive |
| `mu` | pronoun |
| `fk` | adverb |
| `h` | preposition |
| `qr` | particle |
| `xi` | conjunction |
| `l` | masculine |
| `dh` | feminine |
| `ke` | singular |
| `w` | plural |
| `ca` | definite |
| `ac` | indefinite |
| `g` | transitive |
| `mg` | intransitive |
| `lg` | ditransitive |
| `isrog` | conjugation |
| `y` | subject |
| `ly` | object |
| `ld` | documented variant / cross-reference |

This mapping is intentionally incomplete. Add new codes only after checking the source abbreviation table.

## Current reviewed vocabulary datasets

- `data/vocabulary/qaamuus_2012_grammar_words.jsonl`
- `data/vocabulary/qaamuus_2012_everyday_words.jsonl`
- `data/vocabulary/qaamuus_2012_everyday_verbs.jsonl`
- `data/vocabulary/qaamuus_2012_sample_entries.jsonl`

Reviewed inflected word forms remain under `data/morphology/` because morphology and dictionary-style vocabulary are separate layers.

## Current word lookup

`src/vocabulary.py` searches the reviewed vocabulary datasets and then attaches exact reviewed morphology and regional-variant evidence independently.

It preserves multiple dictionary analyses when a surface form has more than one supported interpretation. It does not guess an unseen lemma by blindly removing a suffix.

A vocabulary or morphology match does not by itself authorize an automatic correction.
