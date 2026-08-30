# Somali lexicon layer

The grammar checker needs structured lexical and morphological information in addition to surface correction rules.

## Evidence source

The first schema is based on the SLS `resources/qaamuus/` collection. SLS describes each dictionary entry as a headword followed by grammatical code(s), inflection information where present, definitions, and cross-references. The grammatical code key includes noun, verb, adjective, pronoun, adverb, preposition, particle, conjunction, gender, number, definiteness, transitivity, conjugation, subject, object, and other grammatical features.

The dictionary collection is descriptive evidence. It must not be treated as a final normative spelling authority.

The project now also stores reviewed lexical evidence extracted from `Qaamuuska Af-Soomaaliga` (Puglielli & Mansuur, 2012). Source facts and project regional preferences remain separate layers.

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
9. Regional preference is not grammatical validity. A recognized nonpreferred regional form must not be labeled wrong solely because the Jigjiga-first profile would generate a different form.
10. Sense-sensitive variant pairs must remain context-required. For example, body-sense `jir` may correspond to preferred `jidh`, but the existential verb `jir-` is a different analysis; similarly, `maydh` relates only to the washing sense of polysemous `dhaq`.
11. Morphological lemmatization must be evidence-constrained. The first morphology layer recognizes stored reviewed surface forms; it does not strip a suffix from an unseen word and assume the remainder is a valid lemma.

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

## Current reviewed datasets

The reviewed Qaamuus lexicon is split by purpose instead of putting every word in one growing file:

- `data/lexical/qaamuus_2012_grammar_lexicon_seed.jsonl` — grammar terms, function words, and the first reviewed lexical bridge records.
- `data/lexical/qaamuus_2012_everyday_lexicon_seed.jsonl` — ordinary vocabulary and lexical families mined from dictionary entries. Initial records include `inan`, `gaban`, `duwan`, `kor`, and the noun/verb homographs of `gabay`.
- `data/morphology/qaamuus_2012_reviewed_noun_forms.jsonl` — reviewed inflected noun surface forms linked to candidate lemmas and grammatical features.

`src/lexicon.py` searches both lexical datasets by default and attaches reviewed morphology and regional evidence independently.

## Current reviewed lookup prototype

`src/lexicon.py` preserves multiple dictionary analyses for homographs rather than selecting one without sentence context. Current exact-headword examples include three analyses for `ka`, two for `kee`, masculine/feminine analyses for `inan`, noun/verb analyses for `kor`, and noun/verb analyses for `gabay`.

`src/morphology_candidates.py` now provides the first safe surface-form-to-lemma bridge. It performs exact matching against reviewed morphology records only. Current source-backed examples include:

- `buugga → buug` — masculine definite singular.
- `marada → maro`, `badda → bad`, `qodaxda → qodax`, `bacda → bac`, `usha → ul`, `isha → il`, `bisha → bil` — feminine definite forms with source-described article allomorphy.
- `buugag → buug`, `kabo → kab`, `gacmo → gacan`, `mindiyo → mindi` — plural patterns that must be stored rather than guessed from one universal plural suffix.
- `buuggayga → buug`, `dalkeenna → dal`, `ushiinna → ul` — source-attested possessive surfaces.
- `gabadha → gabadh` — currently stored as a documented derivation from the Qaamuus feminine-article rule plus the reviewed `gabadh` lemma; it is marked non-executable and must not be generalized mechanically to unseen words.

`src/regional_variants.py` attaches reviewed regional metadata separately. It distinguishes `preferred`, `co_preferred`, `recognized_variant`, and `candidate_unverified` forms. It does not rewrite user text.

A morphology candidate does not by itself authorize a correction. All current reviewed noun morphology records remain `executable: false` while we expand coverage and validate ambiguity.

## Next implementation stage

Expand reviewed noun morphology with more dictionary families and sentence-context tests, then add verb-surface morphology in the same conservative style. Only after enough reviewed coverage should the project generalize article/plural/possessive rules beyond explicitly stored forms.
