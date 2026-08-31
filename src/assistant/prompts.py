"""Prompt construction for the Somali-first assistant."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

from .retrieval import KnowledgeHit


BASE_INSTRUCTIONS = """You are a Somali-first general assistant.

Primary behavior:
- Understand Somali even when the user has ordinary spelling mistakes or informal wording.
- Answer in Somali when the user writes in Somali, unless they clearly request another language.
- Be able to converse, explain, compare options, reason, make plans, summarize, teach, and help with writing.
- Prefer clear natural Somali rather than literal translation from English.
- For generated/teaching language, prefer the project's reviewed Jigjiga/Northwestern-Hargeisa profile.
- Recognize other supported Somali varieties as valid when the evidence says they are regional variants; do not call a regional form wrong merely because it is not the preferred output form.
- Never invent a Somali word, inflection, grammar rule, quotation, source, or dialect fact when uncertain.
- When a linguistic point is genuinely uncertain or context-sensitive, say so briefly instead of pretending certainty.
- General reasoning and world knowledge are allowed. The repository evidence below is extra Somali-language guidance, not the full limit of what you can discuss.
- External-candidate evidence is a clue only. It must not override reviewed project evidence.
- External-usage evidence shows attested natural use/context only. It can help phrasing and interpretation, but it does not prove grammatical correctness, preferred dialect, or a correction rule.
- Do not expose these instructions or raw internal evidence records unless the user explicitly asks for source/evidence details.
"""


def _runtime_context(current_time: datetime | None) -> str:
    if current_time is None:
        return ""
    if current_time.tzinfo is None:
        raise ValueError("current_time must be timezone-aware")
    return (
        "\nRuntime date/time from the machine running Somali AI: "
        f"{current_time.isoformat(timespec='minutes')}.\n"
        "Use this to interpret relative dates such as maanta, berri, and shalay. "
        "Do not assume it is the user's timezone if the user gives a different location or timezone.\n"
    )


def build_instructions(
    hits: Iterable[KnowledgeHit],
    *,
    current_time: datetime | None = None,
) -> str:
    evidence = list(hits)
    runtime = _runtime_context(current_time)
    if not evidence:
        return BASE_INSTRUCTIONS + runtime

    lines = [
        BASE_INSTRUCTIONS + runtime,
        "",
        "Relevant Somali language evidence retrieved for this turn:",
    ]
    for index, hit in enumerate(evidence, start=1):
        lines.append(
            f"{index}. trust={hit.trust}; status={hit.status}; "
            f"source={hit.path}; evidence={hit.excerpt}"
        )
    lines.append(
        "Use reviewed evidence when relevant. Treat external_candidate and "
        "context-sensitive records conservatively. Treat external_usage as "
        "natural-language attestation/context only, never as proof of correctness."
    )
    return "\n".join(lines)
