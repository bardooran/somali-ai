"""Conservative Somali pronoun–verb agreement analysis.

This module intentionally works on explicit pronoun/verb pairs rather than
trying to parse unrestricted Somali text. It only reports mismatches when both
the pronoun features and the verb form are present in reviewed project data.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PRONOUN_PATH = Path("rules/grammar/personal_pronouns.jsonl")
AGREEMENT_PATH = Path("rules/grammar/subject_verb_agreement.jsonl")


@dataclass(frozen=True)
class AgreementResult:
    pronoun: str
    verb: str
    known_pronoun: bool
    known_verb: bool
    agrees: bool | None
    expected_forms: tuple[str, ...]
    note: str


def _load_jsonl(path: str | Path) -> list[dict]:
    records: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def _subject_pronouns(records: Iterable[dict]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for record in records:
        if record.get("pronoun_type") != "independent":
            continue
        if "subject" not in record.get("role", []):
            continue
        result[record["form"].casefold()] = record
    return result


def _same_subject_features(pronoun: dict, subject: dict) -> bool:
    if int(subject.get("person")) != int(pronoun.get("person")):
        return False
    if subject.get("number") != pronoun.get("number"):
        return False
    subject_gender = subject.get("gender")
    if subject_gender and subject_gender != pronoun.get("gender"):
        return False
    return True


def _forms_for_subject(pronoun: dict, agreement_records: Iterable[dict]) -> set[str]:
    forms: set[str] = set()
    for record in agreement_records:
        if not _same_subject_features(pronoun, record.get("subject", {})):
            continue
        for key, value in record.get("verb_example", {}).items():
            if key == "lemma" or not isinstance(value, str):
                continue
            forms.add(value.casefold())
    return forms


def analyze_pronoun_verb(
    pronoun: str,
    verb: str,
    pronoun_path: str | Path = PRONOUN_PATH,
    agreement_path: str | Path = AGREEMENT_PATH,
) -> AgreementResult:
    """Compare a known independent subject pronoun with a known verb form.

    ``agrees`` is ``None`` when the project data is insufficient to decide.
    No correction is generated because the current agreement references are
    provisional and intentionally review-only.
    """
    pronouns = _subject_pronouns(_load_jsonl(pronoun_path))
    agreement_records = _load_jsonl(agreement_path)
    pronoun_record = pronouns.get(pronoun.casefold())

    all_known_forms = {
        value.casefold()
        for record in agreement_records
        for key, value in record.get("verb_example", {}).items()
        if key != "lemma" and isinstance(value, str)
    }

    if pronoun_record is None:
        return AgreementResult(
            pronoun=pronoun,
            verb=verb,
            known_pronoun=False,
            known_verb=verb.casefold() in all_known_forms,
            agrees=None,
            expected_forms=(),
            note="Pronoun is not covered by the current reviewed subject-pronoun data.",
        )

    expected = _forms_for_subject(pronoun_record, agreement_records)
    known_verb = verb.casefold() in all_known_forms
    if not known_verb:
        return AgreementResult(
            pronoun=pronoun,
            verb=verb,
            known_pronoun=True,
            known_verb=False,
            agrees=None,
            expected_forms=tuple(sorted(expected)),
            note="Verb form is outside the current reviewed agreement paradigms.",
        )

    agrees = verb.casefold() in expected
    return AgreementResult(
        pronoun=pronoun,
        verb=verb,
        known_pronoun=True,
        known_verb=True,
        agrees=agrees,
        expected_forms=tuple(sorted(expected)),
        note=(
            "Pronoun and verb match the reviewed agreement evidence."
            if agrees
            else "Pronoun and verb conflict within the reviewed agreement evidence; review required."
        ),
    )
