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
| Statement/connective clitics | Active / Growing | Broader clause structures |
| Negation / future / aspect / mood | Active / Growing | More reviewed paradigms and contexts |
| Past habitual | Active / Growing | More independently supported stems |
| Predicate/copula and possession | Growing | Broader sentence coverage |
| Verb Classes I–IV and irregular verbs | Reviewed / Growing | More lemmas and paradigms |
| `arag` / `maydh` reviewed forms | Conservative | More independent evidence |
| Somali cardinal numbers | Active / Reviewed | Carefully extend large and approximate quantities |
| Gregorian month names | Active / Reviewed | More date constructions and ordinals |
| Somali traditional seasons | Active / Region-sensitive | More Jigjiga/Northwestern evidence |
| Weekdays and full Gregorian dates | Active / Reviewed | Broader natural date-sentence QA |
| Relative days/time | Active / Conservative | More independent evidence for rare forms and richer constructions |
| Clock expressions | Evidence collected / Non-generative | Resolve direct vs traditional clock conventions before automatic conversion |
| Age expressions | Active / Conservative | More sentence grammar around age questions/statements |
| Directions/location vocabulary | Active / Conservative | More construction-level route/location grammar |
| Regional variants | Active / Growing | Larger pair-by-pair inventory |
| Vocabulary data | Active / Growing | Expand reviewed everyday words and verbs |
| Word lookup (`src/vocabulary.py`) | Active / Conservative | More reviewed word coverage without guessing |
| Somali corpus | Started | Use `data/corpus/maahmaahyo.json` for research/QA |
| Independent QA / holdouts | Growing | Much larger unseen-example dataset |
| LLM training | Not started | Later, after stronger language foundation |

## High-frequency date/time coverage

The repo now includes `data/vocabulary/somali_datetime_terms.jsonl` and `src/datetime_terms.py` with:

- weekdays `Isniin`, `Talaado`, `Arbaco`, `Khamiis`, `Jimco/Jimce`, `Sabti`, `Axad`;
- full Gregorian date display such as `Arbaco, 5 Agoosto 2026`;
- reviewed relative days `dorraad/daraad`, `shalay`, `maanta`, `berri/berrito`, `saadambe/berri dambe`, and provisionally reviewed `saakuun`;
- submitted `shalay-dambe` and `saakuunta` stored as non-executable candidates;
- reviewed time units and quantity forms such as `daqiiqo`, `saac/saacadood`, `maalin/maalmood`, `bil/bilood`, `sannad/sano`;
- constrained phrases such as `3 saacadood ka hor`, `6 bilood ka dib`, and duration phrases;
- no blind 24-hour-to-Somali clock conversion because sources document more than one clock convention.

## Age and direction coverage

`data/vocabulary/somali_age_terms.jsonl` + `src/age.py` support the productive numeric age construction `N jir`, including independently attested questions/statements such as `Immisa jir baad tahay?` and numeric age answers. Social age labels remain context-sensitive rather than fixed to hard numerical ranges.

`data/vocabulary/somali_direction_terms.jsonl` + `src/directions.py` cover cardinal/intermediate directions and common location terms. Ambiguous forms such as `bari`, `hore`, `kor`, `dhexe`, and `horta` retain context-sensitive status.

## Calendar coverage

`data/vocabulary/somali_calendar_terms.jsonl` and `src/calendar_terms.py` provide the 12 Gregorian month names, documented variants, and reviewed Somali traditional seasons. Seasonal Gregorian alignment is approximate and region-sensitive; Somali seasons are not automatically equated with Western spring/summer/autumn/winter.

## Current data organization

```text
data/vocabulary/  = words, numerals, calendar/date/time, age, and direction terms
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
- Do not flatten region-sensitive seasons, clock conventions, age categories, or ambiguous location words into one universal interpretation.
- Preserve provenance.
- Keep repository names understandable and documentation synchronized with implementation.

## Immediate priorities

1. Expand high-frequency Somali grammar in larger evidence-backed batches.
2. Use the maahmaahyo corpus for research and unseen stress tests, not automatic grammar authority.
3. Increase independent QA and holdout examples.
4. Expand reviewed vocabulary, verbs, nouns, quantities, dates/time, directions, and other high-frequency language areas without open-ended guessing.
5. Improve ambiguity and rule-conflict handling.

Update this dashboard whenever a meaningful language area or major data layer changes.
