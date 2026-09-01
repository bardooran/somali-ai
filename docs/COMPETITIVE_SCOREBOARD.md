# Competitive Scoreboard

Last measured: 2026-09-01

This document records reproducible competitive evidence for Somali AI. It is not a marketing scorecard.

**Claim rule:** a project is only called ahead on a metric that has actually been measured on the same frozen benchmark with the same scoring rules. A narrow metric win is not an overall-system win. Passing Somali AI's own tests is never evidence that Somali AI beat another system.

## Current morphology result: independent paradigm challenge v5

v5 is the current strongest directly comparable morphology benchmark because it uses an independent published source family and tests inflected forms with grammatical features rather than only lexical/headword recognition.

Benchmark identity:

- Source: Morgan Nilsson, *Learner's Somali Grammar* (2025), University of Gothenburg course/reference literature.
- 37 positive rows representing 33 unique positive surfaces, plus 8 deterministic unknown probes.
- Frozen manifest: `data/qa/morphology_paradigm_benchmark_v5.jsonl`.
- Frozen manifest git blob SHA: `75f5e3f7b2da98b5b6eef4d2c76a1249596bc1ec`.
- Freeze commit: `a31cf5fb083870abdb94c0d2996963c2851664d9`.
- Pre-freeze Somali AI runtime commit: `da24c0d11d9e538a92e6fbabd0c2ff7d19b39608`.
- GiellaLT commit: `5278929712e9c0c67f254f1a1dc64c80ea7b2b8d`.
- Successful comparison workflow run: `33441911288`.
- 25 of the 33 positive surfaces were absent from Somali AI master recognition before the benchmark freeze.

| Metric | Somali AI | GiellaLT | Leader |
| --- | ---: | ---: | --- |
| Exact positive-surface recognition | 8 / 33 (24.24%) | **25 / 33 (75.76%)** | GiellaLT |
| Lemma recall | 5 / 33 (15.15%) | **24 / 33 (72.73%)** | GiellaLT |
| POS recall | 5 / 33 (15.15%) | **24 / 33 (72.73%)** | GiellaLT |
| Comparable deep morphology features | 0 / 37 (0%) | **19 / 37 (51.35%)** | GiellaLT |
| Syncretic ambiguity preservation | 0% | **100%** | GiellaLT |
| Unknown-word safety | **8 / 8 (100%)** | **8 / 8 (100%)** | Tie |

### v5 unseen/generalization subset

Among the 25 positive surfaces that were absent from Somali AI master recognition before freeze:

- Somali AI recognized **0 / 25**.
- GiellaLT recognized **17 / 25 (68%)**.

This is the clearest current morphology gap. It shows that Somali AI's main problem is not merely storing more forms; it needs stronger generic paradigm generalization from known lemmas and independently supported class rules.

### v5 interpretation

- **GiellaLT leads 5 measured morphology metrics.**
- **Unknown-word safety is tied.**
- **Somali AI has 0 verified metric wins on v5.**
- No global winner is declared because v5 does not combine unlike metrics into an arbitrary overall score.
- The v5 generation diagnostic for GiellaLT matched 5 / 29 eligible rows (17.24%), but v5 did not evaluate a directly comparable general Somali AI generator. Therefore this is **not** a Somali AI generation win.
- v5 is now visible and must be treated as a diagnostic/regression benchmark, not as an unseen benchmark for future competitive claims.

## Historical lexical benchmark: frozen analyzer-blind challenge v4

v4 remains a valid historical lexical/headword benchmark, but it is narrower than v5 and must not be used to claim overall morphology leadership.

Benchmark identity:

- 160 total cases: 144 positive Somali lexical cases + 16 deterministic unknown probes.
- Positive composition: 64 nouns, 64 verbs, 16 numerals.
- All 230 positive surfaces used by v2/v3 were excluded before v4 selection; overlap is zero.
- Frozen manifest SHA-256: `6a61900ea57a2c0f77121eb133195c4cae1246a518624b361d37d924e33cb3ce`.
- Exact frozen benchmark commit: `03f855e4865a21aea60ea570ecb3a35a2a6d10c7`.
- GiellaLT commit: `5278929712e9c0c67f254f1a1dc64c80ea7b2b8d`.
- Successful compiled comparison run: `33437673300`.
- Scope: fresh lexical recognition, coarse POS agreement, and unknown safety; not deep paradigm morphology.

