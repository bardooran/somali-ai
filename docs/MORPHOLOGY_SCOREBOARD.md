# Competitive Morphology Scoreboard

Somali AI's morphology goal is not to beat another project by counting more rows. The target is to exceed the best available Somali morphology resources in **useful coverage, analysis depth, precision, provenance, regional awareness, and safe handling of unknown forms**.

The first comparison target is GiellaLT Somali because it currently has the broadest mature computational morphology inventory available to this project. Its repository badge reports about **14.5K lemmas**, while its maturity badge is currently `Undefined`. Somali AI therefore uses GiellaLT as a breadth benchmark and evidence source, not as unquestioned truth.

## What we measure

Run:

```bash
python -m src.morphology_competition
```

The command prints a machine-readable JSON snapshot with:

- `reviewed_surface_count` — unique exact surface forms backed by reviewed project morphology;
- `reviewed_lemma_count` — lemmas that already have reviewed morphology records;
- `reviewed_feature_dimensions` — the grammatical information attached to those records, such as person, number, gender, tense/aspect, conjugation class, and related features;
- `reviewed_ambiguous_surface_count` — forms whose analysis correctly preserves ambiguity/context sensitivity;
- `giellalt_candidate_row_count` and `giellalt_candidate_unique_lemma_count` — the breadth available in the audited non-promoting candidate layer;
- candidate counts by part of speech;
- `reviewed_giellalt_shared_lemma_count` — lemmas represented in both reviewed Somali AI morphology and GiellaLT candidates;
- `cross_source_backlog_count` — lemmas already present in project vocabulary and GiellaLT but not yet represented in reviewed morphology;
- `giellalt_only_lemma_count` — external candidates that still lack project vocabulary or reviewed-morphology support;
- the gap from GiellaLT's reported 14.5K-lemma baseline;
- `safety_probe_guess_rate` — whether the exact evidence-backed analyzer fabricated analyses for deliberately unsupported sentinel forms.

## Cross-source backlog

The backlog is a **review queue**, never an automatic promotion queue.

A lemma enters this queue only when:

1. it occurs in the audited GiellaLT lexical candidate layer;
2. it also occurs in Somali AI's existing vocabulary layer; and
3. no reviewed morphology record currently exists for that lemma.

The queue prioritizes everyday vocabulary and verbs/adjectives because those yield the largest conversational benefit. A high priority score does **not** authorize paradigm generation. The normal evidence rules still apply.

## Safety requirement

Coverage growth must not come from guessing suffixes or inventing lemmas. The scoreboard includes deliberately unsupported probes such as `cunXYZ` and `magacaanlaaqoon`. They are not linguistic claims about naturally occurring Somali; they are regression sentinels.

A morphology expansion is considered unsafe if it causes these probes to receive fabricated analyses.

## What counts as beating GiellaLT

Somali AI should only claim a morphology win after independent evaluation demonstrates all of the following:

- reviewed useful lemma/surface coverage at or above the competitor baseline, not merely imported candidate count;
- strong precision on unseen real Somali forms;
- strong recall on an independently assembled holdout set;
- richer correct feature analysis where relevant (person, gender, number, tense/aspect, class, ambiguity, etc.);
- lower unsafe-analysis / hallucinated-morphology rate;
- documented regional and variant handling;
- provenance for promoted analyses;
- independent/native review of a substantial evaluation sample.

Until those conditions are measured, the scoreboard reports progress and gaps rather than a winner.

## Current strategy

```text
GiellaLT broad candidate inventory
             +
Somali AI reviewed vocabulary/evidence
             ↓
   cross-source review backlog
             ↓
independent evidence / native review
             ↓
 reviewed morphology records
             ↓
 exact analyzer + sentence grammar
             ↓
 unseen morphology benchmark
```

This lets Somali AI preserve its current precision advantage while systematically closing GiellaLT's breadth advantage.
