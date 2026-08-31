"""Evidence-backed Somali ordinal-number analysis.

Numeric ordinal notation with -aad is productive (for example 1aad, 2aad,
36-aad). Written-out ordinal words are only recognized when their exact form is
stored in reviewed evidence; this module does not guess unseen morphophonology.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ORDINAL_DATA_PATH = Path("data/vocabulary/somali_ordinals.json")
_NUMERIC_ORDINAL_RE = re.compile(r"^(?P<value>[0-9]+)(?P<hyphen>-?)aad$", re.IGNORECASE)


@dataclass(frozen=True)
class OrdinalAnalysis:
    expression: str
    recognized: bool
    value: int | None
    form_type: str | None
    status: str
    note: str


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().casefold())


def _load_data(path: str | Path = ORDINAL_DATA_PATH) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def analyze_ordinal(
    expression: str,
    path: str | Path = ORDINAL_DATA_PATH,
) -> OrdinalAnalysis:
    """Analyze one Somali ordinal expression conservatively."""
    query = expression.strip()
    numeric = _NUMERIC_ORDINAL_RE.fullmatch(query)
    if numeric:
        value = int(numeric.group("value"))
        if value >= 1:
            return OrdinalAnalysis(
                expression=query,
                recognized=True,
                value=value,
                form_type="numeric_ordinal_notation",
                status="reviewed_productive",
                note=(
                    "Productive numeric ordinal notation using -aad. Both attached "
                    "and hyphenated notation are recognized."
                ),
            )

    folded = _normalize(query)
    for record in _load_data(path)["exact_word_forms"]:
        for form in record["forms"]:
            if _normalize(form) == folded:
                note = "Exact reviewed written-out ordinal form."
                if int(record["value"]) == 7 and folded == "toddobaad":
                    note = (
                        "Exact reviewed ordinal 'seventh', but the same surface form "
                        "also means 'week'; sentence context is required."
                    )
                return OrdinalAnalysis(
                    expression=query,
                    recognized=True,
                    value=int(record["value"]),
                    form_type="written_ordinal",
                    status=record["status"],
                    note=note,
                )

    return OrdinalAnalysis(
        expression=query,
        recognized=False,
        value=None,
        form_type=None,
        status="unknown_unjudged",
        note=(
            "Ordinal form is outside the reviewed inventory. Numeric N-aad notation "
            "is productive, but unseen written-out ordinal morphology is not guessed."
        ),
    )


def format_numeric_ordinal(value: int, *, hyphenated: bool = False) -> str | None:
    """Format a positive integer using reviewed productive Somali N-aad notation."""
    if value < 1:
        return None
    return f"{value}{'-' if hyphenated else ''}aad"
