# Somali Language Standard (goobolabs) source audit

## Status

- Upstream project: `goobolabs/somali-language-standard`
- Local mirror audited: `bardooran/goobolabs`
- Audited mirror/upstream commit: `737cf848bfa8291d5580f5c34db04daef858c955`
- Audit date: 2026-08-31
- Code license: MIT
- SLS-authored linguistic content license: CC BY 4.0
- Role in this project: structured cross-check, evidence map, QA candidates, and source discovery
- Automatic promotion: disabled

The audited commit is pinned. SLS is actively evolving, so every later extraction must record its source commit.

## Important lifecycle boundary

At the audited commit, SLS-0000 through SLS-0005 are not Stable. SLS-0003 (grammar) is `Proposed`, while its individual topic notes remain `Draft`. The public-comment period for SLS-0002 through SLS-0005 is still open at the time of this audit.

Therefore an SLS rule is useful structured evidence, but is not automatically project-approved grammar.

## Strongest value for this project

### Structured proposed grammar rules

`spec/grammar/0010` through `0018` cover:

- parts of speech
- noun gender and plural morphology
- verb tense/aspect/mood and agreement
- pronouns and object/subject clitics
- focus and sentence structure
- negation
- question formation
- bounded common-error diagnostics

The design principles align strongly with this project: unknown and dialectal forms should remain `not covered`; paradigms must not be invented; diagnostics should be construction-specific; agreement must use grammatical features rather than spelling alone; ambiguity must not be silently rewritten.

### Orthography proposals

`spec/orthography/0001` through `0004` provide proposed rules for alphabet/encoding, spelling, capitalization and punctuation. Especially useful are the conservative rules against universal splitting/joining, unsupported morphophonemic rewriting, and unreviewed compound normalization.

### Evidence maps and provenance

`docs/standards/SLS-0003-evidence-map.md` explicitly maps proposed grammar rules to source families and recorded maintainer review. `data/provenance/correction-log.tsv` records cleanup decisions, including unresolved/intentional-retained material. These are valuable for QA and source-lineage analysis.

### Curated descriptive resource families

`resources/` contains a large evidence library:

- `naxwe/` grammar synthesis
- `sarfe/` noun/verb paradigms and morphophonology
- `qoraal/` orthography/writing material
- `dhawaaq/` phonology
- `qaamuus/` monolingual dictionary
- `madax-ereyo/` derived bare headwords
- `erey-bixin/` historical technical glossaries
- `suugaan/` literary material

These collections are descriptive evidence, not automatically normative data.

## Independence warning: do not double-count source families

SLS is often a structured editorial synthesis of sources already used by this project. It must not be counted as an independent confirmation when it traces to the same underlying work.

Examples:

- `resources/naxwe/00`–`12` are an SLS synthesis based principally on *Aasaaska Naxwaha Af Soomaaliga* (1973) and *Barashada Naxwaha Af Soomaaliga* (Mansur/Puglielli, 1999).
- `resources/sarfe/` states that its primary paradigm source is the 1999 Mansur/Puglielli grammar via the curated `naxwe/` layer.

So, for example, a form supported by our existing Mansur/Puglielli evidence and the SLS `sarfe` table is one underlying source family plus an editorial review layer, not two independent publications.

Candidate records derived from SLS must retain `underlying_source_family` when known.

## Regional-profile boundary

SLS-0003 explicitly targets its Standard-Somali (`Aqoondhari` / `Soomaali Maxaa tiri`) profile and defers regional profiles.

This project has a different output preference: Jigjiga-first with Northwestern/Hargeisa compatibility. Therefore:

- SLS can confirm broadly shared Somali grammar.
- SLS Standard-Somali preferences must not automatically override a reviewed Jigjiga/Hargeisa form.
- A disagreement may represent regional variation rather than an error.
- Regional status must be preserved in review records.

