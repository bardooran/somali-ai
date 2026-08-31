"""Shared integration-level grammar decision statuses.

Individual analyzers answer narrow questions. A recognized construction must not
be presented as proof that the whole sentence is correct. This module provides a
small shared vocabulary for combining analyzer signals without erasing uncertainty.

Statuses:
- ``supported``: the reviewed construction has no conflict in the checks that ran.
- ``review``: a supported local conflict or structural problem was found.
- ``context_required``: the construction may be grammatical, but interpretation
  depends on discourse/context (for example, an intentional subject switch).
- ``unjudged``: the available reviewed evidence is insufficient for a safe call.

``supported`` is deliberately construction-level. It never means that every
part of the sentence has been proved correct.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.connective_waxaa_focus import ConnectiveWaxaaFocusAnalysis


STATUS_PRIORITY = {
    "supported": 0,
    "unjudged": 1,
    "context_required": 2,
    "review": 3,
}


@dataclass(frozen=True)
class GrammarDecision:
    status: str
    reasons: tuple[str, ...] = ()
    rule_ids: tuple[str, ...] = ()

    @property
    def needs_review(self) -> bool:
        return self.status in {"review", "context_required"}

    @property
    def is_supported(self) -> bool:
        return self.status == "supported"


def _unique(items: Iterable[str | None]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return tuple(result)


def classify_connective_waxaa_focus(
    result: ConnectiveWaxaaFocusAnalysis,
) -> GrammarDecision:
    """Convert a narrow waxaa-connective analysis into a shared decision.

    Hard/local evidence outranks discourse uncertainty. Thus a local finite-verb
    mismatch or missing reviewed final-focus tail is ``review`` even if the same
    sentence also contains a possible subject switch. A pure subject-switch
    signal remains ``context_required`` because a deliberate switch can be
    grammatical. Unknown finite morphology remains ``unjudged``.
    """
    if not result.recognized:
        return GrammarDecision(
            status="unjudged",
            reasons=("construction_not_recognized",),
        )

    reasons: list[str] = []
    rule_ids: list[str | None] = [result.rule_id]

    if result.agreement_agrees is False:
        reasons.append("local_subject_verb_agreement_conflict")

    if result.focus_structure_agrees is False:
        reasons.append("missing_final_focus_material")
        rule_ids.append(result.focus_rule_id)

    if result.same_subject_continuity_agrees is False:
        reasons.append("possible_subject_switch")
        rule_ids.append(result.continuity_rule_id)

    if (
        "local_subject_verb_agreement_conflict" in reasons
        or "missing_final_focus_material" in reasons
    ):
        status = "review"
    elif "possible_subject_switch" in reasons:
        status = "context_required"
    elif result.subject_persons and result.agreement_agrees is None:
        status = "unjudged"
        reasons.append("finite_morphology_unjudged")
    elif result.subject_persons and result.verb and result.focus_structure_agrees is None:
        status = "unjudged"
        reasons.append("focus_structure_unjudged")
    else:
        status = "supported"
        reasons.append("reviewed_construction_supported")

    return GrammarDecision(
        status=status,
        reasons=_unique(reasons),
        rule_ids=_unique(rule_ids),
    )


def combine_decisions(decisions: Iterable[GrammarDecision]) -> GrammarDecision:
    """Combine narrow analyzer decisions while preserving the strongest caution."""
    items = list(decisions)
    if not items:
        return GrammarDecision(
            status="unjudged",
            reasons=("no_analyzer_decision",),
        )

    strongest = max(items, key=lambda item: STATUS_PRIORITY[item.status]).status
    return GrammarDecision(
        status=strongest,
        reasons=_unique(reason for item in items for reason in item.reasons),
        rule_ids=_unique(rule_id for item in items for rule_id in item.rule_ids),
    )
