# Project Status

This file is the quick dashboard for the Somali grammar foundation.

It should answer three questions quickly:

1. What already exists?
2. How mature is each area?
3. What should be expanded next?

Status labels:

- **Active** — implemented and used by the checker or analyzer layer.
- **Reviewed** — backed by evidence but not necessarily safe for automatic correction.
- **Growing** — useful coverage exists but more verbs, nouns, constructions, or QA are needed.
- **Context required** — the construction is real, but the checker must not make a deterministic judgment without more context.
- **Not started** — planned for later.

## Overall project stage

**Core grammar-engine foundation: approximately 4.5–5/10.**

The repository has moved beyond planning into an executable, evidence-backed grammar engine. The main remaining problem is breadth: more reviewed Somali forms, sentence constructions, lexical coverage, independent QA, and conflict testing are still needed before the checker can be considered broadly reliable.

## Coverage dashboard

| Area | Status | Current position | Main next need |
|---|---|---|---|
| Orthography framework | Active | Safe corrections supported separately from grammar | Expand only with source-backed rules |
| Personal pronouns | Active | Pronoun and subject-clitic evidence encoded | Broader construction coverage |
| Subject–verb agreement | Active / Growing | Person, number, and reviewed gender behavior | More verbs and sentence shapes |
| Noun gender agreement | Active / Growing | Masculine/feminine agreement supported for reviewed nouns/constructions | Larger reviewed noun inventory |
| Singular/plural agreement | Active / Growing | Number-sensitive verb agreement exists | More noun classes and real sentences |
| Noun subject case/forms | Growing | Construction-sensitive subject forms modeled | Broader case/focus validation |
| `baa` / `ayaa` focus | Active / Growing | Subject and object focus patterns represented | More complex focus constructions |
| Fronted/focused objects | Active / Growing | Dedicated analyzers and rules exist | Wider vocabulary and word order |
| Object clitics (`idin`, etc.) | Active / Growing | Object role is separated from agreement controller | Expand clitic inventory and combinations |
| Statement clitics (`wuu`, `way`, etc.) | Active | Core statement agreement represented | Broader clause structures |
| Connective statement forms (`wuuna`, `wayna`) | Growing | Same-subject continuity logic exists | More subject-switch and discourse QA |
| Connective `waxaa` / `wuxuuna` | Growing | Reviewed and holdout-tested constructions exist | More connective forms and contexts |
| Negation | Active / Growing | `ma` patterns and negative agreement represented | Broader paradigms and clitic combinations |
| Negative subject focus | Active / Growing | Reviewed reduced constructions supported conservatively | More independently attested stems |
| Future auxiliary | Active / Growing | Agreement layer exists | More verbs and contexts |
| Negative future | Active / Growing | Separate negative-future agreement exists | More holdout QA |
| Past/aspect | Growing | Reviewed agreement patterns exist | Broader tense/aspect coverage |
| Past habitual | Active / Growing | Reviewed `jir` auxiliary behavior and exact stems supported | More independently supported habitual stems |
| Imperative | Growing | Dedicated grammar layer exists | More verb families |
| Jussive | Growing | Dedicated agreement layer exists | More reviewed paradigms |
| Dependent mood | Growing | Dedicated analyzer exists | More dependent-clause evidence |
| Conditional | Growing | Dedicated agreement analyzer and tests exist | Broader lexical coverage |
| Possession (`leeyahay`) | Active / Growing | Reviewed possession morphology and agreement | More constructions and nouns |
| Predicate/copula agreement | Growing | Dedicated rule/analyzer layer exists | Broader predicates and clause types |
| Verb Class I | Reviewed / Growing | Representative reviewed forms supported | More lemmas |
| Verb Class II | Reviewed / Growing | Representative reviewed forms supported | More independently attested paradigms |
| Verb Class III | Reviewed / Growing | Representative reviewed forms supported | More independently attested paradigms |
| Class IV / fal-sifo | Reviewed / Growing | Reviewed `adag` / `fiican` examples | More adjective/verb families |
| Irregular `dheh` | Reviewed / Growing | Regional and paradigm evidence exists | Broader moods/tenses |
| Irregular `aqaan` | Reviewed / Growing | Past/dependent/jussive material present | More sentence-level validation |
| Irregular `aal/yaal` | Reviewed / Growing | Dedicated reviewed forms and generalization tests | More context testing |
| Irregular `ahaw` | Reviewed / Growing | Reviewed forms and dependent pairs | More sentence-level validation |
| `arag` aspect contrasts | Reviewed | Simple/current contrast stored from project evidence | Broader cross-source validation |
| `maydh` Jigjiga forms | Reviewed / Conservative | Exact native-reviewed forms retained without guessing paradigm | Independent evidence and more forms |
| Regional variants | Active / Growing | Jigjiga-first preferred output profile; supported variants retained | Larger pair-by-pair regional inventory |
| Independent QA / holdouts | Growing | Holdout data and many regression/generalization tests exist | Much larger unseen-example dataset |
| LLM training | Not started | Outside current repository scope | Later, after stronger language foundation |

## Current project principles

- Never invent Somali words or paradigms from a single example.
- Keep evidence separate from executable correction rules.
- Prefer unknown/context-required over an unsafe correction.
- Test with examples that were not used to create the rule.
- Keep regional variation separate from grammatical correctness.
- Preserve provenance for imported and reviewed linguistic facts.

## Immediate priorities

1. Keep expanding high-frequency Somali grammar in evidence-backed batches.
2. Increase independent QA and holdout examples.
3. Expand reviewed verb and noun coverage without open-ended suffix guessing.
4. Improve handling of ambiguity and rule conflicts.
5. Keep repository documentation synchronized with implementation.

## Maintenance rule

When a meaningful grammar area is added, removed, promoted, or found unsafe, update this dashboard in the same development stage so it remains a reliable answer to: **“Where are we?”**
