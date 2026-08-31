# Somali AI — Somali-First Language Intelligence

An evidence-based Somali language foundation and a working Somali-first AI assistant layer.

The project has two connected goals:

1. build reliable Somali grammar, morphology, vocabulary, regional-variant, corpus, and QA knowledge;
2. use that knowledge around a strong reasoning model so people can converse, ask questions, get explanations, compare choices, make plans, and improve Somali writing now.

Grammar is one subsystem inside the larger Somali AI foundation. The language engine remains conservative: unsupported forms stay unknown or context-dependent rather than being guessed.

## Somali AI v0.1

The repository now includes a conversational assistant under `src/assistant/`.

```text
Somali user message
       ↓
reviewed + candidate Somali knowledge retrieval
       ↓
general reasoning language model
       ↓
Somali-first generation instructions
       ↓
conservative Somali response checker
       ↓
final answer
```

The assistant prefers the reviewed **Jigjiga / Northwestern-Hargeisa** output profile while recognizing other supported Somali varieties.

This is not yet a standalone LLM trained from scratch. A general reasoning model supplies broad reasoning and conversation; this repository supplies Somali-specific evidence, preferences, checking, and evaluation. That lets the project be useful now while the Somali foundation keeps improving.

### Run in the terminal

```bash
export OPENAI_API_KEY="..."
python somali_ai.py
```

### Run as a local browser chat

```bash
export OPENAI_API_KEY="..."
python somali_ai_web.py
```

Then open `http://127.0.0.1:8080`.

Optional model override:

```bash
export SOMALI_AI_MODEL="gpt-5.6-terra"
```

See [`docs/SOMALI_AI_V0_1.md`](docs/SOMALI_AI_V0_1.md).

## Assistant evaluation

The repository includes a broad capability suite in:

`data/qa/somali_assistant_capabilities.jsonl`

It tests conversation, multi-turn memory, planning, explanations, comparisons, writing, Somali language help, reasoning, uncertainty, and regional behavior.

With a configured model:

```bash
python -m src.assistant.eval
```

The runner saves model outputs for review. Automated structural checks are deliberately **not** presented as a Somali correctness score; semantic/native-quality review remains explicit.

## External language evidence

Audited external projects are kept as candidate/evidence layers rather than silently becoming grammar truth:

- **GiellaLT Somali** — lexical and morphology discovery/cross-validation;
- **Somali Language Standard (SLS)** — structured grammar and orthography cross-validation;
- **SomNLP-Corpus** — natural-language corpus/QA/frequency workflows.

Candidate extraction is reproducible through `.github/workflows/refresh-external-candidates.yml`. Every generated external candidate preserves provenance and has `promotion_allowed: false` until reviewed.

The large SomNLP corpus is not dumped into this repository. It remains a corpus/QA source with per-source licensing.

## Core safety principle

**Do not invent Somali grammar or word forms.**

The project prefers:

- source-backed forms over guessed forms;
- exact reviewed morphology over blind suffix generation;
- `context_required` or unknown over unsafe correction;
- supported regional variation over falsely marking a valid form wrong;
- provenance-aware external candidates over untraceable bulk copying;
- unseen QA examples over testing only the sentences that created a rule.

## Current language foundation

Implemented or reviewed areas include:

- personal pronouns and subject clitics;
- subject–verb agreement;
- masculine/feminine and singular/plural agreement;
- noun subject forms and focus-sensitive case behavior;
- `baa` / `ayaa` focus constructions;
- object clitics such as `idin`;
- statement clitics such as `wuu`, `way`, `waan`, and `waad`;
- connective forms such as `wuuna`, `wayna`, and reviewed `wuxuuna` constructions;
- negation and negative agreement;
- future, habitual, imperative, jussive, dependent, and conditional patterns;
- possession and predicate/copula agreement;
- reviewed regular and irregular verb families;
- noun morphology and gender polarity;
- Jigjiga-first regional preference handling;
- vocabulary lookup;
- numbers and ordinals;
- dates, weekdays, months, seasons, relative time, and age;
- directions and measurements;
- grammar-bearing high-frequency/function words;
- real Somali corpus material and independent QA layers.

Coverage is intentionally open-ended. Unsupported forms remain unjudged until evidence improves.

## Repository layout

```text
somali-ai/
├── somali_ai.py             # terminal Somali AI
├── somali_ai_web.py         # local browser chat
├── check.py                 # grammar/orthography checker subsystem
├── src/
│   ├── assistant/           # conversation, retrieval, model, evaluation, web
│   └── ...                  # Somali analysis modules
├── rules/
│   ├── grammar/
│   ├── morphology/
│   ├── orthography/
│   └── variants/
├── data/
│   ├── vocabulary/
│   ├── morphology/
│   ├── corpus/
│   ├── qa/
│   ├── imported/            # non-promoting external candidates
│   └── sources/
├── tools/importers/
├── tests/
├── sources/
└── docs/
```

## Running the checker subsystem

```bash
python check.py "Somali text here"
```

## How knowledge becomes trusted behavior

```text
source / native review / real Somali text
                 ↓
        candidate / reviewed evidence
                 ↓
      conflict + lineage checking
                 ↓
        grammar/morphology rule
                 ↓
           analyzer/checker
                 ↓
       unseen tests + independent QA
                 ↓
      assistant retrieval/generation
```

Evidence does not automatically become a correction rule.

## Documentation

- [`docs/SOMALI_AI_V0_1.md`](docs/SOMALI_AI_V0_1.md) — conversational assistant
- [`docs/STATUS.md`](docs/STATUS.md) — project dashboard
- [`docs/REPO_MAP.md`](docs/REPO_MAP.md) — repository map
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — reviewed decisions
- [`docs/GRAMMAR_ANALYSIS.md`](docs/GRAMMAR_ANALYSIS.md) — grammar analysis
- [`docs/VOCABULARY_SCHEMA.md`](docs/VOCABULARY_SCHEMA.md) — vocabulary schema
