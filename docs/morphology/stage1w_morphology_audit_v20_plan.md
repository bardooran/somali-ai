# Stage 1W — morphology audit and v20 plan

## Checkpoint after v19

PR #61 completed the separately staged C2A past-person set for the existing reviewed 11-lemma allowlist. The merge commit is `b85279847233697bf19c808391d8898a30e7b69e`, and the merge commit's `Tests` workflow run `33503938558` completed successfully, including every frozen morphology benchmark through v19.

For the reviewed 11-lemma C2A class cohort, generic class-level coverage now includes all seven persons in both present indicative and past indicative. Both expected syncretisms remain represented as multiple analyses rather than collapsed labels:

- 1sg / 3sg masculine
- 2sg / 3sg feminine

This closes the staged C2A present/past finite-person block. It does **not** mean all Stage 1 morphology is complete.

## Audit result

The next high-value gap is not another finite person cell. The repository's reviewed productive Class-I rule already covers:

- present indicative
- past indicative
- 2sg imperative
- 2pl imperative
- infinitive

The generic C2A class path currently covers only finite present and past. Its reviewed morphophonology file is explicitly scoped to `finite_present_and_past`.

Therefore the next controlled block is **C2A imperative + infinitive/nonfinite morphology** over the already reviewed class cohort.

This gives more Stage 1 value per experiment than adding another tiny finite cell and keeps the work aligned with the project's conservative rule-first architecture.

## v20 pre-answer target selection

Before any v20 answer-form lookup, select three already reviewed C2A lemmas across the existing cohort:

- `aaddi`
- `butaaci`
- `caajisi`

For each lemma, v20 will attempt to score three previously unbenchmarked feature cells:

1. 2sg imperative
2. 2pl imperative
3. infinitive / nonfinite

This creates a maximum nine-row challenge, but only independently attested rows may enter the frozen benchmark. Any unresolved lemma/cell stays unresolved rather than being filled from a pattern.

## Isolation rules

- Target lemmas and requested cells are Git-locked before answer lookup.
- No v20 target surface may be used as runtime development evidence.
- Runtime activation, if justified later, must come from separate class-level development authority.
- No target-specific profiles.
- No open-class generation or reverse suffix stripping.
- No automatic correction authority.
- Mechanical rule-derived candidates are not independent lexical attestations.
- Unknown or unresolved cells remain unjudged.
- Historical v1-v19 benchmarks remain unchanged.

## What comes after v20

After the imperative/infinitive block, Stage 1 should be audited again before selecting the next large morphology unit. Likely remaining categories include broader lemma/class coverage, other verb classes, aspect/negation/mood paradigms, and noun-class/gender-polarity breadth. The next block should be chosen from measured repo gaps rather than assumed in advance.
