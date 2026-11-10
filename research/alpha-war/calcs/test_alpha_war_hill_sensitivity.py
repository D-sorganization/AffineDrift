"""Hill sensitivity and Koike §8.1 consistency guards (#5464)."""

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
    force_couple_with_free_wrist_torque,
    reconstruct_force_couple_mid_nm,
)
from alpha_war_hill_sensitivity import (  # noqa: E402
    hill_active_force_fraction,
    hill_sensitivity_rows,
)


class TestAlphaWarHillSensitivity5464(unittest.TestCase):
    """Hill curve endpoints and club vs wrist-relative sensitivity."""

    def test_hill_endpoints(self) -> None:
        """``F/F0`` is 1 at rest and 0 at ``v_max``."""
        vmax = 0.5
        self.assertAlmostEqual(hill_active_force_fraction(0.0, vmax), 1.0)
        self.assertAlmostEqual(hill_active_force_fraction(vmax, vmax), 0.0)

    def test_omega_club_substitution_is_more_pessimistic(self) -> None:
        """Using ``omega_club`` instead of ``omega_rel`` lowers predicted ``F/F0``."""
        rows = {r["kinematic_label"]: r for r in hill_sensitivity_rows(omega_rel_rad_s=15.0)}
        self.assertEqual(rows["omega_club"]["f_over_f0"], 0.0)
        self.assertGreater(rows["omega_rel"]["f_over_f0"], 0.0)
        self.assertLess(rows["omega_club"]["f_over_f0"], rows["omega_rel"]["f_over_f0"])

    def test_hill_table_matches_documented_decimal_rows(self) -> None:
        """Check two anchor ratios from the draft sensitivity table (``a_rel=0.25``)."""
        vmax = 0.4
        self.assertAlmostEqual(hill_active_force_fraction(0.16, vmax), 0.23, places=2)
        self.assertAlmostEqual(hill_active_force_fraction(0.20, vmax), 0.17, places=2)


class TestAlphaWarKoikeSection81Consistency(unittest.TestCase):
    """§8.1 Koike forces must reconcile with Box 3.1 or state free-torque credit."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.draft_text = (ALPHA_WAR_DIR / "draft" / "alpha-war-v1.md").read_text(encoding="utf-8")

    def test_koike_forces_reconstruct_with_stated_free_torque_credit(self) -> None:
        """200 N opposed shear with ``tau_free = +5.2`` N·m matches ``-10`` N·m total."""
        f_lead, f_trail = 200.0, -200.0
        cf_only = reconstruct_force_couple_mid_nm(f_lead, f_trail, GRIP_SEPARATION_M)
        self.assertAlmostEqual(cf_only, -15.24, places=2)
        tau_free = -10.0 - cf_only
        total = force_couple_with_free_wrist_torque(f_lead, f_trail, tau_free_nm=tau_free)
        self.assertAlmostEqual(total, -10.0, places=2)

    def test_section_81_documents_koike_box_reconciliation(self) -> None:
        """§8.1 must explain the 200 N vs ``-10`` N·m Koike triplet."""
        section = self.draft_text.split("### Layer 2:")[1].split("## 8.2")[0]
        self.assertIn("Box 3.1", section)
        self.assertIn("free wrist", section.lower())


if __name__ == "__main__":
    unittest.main()
