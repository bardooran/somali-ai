# Stage 1V — generic C2A 3sg feminine past

## Goal

Complete the separately staged seven-person Conjugation-2A past set over the existing reviewed 11-lemma allowlist by authorizing **3sg feminine past**.

This activation occurs only after v19 permanently froze and measured its untouched baseline. PR #58 selected `caafi` and `bushi` before answer lookup; PR #59 froze `caafisay` and `bushisay` as evaluation-only 3sg-feminine rows; PR #60 locked the untouched historical result.

The untouched v19 result was deliberately person-sensitive:

- surface recognition: 2/2
- lemma/POS/C2A/past recognition: 2/2
- requested `3sg_f` person: 0/2
- deep-feature rows: 0/2
- existing 2sg analysis: 2/2
- full 2sg/3sg-f syncretic ambiguity preserved: 0/2
- master exact recognition: 0/2
- unknown safety: 8/8

The spellings were already available through the live 2sg class rule, but the analyzer did not yet represent the equally valid 3sg-feminine analysis.

## Independent development authority

The runtime rule does **not** come from the v19 target answers.

Pre-v19 reviewed development evidence already supplies the class mechanics:

- Puglielli & Cabdallah Cumar Mansuur (1997), section 6.3.2.1, explicitly prints `wey kari-s-ay` and analyzes the C2A past form as `kari + t + ay`, with `t` surfacing as `s` after stem-final `i`.
- The same reviewed material independently gives the 2sg pattern `waad joogi-s-ay = joogi + t + ay`.
- Zorc et al., *Somali Textbook*, Chapter 11, independently states that the second-conjugation `t -> s` alternation applies in the 2sg and 3sg-feminine cells.

Therefore the class-level 3sg-feminine rule is independently authorized as:

`lemma + t + ay -> lemma + say`

through the already-reviewed `i_t_assibilation` process.

Frozen v19 `caafisay` and `bushisay` remain evaluation-only and are not used as development authority or target-specific runtime exceptions.

## Runtime rule

For every lemma in the existing 11-lemma reviewed C2A class-past allowlist:

- 2sg: agreement `t` + past `ay` -> `-isay`
- 3sg feminine: agreement `t` + past `ay` -> the same `-isay`

Both person analyses are retained for the same spelling. One does not replace the other.

The 3sg-feminine candidate remains:

- `reviewed_rule_derived`
- forward-generated only
- allowlist-only
- non-corrective

## Safety boundaries

- no target-specific `caafi` or `bushi` profile
- no learning from the frozen v19 answer rows
- no open-class generation
- no arbitrary `i`-final lemma inference
- no reverse suffix stripping
- no automatic correction authority
- generated candidates are not independent attestation claims
- master exact inventory remains separate from the combined morphology analyzer
- historical v19 metadata remains fixed at 0/2 for `3sg_f` person/deep features even after live improvement
- broad `ay/ey` orthographic-variant activation remains deferred

## Expected live v19 effect

After activation:

- surface recognition remains 2/2
- lemma/POS/C2A/past remain 2/2
- `3sg_f` person improves 0/2 -> 2/2
- deep features improve 0/2 -> 2/2
- both 2sg and 3sg-f analyses are preserved for both target spellings
- master exact remains 0/2
- unknown safety remains 8/8

This is an improvement in **analysis resolution**, not a claim that v19 discovered previously unknown spellings.

## Staged C2A past status

The reviewed allowlist now has all seven staged person cells:

- 1sg
- 1pl
- 2sg
- 2pl
- 3sg masculine
- 3sg feminine
- 3pl

This completes the staged C2A past-person set for these 11 reviewed lemmas. It does **not** by itself declare all Stage 1 morphology complete, open-class C2A coverage complete, or all Somali past morphology solved.