A concrete example is the SLS prefix-verb table, which presents `iraahdaa/tiraahdaa/yiraahdaa`; this project separately preserves reviewed Northwestern `odhan/yidhi/tidhi` evidence. The SLS table is not a reason to replace the Northwestern forms.

## High-value cross-checks already identified

The proposed SLS grammar supports several conservative principles and constructions relevant to this project:

- `Adigu moos baad cuntay.` requires the reviewed second-person subject clitic for that construction.
- `Wiilkii moos buu cunay.` is the reviewed object-focus pattern; bare `baa` is not interchangeable for the same intended reading.
- plural subject focus can license reduced agreement, e.g. `Nimankii baa yimid`; do not flag this as a simple plural mismatch.
- noun plural forms are lexical and must not be guessed from singular spelling.
- gender polarity applies after a reviewed plural form/class is known; it must not be used to invent that plural.
- first/second-person object clitics cannot simply be dropped where the reviewed construction licenses them.
- `annaga` / `innaga` meaning is context-sensitive in actual usage, so blind correction is unsafe.
- negative `ma`, focused negative forms, prohibitive `ha`, and question `ma` require construction-specific analysis.
- unknown relative-clause patterns should remain unjudged rather than be forced into agreement rules.

These are cross-checks, not automatic promotions.

## Dictionary and headword library: HOLD bulk import

`resources/qaamuus/` reports about 48,119 entries and `resources/madax-ereyo/` about 47,502 derived bare headwords. This is potentially very valuable, but the qaamuus source registry itself says the edition, publisher, compiler/editor and rights confirmation remain pending.

Although SLS declares its own linguistic content CC BY 4.0, the project must not assume that this resolves every underlying third-party source right. Therefore:

- do not bulk-copy the SLS qaamuus or madax-ereyo collections into trusted project data yet;
- use individual records only when separately supported by a source whose reuse/provenance is already acceptable;
- revisit bulk import after the underlying dictionary rights/edition metadata is clarified.

The same caution applies to other historical resource collections according to their own source registry.

## Resource-cleanup boundary

SLS records a substantial OCR/editorial cleanup process. Its own documentation says cleanup does not guarantee that every word, grammatical analysis, transcription, or attribution is correct. Some historical/regional forms are intentionally retained.

Therefore a cleanup status such as `approved` means the repository accepted the editorial repair; it does not by itself prove a linguistic form is universally correct.

## Import map

### TAKE as unreviewed structured candidates

- proposed rule metadata/text from `spec/grammar/0010`–`0018`
- proposed orthography rule metadata/text from `spec/orthography/`
- evidence-map/source-lineage metadata
- correction-log metadata for QA/provenance analysis

### REVIEW before promotion

- examples in proposed grammar specs
- `resources/naxwe/` synthesis
- `resources/sarfe/` paradigm tables
- `resources/qoraal/` and `resources/dhawaaq/`
- native-speaker maintainer review decisions, especially where regional scope may differ from this project

### QA / discovery use

- proposed negative examples as candidate stress tests
- alternative constructions and edge cases
- unresolved/intentional-retained correction-log entries as ambiguity tests

### HOLD / SKIP for direct bulk import now

- `resources/qaamuus/` and derived `madax-ereyo/` until underlying rights/edition metadata is clarified
- empty placeholder areas such as current `schemas/`, structured `data/lexicon/`, AI datasets, and benchmarks; they do not yet provide the machine-readable content implied by the long-term architecture
- any material whose source registry marks rights unconfirmed unless separately cleared

## Initial importer scope

The first SLS importer in this repository is intentionally limited to allowlisted SLS-authored `spec/` files. It extracts rule statements with exact path, line, source commit, lifecycle status and license attribution.

It does not import the 48k dictionary, does not write into reviewed grammar rules, and sets `promotion_allowed: false` on every extracted record.

Future stages may extract resource evidence after source-family and rights metadata are represented explicitly.
