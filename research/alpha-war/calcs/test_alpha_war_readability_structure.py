"""Pin the reader-facing structure of the Alpha War draft (#5369).

This pins what already holds (summary first, one-page verdict, early glossary link,
derivations in callouts). It does not replace the human readability review the issue
asks for.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

DRAFT = Path(__file__).resolve().parents[1] / "draft" / "alpha-war-v1.md"
#: One printed page of plain language (the paradox plus the verdict preview).
ONE_PAGE_WORDS = 500


def _section(text: str, start: str, end: str) -> str:
    """Return the text between the heading ``start`` and the heading ``end``."""
    return text.split(start, 1)[1].split(end, 1)[0]


class TestReadabilityStructure(unittest.TestCase):
    """The summary, glossary link and callouts that a lay reader needs are in place."""

    def setUp(self) -> None:
        """Load the draft once per test."""
        self.text = DRAFT.read_text(encoding="utf-8")

    def test_summary_precedes_chapter_one_and_has_both_layers(self) -> None:
        """The plain-language summary comes first and previews both verdict layers."""
        self.assertTrue(
            self.text.index("# Executive Summary (Plain Language)")
            < self.text.index("# 1. Problem Statement")
        )
        verdict = _section(self.text, "## The Two-Layer Verdict (Preview)", "\n## ")
        self.assertTrue("**Layer 1" in verdict)
        self.assertTrue("**Layer 2" in verdict)

    def test_paradox_and_verdict_fit_one_page(self) -> None:
        """The paradox plus the verdict preview stay within one page of words."""
        summary = _section(self.text, "# Executive Summary (Plain Language)", "\n# 1. ")
        paradox = _section(summary, "## The Core Paradox", "\n## The Three")
        verdict = _section(summary, "## The Two-Layer Verdict (Preview)", "\n## Document")
        self.assertTrue(len((paradox + verdict).split()) <= ONE_PAGE_WORDS)

    def test_glossary_is_linked_before_chapter_one_and_exists(self) -> None:
        """The first screen links the glossary, and the glossary has its four parts."""
        front = self.text.split("# 1. Problem Statement", 1)[0]
        self.assertTrue("[§9 Glossary](#9-glossary)" in front)
        glossary = _section(self.text, "# 9. Glossary {#9-glossary}", "\n# 10. ")
        self.assertTrue(len(re.findall(r"^## 9\.\d ", glossary, re.M)) >= 4)

    def test_derivations_sit_in_callouts_and_appendices(self) -> None:
        """Chapters carry derivation callouts and Appendices A to D exist."""
        self.assertTrue(len(re.findall(r"^:{3,4} \{\.callout", self.text, re.M)) >= 9)
        for letter in "ABCD":
            self.assertTrue(f"## Appendix {letter}:" in self.text, msg=letter)


if __name__ == "__main__":
    unittest.main()
