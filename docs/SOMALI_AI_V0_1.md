# Somali AI Foundation v0.1

This layer turns the repository from a language-analysis library into a usable Somali-first conversational assistant while keeping the evidence-first grammar work intact.

## What it can do

With a configured reasoning model, the assistant can hold multi-turn conversations, answer general questions, explain ideas, compare options, make plans, help with writing, and use the repository's Somali language evidence as extra guidance.

The preferred generation profile is **Jigjiga / Northwestern-Hargeisa**. Supported regional alternatives remain valid recognition targets.

## Architecture

```text
user message
    -> retrieve relevant Somali evidence
    -> reasoning language model
    -> Somali-first generation instructions
    -> conservative orthography/variant checker
    -> final answer
```

The reasoning model provides broad reasoning and world knowledge. The repository provides Somali-specific evidence, regional preferences, checking, provenance, and evaluation.

## Evidence policy

Retrieval searches reviewed vocabulary, morphology, grammar, orthography, and variant records. `data/imported/` records can also be retrieved but are labelled `external_candidate` and cannot override reviewed project evidence.

Current reproducible external extraction includes GiellaLT lexical/morphology candidates and SLS rule candidates. All generated records preserve exact source commit/path metadata and have `promotion_allowed: false`.

The large SomNLP corpus is deliberately not loaded into every assistant turn. Corpus evidence belongs in sampled QA, usage, and frequency workflows so a frequent error cannot automatically become a grammar rule.

## Terminal chat

```bash
export OPENAI_API_KEY="..."
python somali_ai.py
```

or:

```bash
python -m src.assistant
```

Commands: `/clear`, `/quit`.

## Browser chat

```bash
export OPENAI_API_KEY="..."
python somali_ai_web.py
```

Open `http://127.0.0.1:8080`.

The web server binds to localhost by default and stores conversation history only in process memory.

## Model configuration

The production adapter uses the OpenAI Responses API through Python's standard library.

Environment variables:

- `OPENAI_API_KEY` — required for the OpenAI adapter;
- `SOMALI_AI_MODEL` — optional model override;
- `OPENAI_BASE_URL` — optional Responses-compatible base URL.

The request sets `store: false`.

## Capability evaluation

`data/qa/somali_assistant_capabilities.jsonl` contains a broad Somali capability suite, including:

- ordinary conversation;
- multi-turn context memory;
- planning and scheduling;
- explanations at different levels;
- comparison and decision support;
- writing and rewriting;
- Somali grammar/language questions;
- arithmetic and simple reasoning;
- uncertainty handling;
- Jigjiga/Northwestern and regional-variation behavior.

Run real model outputs through it with:

```bash
python -m src.assistant.eval
```

Optional:

```bash
python -m src.assistant.eval --limit 10 --output reports/assistant_smoke.jsonl
```

Every case carries human-review criteria. The harness performs objective structural checks but deliberately does not call response length or keyword matching a Somali correctness score.

## Programmatic use

```python
from src.assistant import ConversationSession, OpenAIResponsesAdapter, SomaliAssistant

model = OpenAIResponsesAdapter.from_env()
assistant = SomaliAssistant(model)
chat = ConversationSession(assistant)

reply = chat.ask("Ii samee qorshe aan maanta wax ku barto.")
print(reply.text)
```

`AssistantResult` retains the original draft, final checked text, checker findings, model name, and the project evidence paths retrieved for the turn.

## What v0.1 is not

- It is not a standalone Somali LLM trained from scratch.
- It does not claim all Somali grammar is solved.
- It does not automatically promote imported evidence.
- It does not equate corpus frequency with correctness.
- It does not yet include speech-to-text or voice output.

Those are separate layers that can be added without weakening the evidence model.
