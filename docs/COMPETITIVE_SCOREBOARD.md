# Competitive Scoreboard

Last measured: 2026-08-31

This document records reproducible competitive evidence for Somali AI. It is not a marketing scorecard. A project is only called ahead on a metric that has actually been measured on the same frozen benchmark or on another directly comparable evaluation.

## Morphology: frozen analyzer-blind challenge v4

Benchmark identity:

- 160 total cases: 144 positive Somali lexical cases + 16 deterministic unknown probes.
- Positive composition: 64 nouns, 64 verbs, 16 numerals.
- All 230 positive surfaces used by v2/v3 were excluded before v4 selection; overlap is zero.
- Frozen manifest SHA-256: `6a61900ea57a2c0f77121eb133195c4cae1246a518624b361d37d924e33cb3ce`.
- Exact frozen benchmark commit: `03f855e4865a21aea60ea570ecb3a35a2a6d10c7`.
- Selection was analyzer-blind and frozen before v4 runtime evaluation.
- GiellaLT was compiled from commit `5278929712e9c0c67f254f1a1dc64c80ea7b2b8d`.
- Successful compiled comparison run: GitHub Actions `33437673300`.
- Normal Somali AI CI for the benchmark harness also passed: run `33437673310`, 992 tests.
- Scope is fresh lexical recognition, coarse part-of-speech agreement, and unknown safety. It is not a complete morphology-quality score.

| Metric | Somali AI reviewed-only | Somali AI master exact recognition | Compiled GiellaLT | Current leader |
| --- | ---: | ---: | ---: | --- |
| Positive recognition | 1 / 144 (0.69%) | **62 / 144 (43.06%)** | 58 / 144 (40.28%) | Somali AI master |
| Expected POS coverage | 1 / 144 (0.69%) | **57 / 144 (39.58%)** | 50 / 144 (34.72%) | Somali AI master |
| Exact POS cases | 1 / 144 (0.69%) | **55 / 144 (38.19%)** | 43 / 144 (29.86%) | Somali AI master |
| POS precision | **100.00%** | **91.94%** | 78.13% | Reviewed-only on precision; Somali AI master leads broad systems |
| Unknown safety | 16 / 16 (100%) | 16 / 16 (100%) | 16 / 16 (100%) | Tie |

The reviewed-only runtime is deliberately tiny and conservative, so its 100% POS precision is not a breadth claim. The directly useful competitive comparison is master recognition vs compiled GiellaLT: Somali AI master leads every aggregate positive metric on this untouched v4 draw while both systems reject all unknown probes.

### v4 category diagnostics

| Category | Metric | Somali AI master | Compiled GiellaLT | Leader |
| --- | --- | ---: | ---: | --- |
| Noun (64) | Recognition | **10 / 64 (15.63%)** | 6 / 64 (9.38%) | Somali AI |
| Noun | Expected POS coverage | **7 / 64 (10.94%)** | 0 / 64 (0.00%) | Somali AI |
| Noun | Exact POS | **6 / 64 (9.38%)** | 0 / 64 (0.00%) | Somali AI |
| Noun | POS precision | **70.00%** | 0.00% | Somali AI |
| Verb (64) | Recognition | 44 / 64 (68.75%) | 44 / 64 (68.75%) | Tie |
| Verb | Expected POS coverage | 43 / 64 (67.19%) | 43 / 64 (67.19%) | Tie |
| Verb | Exact POS | 42 / 64 (65.63%) | **43 / 64 (67.19%)** | GiellaLT |
| Verb | POS precision | 97.73% | **100.00%** | GiellaLT |
| Numeral (16) | Recognition | 8 / 16 (50.00%) | 8 / 16 (50.00%) | Tie |
| Numeral | Expected POS coverage | 7 / 16 (43.75%) | 7 / 16 (43.75%) | Tie |
| Numeral | Exact POS | **7 / 16 (43.75%)** | 0 / 16 (0.00%) | Somali AI |
| Numeral | POS precision | **87.50%** | 46.67% | Somali AI |

v4 changes the immediate morphology target. The prior v3 raw-recognition deficit should **not** be answered by adding benchmark words: on a fresh disjoint draw Somali AI master already leads GiellaLT 62–58 overall and 10–6 on nouns. The harder next proof is paradigm-level morphology: held-out surface analysis and generation with lemma/person/tense/mood/class features, ambiguity handling, and overgeneration safety.

Important limitation: v2, v3, and v4 are disjoint selections but come from the same pinned Qaamuus source family. They are strong leakage-controlled lexical tests, not fully source-independent morphology evidence. The next morphology benchmark should therefore use an independent published source and report pre-freeze runtime overlap explicitly.

