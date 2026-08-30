"""Role-aware checks for reviewed Somali sentence constructions.

The analyzer verifies grammatical roles in a very small set of native-reviewed
patterns. In particular, object clitics such as ``idin`` and ``na`` must not be
mistaken for subject agreement controllers. Unknown constructions are left
unjudged and no automatic rewrite is produced.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.clitic_roles import analyze_clitic_role


@dataclass(frozen=True)
class RoleAwareSentenceResult:
    sentence: str
    recognized: bool
    agrees: bool | None
    subject: str | None
    subject_gender: str | None
    object_clitic: str | None
    verb: str | None
    expected_verb: str | None
    note: str


_TOKEN_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)?", re.UNICODE)

_REVIEWED = {
    ("libaaxu", "idin"): ("masculine", "eryanayaa"),
    ("libaaxadu", "idin"): ("feminine", "eryanaysaa"),
    ("libaaxu", "na"): ("masculine", "eryanayaa"),
    ("libaaxadu", "na"): ("feminine", "eryanaysaa"),
}


def _tokens(sentence: str) -> list[str]:
    return [token.casefold() for token in _TOKEN_RE.findall(sentence)]


def analyze_role_aware_sentence(sentence: str) -> RoleAwareSentenceResult:
    tokens = _tokens(sentence)
    if not tokens:
        return RoleAwareSentenceResult(sentence, False, None, None, None, None, None, None, "Empty sentence.")

    subject = tokens[0]
    object_clitic = next((token for token in tokens[1:] if token in {"idin", "na"}), None)
    if object_clitic is None:
        # Surface maydin fuses a question element with idin in reviewed data.
        object_clitic = "idin" if "maydin" in tokens else None

    key = (subject, object_clitic) if object_clitic else None
    reviewed = _REVIEWED.get(key) if key else None
    if reviewed is None:
        return RoleAwareSentenceResult(
            sentence, False, None, subject if subject else None, None, object_clitic, tokens[-1] if tokens else None, None,
            "Sentence is outside the current reviewed role-aware templates.",
        )

    role = analyze_clitic_role(object_clitic)
    if not role.recognized or "object" not in role.allowed_roles or not role.executable:
        return RoleAwareSentenceResult(
            sentence, True, None, subject, reviewed[0], object_clitic, tokens[-1], reviewed[1],
            "The clitic role is not executable under the current evidence; sentence remains unjudged.",
        )

    gender, expected_verb = reviewed
    verb = tokens[-1]
    known_pair = {"eryanayaa", "eryanaysaa"}
    if verb not in known_pair:
        return RoleAwareSentenceResult(
            sentence, True, None, subject, gender, object_clitic, verb, expected_verb,
            "Subject/object roles are recognized, but this verb form is outside the reviewed gender contrast.",
        )

    agrees = verb == expected_verb
    return RoleAwareSentenceResult(
        sentence, True, agrees, subject, gender, object_clitic, verb, expected_verb,
        (
            "Reviewed subject gender controls the verb; the object clitic does not control agreement."
            if agrees
            else "Reviewed subject gender conflicts with the verb. The object clitic is an object and must not control agreement."
        ),
    )