| Metric | Somali AI reviewed-only | Somali AI master exact recognition | Compiled GiellaLT | Leader on v4 |
| --- | ---: | ---: | ---: | --- |
| Positive recognition | 1 / 144 (0.69%) | **62 / 144 (43.06%)** | 58 / 144 (40.28%) | Somali AI master |
| Expected POS coverage | 1 / 144 (0.69%) | **57 / 144 (39.58%)** | 50 / 144 (34.72%) | Somali AI master |
| Exact POS cases | 1 / 144 (0.69%) | **55 / 144 (38.19%)** | 43 / 144 (29.86%) | Somali AI master |
| POS precision | **100.00%** | **91.94%** | 78.13% | Reviewed-only on precision; Somali AI master over broad systems |
| Unknown safety | 16 / 16 (100%) | 16 / 16 (100%) | 16 / 16 (100%) | Tie |

Correct interpretation: Somali AI master led GiellaLT on these **v4 lexical metrics only**. This never proved that Somali AI was a better morphology system overall, and the later, deeper v5 paradigm benchmark shows GiellaLT substantially ahead on inflected-form analysis/generalization.

## Historical analyzer-blind challenge v3

v3 remains a historical diagnostic. It has no principled weighted composite score and no overall winner should be declared.

| Metric | Somali AI reviewed-only | Somali AI master exact recognition | Compiled GiellaLT | Leader on v3 |
| --- | ---: | ---: | ---: | --- |
| Positive recognition | 0 / 110 (0.00%) | 44 / 110 (40.00%) | **53 / 110 (48.18%)** | GiellaLT |
| Expected POS coverage | 0 / 110 (0.00%) | **40 / 110 (36.36%)** | 37 / 110 (33.64%) | Somali AI master |
| Exact POS cases | 0 / 110 (0.00%) | **37 / 110 (33.64%)** | 28 / 110 (25.45%) | Somali AI master |
| POS precision | 0.00% | **85.11%** | 59.68% | Somali AI master |
| Unknown safety | 16 / 16 (100%) | 16 / 16 (100%) | 16 / 16 (100%) | Tie |

## Competitive areas

| Area | Current external reference | Measurement status | Somali AI next proof target |
| --- | --- | --- | --- |
| Morphology / paradigms | GiellaLT | v5: GiellaLT leads 5 metrics, unknown safety tied | Improve generic class-level generalization, then freeze a new unseen cross-source benchmark |
| Lexical/headword recognition | GiellaLT | v4: Somali AI master led aggregate lexical metrics on that frozen draw | Preserve as historical result; do not generalize it to full morphology |
| Grammar / syntax | SLS plus project evidence | Not yet directly comparable | Build frozen sentence-level benchmark before claiming leadership |
| Orthography / spellchecking | GiellaLT | Not yet directly benchmarked | Build typo, real-word error, variant, and false-positive suites |
| Corpus quality / scale | SomNLP | No competitive win established | Measure clean usable text, provenance, duplication, dialect distribution, and license-safe training eligibility |
| Tokenization | SomNLP | Not yet directly benchmarked | Compare fragmentation and compression on held-out Somali text |
| Regional Somali | No established single leader | No competitive benchmark yet | Build region-labeled held-out evaluation without treating variation as error |
| QA / evaluation | No established single leader | Multiple frozen morphology benchmarks exist | Expand independent held-out suites across morphology, grammar, orthography, regional usage, and assistant quality |
| Conversation / reasoning | No comparable system among these repositories | Assistant exists; no fair external win established | Build Somali-first blind evaluation with leakage controls |
| Standalone Somali model | No current project result | Not yet built | Train/fine-tune only after data and evaluation foundations are strong enough |

## Rules for future claims

A statement such as **"Somali AI beat GiellaLT"** is not allowed unless all of the following are true:

1. Both systems ran the same task.
2. Both systems used the same frozen test set.
3. The same scoring rules were applied.
4. The evaluation data was genuinely unseen/frozen before the relevant development work.
5. Raw outputs and exact system versions/commits are reproducible.
6. The result is saved and inspectable.
7. The wording names the exact task/benchmark instead of implying overall superiority.

Raw record counts are not competitive wins. Internal regression-test counts are not competitive wins. Derived sources are not independent confirmation. Benchmark answers must never be copied into runtime as trusted knowledge merely to raise a score. Corpus occurrence is attestation, not grammatical correctness.
