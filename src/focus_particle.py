"""Conservative review detector for Somali baa/ayaa subject-clitic requirements.

This module implements only source-backed structures where omission of the
subject clitic is explicitly described as invalid. It does not rewrite text.
Optional clitic environments are intentionally ignored.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿʼ’'-]+", re.UNICODE)

# Subject-marked independent forms documented across the SLS grammar examples.
# This first executable layer is limited to first/second person, for which the
# source says the clitic is required regardless of subject position in the
# described baa/ayaa focus constructions.
FIRST_SECOND_SUBJECTS = {
    "anigu": "first_singular",
    "adigu": "second_singular",
    "annagu": "first_plural_exclusive",
    "innagu": "first_plural_inclusive",
    "idinku": "second_plural",
}

# Bare focus particles. Contracted forms such as baan/baad already contain a
# subject clitic and therefore are not violations of this particular rule.
BARE_FOCUS_PARTICLES = {"baa", "ayaa"}


@dataclass(frozen=True)
class FocusParticleFinding:
    subject: str
    particle: str
    subject_start: int
    particle_start: int
    rule_id: str
    note: str


def scan_focus_particle_clitics(text: str) -> list[FocusParticleFinding]:
    """Find clear first/second-person bare-baa/ayaa clitic omissions.

    Current supported shape:
        SUBJECT + focused material + baa/ayaa + following predicate material

    At least one token must occur between the explicit subject and the focus
    particle. This avoids flagging examples such as ``Adiga baa moos cunay``,
    where baa may be focusing the subject itself rather than a non-subject NP.

    The detector is review-only and deliberately does not infer a correction.
    """
    tokens = list(TOKEN_RE.finditer(text))
    findings: list[FocusParticleFinding] = []

    for index, match in enumerate(tokens):
        subject = match.group(0)
        if subject.casefold() not in FIRST_SECOND_SUBJECTS:
            continue

        # Keep this first executable pattern local and simple: one to four
        # tokens of focused material may occur before bare baa/ayaa.
        upper = min(len(tokens), index + 6)
        for particle_index in range(index + 2, upper):
            particle_match = tokens[particle_index]
            particle = particle_match.group(0)
            if particle.casefold() not in BARE_FOCUS_PARTICLES:
                continue

            # Require predicate material after the particle; sentence-final baa
            # alone is not enough evidence for this rule.
            if particle_index + 1 >= len(tokens):
                break

            findings.append(
                FocusParticleFinding(
                    subject=subject,
                    particle=particle,
                    subject_start=match.start(),
                    particle_start=particle_match.start(),
                    rule_id="GRAM-FOCUS-004",
                    note=(
                        "First/second-person subject with baa/ayaa focusing a non-subject "
                        "requires a subject clitic in the reviewed SLS structure."
                    ),
                )
            )
            break

    return findings
