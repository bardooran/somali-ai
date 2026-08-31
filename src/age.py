"""Conservative Somali age-expression helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class AgeAnalysis:
    expression: str
    recognized: bool
    age: int | None
    status: str
    note: str


def format_age(age: int) -> str | None:
    """Return the reviewed Somali numeric age construction ``N jir``."""
    if age < 0:
        return None
    return f"{age} jir"


def analyze_age_expression(expression: str) -> AgeAnalysis:
    """Analyze exact numeric ``N jir`` age expressions without guessing ranges."""
    query = expression.strip()
    match = re.fullmatch(r"([0-9]+)\s+jir", query.casefold())
    if match is None:
        return AgeAnalysis(
            expression=query,
            recognized=False,
            age=None,
            status="unknown_unjudged",
            note="Only the reviewed numeric N jir age construction is analyzed; age-category labels require context.",
        )
    age = int(match.group(1))
    return AgeAnalysis(
        expression=query,
        recognized=True,
        age=age,
        status="reviewed_pattern",
        note="Reviewed Somali age construction, supported by University of Gothenburg teaching examples.",
    )
