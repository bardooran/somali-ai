# Morphology Challenge v4

Challenge v4 is the next frozen, analyzer-blind morphology holdout used to measure Somali AI against compiled GiellaLT before the next morphology breadth pass.

## Frozen identity

- Source: pinned Qaamuus material in `bardooran/goobolabs` at commit `737cf848bfa8291d5580f5c34db04daef858c955`.
- Selection seed: `somali-ai-morphology-challenge-v4-2026-08-31`.
- Manifest: `data/qa/morphology_challenge_v4.jsonl`.
- SHA-256: `6a61900ea57a2c0f77121eb133195c4cae1246a518624b361d37d924e33cb3ce`.
- 160 total cases: 144 positive lexical cases + 16 deterministic nonsense safety probes.
- Positive quotas: 64 nouns, 64 verbs, 16 numerals.
- Zero positive surface overlap with v2 or v3; 230 prior positive surfaces were excluded before selection.
- No adjectives: v2 and v3 already consumed all 22 eligible adjective headwords in the pinned source.
- Definitions are not copied into the benchmark.

The freeze generator does not import or call Somali AI analyzers, master recognition, GiellaLT, or HFST. The exact manifest was committed by GitHub Actions only after targeted freeze tests, disjointness checks, and the full project test suite succeeded.

## What v4 measures

v4 carries forward the v3 scoring contract: positive lexical recognition, expected coarse POS coverage, exact coarse POS cases, POS precision, and unknown safety. Per-POS diagnostics are reported for noun, verb, and numeral cases.

These metrics do **not** constitute a complete morphology score. They do not by themselves measure paradigm generation quality, allomorphy, contextual syntax, correction quality, dialect preference, or semantic validity. No arbitrary weighted composite winner is declared.

## Leakage rule

The v4 labels are evaluation-only. A form appearing in v4 must never be copied into trusted runtime data merely because the benchmark reveals its expected category. Future breadth improvements must come from independent evidence or already-reviewed productive morphology. Recognition derived from a reviewed rule must preserve provenance and must not automatically gain correction authority.

The intended experiment is therefore:

1. Measure Somali AI reviewed-only, Somali AI master recognition, and compiled GiellaLT on the frozen v4 manifest.
2. Improve generic morphology from evidence independent of v4.
3. Re-run the unchanged v4 manifest.
4. Report pre/post changes, including precision and unknown-safety regressions, not just recognition gains.
