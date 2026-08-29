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
