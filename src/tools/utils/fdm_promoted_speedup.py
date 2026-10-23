"""Promoted-speedup qualifier lint for Forward Dynamics Matching chapters."""

from __future__ import annotations

import re

SPEEDUP_QUALIFIERS: tuple[str, ...] = (
    "diagnostic",
    "unmeasured",
    "synthetic-only",
    "decline to repeat",
    "declines to repeat",
    "not consistent",
    "discrepancy",
    "inconsisten",
    "per the cited",
    "the cited",
)

_TRIGGER_RE = re.compile(r"promot|speed-?up", re.IGNORECASE)
_FIGURE_RE = re.compile(r"\d")
_SKIP_PREFIXES = ("description:", "**Evidence")


def passage_has_speedup_qualifier(sentence: str) -> bool:
    """True when the sentence qualifies a promoted or speedup figure per book policy."""
    lowered = sentence.lower()
    return any(q in lowered for q in SPEEDUP_QUALIFIERS)


def lint_promoted_speedups(chapter_text: str) -> list[str]:
    """Return sentences that cite a promoted/speedup figure without an accepted qualifier."""
    flagged: list[str] = []
    for para in re.split(r"\n\s*\n", chapter_text):
        for sentence in re.split(r"(?<=[.!?])\s+", para):
            if not (_TRIGGER_RE.search(sentence) and _FIGURE_RE.search(sentence)):
                continue
            if sentence.lstrip().startswith(_SKIP_PREFIXES):
                continue
            if not passage_has_speedup_qualifier(sentence):
                flagged.append(sentence.strip())
    return flagged
