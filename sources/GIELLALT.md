# GiellaLT Somali source audit

## Status

- Upstream project: `giellalt/lang-som`
- Local mirror used for this audit: `bardooran/GiellaLT`
- Audited mirror commit: `5278929712e9c0c67f254f1a1dc64c80ea7b2b8d`
- License: GNU LGPL v3 (repository-level license; preserve per-file notices where present)
- Role in this project: external evidence and candidate discovery, not automatic authority
- Audit date: 2026-08-31

The mirror commit is pinned because the upstream repository can continue changing. Re-imports must record the exact source commit used.

## Core rule

A GiellaLT analysis is evidence that a form or analysis exists in that project. It is **not** enough by itself to mark a Somali form correct, preferred, or safe for autocorrection.

Promotion path:

`GiellaLT candidate -> provenance preserved -> compare with independent evidence -> review regional/context status -> project reviewed data -> executable rule only when justified`

## High-value Somali source files

### Collect as candidates

- `src/fst/morphology/stems/nouns.lexc`
  - large Somali noun inventory
  - declension assignment and gender information
  - useful for noun morphology and gender-polarity research
- `src/fst/morphology/stems/verbs.lexc`
  - large Somali verb inventory
  - useful class/transitivity assignments
- `src/fst/morphology/stems/adjectives.lexc`
  - adjective/state-word inventory and continuation classes
  - plain lexical rows are collected as non-promoting candidates; tagged irregular rows remain excluded from the simple importer
- `src/fst/morphology/affixes/verbs.lexc`
  - person, number, gender, tense, progressive, reduced and relative morphology
- `src/fst/morphology/affixes/irregularverbs.lexc`
  - high-value irregular systems including `iman`, `aqoon`, `odhan`, and `ah`
- `src/fst/morphology/affixes/nouns.lexc`
  - noun inflection classes, definiteness, case, number and gender-polarity behavior
- `src/fst/morphology/stems/numerals.lexc`
  - cardinal and ordinal lexical evidence
- `src/fst/morphology/phonology.twolc`
  - Somali morphophonological evidence such as `arag -> arkaa/aragtaa`, noun alternations and reduplication

### Review carefully before promotion

- `src/fst/morphology/stems/pronouns.lexc`
  - useful subject/object/clitic analyses
  - file contains explicit TODO warnings, especially around subject clitics and negative forms
- `src/fst/morphology/stems/subjunctions.lexc`
  - useful `baa`, `ayaa`, `waxa`, `waa`, `in`, `oo`, `ee`, `ma`, etc.
  - several analyses are marked TODO or uncertain
- `src/fst/morphology/stems/adpositions.lexc`
  - valuable `u/ku/ka/la` and fused object/adposition material
  - some combinations are explicitly marked TODO
- `src/fst/morphology/clitics.final.lexc`
  - `-na`, `-se`, `-ba`, `-ee` and focus attachment
- `src/cg3/disambiguator.cg3`
  - contains genuine Somali agreement, focus, adposition, reduced/relative and clause-disambiguation work
  - use as research/QA evidence; do not port rules blindly

## Known useful cross-checks

The audited source independently contains or discusses forms/analyses already important to this project, including:

- `jidh` as a feminine noun entry
- `odhan` with northern-style forms including `yidhi`, `tidhi`, and imperative `dheh`
- subject clitics/markers such as `aan`, `aad`, `uu`, `ay`, plus 2pl analyses that must remain context-sensitive
- object `idin`
- focus systems for `baa/ayaa` and `waxa`
- number spellings such as `toddoba`, `siddeed`, `toddobaatan`, `siddeetan`
- ordinal forms including `kowaad`, `labaad`, `saddexaad`, `afraad/afaraad`, `siddeedaad`, `tobnaad/tobanaad`, and others
- northern `-ay-` versus other `-ey-` variation notes

These matches increase confidence only when combined with independent evidence already held by this project.

## Do not import as Somali evidence

The repository contains inherited/template material from other GiellaLT languages. The audit found concrete examples:

- `tools/grammarcheckers/grammarchecker.cg3` is largely a generic/template grammar checker rather than a trustworthy Somali rule set.
- `tools/grammarcheckers/errors.source.xml` contains Sámi examples.
- `tools/grammarcheckers/errors-so.ftl` contains placeholder Somali messages.
- `src/fst/transcriptions/transcriptor-clock-digit2text.lexc` identifies itself as a Plains Cree clock and says it was not native-speaker checked.
- `src/fst/transcriptions/transcriptor-date-digit2text.lexc` contains non-Somali date/month output.
- `src/fst/transcriptions/transcriptor-numbers-digit2text.lexc` contains non-Somali number words.
- `src/cg3/dependency.cg3` identifies itself as deprecated Faroese dependency grammar.
- `tools/analysers/test/corpus.txt` explicitly says it should be replaced and currently contains Sámi text.
- sample speller tests and typo files include non-Somali data.

These files must not enter Somali training, QA, lexical, or grammar datasets simply because they live inside `lang-som`.

## Legacy/generated areas

- `src/fst/morphology/generated_files/` is generated build output. GiellaLT itself says these files can be deleted and should not be edited. Skip them.
- `src/fst/morphology/incoming/` is a source-staging area, not authoritative compiled linguistic data. Treat only as provenance/research material.
- top-level `hfst/` contains older infrastructure and template residue. The current `src/fst/` tree is the preferred source family for this project.

## Known limitations in the real Somali core

The real Somali morphology is valuable but unfinished. The source contains explicit TODOs about tone, pronouns, several paradigms, subordinate/reduced forms and analyzer behavior. Its own TODO also notes analysis problems for forms such as `ayuu` because of suprasegmental/tone handling.

Therefore absence from GiellaLT does not prove a form is wrong, and presence does not automatically prove a form is project-approved.

## Current lexical importer scope

The conservative lexical importer supports clean candidate extraction from:

- `src/fst/morphology/stems/nouns.lexc`
- `src/fst/morphology/stems/verbs.lexc`
- `src/fst/morphology/stems/numerals.lexc`
- `src/fst/morphology/stems/adjectives.lexc`

It skips entries carrying markers such as `Err/Orth`, `Use/NG`, or `TODO`, and its simple parser also excludes tagged/fused lexical rows. It does not generate inflected forms and does not write into reviewed vocabulary/morphology directories.

The imported inventory feeds `src.morphology_competition`, which measures reviewed Somali AI morphology against the broader candidate inventory and builds a cross-source review backlog. Candidate breadth is never treated as reviewed coverage.

Future import stages may add structured extraction for affix paradigms, irregular verbs, clitics and other syntax only after separate parser/tests are designed for those formats.
