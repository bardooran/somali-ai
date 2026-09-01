# Stage 1P — narrow Conjugation-2A class past activation

Stage 1P adds the first generic **class-level C2A past** behavior.  The scope is
deliberately only **3rd-person plural past**.  It does not authorize a full past
paradigm.

## Why this stage exists

Frozen benchmark v13 was measured before this change.  Its untouched result was:

- `abhiyaa` — recognized through the already-existing generic C2A present rule;
- `afceliyeen` — unrecognized because class-level C2A past generation did not
  exist;
- overall v13: 1/2 positive surfaces and 1/2 deep feature rows, with 8/8 unknown
  safety.

That historical result is stored in the v13 metadata and is not rewritten by this
stage.

## Independent development evidence

The new runtime rule does **not** use the v13 `afceliyeen` answer row.

1. John I. Saeed, *Somali* (1999), section 4.3.4.3, p. 86, prints the C2A
   past-simple paradigm and explicitly gives 3PL `kariyeen`.
2. Michal Allon Livnat, “The Indicator Particle baa in Somali” (1983), section
   4.6, p. 118, independently prints plural-subject examples including
   `cuntadii bay dumarku kariyeen` and `dumarkii way kariyeen cuntadii`.

Together these support the narrow structural operation used here:

```text
C2A i-final lemma + 3PL past -een
                  ↓
          y between i and e
                  ↓
              ...iyeen
```

## Authorization boundary

`rules/morphology/reviewed_conjugation_2_class_past_activation.json` authorizes:

- POS: verb;
- class: 2A;
- tense/aspect: past;
- mood: indicative;
- person: **3pl only**;
- the complete eleven-lemma Stage 1O activation cohort;
- forward generation only;
- recognition/analysis only, never correction authority.

It does not authorize:

- 1sg, 2sg, 3sg masculine, 3sg feminine, 1pl, or 2pl class-level past;
- arbitrary verbs merely because they end in `i`;
- future class-lexicon entries automatically;
- `nadiifi` or `qurxi` from frozen v10;
- any v13 target-specific profile;
- reverse suffix stripping;
- automatic correction.

The remaining past persons are intentionally deferred.  Saeed's table provides
important evidence, but the project's existing spelling conventions include an
`-ay`/`-ey` question in singular cells and a separately reviewed 1pl manner
alternation.  Those issues will be handled in later evidence-gated stages rather
than silently bundled into Stage 1P.

## Experimental meaning

If v13 moves from its frozen 1/2 baseline to 2/2 after Stage 1P, the improvement
must come through the same generic rule available to all eleven authorized C2A
lemmas.  The runtime rule is backed by `kariyeen` development evidence and never
reads `afceliyeen` as rule evidence.

Mechanical outputs for non-benchmark lemmas in tests demonstrate uniformity only;
they are not promoted as independently attested Somali forms merely because the
generator can produce them.
