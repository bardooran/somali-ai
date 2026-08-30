"""Conservative Somali subject-marker–verb agreement analysis.

This module intentionally works on explicit subject-marker/verb pairs rather
than trying to parse unrestricted Somali text. A surface subject marker may
have more than one grammatical analysis (for example, ``ay`` can represent
more than one subject feature set), so analyses are retained rather than
silently overwritten. Context-required records remain reference evidence and
do not participate in executable agreement decisions.
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
    analyses_count: int = 0

def _load_jsonl(path: str | Path) -> list[dict]:
    records: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records

def _subject_pronouns(records: Iterable[dict]) -> dict[str, list[dict]]:
    """Return executable subject analyses for each surface form."""
    result: dict[str, list[dict]] = {}
    for record in records:
        if record.get("status") == "context_required":
            continue
        is_independent_subject = (
            record.get("pronoun_type") == "independent"
            and "subject" in record.get("role", [])
        )
        is_subject_clitic = record.get("category") == "subject_clitic"
        if not (is_independent_subject or is_subject_clitic):
            continue
        result.setdefault(record["form"].casefold(), []).append(record)
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

def analyze_pronoun_verb(pronoun: str, verb: str, pronoun_path: str | Path = PRONOUN_PATH, agreement_path: str | Path = AGREEMENT_PATH) -> AgreementResult:
    """Compare an executable subject marker with a reviewed verb form."""
    pronouns = _subject_pronouns(_load_jsonl(pronoun_path))
    agreement_records = _load_jsonl(agreement_path)
    pronoun_records = pronouns.get(pronoun.casefold(), [])
    all_known_forms = {
        value.casefold()
        for record in agreement_records
        for key, value in record.get("verb_example", {}).items()
        if key != "lemma" and isinstance(value, str)
    }
    if not pronoun_records:
        return AgreementResult(pronoun, verb, False, verb.casefold() in all_known_forms, None, (), "Subject marker is not covered by the current executable pronoun/clitic data.", 0)
    expected: set[str] = set()
    for pronoun_record in pronoun_records:
        expected.update(_forms_for_subject(pronoun_record, agreement_records))
    known_verb = verb.casefold() in all_known_forms
    if not known_verb:
        return AgreementResult(pronoun, verb, True, False, None, tuple(sorted(expected)), "Verb form is outside the current reviewed agreement paradigms.", len(pronoun_records))
    agrees = verb.casefold() in expected
    ambiguity_note = " Surface marker has multiple reviewed subject analyses." if len(pronoun_records) > 1 else ""
    note = ("Subject marker and verb match the reviewed agreement evidence." if agrees else "Subject marker and verb conflict within the reviewed agreement evidence; review required.") + ambiguity_note
    return AgreementResult(pronoun, verb, True, True, agrees, tuple(sorted(expected)), note, len(pronoun_records))
