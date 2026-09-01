# Stage 1T — generic C2A 1sg past

## Goal

Extend the already-reviewed, allowlist-only Conjugation-2A class-past analyzer by one cell: **1sg past**.

This stage occurs only after v17 permanently froze and measured its untouched baseline. PR #50 selected `aaddi`, `afceli`, and `buufi` before answer lookup; PR #51 froze the attested rows; PR #52 locked the untouched historical result at 0/2 for `aaddiyay` and `buufiyay`, with `afceli` unresolved and 8/8 unknown safety.

The v17 answer rows are evaluation-only and do not authorize this rule.

## Independent development authority

Martin Orwin, *Colloquial Somali: A Complete Language Course* (1995), general-past C2A table, p. 51, explicitly gives the `kari` paradigm with:

- 1sg `kariyay`
- 3sg masculine `kariyay`
- 1pl `karinnay`
- 2sg `karisay`
- 2pl `kariseen`
- 3pl `kariyeen`

The same discussion states that `y` is inserted between stem-final `i` and `a`. This independently authorizes the 1sg structure as empty person agreement + past `ay`, using the already-reviewed `i_vowel_glide` process.

Zorc & Issa's Somali Reference Grammar independently indexes `kariyey` as both C2A 1sg past and 3sg masculine past, corroborating the syncretism. The project keeps the broad `ay/ey` orthographic-variant question deferred; this stage activates only the existing `-ay` policy.

Neither `aaddiyay` nor `buufiyay` is used as development evidence.

## Runtime scope

The class-past policy now authorizes:

- 1sg: empty agreement + `ay` -> `-iyay` through `i_vowel_glide`
- 1pl: `n + ay` -> `-innay`
- 2sg: `t + ay` -> `-isay`
- 2pl: `s + een` -> `-iseen`
- 3pl: empty agreement + `een` -> `-iyeen`

The same 11 reviewed C2A class lemmas receive the rule uniformly. No target-specific profile is added.

## Safety boundaries

- no open-class generation
- no inference from arbitrary `i`-final spelling
- no reverse suffix stripping
- no automatic correction authority
- generated forms are `reviewed_rule_derived` analysis candidates, not independent attestation claims
- `afceli` remains unresolved as v17 1sg attestation evidence even though the generic mechanics can produce `afceliyay`
- 3sg masculine remains a separately staged runtime cell even though independent evidence documents its syncretism with 1sg
- 3sg feminine also remains unjudged at class level
- frozen v17 historical metadata remains 0/2 after live runtime improvement
- master exact inventory remains distinct from the combined morphology analyzer
