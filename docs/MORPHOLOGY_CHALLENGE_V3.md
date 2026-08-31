# Morphology Challenge v3

v3 is the next protected holdout for morphology breadth work. It must be frozen before any new provisional lexical-recognition layer is built from external evidence.

## Source and fairness

- Pinned source: `bardooran/goobolabs` at `737cf848bfa8291d5580f5c34db04daef858c955`
- Collection: `resources/qaamuus/`
- New fixed seed: `somali-ai-morphology-challenge-v3-2026-08-31`
- Same coarse-POS quotas as v2: 48 nouns, 48 verbs, 16 adjectives, 8 numerals
- 16 deterministic explicit nonsense safety probes
- Dictionary definitions are not copied.

The v3 generator excludes **every positive v2 surface before hashing**, so v2 and v3 cannot share positive test words. It does not import or call Somali AI morphology analyzers, GiellaLT, HFST, or analyzer output.

## Purpose

v2 has now been evaluated and may be used only as diagnostic evidence about the current system; its exact words must not be directly promoted while it remains a reported holdout. v3 is frozen before the next breadth-expansion implementation so that the new layer can be evaluated on unseen words.

The upcoming breadth layer should remain separate from trusted reviewed morphology. External cross-source agreement may support **provisional recognition**, but it must not silently become autocorrection, grammar authority, or a claimed reviewed paradigm.

## Freeze protocol

1. Commit the v3 selection code, tests, and artifact-only workflow.
2. Run it against the pinned source and verify zero positive overlap with v2.
3. Commit the exact generated v3 JSONL, metadata, and SHA-256.
4. Only after that commit may the provisional breadth layer be implemented or v3 scored.

If v3 is later used for direct promotion/training, it must be retired as a holdout and replaced by another frozen challenge first.
