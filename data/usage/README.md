# Natural Somali Usage Layer

This directory contains **bounded natural-language attestation data** for the Somali AI assistant.

It is intentionally separate from:

- `data/vocabulary/` and `data/morphology/` — reviewed language knowledge;
- `data/imported/` — external lexical/grammar candidates;
- `data/qa/` — holdout/evaluation material that must not leak into normal retrieval;
- `data/corpus/` — larger research corpora.

## `external/`

Generated Tier-A usage samples currently come from the audited SomNLP source pipeline:

- Somali Wikipedia (`wikimedia/wikipedia`, config `20231101.so`) — CC-BY-SA-4.0;
- Somali XL-Sum (`csebuetnlp/xlsum`, Somali summaries) — CC-BY-4.0.

Each record keeps its own source, dataset, configuration, license, SomNLP commit, source row, and content hash.

These files are **source-separated** because their licenses differ. There is no single license automatically applied to all usage data.

## Safety meaning

Every external usage record has:

```text
status = external_natural_usage_unreviewed
promotion_allowed = false
correctness_inference_allowed = false
```

A sentence appearing in Wikipedia or XL-Sum means only that it is an attested usage example from that source. It does **not** automatically mean:

- the grammar is correct in every context;
- the wording is preferred for Jigjiga/Hargeisa output;
- a spelling or construction should become an autocorrection rule;
- the assistant should copy the sentence verbatim.

The assistant may use this layer for phrasing/context alongside stronger reviewed linguistic evidence.

## Refresh

`.github/workflows/refresh-tier-a-usage.yml` builds a small bounded sample using the pinned SomNLP downloaders. It runs the full Somali AI test suite before generated usage data can be committed.
