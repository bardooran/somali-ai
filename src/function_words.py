"""Grammar-aware Somali high-frequency/function-word lookup.

This is deliberately not a generic stopword-removal module. Somali particles,
clitics, focus markers, and connectives often carry essential grammar, so every
reviewed item is marked unsafe for blind deletion.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

FUNCTION_WORD_DATA_PATH = Path("data/vocabulary/somali_function_words.json")


@dataclass(frozen=True)
class FunctionWordAnalysis:
    form: str
    recognized: bool
    categories: tuple[str, ...]
    removal_safe: bool
    status: str
    note: str


def _load_data(path: str | Path = FUNCTION_WORD_DATA_PATH) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def analyze_function_word(
    form: str,
    path: str | Path = FUNCTION_WORD_DATA_PATH,
) -> FunctionWordAnalysis:
    """Classify a reviewed Somali grammatical/high-frequency word."""
    query = form.strip()
    folded = query.casefold()
    data = _load_data(path)

    for record in data["words"]:
        if record["form"].casefold() == folded:
            return FunctionWordAnalysis(
                form=query,
                recognized=True,
                categories=tuple(record["categories"]),
                removal_safe=bool(record["removal_safe"]),
                status="reviewed_grammar_word",
                note="Grammar-bearing high-frequency word; preserve it for grammar analysis.",
            )

    for record in data.get("submitted_but_not_function_words", []):
        if record["form"].casefold() == folded:
            return FunctionWordAnalysis(
                form=query,
                recognized=False,
                categories=(),
                removal_safe=False,
                status="excluded_from_function_word_inventory",
                note=record["reason"],
            )

    return FunctionWordAnalysis(
        form=query,
        recognized=False,
        categories=(),
        removal_safe=False,
        status="unknown_unjudged",
        note="Not in the reviewed grammatical function-word inventory.",
    )