## Morphology: independent paradigm challenge v5 (freeze in progress)

Source family: Morgan Nilsson, *Learner's Somali Grammar* (2025), University of Gothenburg course/reference literature. The source is independent of the Qaamuus family used for v2-v4. v5 is designed to test explicit inflected surface forms with grammatical features rather than headword recognition. Its freeze protocol must record pre-freeze overlap with the Somali AI reviewed runtime and master recognition index, and the unseen subset must be scored separately.

No v5 winner is recorded until the manifest is frozen and both systems have been evaluated unchanged.

## Morphology: frozen analyzer-blind challenge v3

Benchmark identity:

- 126 total cases: 110 positive Somali lexical cases + 16 unknown probes.
- Positive composition: 48 nouns, 48 verbs, 8 numerals, 6 adjectives.
- Zero positive overlap with challenge v2.
- Frozen manifest SHA-256: `7222ef7a4e4f0c9b960b5feece50aaba11737dc7f3265040cfdac6a3e99ffd6c`.
- Selection was frozen before the master-recognition bridge was evaluated.
- GiellaLT was compiled from commit `5278929712e9c0c67f254f1a1dc64c80ea7b2b8d`, which was also the live `bardooran/GiellaLT` `main` commit when this result was checked on 2026-08-31.
- Scope is lexical recognition, coarse part-of-speech agreement, and unknown safety. It is not a complete morphology-quality score.

| Metric | Somali AI reviewed-only | Somali AI master exact recognition | Compiled GiellaLT | Current leader |
| --- | ---: | ---: | ---: | --- |
| Positive recognition | 0 / 110 (0.00%) | 44 / 110 (40.00%) | **53 / 110 (48.18%)** | GiellaLT |
| Expected POS coverage | 0 / 110 (0.00%) | **40 / 110 (36.36%)** | 37 / 110 (33.64%) | Somali AI master |
| Exact POS cases | 0 / 110 (0.00%) | **37 / 110 (33.64%)** | 28 / 110 (25.45%) | Somali AI master |
| POS precision | 0.00% | **85.11%** | 59.68% | Somali AI master |
| Unknown safety | 16 / 16 (100%) | 16 / 16 (100%) | 16 / 16 (100%) | Tie |

No overall winner is declared. v3 has no principled weighted composite score. The later v4 result is the current lexical benchmark; v3 remains useful as a historical disjoint diagnostic.

The runtime distinction is intentional. Reviewed-only data remains the conservative correction authority. Master-store records may be recognized at trusted, supported, or provisional confidence, but provisional recognition does not authorize correction.

## Competitive areas

| Area | Current external reference | Measurement status | Somali AI next proof target |
| --- | --- | --- | --- |
| Morphology / lexical breadth | GiellaLT | v4: Somali AI master leads aggregate lexical metrics; no full morphology winner | Freeze independent cross-source paradigm analysis/generation benchmark |
| Grammar / syntax | SLS plus project evidence | Not yet a directly comparable executable benchmark | Build a frozen sentence-level benchmark before claiming leadership |
| Orthography / spellchecking | GiellaLT | Not yet directly benchmarked | Build typo, real-word error, variant, and false-positive suites |
| Corpus quality / scale | SomNLP | Source corpus measurements exist; not a Somali AI win claim | Measure clean usable text, provenance, duplication, dialect distribution, and license-safe training eligibility |
| Tokenization | SomNLP | Not yet directly benchmarked by Somali AI | Compare Somali words/token, fragmentation, names, clitics, morphology, and compression on held-out Somali text |
| Regional Somali | No established single leader | Foundation exists; no competitive benchmark yet | Build region-labeled held-out evaluation without treating variation as error |
| QA / evaluation | No established single leader | Four frozen morphology benchmark generations now exist | Expand independent held-out suites across morphology, grammar, orthography, regional usage, and assistant quality |
| Conversation / reasoning | No comparable system among these repositories | Assistant exists; live-model semantic eval awaits credentials | Build Somali-first blind human/LLM-judge evaluation with leakage controls |
| Standalone Somali model | No current winner among these four projects | Not yet built | Train/fine-tune only after data and evaluation foundations are strong enough |

## Rules for future claims

Raw record counts are not competitive wins. Derived sources are not counted as independent confirmation. Benchmark answers must never be copied into runtime as trusted knowledge merely to raise the score. Corpus occurrence is attestation, not grammatical correctness. Every competitive result should name the benchmark identity, exact repository commits, metric definitions, and known limitations.
