"""Conservative Somali measurement-unit analysis.

The module recognizes reviewed unit names/variants and common metric symbols.
It parses quantities but does not perform unit conversion or invent corrections.
Candidate spellings marked non-executable remain recognizable only as evidence.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

MEASUREMENT_DATA_PATH = Path("data/vocabulary/somali_measurement_terms.jsonl")
_MEASUREMENT_RE = re.compile(r"^\s*(?P<quantity>[+-]?(?:\d+(?:[.,]\d+)?))\s*(?P<unit>[^\d\s].*?)\s*$")
_TEMPERATURE_SYMBOL_RE = re.compile(r"^\s*(?P<quantity>[+-]?(?:\d+(?:[.,]\d+)?))\s*°\s*[cC]\s*$")


@dataclass(frozen=True)
class MeasurementAnalysis:
    expression: str
    recognized: bool
    quantity: str | None
    unit: str | None
    canonical_form: str | None
    symbol: str | None
    domain: str | None
    status: str
    executable: bool
    note: str


def _load_records(path: str | Path = MEASUREMENT_DATA_PATH) -> list[dict]:
    records: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def _match_unit(unit_text: str, records: list[dict]) -> dict | None:
    folded = unit_text.strip().casefold()
    # Prefer lexical form matches before symbol matches so ambiguous one-letter
    # strings do not override full Somali words.
    for record in records:
        if record.get("lemma", "").casefold() == folded:
            return record
    for record in records:
        symbol = record.get("symbol")
        if symbol and symbol.casefold() == folded:
            return record
    return None


def analyze_measurement(
    expression: str,
    path: str | Path = MEASUREMENT_DATA_PATH,
) -> MeasurementAnalysis:
    """Analyze a Somali metric measurement expression without conversion."""
    query = expression.strip()
    temp = _TEMPERATURE_SYMBOL_RE.fullmatch(query)
    if temp:
        return MeasurementAnalysis(
            expression=query,
            recognized=True,
            quantity=temp.group("quantity"),
            unit="celsius",
            canonical_form="°C",
            symbol="°C",
            domain="temperature",
            status="reviewed_symbol_notation",
            executable=True,
            note=(
                "Celsius symbol notation is recognized. The project does not yet "
                "force one Somali lexical name for Celsius because submitted "
                "'Selsiyas' still needs stronger independent evidence."
            ),
        )

    match = _MEASUREMENT_RE.fullmatch(query)
    if not match:
        return MeasurementAnalysis(query, False, None, None, None, None, None, "unknown_unjudged", False, "Not a reviewed measurement expression.")

    quantity = match.group("quantity")
    record = _match_unit(match.group("unit"), _load_records(path))
    if record is None:
        return MeasurementAnalysis(query, False, quantity, None, None, None, None, "unknown_unjudged", False, "Measurement unit is outside the reviewed inventory; no spelling is guessed.")

    executable = bool(record.get("executable", True))
    return MeasurementAnalysis(
        expression=query,
        recognized=True,
        quantity=quantity,
        unit=record.get("unit") or record.get("meaning"),
        canonical_form=record.get("canonical_form", record.get("lemma")),
        symbol=record.get("symbol"),
        domain=record.get("domain"),
        status=record.get("status", "reviewed"),
        executable=executable,
        note=(
            "Reviewed measurement unit or documented variant."
            if executable
            else "Stored project candidate only; not correction/generation authority."
        ),
    )
