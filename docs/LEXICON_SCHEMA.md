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
12. Verb person must not be inferred from an ending when the paradigm is syncretic. Forms such as `cunaa`, `cunay`, `cuntaa`, and `cuntay` retain all source-supported person possibilities until sentence context resolves them.
13. Irregular/suppletive verbs must be stored explicitly. The `dheh` family uses multiple stems (`dheh`, `iraah-/tiraah-/yiraah-/niraah-`, `iri/tiri/yiri/niri`, `oran-`) and must not be forced through an ordinary suffix-only template.
14. Regional morphology provenance remains separate from source paradigms. Jigjiga-preferred `yidhi`, `tidhi`, and `odhan` are native-reviewed project evidence; they are not falsely attributed to a Qaamuus table that lists `yiri`, `tiri`, and `oran` in the corresponding source paradigm.

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
- `data/lexical/qaamuus_2012_everyday_lexicon_seed.jsonl` — ordinary vocabulary and lexical families mined from dictionary entries.
- `data/morphology/qaamuus_2012_reviewed_noun_forms.jsonl` — reviewed inflected noun surface forms linked to candidate lemmas and grammatical features.
- `data/morphology/qaamuus_2012_reviewed_verb_forms.jsonl` — reviewed verb surfaces for ordinary and irregular paradigms, with tense/aspect/person ambiguity and regional provenance preserved.

`src/lexicon.py` searches both lexical datasets by default and attaches reviewed morphology and regional evidence independently.

## Current reviewed lookup prototype

`src/lexicon.py` preserves multiple dictionary analyses for homographs rather than selecting one without sentence context. Current exact-headword examples include three analyses for `ka`, two for `kee`, masculine/feminine analyses for `inan`, noun/verb analyses for `kor`, and noun/verb analyses for `gabay`.

`src/morphology_candidates.py` provides the safe surface-form-to-lemma bridge. It performs exact matching against both reviewed noun and verb morphology records; it still performs no open-ended suffix stripping or productive conjugation guessing.

Current noun examples include `buugga → buug`, `marada → maro`, `kabo → kab`, `gacmo → gacan`, `mindiyo → mindi`, `buuggayga → buug`, and the reviewed derivation `gabadha → gabadh`.

Current verb examples include:

- `cunaa → cun` with possible persons 1sg / 3sg masculine.
- `cuntaa → cun` with possible persons 2sg / 3sg feminine.
- `cunay → cun` with possible persons 1sg / 3sg masculine.
- `cuntay → cun` with possible persons 2sg / 3sg feminine.
- `cunnaa`, `cuntaan`, `cunaan`, `cunnay`, `cunteen`, `cuneen` with explicit plural-person evidence.
- `cunin → cun` as a context-required negative form with several possible grammatical functions.
- `dheh`, `dhaha`, `dhihi`, `oran`, `iraahdaa`, `tiraahdaa`, `yiraahdaa`, `niraahdaa`, `iri`, `tiri`, `yiri`, `niri` → the irregular lemma family `dheh`.
- Jigjiga-preferred `yidhi`, `tidhi`, and `odhan` → `dheh`, stored as native-reviewed/regional evidence rather than rewritten source evidence.

`src/regional_variants.py` attaches reviewed regional metadata separately. It distinguishes `preferred`, `co_preferred`, `recognized_variant`, and `candidate_unverified` forms. It does not rewrite user text.

A morphology candidate does not by itself authorize a correction. All current reviewed morphology records remain `executable: false` while coverage and contextual disambiguation grow.

## Next implementation stage

Expand the reviewed verb layer beyond `cun` and `dheh` with representative regular conjugation classes and high-value irregular verbs. Then add sentence-context resolution so subject pronouns/focus markers can narrow person ambiguity without treating object clitics as agreement controllers. Continue enlarging noun/lexical coverage in parallel.
