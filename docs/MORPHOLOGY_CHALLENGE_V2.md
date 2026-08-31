# Morphology Challenge v2

Morphology Challenge v2 is the first analyzer-blind competitive morphology set for this project.

## Why v2 exists

Benchmark v1 is intentionally asymmetric: its development cases were already reviewed by Somali AI, while its holdouts are deliberately excluded from Somali AI runtime. v1 is useful for regression and safety, but it must not be used to declare an overall runtime winner.

v2 removes that selection bias. Its cases are selected before either Somali AI or GiellaLT is evaluated on them.

## Frozen source

- Source repository: `bardooran/goobolabs`
- Source commit: `737cf848bfa8291d5580f5c34db04daef858c955`
- Source collection: `resources/qaamuus/`
- Source registry reports 48,119 headword entries.

The dictionary metadata and rights review are still incomplete, so the frozen benchmark does **not** copy definitions. It stores only the minimum evidence needed for evaluation: headword, coarse grammatical category, source path, source line, source code, source commit, and deterministic selection hash.

## Selection procedure

The freeze generator reads all letter files `01-*.md` through `31-*.md`, then:

1. Parses dictionary headwords and their grammatical code without consulting either analyzer.
2. Keeps single-token entries whose code supplies an unambiguous coarse category for this benchmark:
   - an explicit `t` (tiraale / numeral) segment, including composite codes such as `m.l.t`, → numeral
   - otherwise `m` / `m.*` → noun
   - otherwise `f` / `f.*` → verb
   - otherwise `s` / `s.*` → adjective
3. Removes homograph superscript digits from the surface form and groups identical surface+POS pairs.
4. Hashes each pair with SHA-256 using the fixed seed `somali-ai-morphology-challenge-v2-2026-08-31`.
5. Takes the lowest hashes for fixed quotas: 48 nouns, 48 verbs, 16 adjectives, and 8 numerals.
6. Merges a surface into one case if more than one selected POS applies, preserving all expected coarse types and provenance.
7. Adds 16 deterministic synthetic nonsense probes containing `p/v/z`, letters outside standard Somali orthography. These are explicit safety probes, not claims that unattested Somali-looking forms are ungrammatical.

The selection algorithm never imports or calls Somali AI morphology code, GiellaLT, HFST, or any analyzer output.

## Freeze protocol

The process is deliberately two-phase:

1. Commit the selection specification, generator, tests, and artifact-only freeze workflow.
2. Run that workflow against the pinned source and commit the exact generated JSONL plus its metadata and SHA-256.

Only **after** the generated manifest is committed may runtime scoring be wired to either analyzer. This prevents benchmark shopping or silently changing cases after seeing results.

## Interpretation

v2 initially measures lexical recognition and coarse POS/type agreement, plus explicit unknown-safety behavior. Recognition alone is not proof of full morphological correctness. Later challenge versions can add independently reviewed inflected forms, ambiguity, paradigms, and feature-level scoring without changing the frozen v2 set.
