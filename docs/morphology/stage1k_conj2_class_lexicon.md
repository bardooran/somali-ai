# Stage 1K — pre-benchmark Conjugation-2A class lexicon

## Purpose

Separate **lemma/class knowledge** from **surface-generation authority** before the next generalization benchmark is frozen.

The repository already knows a complete reviewed present paradigm for the development lemma `kari`, but the finite generator deliberately refuses to infer paradigms for arbitrary i-final verbs. To test genuine cross-lemma generalization, we first need a reviewed inventory saying which lemmas are Conjugation 2A without yet generating any of their inflected surfaces.

## Source

R. David Zorc, *Somali-English Dictionary*, revision 2019-06-05, contiguous B/C dictionary slice.

The admitted entries are explicitly labelled `v2a` by the dictionary. No inflected paradigm surface is imported from this source.

This work is distinct from the Zorc & Issa 1990 textbook used for frozen v7. Because R. David Zorc is an author of both works, this is **not claimed author-independent**. The isolation claim is narrower and explicit: no v7 benchmark lemma or answer row is used as runtime evidence.

## Class-only entries

- `bushi`
- `butaaci`
- `buubi`
- `buufi`
- `buuxi`
- `caafi`
- `caajisi`

Each entry records only:

- lemma
- verb POS
- Conjugation `2A`
- source label/page
- gloss

## Safety boundary

Every class-only entry has:

- `generation_enabled: false`
- no tense/person authorization
- no reverse suffix stripping
- no correction authority

Tests require all seven lemmas to remain unable to generate present surfaces and require the class-only inventory to be disjoint from frozen v5-v10 positive lemmas.

## Next gate

After this class-only inventory is merged, freeze v11 from a separate source that explicitly prints an inflected paradigm for one of the already-authorized lemmas. Only after v11 is frozen and measured may a class-level C2A generator be allowed to consume this lexicon.
