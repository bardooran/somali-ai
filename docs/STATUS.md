# Somali AI Project Status

This is the quick dashboard for **Somali AI — Somali-First Language Intelligence**.

## Overall stage

**Somali-first assistant MVP: active. Language foundation: broad and still expanding.**

The repository is no longer only a grammar checker. It now combines an evidence-backed Somali language foundation with a conversational assistant layer around a strong reasoning model.

The current goal is two-track:

1. keep expanding and reviewing Somali grammar, morphology, vocabulary, regional variation, corpora, and QA;
2. make that knowledge directly useful to a Somali-first assistant that can converse, explain, reason, compare, plan, teach, and help with writing.

## Working AI layer

Implemented now:

- terminal chat via `somali_ai.py`;
- local browser chat via `somali_ai_web.py`;
- OpenAI Responses API model adapter;
- multi-turn in-process conversation history;
- retrieval over reviewed Somali knowledge and external candidate layers;
- exact-form and sentence-level grammatical retrieval;
- runtime local date/time context for relative-date planning;
- conservative response checking and safe orthography/variant fixes;
- a 60-task Somali assistant capability evaluation set;
- offline deterministic tests that do not require an API key.

The assistant prefers the reviewed **Jigjiga / Northwestern-Hargeisa** output profile while recognizing supported regional variation.

## External evidence now stored

The project has audited and connected three major external sources without treating them as automatic truth:

| Source | Current role | Stored/imported status |
|---|---|---|
| GiellaLT Somali | morphology, vocabulary, grammatical-word discovery | 12,363 lexical candidates + 352 grammatical candidates |
| Somali Language Standard (SLS) | grammar and orthography cross-checking | 108 structured rule candidates |
| SomNLP-Corpus | natural-text QA, frequency, later training/evaluation | pipeline audited; bulk corpus not copied into this repo |

All generated external candidate records preserve provenance and remain `promotion_allowed: false` until reviewed.

## Language coverage dashboard

| Area | Status | Main next need |
|---|---|---|
| Conversational assistant | Active MVP | Real-model quality evaluation and richer natural Somali examples |
| Knowledge retrieval | Active | Better cross-source ranking and natural-text evidence |
| Orthography | Active | Expand only with safe source-backed rules |
| Personal pronouns / clitics | Active | Broader construction coverage |
| Subject–verb / noun agreement | Active / Growing | More verbs, nouns, sentence shapes |
| Focus (`baa` / `ayaa`) | Active / Growing | More complex constructions and contextual QA |
| Negation / future / aspect / mood | Active / Growing | More reviewed paradigms and contexts |
| Verb morphology | Reviewed / Growing | Larger independently verified paradigm coverage |
| Noun morphology / gender polarity | Active / Growing | More noun classes and real-sentence QA |
| Somali cardinal numbers | Active / Reviewed | Carefully extend large/approximate quantities |
| Somali ordinals | Active / Reviewed | More compound written-out ordinal evidence |
| Dates / weekdays / months | Active / Reviewed | More natural planning/date QA |
| Relative days/time | Active / Conservative | More rare forms and contextual examples |
| Clock expressions | Preference decided / Conservative | Implement broader Jigjiga/Hargeisa direct-clock behavior |
| Age expressions | Active / Conservative | More age sentence grammar |
| Directions/location | Active / Conservative | More route/location constructions |
| Measurements | Active / Reviewed | More units and natural sentence QA |
| Grammar-bearing function words | Active / Reviewed | Expand categories without blind stopword deletion |
| Regional variants | Active / Growing | Larger pair-by-pair inventory |
| Vocabulary | Active / Growing | Promote more independently supported everyday words |
| Natural Somali corpus | Started / External pipeline audited | High-quality provenance-preserving conversational examples |
| Independent QA / holdouts | Growing | Much larger unseen assistant + language evaluation |
| Standalone Somali model training | Not started | Later, after stronger clean training data and evaluation |

## Important distinction

The repository now **uses a general reasoning model as the assistant brain**, but it does not yet train a standalone Somali LLM from scratch.

Current architecture:

```text
Somali user message
        ↓
conversation history + runtime context
        ↓
Somali evidence retrieval
        ↓
general reasoning model
        ↓
Somali-first generation instructions
        ↓
conservative Somali response checker
        ↓
final answer
```

This lets the project be useful now while the Somali-specific foundation continues improving.

## Current principles

- Evidence before trusted language rules.
- Never invent Somali words or paradigms from one example.
- Prefer unknown/context-required over unsafe correction.
- Preserve regional variation and source provenance.
- External candidates are clues, not automatic truth.
- Test new behavior against the full GitHub Actions suite.
- Keep QA/holdout data separate from the normal knowledge index.
- Build broad useful capabilities now, then continuously improve rare grammar and edge cases.

## Immediate priorities

1. Run the assistant against a real configured reasoning model and score the 60-task capability suite with human/native review.
2. Add high-quality natural Somali example/conversation evidence with provenance and license tracking.
3. Improve long-conversation memory/session behavior without contaminating reviewed language knowledge.
4. Continue large cross-source promotion passes across syntax, verbs, nouns, orthography, and regional variants.
5. Grow evaluation coverage before any claim that the system is complete or fully independent.
