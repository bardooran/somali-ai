"""Evidence-backed Somali Gregorian-month and traditional-season lookup.

Month names are exact reviewed vocabulary. Somali traditional seasons are kept
separate from Western spring/summer/autumn/winter labels because their climate
meaning and boundaries are region-sensitive. Typical month alignments are
therefore descriptive, not automatic correction rules.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CALENDAR_TERMS_PATH = Path("data/vocabulary/somali_calendar_terms.jsonl")


@dataclass(frozen=True)
class CalendarTermAnalysis:
    expression: str
    recognized: bool
    calendar_type: str | None
    canonical_form: str | None
    month_number: int | None
    typical_month_numbers: tuple[int, ...]
    status: str
    note: str


def _load_records(path: str | Path = CALENDAR_TERMS_PATH) -> list[dict]:
    records: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def analyze_calendar_term(
    expression: str,
    path: str | Path = CALENDAR_TERMS_PATH,
) -> CalendarTermAnalysis:
    """Look up one exact reviewed Somali month or season term.

    Matching is case-insensitive, but the stored canonical spelling is returned.
    Unknown spellings remain unjudged rather than being normalized by guessing.
    """
    query = expression.strip()
    folded = query.casefold()
    for record in _load_records(path):
        if record.get("lemma", "").casefold() != folded:
            continue
        calendar_type = record.get("calendar_type")
        typical_months = tuple(int(value) for value in record.get("typical_month_numbers", []))
        if calendar_type == "month":
            note = "Reviewed Gregorian month name or documented spelling variant."
        else:
            note = (
                "Reviewed Somali seasonal term. Month alignment is approximate and "
                "region-sensitive; do not replace it mechanically with a Western season label."
            )
        return CalendarTermAnalysis(
            expression=query,
            recognized=True,
            calendar_type=calendar_type,
            canonical_form=record.get("canonical_form", record.get("lemma")),
            month_number=(
                int(record["month_number"])
                if record.get("month_number") is not None
                else None
            ),
            typical_month_numbers=typical_months,
            status=record.get("status", "reviewed"),
            note=note,
        )

    return CalendarTermAnalysis(
        expression=query,
        recognized=False,
        calendar_type=None,
        canonical_form=None,
        month_number=None,
        typical_month_numbers=(),
        status="unknown_unjudged",
        note="Calendar term is outside the reviewed dataset; no spelling or season is guessed.",
    )


def month_name(
    month_number: int,
    path: str | Path = CALENDAR_TERMS_PATH,
) -> str | None:
    """Return the project's reviewed canonical name for a Gregorian month."""
    if not 1 <= month_number <= 12:
        return None
    for record in _load_records(path):
        if (
            record.get("calendar_type") == "month"
            and record.get("month_number") == month_number
            and record.get("lemma") == record.get("canonical_form")
        ):
            return record["lemma"]
    return None


def typical_season_for_month(
    month_number: int,
    path: str | Path = CALENDAR_TERMS_PATH,
) -> tuple[str, ...]:
    """Return reviewed *approximate* Somali season alignment for a month.

    This is intentionally descriptive. Seasonal onset/end dates vary by year and
    region, and some Northwestern/Ethiopian Somali systems include additional
    rainy-season distinctions such as Karan.
    """
    if not 1 <= month_number <= 12:
        return ()
    seasons: list[str] = []
    for record in _load_records(path):
        if record.get("calendar_type") != "season":
            continue
        if record.get("lemma") != record.get("canonical_form"):
            continue
        months = {int(value) for value in record.get("typical_month_numbers", [])}
        if month_number in months:
            seasons.append(record["canonical_form"])
    return tuple(seasons)
