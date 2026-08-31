# Project Status

This is the quick dashboard for the Somali grammar foundation.

## Overall stage

**Core grammar-engine foundation: approximately 4.5–5/10.**

The project has an executable, evidence-backed grammar engine. The main remaining job is breadth: more reviewed Somali words, word forms, sentence constructions, independent QA, and conflict testing.

## Coverage dashboard

| Area | Status | Main next need |
|---|---|---|
| Orthography | Active | Expand only with safe source-backed rules |
| Personal pronouns | Active | Broader construction coverage |
| Subject–verb agreement | Active / Growing | More verbs and sentence shapes |
| Noun gender agreement | Active / Growing | Larger reviewed noun inventory |
| Singular/plural agreement | Active / Growing | More noun classes and real sentences |
| Noun subject case/forms | Growing | Broader focus/case validation |
| `baa` / `ayaa` focus | Active / Growing | More complex focus constructions |
| Object clitics | Active / Growing | More clitics and combinations |
| Statement clitics (`wuu`, `way`, etc.) | Active | Broader clause structures |
| Connectives (`wuuna`, `wayna`, `wuxuuna`) | Growing | More subject-switch and discourse QA |
| Negation | Active / Growing | Broader paradigms and clitic combinations |
| Negative subject focus | Active / Growing | More independently attested stems |
| Future / negative future | Active / Growing | More verbs and holdout QA |
| Past / aspect | Growing | Broader tense/aspect coverage |
| Past habitual | Active / Growing | More independently supported habitual stems |
| Imperative / jussive / dependent / conditional | Growing | More reviewed verb families and contexts |
| Possession (`leeyahay`) | Active / Growing | More constructions and nouns |
| Predicate/copula agreement | Growing | Broader predicates and clause types |
| Verb Classes I–IV | Reviewed / Growing | More lemmas and independent paradigms |
| Irregular verbs (`dheh`, `aqaan`, `aal/yaal`, `ahaw`) | Reviewed / Growing | More tense/mood and sentence validation |
| `arag` aspect contrasts | Reviewed | Broader cross-source validation |
| `maydh` Jigjiga forms | Reviewed / Conservative | Independent evidence and more forms |
| Regional variants | Active / Growing | Larger pair-by-pair inventory |
| Vocabulary data | Active / Growing | Expand reviewed everyday words and verbs |
| Word lookup (`src/vocabulary.py`) | Active / Conservative | More reviewed word coverage without guessing |
| Somali corpus | Started | Review and use `data/corpus/maahmaahyo.json` for research/QA |
| Independent QA / holdouts | Growing | Much larger unseen-example dataset |
| LLM training | Not started | Later, after stronger language foundation |

## Current data organization

```text
data/vocabulary/  = information about words
data/morphology/  = reviewed word forms/paradigms
data/corpus/      = real Somali text collections
data/qa/          = independent test material
data/sources/     = structured source evidence
```

## Current principles

- Never invent Somali words or paradigms from a single example.
- Keep evidence separate from executable correction rules.
- Prefer unknown/context-required over unsafe correction.
- Test with examples not used to create the rule.
- Keep regional variation separate from grammatical correctness.
- Preserve provenance.
- Keep repository names understandable and documentation synchronized with the implementation.

## Immediate priorities

1. Expand high-frequency Somali grammar in larger evidence-backed batches.
2. Use the maahmaahyo corpus as a source of new research and stress-test candidates, not as automatic grammar authority.
3. Increase independent QA and holdout examples.
4. Expand reviewed vocabulary, verbs, and nouns without open-ended guessing.
5. Improve ambiguity and rule-conflict handling.

Update this dashboard whenever a meaningful language area or major data layer changes.
