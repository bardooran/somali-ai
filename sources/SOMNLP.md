# SomNLP-Corpus source audit

## Status

- Upstream project: `goobolabs/SomNLP-Corpus`
- Local mirror audited: `bardooran/SomNLP`
- Audited mirror/upstream commit: `5281c76787b69ddbf3a8fc8c45cfcc3ad927467b`
- Audit date: 2026-08-31
- Role in this project: corpus attestation, unseen QA, frequency/variant discovery, and future training-data research
- Grammar authority: no
- Automatic promotion: disabled

The upstream and mirror were at the same audited commit. Pin the commit on every later extraction because the corpus pipeline and source registry are actively changing.

## Repository versus corpus

The Git repository contains the pipeline, source registry, cleaning code, tokenizer and documentation. The multi-gigabyte corpus itself is gitignored and must be downloaded/rebuilt locally.

The measured six-source baseline reported by SomNLP is roughly 1.67 million final documents and 529 million words. Full eleven-source figures are projections until all sources are rerun together.

Therefore this repository is not a ready-to-copy corpus bundle. Our integration should consume a locally generated provenance-bearing JSONL release or controlled per-source outputs.

## Licensing boundary

There is no single corpus license. SomNLP explicitly tracks licenses per source. Its Track A registry currently includes CC0, CC BY, CC BY-SA, ODC-BY, and source-specific/unresolved terms.

At the audited commit, no root repository `LICENSE` file was found and the Cargo workspace did not declare a package license. The pipeline code is public, but this project should **not copy SomNLP code** into `somali-grammar` unless its code license is clarified separately.

Our importer below is independently implemented and only consumes corpus record data.

For corpus text, redistribution must follow each upstream source license. Sources whose registry says `see source` / `Other` are not redistributed by our initial importer.

## Provenance implementation

SomNLP's current merge implementation writes both `text` and the source registry key. The clean stage converts that into a `CorpusRecord` with source key, collection time, per-source license, content hash, document ID, quality status and dedup metadata.

This is stronger than an older note in `docs/METADATA_SCHEMA.md` that says merge writes text only; the implementation at the pinned commit is the current evidence.

Important limitation: the current merge path usually preserves the **dataset source key**, not the original article URL/author/title. That is adequate for source-tier QA, but not enough to cite an individual web document as scholarly evidence.

Another limitation: exact dedup is first-seen-wins. If the same text occurs in more than one source, the kept record inherits whichever source appears first in the configured merge order. A source key therefore identifies the retained pipeline source, not necessarily original authorship.

## Quality pipeline

The pipeline performs:

- exact dedup at merge
- text cleaning and normalization
- language identification for document sources
- deeper boilerplate/HTML/corruption cleanup
- near-duplicate filtering for document sources
- quality dispositions: `kept`, `rejected`, `review`

Rejected records are preserved in sidecars rather than silently erased. This is useful for QA research because thresholds can be revisited.

For this project, only `quality.disposition == kept` records should enter ordinary corpus-attestation sampling. Review/rejected records may be studied separately but must not be mixed into clean QA evidence.

## Evidence tiers for Somali grammar work

The tiers below describe **how this project may use the source**, not a claim that every sentence in a tier is grammatically correct.

### Tier A — edited/native-use QA candidates

- `wikipedia` — Somali Wikipedia
- `xlsum` — Somali news/summary material

Use for:
- unseen grammar-checker stress tests
- natural sentence/construction discovery
- variant frequency comparison

Still not automatic correctness authority. Edited text can contain mistakes, translations, and regional variation.

### Tier B — broad web attestation

- `hplt`
- `cc100`
- `mc4`
- `madlad`

Use for:
- frequency and distribution
- finding spelling/grammar variants
- discovering constructions to verify elsewhere
- false-positive hunting

Do not infer correctness from frequency. Web crawls include noisy, duplicated, translated, informal, and erroneous language even after cleaning.

### Tier C — parallel/translation evidence

- `opus`
- `mt560`
- `nllb`

Use for:
- candidate vocabulary and construction discovery
- translation-oriented QA
- comparison with native editorial sources

Do not use as primary Somali grammar authority. Translationese and alignment artifacts can alter natural word order, lexical choice, and constructions.

### Tier D — specialized religious translation

- `quran`
- `tanzil`
- `quran-tanzil`

Use only as specialized/domain evidence after the exact upstream rights are verified. Their style is translated and religious, not a neutral modern-usage baseline.

The initial importer blocks these unresolved-license sources by default.

## Language-ID and dedup caveats

Document sources use a Somali language-ID gate and near-deduplication. Sentence/parallel/religious sources use a tag-only LID policy and skip near-dedup. Therefore all final records have not passed identical evidence filters.

Corpus counts must remain source-stratified. We must never say “555M Somali words prove X” without checking which source families actually contain X.

## Cleaning versus exact orthographic evidence

SomNLP cleaning may decode entities, repair mojibake, normalize Unicode/whitespace, collapse excessive repeated characters, strip markup/boilerplate, and make other surface repairs.

Use final cleaned text for:
- grammar stress testing
- broad usage/frequency
- construction discovery

For an exact orthographic quotation or a contested spelling decision, trace the item back to a raw/original source when possible. The cleaned corpus should not be the sole evidence that a particular original spelling was used.

## Stopword warning

SomNLP's frequency-analysis helper contains a stopword list with highly grammatical Somali items such as `oo`, `ayaa`, `buu`, `bay`, `aan`, `aad`, `uu`, `ay`, `waa`, `wuu`, `way`, `ku`, `ka`, `u`, `la`, `in`, `ha`, and many fused forms.

That list is acceptable as an optional **frequency-report filter**. It must not be imported as a grammar/NLP rule that deletes these tokens. In this project, such words are grammar-bearing and often central to agreement, focus, negation and clause structure.

## Import map

### TAKE

- source-registry metadata and source classes
- source/license labels on locally generated corpus records
- `kept` records for bounded corpus-attestation/QA samples
- corpus statistics as descriptive pipeline metadata, clearly marked measured versus projected

### REVIEW

- natural sentences discovered in Tier A/B sources
- variants/frequencies that could support a linguistic claim
- source-specific cleaning effects
- translation-derived constructions

### QA / DISCOVERY

- unseen sentence stress tests
- false-positive and false-negative discovery
- spelling/variant candidate frequency
- construction search
- disagreement hunting between our checker and real-world text

### SKIP / HOLD

- direct copying of SomNLP pipeline code while its repository code license is not explicit
- bulk copying of the entire corpus into `somali-grammar`
- unresolved-license religious text redistribution
- treating frequency as grammatical correctness
- treating SomNLP stopwords as safe-to-remove grammar tokens
- training/evaluation mixing without source/license/domain stratification

## Initial importer scope

`tools/importers/somnlp_extract.py` consumes a **local SomNLP processed JSONL** rather than cloning code or data into this repository.

It:

- requires the exact SomNLP source commit
- requires a recognized source key
- requires a source license on the record
- accepts only `quality.disposition == kept`
- assigns the evidence tier/role above
- blocks unresolved-license Tier D records by default
- preserves corpus record ID and source/license provenance
- marks every record `external_corpus_attestation_unreviewed`
- sets `promotion_allowed: false`
- never writes directly to reviewed vocabulary, morphology or grammar rules

A future cross-source promotion layer can use these records to confirm **attestation** after GiellaLT/SLS/academic evidence has established a linguistic hypothesis.
