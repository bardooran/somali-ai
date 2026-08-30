# Grammar reference layer

This directory stores structured Somali grammar evidence used by the project.

The files are intentionally separated by construction or grammatical function so that the checker does not confuse surface similarity with grammatical role. For example, `idin` can be an object clitic, subject agreement belongs to the subject/agent, focus particles interact with word order, and negation changes verb morphology according to the paradigm.

## Evidence and execution

A record in this directory is not automatically an autocorrection rule.

- `descriptive` records preserve a source-backed grammatical pattern.
- `provisional` records have stronger project support but still require care before automatic correction.
- `context_required` records depend on syntax, discourse, dialect/register, or unresolved evidence.

Automatic rewriting should be limited to rules that have been explicitly promoted as safe. Context-sensitive grammar should instead be analyzed or flagged for review.

## Current layers

- `personal_pronouns.jsonl` — independent pronouns and clitic evidence.
- `subject_verb_agreement.jsonl` — reviewed agreement reference forms.
- `focus_particle_subject_clitic.jsonl` — `baa/ayaa` and related subject-clitic/focus evidence.
- `object_clitic_subject_agreement.jsonl` — constructions where object clitics such as `idin` must remain separate from the agreement controller.
- `special_clitics.jsonl` — context-sensitive `is` reflexive/reciprocal evidence and `la` impersonal constructions, including reviewed `la + idin` examples.
- `waydinkii_construction.jsonl` — separate context-sensitive `waydinkii` evidence.
- `negation_patterns.jsonl` — paradigm-sensitive verb negation and conjugation-class samples.

## Safety principle

Somali grammar must be modeled construction-first. Do not infer a correction from one token alone when its grammatical role depends on the sentence around it.
