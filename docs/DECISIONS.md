# Project Decisions

## 2026-08-30 — Grammar-first scope

The repository focuses on Somali grammar and writing. Contexto-style gameplay and chatbot/model training are outside the current scope.

## 2026-08-30 — Two user groups

The grammar product should support both:

- Somali speakers who want to improve their written Somali.
- People learning Somali as a new language.

## 2026-08-30 — Source-backed rules

Grammar and orthography rules should not be invented from intuition alone. Each machine-readable rule should carry provenance where possible.

## 2026-08-30 — Provisional SLS rules

Somali Language Standard (SLS) is useful as a structured linguistic reference, but SLS currently says no standard is Stable. Rules derived from it remain provisional until reviewed against additional sources and real Somali usage.

## 2026-08-30 — Context-sensitive corrections

A grammar checker must distinguish safe deterministic corrections from ambiguous forms. Ambiguous contractions such as `bay` must not be automatically expanded without enough grammatical context.

## 2026-08-30 — Source conflicts are not errors

When reliable project sources use different Somali forms, the checker must not choose one as wrong automatically. Conflicts such as `Jimce` / `Jimco` and `Jannaayo` / `Janaayo` are stored as reference variants until broader linguistic validation provides usage guidance.

## 2026-08-30 — SomKit role

SomKit is a secondary lexical, learning, and variant-evidence source. Its vocabulary, calendar terms, phrases, and related material can support research and examples, but it does not override grammar sources automatically.

## 2026-08-30 — Lexin pipeline role

The Swedish–Somali Lexin data is used as bilingual lexical and usage evidence. Somali material in `TargetLang` can contribute translations, examples, idioms, compounds, comments, synonyms, and explanations. Swedish `BaseLang` grammatical type and inflection data must not be interpreted as Somali morphology.

## 2026-08-30 — Multi-source grammar pipeline

The grammar foundation combines sources by role instead of mixing them into one undifferentiated dataset:

- SLS: grammar, orthography, dictionary evidence, and descriptive lexical codes.
- GiellaLT: Somali morphology and proofing technology.
- Lexin: bilingual Somali vocabulary and usage/context evidence.
- SomKit: supplemental vocabulary, learning content, and variant evidence.
- Project tests: enforce safe behavior before information becomes an automatic correction.

Every imported fact should retain provenance and source role.

## 2026-08-30 — Overlapping corrections

Automatic fixes must not apply multiple edits to the same text span. When safe findings overlap, the current checker prefers the longer, more specific span and applies only one compatible correction.
