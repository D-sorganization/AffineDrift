"""Pin the Nesbit (2005) claims to what the primary JSSM texts say (#5364).

Primary sources (open access, read 2026-11-06):
- Nesbit (2005) JSSM 4(4):499-519, https://www.jssm.org/vol4/n4/17/v4n4-17text.php
- Nesbit & Serrano (2005) JSSM 4(4):520-533, https://www.jssm.org/vol4/n4/18/v4n4-18text.php

Findings are recorded in ``work/audit-5364-nesbit-primary-check.md``.
"""

from __future__ import annotations

import unittest
from pathlib import Path

ALPHA_WAR_DIR = Path(__file__).resolve().parent.parent
DRAFT = ALPHA_WAR_DIR / "draft" / "alpha-war-v1.md"
CLAIMS = ALPHA_WAR_DIR / "work" / "03_claims.md"

# Nesbit & Serrano (2005), p. 531, Discussion, verbatim.
NESBIT_QUOTE = (
    "Because the wrist joints cannot keep up with the angular speed of the club, "
    "they actually retard the angular motion of the club just prior to impact resulting "
    "in the straightening of the club and the release of its stored strain energy."
)


def _flat(path: Path) -> str:
    """Return the file text with all whitespace runs collapsed to single spaces."""
    return " ".join(path.read_text(encoding="utf-8").split())


class TestNesbitPrimaryClaims(unittest.TestCase):
    """Containment checks use assertTrue so a failure never diffs a whole chapter."""

    def test_quote_is_verbatim_including_strain(self) -> None:
        """The p. 531 quote matches the paper, including the word "strain"."""
        text = _flat(DRAFT).replace("_", "").replace('"', "").replace("“", "")
        self.assertTrue(NESBIT_QUOTE in text)

    def test_cohort_is_stated_as_the_paper_states_it(self) -> None:
        """The 85-golfer cohort is described as 84 male and one female."""
        self.assertTrue("84 male and one female" in _flat(DRAFT))

    def test_table_4_1_asserts_no_unsourced_speed_or_impact_signs(self) -> None:
        """Table 4.1 and the Camp A paragraph make no unsourced per-subject claims."""
        # Neither claim is in the paper: no per-subject clubhead speeds, and Fig. 11 is a
        # -0.3..+0.3 s time series, not a per-subject sign at impact.
        text = _flat(DRAFT)
        self.assertFalse("Highest in cohort" in text)
        self.assertFalse("Strongly NEGATIVE" in text)
        self.assertFalse("(Subjects 2 and 4) finished the downswing" in text)
        self.assertTrue("(Subjects 2 and 4); this per-subject reading is unverified" in text)

    def test_free_hinge_text_is_p531_and_not_subject_4(self) -> None:
        """The claims dossier cites p. 531 and calls the scratch golfer Subject 1."""
        claims = _flat(CLAIMS)
        self.assertFalse("Nesbit & Serrano (2005, p. 528)" in claims)
        self.assertFalse("Subject 4 (scratch" in claims)
        self.assertFalse("for Subject 4..." in claims)


if __name__ == "__main__":
    unittest.main()
