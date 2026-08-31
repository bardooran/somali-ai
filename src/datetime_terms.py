"""Evidence-constrained Somali date and relative-time helpers.

This module handles Gregorian weekday/date display, exact reviewed relative-day
terms, and a small reviewed set of relative-duration patterns. Clock-hour
conversion is deliberately excluded because Somali sources show more than one
clock convention; the project must not guess between them.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from src.calendar_terms import month_name

DATETIME_TERMS_PATH = Path("data/vocabulary/somali_datetime_terms.jsonl")


@dataclass(frozen=True)
class RelativeDayAnalysis:
    expression: str
    recognized: bool
    offset_days: int | None
    canonical_form: str | None
    status: str
    executable: bool
    note: str


def _load_records(path: str | Path = DATETIME_TERMS_PATH) -> list[dict]:
    records: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def weekday_name(value: date | datetime, path: str | Path = DATETIME_TERMS_PATH) -> str | None:
    """Return the reviewed project display form for a Gregorian weekday."""
    index = value.weekday()
    for record in _load_records(path):
        if record.get("calendar_type") == "weekday" and record.get("weekday_index") == index:
            if record.get("lemma") == record.get("canonical_form"):
                return record["lemma"]
    return None


def format_gregorian_date(value: date | datetime) -> str | None:
    """Format a Gregorian date as ``Weekday, D Month YYYY`` in Somali."""
    weekday = weekday_name(value)
    month = month_name(value.month)
    if weekday is None or month is None:
        return None
    return f"{weekday}, {value.day} {month} {value.year}"


def analyze_relative_day(expression: str, path: str | Path = DATETIME_TERMS_PATH) -> RelativeDayAnalysis:
    """Analyze one exact reviewed relative-day expression."""
    query = expression.strip()
    folded = query.casefold()
    for record in _load_records(path):
        if record.get("source_pos") != "relative_day":
            continue
        if record.get("lemma", "").casefold() != folded:
            continue
        executable = bool(record.get("executable", True))
        return RelativeDayAnalysis(
            expression=query,
            recognized=True,
            offset_days=int(record["offset_days"]),
            canonical_form=record.get("canonical_form", record["lemma"]),
            status=record.get("status", "reviewed"),
            executable=executable,
            note=(
                "Reviewed relative-day term."
                if executable
                else "Stored candidate/variant evidence only; not safe for automatic generation or correction."
            ),
        )
    return RelativeDayAnalysis(
        expression=query,
        recognized=False,
        offset_days=None,
        canonical_form=None,
        status="unknown_unjudged",
        executable=False,
        note="Relative-day expression is outside the reviewed dataset; no offset is guessed.",
    )


def relative_day_for_offset(offset_days: int) -> str | None:
    """Return a reviewed executable relative-day term for a small exact offset."""
    preferred = {0: "maanta", -1: "shalay", 1: "berri", -2: "dorraad", 2: "saadambe", 3: "saakuun"}
    form = preferred.get(offset_days)
    if form is None:
        return None
    analysis = analyze_relative_day(form)
    return analysis.canonical_form if analysis.recognized and analysis.executable else None


def _unit_form(count: int, unit: str) -> str | None:
    if count < 1:
        return None
    singular = {
        "second": "ilbiriqsi",
        "minute": "daqiiqo",
        "hour": "saac",
        "day": "maalin",
        "week": "toddobaad",
        "month": "bil",
        "year": "sano",
    }
    multiple = {
        "second": "ilbiriqsi",
        "minute": "daqiiqo",
        "hour": "saacadood",
        "day": "maalmood",
        "week": "toddobaad",
        "month": "bilood",
        "year": "sano",
    }
    table = singular if count == 1 else multiple
    return table.get(unit)


def format_relative_duration(count: int, unit: str, direction: str) -> str | None:
    """Format a small reviewed relative-duration construction.

    ``direction`` is ``past`` or ``future``. This is a grammatical phrase
    formatter, not a datetime-difference calculator.
    """
    form = _unit_form(count, unit)
    if form is None:
        return None
    if direction == "past":
        return f"{count} {form} ka hor"
    if direction == "future":
        return f"{count} {form} ka dib"
    return None


def format_duration(count: int, unit: str) -> str | None:
    """Format a reviewed count + time-unit duration phrase."""
    form = _unit_form(count, unit)
    return f"{count} {form}" if form is not None else None
