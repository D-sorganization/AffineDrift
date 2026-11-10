"""Tests for §5A.1 hand-force bound arithmetic and draft claim wording (#5464)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

CALCS_DIR = Path(__file__).resolve().parent
ALPHA_WAR_DIR = CALCS_DIR.parent
if str(CALCS_DIR) not in sys.path:
    sys.path.insert(0, str(CALCS_DIR))

from alpha_war_hand_force_bounds import (  # noqa: E402
    GRIP_SEPARATION_M,
    differential_force_y_from_force_couple,
    newtons_to_lbf,
    opposed_pure_couple_contact_forces_y,
    reconstruct_force_couple_mid_nm,
)

TARGET_COUPLE_NM = 30.0
EXPECTED_F_DY_N = 393.7
EXPECTED_PER_HAND_LBF = 88.5


class TestAlphaWarHandForceBounds(unittest.TestCase):
    """Box 3.1 couple arithmetic must not halve per-hand shear magnitudes."""

    def test_differential_force_for_plus_30_nm_couple(self) -> None:
        """+30 N·m pure couple yields the Box 3.1 differential shear magnitude."""
        f_d_y = differential_force_y_from_force_couple(TARGET_COUPLE_NM)
        self.assertAlmostEqual(abs(f_d_y), EXPECTED_F_DY_N, places=1)

    def test_opposed_hands_each_carry_full_differential_magnitude(self) -> None:
        """Each hand carries the full differential magnitude, not half, in lbf."""
        f_lead_y, f_trail_y = opposed_pure_couple_contact_forces_y(TARGET_COUPLE_NM)
        self.assertAlmostEqual(abs(f_lead_y), EXPECTED_F_DY_N, places=1)
        self.assertAlmostEqual(abs(f_trail_y), EXPECTED_F_DY_N, places=1)
        self.assertAlmostEqual(f_lead_y, -f_trail_y)
        per_hand_lbf = newtons_to_lbf(abs(f_lead_y))
        self.assertAlmostEqual(per_hand_lbf, EXPECTED_PER_HAND_LBF, places=1)

    def test_reconstruct_moment_from_both_contact_forces(self) -> None:
        """Mid-hand couple reconstruction inverts the opposed contact-force model."""
        f_lead_y, f_trail_y = opposed_pure_couple_contact_forces_y(TARGET_COUPLE_NM)
        reconstructed = reconstruct_force_couple_mid_nm(f_lead_y, f_trail_y)
        self.assertAlmostEqual(reconstructed, TARGET_COUPLE_NM, places=6)
        self.assertAlmostEqual(
            reconstruct_force_couple_mid_nm(f_lead_y, f_trail_y, GRIP_SEPARATION_M),
            -GRIP_SEPARATION_M * 0.5 * (f_lead_y - f_trail_y),
        )

    def test_wscg_minimum_couple_example_from_box_3(self) -> None:
        """Box 3 WSCG minimum-couple contact forces reconstruct to -18.60 N·m."""
        f_lead_y = 228.57
        f_trail_y = -259.53
        couple = reconstruct_force_couple_mid_nm(f_lead_y, f_trail_y)
        self.assertAlmostEqual(couple, -18.60, places=2)


class TestAlphaWarDraftHandForceBoundProse(unittest.TestCase):
    """Draft must state corrected forces and reclassified CLM-SGN-05 (#5464)."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load the v1 draft once for prose assertions."""
        cls.draft_text = (ALPHA_WAR_DIR / "draft" / "alpha-war-v1.md").read_text(encoding="utf-8")

    def test_section_5a_per_hand_lbf_not_halved(self) -> None:
        """§5A.1 must report 88.5 lbf per hand, not a halved 44–45 lbf range."""
        self.assertIn("88.5\\text{ lbf}", self.draft_text)
        self.assertNotIn("44\\text{ to }45\\text{ lbf}", self.draft_text)

    def test_clm_sgn_05_not_marked_impossible_or_settled(self) -> None:
        """Table 8.2 must not label CLM-SGN-05 impossible or biomechanically settled."""
        table_82 = self.draft_text.split("## 8.2")[1].split("## 8.3")[0]
        sgn05_lines = [ln for ln in table_82.splitlines() if "CLM-SGN-05" in ln]
        self.assertEqual(len(sgn05_lines), 1)
        row = sgn05_lines[0]
        self.assertNotIn("impossible", row.lower())
        self.assertNotIn("Settled (Biomechanical Constraint)", row)

    def test_section_5a_separates_velocity_quantities(self) -> None:
        """§5A.1 prose must distinguish club, wrist, and fascicle velocity wording."""
        section_5a = self.draft_text.split("## 5A.1")[1].split("Table 5A.1")[0]
        for phrase in (
            "club angular velocity",
            "wrist relative angular velocity",
            "fascicle shortening velocity",
        ):
            self.assertIn(phrase, section_5a.lower())


class TestAlphaWarWorkClaimsHandBound5464(unittest.TestCase):
    """Work claim matrix must mirror §5A.1 hand-force bound wording (#5464)."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load work/03_claims.md once."""
        claims_path = ALPHA_WAR_DIR / "work" / "03_claims.md"
        cls.claims_text = claims_path.read_text(encoding="utf-8")

    def test_clm_sgn_05_per_hand_lbf_in_work_claims(self) -> None:
        """CLM-SGN-05 row reports ~88.5 lbf per hand, not ~89 or halved load."""
        row = next(ln for ln in self.claims_text.splitlines() if "CLM-SGN-05" in ln)
        self.assertIn("88.5 lbf", row)
        self.assertIn("per hand", row)
        self.assertNotIn("~89 lbf", row)
        self.assertIn("not impossibility", row)


if __name__ == "__main__":
    unittest.main()
