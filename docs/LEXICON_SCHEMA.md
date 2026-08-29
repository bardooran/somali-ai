# Somali lexicon layer

The grammar checker needs structured lexical and morphological information in addition to surface correction rules.

## Evidence source

The first schema is based on the SLS `resources/qaamuus/` collection. SLS describes each dictionary entry as a headword followed by grammatical code(s), inflection information where present, definitions, and cross-references. The grammatical code key includes noun, verb, adjective, pronoun, adverb, preposition, particle, conjunction, gender, number, definiteness, transitivity, conjugation, subject, object, and other grammatical features.

The dictionary collection is descriptive evidence. It must not be treated as a final normative spelling authority.

## Proposed normalized record

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
2. Keep the original inflection notation as `inflection_raw` until we have a tested parser for it.
3. Decode only codes explicitly defined by the source abbreviation table.
4. Keep variants/cross-references separate from automatic spelling corrections.
5. Never infer gender, number, tense, conjugation, or part of speech from spelling alone when the source does not state it.
6. Preserve homonym distinctions such as superscript-numbered entries.
7. Record provenance for every imported lexical record.
8. Validate extracted records with tests before the checker uses them for grammatical decisions.

## Initial grammatical code mapping

| Code | Normalized meaning |
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
| `ld` | variant / same-as cross-reference |

This mapping is deliberately incomplete. New codes should be added only after checking the source abbreviation table.

## Next implementation stage

Build a parser against a small reviewed sample first. Do not bulk-import the whole dictionary until parsing of headwords, compound grammatical codes, inflection notation, homonyms, definitions, and `ld`/`eeg` cross-references is reliable.
