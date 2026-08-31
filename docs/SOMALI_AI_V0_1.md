# Somali AI Foundation v0.1

This layer turns the repository from a language-analysis library into a usable
Somali-first conversational assistant while keeping the evidence-first grammar
work intact.

## Goal

The assistant should be able to:

- hold a normal Somali conversation;
- understand informal Somali and ordinary spelling mistakes;
- answer general questions;
- explain ideas at different levels;
- compare choices and make plans;
- help write and revise Somali;
- use the repository's reviewed vocabulary, morphology, grammar, variants,
  numbers, dates, time, and orthography as extra language guidance.

It is **not** a claim that every Somali construction is solved. Unknown,
regional, ambiguous, and context-sensitive language remains labelled as such.

## Architecture

```text
user message
    -> retrieve relevant Somali evidence
    -> reasoning language model
    -> Somali-first generation instructions
    -> conservative orthography/variant checker
    -> final answer
```

The reasoning model supplies broad conversation and planning ability. The
repository supplies Somali-specific evidence and preferred output behavior.

## Evidence policy

Retrieval searches reviewed vocabulary, morphology, grammar, orthography, and
variant records. Small `data/imported/` candidate layers may also be retrieved,
but they are labelled `external_candidate` and must not override reviewed
project evidence.

The large SomNLP corpus is deliberately not loaded into the in-process
retriever. Corpus evidence belongs in sampled QA/frequency workflows so a
frequent error cannot become an automatic grammar rule.

## Run it

Python 3.12+ is sufficient. The production adapter uses the OpenAI Responses API
through the standard library.

```bash
export OPENAI_API_KEY="..."
# Optional:
export SOMALI_AI_MODEL="gpt-5.6-terra"

python somali_ai.py
```

You can also run:

```bash
python -m src.assistant
```

The default API request sets `store: false`. A different Responses-compatible
base can be configured with `OPENAI_BASE_URL`.

## Programmatic use

```python
from src.assistant import ConversationSession, OpenAIResponsesAdapter, SomaliAssistant

model = OpenAIResponsesAdapter.from_env()
assistant = SomaliAssistant(model)
chat = ConversationSession(assistant)

reply = chat.ask("Ii samee qorshe aan maanta wax ku barto.")
print(reply.text)
```

`AssistantResult` keeps an audit trail containing the model name, retrieved
knowledge paths, original draft, checker findings, and final text.

## What v0.1 does not do yet

- voice/audio input or speech output;
- web browsing or live external tools;
- training a standalone LLM from scratch;
- automatic promotion of imported evidence;
- claiming corpus frequency is grammatical correctness.

Those can be added as separate layers without weakening the evidence model.
