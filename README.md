# Somali Grammar

A Somali grammar project focused on two goals:

1. Help Somali speakers improve spelling and grammar.
2. Help new learners understand Somali grammar through clear explanations and examples.

## Current scope

This repository is for the Somali grammar foundation only. It is not the Contexto-style game and it is not the Somali chatbot/model repository.

We are starting with a rule-based and linguistic foundation before adding product UI or model training.

## Planned components

- `rules/` — machine-readable Somali grammar and spelling rules
- `examples/` — correct/incorrect sentence examples used to validate rules
- `tests/` — test cases for grammar behavior
- `sources/` — notes about linguistic sources and reusable open-source projects
- `docs/` — architecture and project decisions

## Technical direction

We will evaluate existing Somali linguistic resources instead of rebuilding everything from zero. The main candidates currently being studied are GiellaLT `lang-som` for Somali morphology/proofing technology and Somali Language Standard (SLS) as a structured linguistic reference.

No large AI model is being trained in this repository at this stage.

## Status

Early foundation / planning stage.
