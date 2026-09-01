# Stage 1U — generic C2A 3sg masculine past

## Goal

Extend the reviewed, allowlist-only Conjugation-2A class-past analyzer by one separately staged cell: **3sg masculine past**.

This activation occurs only after v18 permanently froze and measured its untouched baseline. PR #54 selected `aammusi` and `abhi` before answer lookup; PR #55 froze `aammusiyay` and `abhiyay` as evaluation-only 3sg-masculine rows; PR #56 locked the untouched historical result.

The untouched v18 result was intentionally subtle:

- surface recognition: 2/2
- lemma/POS/C2A/past recognition: 2/2
- requested `3sg_m` person: 0/2
- deep-feature rows: 0/2
- existing 1sg analysis: 2/2
- full 1sg/3sg-m syncretic ambiguity preserved: 0/2
- master exact recognition: 0/2
- unknown safety: 8/8

The spellings were already available through the live 1sg class rule, but the analyzer did not yet represent the equally valid 3sg-masculine analysis.

## Independent development authority

The runtime rule does **not** come from the v18 target answers.

Martin Orwin, *Colloquial Somali: A Complete Language Course* (1995), general-past C2A table, p. 51, explicitly gives `kariyay` for both:

- 1sg past
- 3sg masculine past

The same discussion states that `y` is inserted between stem-final `i` and `a`. Zorc & Issa independently index `kariyey` as both C2A 1sg and 3sg-masculine past. This evidence was already reviewed before v18 and therefore independently authorizes the syncretic class structure.

The project continues to defer broad `ay/ey` orthographic-variant activation. Stage 1U uses the existing `-ay` policy only.

## Runtime rule

For every lemma in the existing 11-lemma reviewed C2A class-past allowlist:

- 1sg: empty agreement + `ay` -> `-iyay`
- 3sg masculine: empty agreement + `ay` -> the same `-iyay`

Both analyses are retained for the same spelling. One does not replace the other.

The newly authorized 3sg-masculine candidate remains:

- `reviewed_rule_derived`
- forward-generated only
- allowlist-only
- non-corrective

## Safety boundaries

- no target-specific `aammusi` or `abhi` profile
- no learning from the frozen v18 answer rows
- no open-class generation
- no arbitrary `i`-final lemma inference
- no reverse suffix stripping
- no automatic correction authority
- generated candidates are not independent attestation claims
- master exact inventory remains separate from the combined morphology analyzer
- historical v18 metadata remains fixed at 0/2 for `3sg_m` person/deep features even after live improvement
- 3sg feminine remains unjudged at class level and must be staged separately

## Expected live v18 effect

After activation:

- surface recognition remains 2/2
- lemma/POS/C2A/past remain 2/2
- `3sg_m` person improves 0/2 -> 2/2
- deep features improve 0/2 -> 2/2
- both 1sg and 3sg-m analyses are preserved for both target spellings
- master exact remains 0/2
- unknown safety remains 8/8

This is an improvement in **analysis resolution**, not a claim that v18 discovered two previously unknown spellings.
