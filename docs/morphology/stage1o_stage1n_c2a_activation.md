# Stage 1O — activate the complete Stage 1N C2A cohort

## Goal

Stage 1O tests a second class-level Conjugation-2A generalization step without adding benchmark-target-specific profiles.

Stage 1N selected and merged four reviewed C2A class-only lemmas from Zorc 2019 **before any finite answer-source search**:

- `aaddi`
- `aammusi`
- `abhi`
- `afceli`

All four had `generation_enabled=false` and remained outside the explicit activation allowlist.

## Historical order

1. Stage 1N merged the four lemma/class entries at `0ab8f13d2e5bc932048b413ebb3a82b445193b6a`.
2. Only afterward were v12 answer sources searched.
3. v12 froze two naturally attested 3pl targets, `aaddiyaan` and `aammusiyaan`.
4. The untouched v12 baseline measured 0/2 recognition and 0/2 complete feature rows with 8/8 unknown safety while all four Stage 1N lemmas remained unactivated.
5. Stage 1O activates the **complete four-lemma Stage 1N cohort**, not merely the two v12 targets.

## What Stage 1O changes

The existing `MORPH-CONJ-IIA-CLASS-ACT-001` explicit allowlist is extended from seven pre-v11 lemmas to eleven total lemmas by adding the complete Stage 1N cohort.

No generator algorithm changes are needed. The already-reviewed C2A processes remain:

- `i_vowel_glide`
- `i_t_assibilation`
- `i_n_weak_causative_manner_alternation`

The process evidence remains the pre-v12 evidence already used by the class activation system. Neither the Dalka Journal v12 sentence nor Kapchits 2005 v12 example is cited as runtime process evidence.

## Safety boundary

Stage 1O keeps all existing conservative restrictions:

- finite forward generation only;
- present indicative only for the class-activation path;
- explicit activated-lemma allowlist;
- future class-lexicon entries do not auto-activate;
- no class inference from an `i`-final spelling;
- no reverse suffix stripping;
- no target-specific profile for `aaddi` or `aammusi`;
- no past generation for the Stage 1N cohort;
- no correction authority for generated forms.

`abhi` and `afceli` are deliberately activated alongside the v12 targets because they belonged to the same pre-answer Stage 1N cohort. Mechanical outputs from those reserve lemmas are **predictions of the reviewed rule system, not independently verified Somali forms**. They must be checked later against a separately frozen source before they are treated as benchmark-supported surface evidence.

## Expected evaluation behavior

The intended Stage 1O result is:

- v10 remains at its frozen zero-overlap state;
- v11 remains fully covered through generic class activation;
- v12 moves from the historical 0/2 baseline to 2/2 only through `reviewed_rule_derived` generic C2A analyses;
- v12 master exact recognition remains zero;
- v12 unknown safety remains 8/8.

These are merge-gate expectations, not claims of success until the actual GitHub Actions run confirms them.
