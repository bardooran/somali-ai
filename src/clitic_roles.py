"""Conservative Somali clitic-role lookup.

This module exposes only explicitly recorded role constraints. Ambiguous
subject clitics preserve all documented analyses; context-required forms are
never promoted to executable grammar rules.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CLITIC_ROLE_PATH = Path("rules/grammar/clitic_role_constraints.jsonl")


@dataclass(frozen=True)
class CliticRoleAnalysis:
    surface: str
    recognized: bool
    status: str | None
    allowed_roles: tuple[str, ...]
    analyses: tuple[dict, ...]
    executable: bool
    note: str


def _load(path: str | Path = CLITIC_ROLE_PATH) -> list[dict]:
    records: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def analyze_clitic_role(surface: str, path: str | Path = CLITIC_ROLE_PATH) -> CliticRoleAnalysis:
    normalized = surface.casefold().strip()
    for record in _load(path):
        if record.get("surface", "").casefold() != normalized:
            continue
        analyses = record.get("person_analyses")
        if analyses is None:
            analyses = [
                {
                    key: record[key]
                    for key in ("person", "number", "gender", "clusivity")
                    if key in record
                }
            ]
        status = record.get("status")
        return CliticRoleAnalysis(
            surface=surface,
            recognized=True,
            status=status,
            allowed_roles=tuple(record.get("allowed_roles", [])),
            analyses=tuple(analyses),
            executable=status != "context_required",
            note=record.get("note", ""),
        )
    return CliticRoleAnalysis(surface, False, None, (), (), False, "Clitic is outside the current reviewed role constraints.")
