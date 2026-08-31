# Repository Cleanup Audit

This file tracks structural cleanup separately from linguistic development.

Rule: **do not delete or move language data until dependencies and unique evidence are checked.**

## Cleanup completed — 2026-08-31

| Old location/name | New location/name | Result |
|---|---|---|
| `data/lexical/` | `data/vocabulary/` | Renamed to plain-English project terminology |
| `data/lexical/qaamuus_2012_grammar_lexicon_seed.jsonl` | `data/vocabulary/qaamuus_2012_grammar_words.jsonl` | Preserved data, clearer filename |
| `data/lexical/qaamuus_2012_everyday_lexicon_seed.jsonl` | `data/vocabulary/qaamuus_2012_everyday_words.jsonl` | Preserved data, clearer filename |
| `data/lexical/qaamuus_2012_everyday_verb_lexicon_seed.jsonl` | `data/vocabulary/qaamuus_2012_everyday_verbs.jsonl` | Preserved data, clearer filename |
| `lexicon/samples.jsonl` | `data/vocabulary/qaamuus_2012_sample_entries.jsonl` | Unique early sample evidence preserved and merged into the main vocabulary area |
| root `lexicon/` folder | removed after migration | No separate legacy word-data folder needed |
| `src/lexicon.py` | `src/vocabulary.py` | Word lookup uses the clearer project term |
| `tests/test_lexicon_lookup.py` | `tests/test_vocabulary_lookup.py` | Test name matches implementation |
| `docs/LEXICON_SCHEMA.md` | `docs/VOCABULARY_SCHEMA.md` | Documentation name made clearer |
| root `Maahmaahyo.json` | `data/corpus/maahmaahyo.json` | Real Somali text moved out of root into the corpus layer |

## Main structure after cleanup

```text
src/              executable code
rules/            machine-readable language rules
data/vocabulary/  information about words
data/morphology/  reviewed word forms
data/corpus/      real Somali text collections
data/qa/          independent test data
data/sources/     structured source evidence
tests/            automated tests
sources/          human-readable source notes
docs/             project documentation
```

## Items deliberately not renamed

Some internal linguistic data may still use technical words such as `lexical` in a record category or source-evidence filename. Those names can be technically precise and do not control repository navigation. We should only rename them when it improves clarity without obscuring source terminology or breaking provenance.

## Future cleanup

Potential future work:

- reorganize the increasingly large flat `tests/` directory by domain;
- eventually package Python code as `src/somali_grammar/`;
- continue auditing duplicate or obsolete files;
- keep root files minimal.

These should remain behavior-neutral refactors and should always be followed by the full automated test suite.
