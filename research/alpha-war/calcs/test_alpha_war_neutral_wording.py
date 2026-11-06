"""The Alpha War draft describes people and camps in neutral wording (#5365).

The review flagged loaded or adjectival characterizations ("ultimate casus belli", "famously",
"landmark", "The Irony of Figure 11"). This pins the flagged words and their near neighbours
out of the v1 draft, and checks the conflict-of-interest disclosure is in the preface with
the author's own analysis kept in its own section.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

DRAFT = Path(__file__).resolve().parent.parent / "draft" / "alpha-war-v1.md"
LOADED = (
    "casus belli",
    "famously",
    "landmark",
    "irony of figure 11",
    "seized upon",
    "most prominent",
    "founding studies",
    "founding paper",
    "legendary",
    "definitively proved",
)


class TestNeutralWording(unittest.TestCase):
    """Use assertTrue/assertFalse so a failure never diffs a whole chapter."""

    def setUp(self) -> None:
        self.text = DRAFT.read_text(encoding="utf-8")

    def test_no_loaded_characterizations(self) -> None:
        lowered = self.text.lower()
        found = [word for word in LOADED if word in lowered]
        self.assertEqual(found, [])

    def test_conflict_of_interest_is_disclosed_in_the_preface(self) -> None:
        preface = self.text.split("# Executive Summary", 1)[0]
        self.assertTrue("**Conflict of interest.**" in preface)

    def test_author_analysis_is_a_separate_top_level_section(self) -> None:
        heading = re.search(r"^# 5A\. Author Supplementary Analysis", self.text, re.M)
        self.assertTrue(heading is not None)


if __name__ == "__main__":
    unittest.main()
