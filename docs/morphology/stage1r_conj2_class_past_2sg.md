# Stage 1R — generic C2A 2SG past activation

Stage 1R widens the reviewed class-level Conjugation-2A past policy from **2PL + 3PL** to **2SG + 2PL + 3PL**. It does not add a new lemma, target-specific profile, reverse analyzer, or correction rule.

## Development authority

The 2SG rule is authorized from development evidence that predates v15 and is independent of the v15 answer sources:

- `rules/morphology/reviewed_conjugation_2_morphophonology.json` already records 2SG past morphology as `agreement=t`, `tam=ay`.
- The same reviewed rule cites Puglielli & Cabdallah Cumar Mansuur (1997), which explicitly gives `waad joogi-s-ay`, decomposes it as `joogi+t+ay`, and states that `t` changes to `s` after an `i`-final stem.
- The existing present class policy had already recorded this same `i_t_assibilation` process before v15.
- Zorc et al.'s Somali textbook independently prints the C2A `kari` paradigm with second-person singular `karisey`; GiellaLT's Somali morphophonology documentation prints the modern `karisay` spelling and the same C2A pattern.

The frozen v15 answer `buuxisay` is evaluation-only. It is not cited to authorize the rule and no `buuxi` special profile is added.

## Runtime scope

For the existing explicit eleven-lemma C2A activation cohort:

- 2SG past: `lemma + t + ay`, with reviewed `i+t -> is` assibilation;
- 2PL past: existing `lemma + s + een`;
- 3PL past: existing reviewed `i`-vowel glide before `een`.

The remaining class-level past persons stay unjudged:

- 1SG
- 3SG masculine
- 3SG feminine
- 1PL

The policy remains forward-only and allowlist-only:

- no open-class generation;
- no arbitrary `i`-final inference;
- no reverse suffix stripping;
- no future class entry auto-activation;
- no automatic correction authority.

Mechanical forms produced for cohort lemmas are rule-derived analyses, not claims that every generated surface has been independently attested. In particular, `caajisi` remains unresolved as v15 attestation evidence even though the generic rule can mechanically generate a 2SG candidate.

## v15 isolation

v15 selected `buuxi` and `caajisi` before answer lookup. Only `buuxisay` was independently resolved and scored; `caajisi` remained unresolved rather than guessed.

PR #44 locked the untouched baseline at:

- recognition: 0/1
- lemma/POS/class/past/person: 0/1 each
- deep features: 0/1
- reviewed-rule-derived hits: 0/1
- unknown safety: 8/8

The baseline merge commit is `22959891cb4953e65a3037e4ace756f29febc8f8`.

Stage 1R may improve live v15 only through the generic pre-v15-authorized 2SG mechanics. `buuxi` and `caajisi` must never become target-specific profiles from v15 evidence.

## Pass condition

The change is acceptable only if GitHub Actions confirms:

- v10 remains at its protected 0/10 baseline;
- v11 remains complete;
- v12 remains complete;
- v13 remains complete;
- v14 remains complete;
- live v15 becomes 1/1 with the correct lemma, POS, C2A class, past tense, 2SG person, and reviewed-rule-derived authority for `buuxisay`;
- v15 historical metadata still records the untouched 0/1 baseline;
- all eight v15 synthetic unknown probes remain rejected;
- the complete test suite stays green.
