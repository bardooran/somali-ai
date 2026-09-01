# Stage 1Q — generic C2A 2PL past activation

Stage 1Q widens the reviewed class-level Conjugation-2A past policy from 3PL-only to **2PL + 3PL**. It does not add a new lemma, target-specific profile, reverse analyzer, or correction rule.

## Development authority

The 2PL rule is authorized from evidence that predates v14:

- John I. Saeed (1999), *Somali*, §4.3.4.3, p. 86, explicitly prints the C2A past-simple table including **2PL `kariseen`** and **3PL `kariyeen`**.
- This Saeed table was already recorded in the Stage 1P past-policy file before the v14 targets were selected and before the v14 answer search began.
- Livnat (1983) remains independent corroboration for the 3PL `kariyeen` cell only; it is not presented as 2PL evidence.

The frozen v14 answer `buufiseen` is evaluation-only and is **not** runtime evidence.

## Runtime scope

For the existing explicit eleven-lemma C2A activation cohort:

- 2PL past: `lemma + s + een`
- 3PL past: existing reviewed `i`-vowel glide before `een`

All other class-level past persons remain unjudged:

- 1SG
- 2SG
- 3SG masculine
- 3SG feminine
- 1PL

The policy remains forward-only and allowlist-only:

- no open-class generation;
- no arbitrary `i`-final inference;
- no reverse suffix stripping;
- no future class entry auto-activation;
- no automatic correction authority.

## v14 isolation

v14 selected `buufi` and `caafi` for the unsupported 2PL-past cell before answer lookup. Only `buufiseen` was independently attested and scored; `caafi` remained unresolved rather than guessed.

The untouched v14 baseline was then measured and locked at:

- recognition: 0/1
- deep features: 0/1
- reviewed-rule-derived hits: 0/1
- master hits: 0/1
- unknown safety: 8/8

Stage 1Q is allowed to improve the live v14 score only through the generic Saeed-authorized 2PL rule. `buufi` must never become a special profile. A mechanical `caafiseen` output after generic activation is a **prediction only** and must not be described as independently attested unless separate evidence is later found.

## Pass condition

The change is acceptable only if GitHub Actions confirms:

- v10 remains at its protected zero baseline;
- v11 remains complete;
- v12 remains complete;
- v13 remains complete;
- live v14 becomes 1/1 with a reviewed-rule-derived analysis for `buufiseen`;
- v14 historical metadata still records the untouched 0/1 baseline;
- all eight v14 synthetic unknown probes remain rejected.
