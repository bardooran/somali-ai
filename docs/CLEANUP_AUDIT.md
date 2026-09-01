# Repository Cleanup Audit

This file tracks structural cleanup separately from linguistic development.

Rule: **do not delete or move language data until dependencies and unique evidence are checked.**

## Cleanup completed — 2026-09-01

### Competitive-evidence safety pass

- Corrected `docs/COMPETITIVE_SCOREBOARD.md`, which still described v5 as "freeze in progress" after the benchmark had already completed.
- Recorded the measured v5 result: GiellaLT leads 5 directly comparable morphology metrics; unknown-word safety is tied; Somali AI has 0 metric wins on v5.
- Preserved the historical v4 lexical result but narrowed its interpretation explicitly: it is a lexical/headword benchmark result, not proof of overall morphology leadership.
- Added `docs/BENCHMARK_CLAIMS_POLICY.md` so internal test counts, development probes, and narrow benchmark wins cannot be reported as broader competitive wins.
- Explicitly marked inspected frozen benchmarks as diagnostic/regression data for future development; new unseen claims require newly frozen evaluation data.
- Added `tests/test_benchmark_runtime_isolation.py`, a CI guard that scans production `src/` modules and fails if they directly read `data/qa/` or import benchmark/challenge/paradigm evaluation modules.
- The guard deliberately exempts benchmark/evaluation tooling itself, because those programs must read frozen manifests in order to score them.
- The guard includes coverage assertions for core morphology runtime files so those files cannot silently fall out of protection because of a naming change.
- No morphology runtime rules, reviewed evidence, benchmark manifests, or language data were changed in this pass.

### Unused-file audit pass

- Investigated `tools/importers/somnlp_extract.py` as a possible orphan because no current workflow calls it and the live Tier-A refresh uses `tools/importers/somnlp_tier_a_usage.py`.
- A trial deletion failed CI because `tests/test_somnlp_importer.py` imports and validates this module directly. The file was restored unchanged and is therefore retained.
- Kept the GiellaLT, SLS, master-data, and Tier-A importer scripts because current GitHub Actions workflows call them directly.
- Historical benchmark manifests and reports were deliberately kept: old benchmark files are part of the reproducible evidence trail, not disposable clutter.
- No file was deleted in this audit unless its dependency status could be proven safe by tests.

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

- audit scoreboard/status documents for stale benchmark states when a new benchmark finishes;
- consider a manifest registry if benchmark count grows enough that filename-based evaluation-tool classification becomes hard to maintain;
- reorganize the increasingly large flat `tests/` directory by domain;
- eventually package Python code as `src/somali_grammar/`;
- continue auditing duplicate or obsolete files;
- keep root files minimal.

These should remain behavior-neutral refactors and should always be followed by the full automated test suite when code or runtime-sensitive files are touched.
