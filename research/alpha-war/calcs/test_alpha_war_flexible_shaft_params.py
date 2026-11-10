"""Oracle-3 stiffness metadata and draft §7.6 parameter prose (#5463 slice 2)."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

CALCS_DIR = Path(__file__).resolve().parent
ALPHA_WAR_DIR = CALCS_DIR.parent
JSON_PATH = CALCS_DIR / "alpha_war_calculations.json"

if str(CALCS_DIR) not in sys.path:
    sys.path.insert(0, str(CALCS_DIR))

from alpha_war_flexible_shaft_params import (  # noqa: E402
    REFERENCE_GRAVITY_PLANAR_M_S2,
    REFERENCE_SHAFT_STIFFNESS_NM_RAD,
    lumped_shaft_cpm,
    planar_gravity_m_s2,
    reference_stiffness_metadata,
)


def _find_draft_path() -> Path:
    """Return alpha-war-v1.md if present, else alpha-war-v0.md."""
    v1 = ALPHA_WAR_DIR / "draft" / "alpha-war-v1.md"
    if v1.exists():
        return v1
    return ALPHA_WAR_DIR / "draft" / "alpha-war-v0.md"


class TestAlphaWarFlexibleShaftParams(unittest.TestCase):
    """Study 6 reference k, cpm, and gravity projection are stated and pinned in JSON."""

    def test_oracle_3_cpm_matches_reference_k(self) -> None:
        """Small-oscillation cpm from k=80 N·m/rad matches oracle-3 closed form."""
        cpm = lumped_shaft_cpm(REFERENCE_SHAFT_STIFFNESS_NM_RAD, 0.20, 0.55)
        self.assertAlmostEqual(cpm, 347.25, places=1)

    def test_planar_gravity_cos_35_interpretation(self) -> None:
        """35° FSP tilt maps standard gravity to ~8.04 m/s² (reference pins 8.033)."""
        projected = planar_gravity_m_s2(35.0)
        self.assertAlmostEqual(projected, 8.036, places=2)
        self.assertAlmostEqual(REFERENCE_GRAVITY_PLANAR_M_S2, 8.033, places=3)

    def test_json_exports_model_parameters_block(self) -> None:
        """``study_6`` JSON carries k, cpm, and gravity metadata (#5463)."""
        payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        meta = payload["study_6_shaft_flex_contribution"]["upstream_drift_matched_3link_study"][
            "model_parameters"
        ]
        expected = reference_stiffness_metadata()
        for key in (
            "shaft_stiffness_nm_rad",
            "lumped_shaft_equivalent_cpm",
            "gravity_planar_m_s2",
            "swing_plane_tilt_from_horizontal_deg",
        ):
            self.assertAlmostEqual(meta[key], expected[key], places=3, msg=key)
        self.assertIn("oracle 3", meta["cpm_formula"])

    def test_draft_section_7_6_states_k_cpm_and_gravity_projection(self) -> None:
        """Draft §7.6 names k, its cpm equivalent, and planar gravity projection."""
        section = _find_draft_path().read_text(encoding="utf-8").split("## 7.6")[1].split("# 8.")[0]
        for phrase in ("80", "347", "cpm", "8.033", "cos", "35", "model_parameters"):
            self.assertIn(phrase, section, msg=f"missing {phrase!r}")
        self.assertLess(abs(planar_gravity_m_s2(35.0) - REFERENCE_GRAVITY_PLANAR_M_S2), 0.01)


if __name__ == "__main__":
    unittest.main()
