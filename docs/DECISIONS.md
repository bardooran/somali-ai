# Project Decisions

## 2026-08-30 — Grammar-first scope

The repository focuses on Somali grammar and writing. Contexto-style gameplay and chatbot/model training are outside the current scope.

## 2026-08-30 — Two user groups

The grammar product should support both Somali speakers improving written Somali and people learning Somali as a new language.

## 2026-08-30 — Source-backed rules

Grammar and orthography rules should not be invented from intuition alone. Each machine-readable rule should carry provenance where possible.

## 2026-08-30 — Provisional SLS rules

Somali Language Standard (SLS) is useful as structured linguistic evidence, but its current proposals are not automatically final project authority. Rules remain provisional until reviewed against additional sources and real Somali usage.

## 2026-08-30 — Native-speaker project review

Native-speaker project review is retained as explicit evidence when it confirms or conflicts with an external source. A single review is not automatically universal across all Somali varieties, but source-only constructions must not be promoted as normal teaching or automatic correction when project review identifies a semantic or usage conflict.

Reviewed focus examples currently include `Cali baa yimid.`, `Maryan baa qososhay.`, `Wiilku muus buu cunay.`, `Muus ayuu wiilku cunay.`, and `Maryan muus bay cuntay.` The source example `Moos baa wiilkii cunay.` must not be taught as meaning “the boy ate the banana”; the project native reviewer reads it with reversed semantic roles, approximately “the banana ate the boy.” It remains disputed/context-required pending broader validation.

## 2026-08-30 — Second-person plural statement pattern

Project native review confirms ordinary second-person plural statements with `idinku` use the `waad` pattern, for example `Idinku waad timaaddeen.`, `Idinku waad tagteen.`, and `Idinku waad cunteen.` The source-listed `aydin` form remains reference evidence, but `Idinku waydin + verb` is not accepted as the ordinary statement pattern and must not be generated or taught as equivalent to `Idinku waad + verb`.

`Waydinkii` may occur in a different construction, with project examples such as `Waydinkii shalay yimid.` and `Waydinkii ballanka qaaday.` This is stored as a separate item for future analysis; it is not evidence that ordinary `waydin + verb` is valid.

## 2026-08-30 — Context-sensitive corrections

A grammar checker must distinguish safe deterministic corrections from ambiguous forms. Ambiguous contractions such as `bay` must not be automatically expanded without enough grammatical context.

## 2026-08-30 — Source conflicts are not errors

When reliable project sources use different Somali forms, the checker must not choose one as wrong automatically. Conflicts such as `Jimce` / `Jimco` and `Jannaayo` / `Janaayo` are stored as reference variants until broader linguistic validation provides usage guidance.

## 2026-08-30 — SomKit role

SomKit is a secondary lexical, learning, and variant-evidence source. Its vocabulary, calendar terms, phrases, and related material can support research and examples, but it does not override grammar sources automatically.

## 2026-08-30 — Lexin pipeline role

The Swedish–Somali Lexin data is used as bilingual lexical and usage evidence. Somali material in `TargetLang` can contribute translations, examples, idioms, compounds, comments, synonyms, and explanations. Swedish `BaseLang` grammatical type and inflection data must not be interpreted as Somali morphology.

## 2026-08-30 — Multi-source grammar pipeline

The grammar foundation combines sources by role instead of mixing them into one undifferentiated dataset: SLS for structured grammar/orthography evidence; GiellaLT for morphology/proofing technology; Lexin for bilingual usage/context evidence; SomKit for supplemental vocabulary/learning/variant evidence; and project tests for safe executable behavior. Every imported fact should retain provenance and source role.

## 2026-08-30 — Overlapping corrections

Automatic fixes must not apply multiple edits to the same text span. When safe findings overlap, the current checker prefers the longer, more specific span and applies only one compatible correction.
