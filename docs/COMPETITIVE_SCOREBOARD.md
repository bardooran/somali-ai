# Competitive Scoreboard

Last measured: 2026-08-31

This document records reproducible competitive evidence for Somali AI. It is not a marketing scorecard. A project is only called ahead on a metric that has actually been measured on the same frozen benchmark or on another directly comparable evaluation.

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
| Positive recognition | 0 / 110 (0.00%) | 44 / 110 (40.00%) | 53 / 110 (48.18%) | GiellaLT |
| Expected POS coverage | 0 / 110 (0.00%) | 40 / 110 (36.36%) | 37 / 110 (33.64%) | Somali AI master |
| Exact POS cases | 0 / 110 (0.00%) | 37 / 110 (33.64%) | 28 / 110 (25.45%) | Somali AI master |
| POS precision | 0.00% | 85.11% | 59.68% | Somali AI master |
| Unknown safety | 16 / 16 (100%) | 16 / 16 (100%) | 16 / 16 (100%) | Tie |

No overall winner is declared. v3 has no principled weighted composite score. The current morphology target is precise: close the **9-case raw recognition gap** while preserving Somali AI master's higher POS precision and 100% unknown safety.

The runtime distinction is intentional. Reviewed-only data remains the conservative correction authority. Master-store records may be recognized at trusted, supported, or provisional confidence, but provisional recognition does not authorize correction.

## Competitive areas

| Area | Current external reference | Measurement status | Somali AI next proof target |
| --- | --- | --- | --- |
| Morphology / lexical breadth | GiellaLT | Active; v1, v2, v3 harnesses exist | Beat raw recognition while retaining precision and unknown safety |
| Grammar / syntax | SLS plus project evidence | Not yet a directly comparable executable benchmark | Build a frozen sentence-level benchmark before claiming leadership |
| Orthography / spellchecking | GiellaLT | Not yet directly benchmarked | Build typo, real-word error, variant, and false-positive suites |
| Corpus quality / scale | SomNLP | Source corpus measurements exist; not a Somali AI win claim | Measure clean usable text, provenance, duplication, dialect distribution, and license-safe training eligibility |
| Tokenization | SomNLP | Not yet directly benchmarked by Somali AI | Compare Somali words/token, fragmentation, names, clitics, morphology, and compression on held-out Somali text |
| Regional Somali | No established single leader | Foundation exists; no competitive benchmark yet | Build region-labeled held-out evaluation without treating variation as error |
| QA / evaluation | No established single leader | Multiple frozen morphology challenges already exist | Expand independent held-out suites across grammar, orthography, regional usage, and assistant quality |
| Conversation / reasoning | No comparable system among these repositories | Assistant exists; live-model semantic eval awaits credentials | Build Somali-first blind human/LLM-judge evaluation with leakage controls |
| Standalone Somali model | No current winner among these four projects | Not yet built | Train/fine-tune only after data and evaluation foundations are strong enough |

## Rules for future claims

Raw record counts are not competitive wins. Derived sources are not counted as independent confirmation. Benchmark answers must never be copied into runtime as trusted knowledge merely to raise the score. Corpus occurrence is attestation, not grammatical correctness. Every competitive result should name the benchmark identity, exact repository commits, metric definitions, and known limitations.
