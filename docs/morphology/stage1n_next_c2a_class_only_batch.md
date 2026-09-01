# Stage 1N — next blind C2A class-only batch

## Purpose

Prepare the next cross-lemma generalization experiment without exposing the runtime to the target paradigms.

Stage 1M froze the generic C2A activation cohort to the seven lemmas that existed before v11. Stage 1N therefore can add new reviewed C2A class knowledge while keeping finite generation disabled.

## Class-only source

R. David Zorc, *Somali-English Dictionary*, revised 2019-06-05.

The following entries are explicitly labelled `v2a` in the dictionary:

- `aaddi` — printed dictionary page 2 — `v2a=` — direct; send
- `aammusi` — printed dictionary page 3 — `v2a=` — silence someone; shut someone up
- `abhi` — printed dictionary page 6 — `v2a=` — plead; beseech; admonish
- `afceli` — printed dictionary page 10 — `v2a=cmp` — interpret; translate

Only lemma, verb POS, and C2A class knowledge are admitted in this stage. No finite inflected surface is taken from this source.

## Historical cleanliness

Before Stage 1N was written, repository search returned zero matches for all four target lemmas.

The four lemmas are also required by tests to be disjoint from every frozen positive target in morphology benchmarks v5 through v11.

## Generation boundary

The Stage 1M activation allowlist remains exactly:

`bushi`, `butaaci`, `buubi`, `buufi`, `buuxi`, `caafi`, `caajisi`.

The four Stage 1N lemmas are **not** added to that allowlist. For every present person cell, `generate_class_authorized_conj2_present()` must therefore return no candidate for them.

The class registry still has `generation_enabled=false` and `correction_authority=false`.

## Future benchmark protocol

Only after this class-only checkpoint is merged may a separate source family be searched for explicit finite paradigms for one or more Stage 1N lemmas. Those answer rows must be frozen before any activation cohort is extended.

The future answer source must not be used to alter class membership or to special-case target surfaces. After freeze and baseline measurement, a later activation may admit a preauthorized batch uniformly and measure genuine cross-lemma rule generalization.
