"""Conservative review detector for Somali baa/ayaa subject-clitic requirements.

This module implements only source-backed structures where omission of the
subject clitic is explicitly described as invalid. It does not rewrite text.
Optional clitic environments and true subject-focus ``SUBJECT + baa/ayaa`` are
intentionally kept separate.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.noun_gender_agreement import infer_subject_gender, infer_subject_number


TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿʼ’'-]+", re.UNICODE)

# Subject-marked independent forms documented across the SLS grammar examples.
FIRST_SECOND_SUBJECTS = {
    "anigu": "first_singular",
    "adigu": "second_singular",
    "annagu": "first_plural_exclusive",
    "innagu": "first_plural_inclusive",
    "idinku": "second_plural",
}

# Exact third-person proper-name evidence from the reviewed object-focus example
# ``Maryan muus bay cuntay``. Do not infer arbitrary proper-name gender.
REVIEWED_THIRD_PROPER_NAMES = {"maryan"}

# Third-person executable object-focus evidence is still lexically bounded in
# this layer. These focused-object heads have direct project/source review.
REVIEWED_FOCUSED_OBJECT_HEADS = {"muus", "moos", "cali"}

# Bare focus particles. Contracted forms such as baan/baad/buu/bay already
# contain a subject clitic and therefore are not violations of this rule.
BARE_FOCUS_PARTICLES = {"baa", "ayaa"}


@dataclass(frozen=True)
class FocusParticleFinding:
    subject: str
    particle: str
    subject_start: int
    particle_start: int
    rule_id: str
    note: str


def _reviewed_third_person_subject(form: str) -> bool:
    folded = form.casefold()
    if folded in REVIEWED_THIRD_PROPER_NAMES:
        return True

    number, _ = infer_subject_number(form)
    gender, _ = infer_subject_gender(form)
    if number == "plural":
        return True
    return number == "singular" and gender in {"masculine", "feminine"}


def scan_focus_particle_clitics(text: str) -> list[FocusParticleFinding]:
    """Find clear reviewed bare-baa/ayaa subject-clitic omissions.

    Supported shape::

        SUBJECT + focused material + baa/ayaa + following predicate material

    At least one token must occur between the explicit subject and the focus
    particle. This is crucial: adjacent ``Cali baa yimid``, ``Cali ayaa yimid``,
    ``Maryan baa qososhay`` and ``Maryan ayaa qososhay`` are true subject-focus
    examples and must not be flagged here.

    First/second-person reviewed subjects follow the existing SLS rule. For
    third-person subjects, execution is conservative: subject person/number must
    be independently reviewed and the focused-object head must be one of the
    directly reviewed object-focus items. The detector never infers a rewrite.
    """
    tokens = list(TOKEN_RE.finditer(text))
    findings: list[FocusParticleFinding] = []

    for index, match in enumerate(tokens):
        subject = match.group(0)
        subject_key = subject.casefold()
        first_second = subject_key in FIRST_SECOND_SUBJECTS
        reviewed_third = _reviewed_third_person_subject(subject)
        if not first_second and not reviewed_third:
            continue

        # Keep the executable pattern local: one to four focused tokens may
        # occur before bare baa/ayaa. Starting at index+2 intentionally excludes
        # adjacent true subject focus.
        upper = min(len(tokens), index + 6)
        for particle_index in range(index + 2, upper):
            particle_match = tokens[particle_index]
            particle = particle_match.group(0)
            if particle.casefold() not in BARE_FOCUS_PARTICLES:
                continue

            # Require predicate material after the particle; sentence-final baa
            # or ayaa alone is not enough evidence for this rule.
            if particle_index + 1 >= len(tokens):
                break

            focused_tokens = [
                token.group(0).casefold() for token in tokens[index + 1 : particle_index]
            ]
            if reviewed_third and not first_second:
                # Do not turn every third-person non-adjacent baa/ayaa phrase into
                # an object-focus claim. Require a directly reviewed focused-object
                # head in the intervening material.
                if not focused_tokens or focused_tokens[0] not in REVIEWED_FOCUSED_OBJECT_HEADS:
                    continue
                rule_id = "GRAM-FOCUS-001"
                note = (
                    "Reviewed third-person subject precedes a separately focused object. "
                    "The reviewed structure requires the matching subject clitic (for example "
                    "buu/bay/ayuu/ayay) rather than bare baa/ayaa. True adjacent subject focus "
                    "is a different construction."
                )
            else:
                rule_id = "GRAM-FOCUS-004"
                note = (
                    "First/second-person subject with baa/ayaa focusing a non-subject "
                    "requires a subject clitic in the reviewed SLS structure."
                )

            findings.append(
                FocusParticleFinding(
                    subject=subject,
                    particle=particle,
                    subject_start=match.start(),
                    particle_start=particle_match.start(),
                    rule_id=rule_id,
                    note=note,
                )
            )
            break

    return findings
