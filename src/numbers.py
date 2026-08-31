"""Evidence-constrained Somali cardinal-number analysis.

The analyzer recognizes only forms licensed by the reviewed number dataset:
base numerals, the documented 11-99 composition rule, 100, and explicitly
reviewed large-number expressions. It does not attempt open-ended parsing of
arbitrary large numbers.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

NUMBER_DATA_PATH = Path("data/vocabulary/somali_numbers.json")


@dataclass(frozen=True)
class NumberAnalysis:
    expression: str
    recognized: bool
    value: int | None
    form_type: str | None
    status: str
    executable: bool
    note: str


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().casefold())


def _load_data(path: str | Path = NUMBER_DATA_PATH) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _build_index(data: dict) -> dict[str, NumberAnalysis]:
    index: dict[str, NumberAnalysis] = {}

    def add(
        form: str,
        value: int,
        form_type: str,
        status: str,
        executable: bool = True,
        note: str = "",
    ) -> None:
        key = _normalize(form)
        index[key] = NumberAnalysis(
            expression=form,
            recognized=True,
            value=value,
            form_type=form_type,
            status=status,
            executable=executable,
            note=note,
        )

    units: dict[int, str] = {}
    ten_form: str | None = None
    for record in data["base_numbers"]:
        value = int(record["value"])
        canonical = record["canonical"]
        if 1 <= value <= 9:
            units[value] = canonical
        elif value == 10:
            ten_form = canonical
        add(
            canonical,
            value,
            "base_number",
            record["status"],
            note="Reviewed standalone/base numeral.",
        )
        for variant in record.get("variants", []):
            if value == 1 and variant == "hal":
                note = (
                    "Reviewed value 1 with usage restrictions: especially before a noun, "
                    "in digit sequences, and in some independent uses; complex numbers use kow."
                )
            else:
                note = "Reviewed standard/regional variant of the base numeral."
            add(variant, value, "base_number_variant", record["status"], note=note)

    if ten_form is None:
        raise ValueError("Reviewed number data is missing the base form for 10.")

    tens: dict[int, str] = {10: ten_form}
    for record in data["tens"]:
        value = int(record["value"])
        form = record["form"]
        tens[value] = form
        add(form, value, "tens", "reviewed", note="Reviewed multiple-of-ten numeral.")

    composition = data["composition_11_99"]
    for value in range(int(composition["range"][0]), int(composition["range"][1]) + 1):
        if value % 10 == 0:
            continue
        tens_value = (value // 10) * 10
        unit_value = value % 10
        unit = units[unit_value]
        tens_form = tens[tens_value]
        canonical = composition["canonical_pattern"].format(unit=unit, tens=tens_form)
        alternate = composition["recognized_variant_pattern"].format(unit=unit, tens=tens_form)
        add(
            canonical,
            value,
            "composed_11_99",
            "reviewed_compositional_rule",
            note="Generated only from the documented finite 11-99 numeral-composition rule.",
        )
        add(
            alternate,
            value,
            "composed_11_99_order_variant",
            "documented_order_variant",
            note="Recognized order variant; not an automatic correction target.",
        )

    hundred = data["hundred"]
    add(
        hundred["form"],
        int(hundred["value"]),
        "hundred",
        hundred["status"],
        note="Reviewed numeral.",
    )

    for record in data["reviewed_large_numbers"]:
        executable = bool(record.get("executable", True))
        for form in record["forms"]:
            add(
                form,
                int(record["value"]),
                "reviewed_large_number",
                record["status"],
                executable=executable,
                note=(
                    "Exact reviewed large-number expression."
                    if executable
                    else "Recognized from weaker evidence only; not executable for correction."
                ),
            )

    return index


def analyze_number_expression(
    expression: str,
    path: str | Path = NUMBER_DATA_PATH,
) -> NumberAnalysis:
    """Analyze one exact Somali cardinal-number expression.

    Unknown or not-yet-reviewed expressions remain unjudged. This function
    never rewrites a spelling and never extrapolates arbitrary large numbers.
    """
    normalized = _normalize(expression)
    data = _load_data(path)
    analysis = _build_index(data).get(normalized)
    if analysis is not None:
        return NumberAnalysis(
            expression=expression,
            recognized=True,
            value=analysis.value,
            form_type=analysis.form_type,
            status=analysis.status,
            executable=analysis.executable,
            note=analysis.note,
        )
    return NumberAnalysis(
        expression=expression,
        recognized=False,
        value=None,
        form_type=None,
        status="unknown_unjudged",
        executable=False,
        note="Expression is outside the reviewed number system; no number form is guessed.",
    )


def reviewed_forms_for_value(
    value: int,
    path: str | Path = NUMBER_DATA_PATH,
) -> tuple[str, ...]:
    """Return all currently recognized exact forms for a reviewed value."""
    data = _load_data(path)
    index = _build_index(data)
    return tuple(
        analysis.expression
        for analysis in index.values()
        if analysis.value == value
    )
