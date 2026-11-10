"""Unit tests for FSP/club roll projection algebra (#5461)."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np

CALCS_DIR = Path(__file__).resolve().parent
ALPHA_WAR_DIR = CALCS_DIR.parent
if str(CALCS_DIR) not in sys.path:
    sys.path.insert(0, str(CALCS_DIR))

from alpha_war_roll_projection import (  # noqa: E402
    ILLUSTRATIVE_M_IN_PLANE_NM,
    ILLUSTRATIVE_M_OUT_OF_PLANE_NM,
    ILLUSTRATIVE_M_SHAFT_NM,
    alpha_couple_in_club_frame,
    couple_spatial_norm_nm,
    couple_vector_fsp_to_club,
    illustrative_alpha_zero_crossing_deg,
    rotation_fsp_to_club_about_shaft,
)


class TestAlphaWarRollProjection(unittest.TestCase):
    """Roll matrix, projections, and draft Box 2.1 illustrative inputs."""

    def test_rotation_matrix_orthonormal_and_proper(self) -> None:
        """R(phi) is orthonormal with determinant +1 for several roll angles."""
        for phi_deg in (0.0, 45.0, 61.93, 90.0, -90.0, 180.0):
            phi = math.radians(phi_deg)
            rot = rotation_fsp_to_club_about_shaft(phi)
            identity = rot @ rot.T
            self.assertTrue(np.allclose(identity, np.eye(3), atol=1e-12))
            self.assertAlmostEqual(float(np.linalg.det(rot)), 1.0, places=9)

    def test_round_trip_fsp_club_couple(self) -> None:
        """Club components invert through R^T back to FSP components."""
        phi = math.radians(61.93)
        rot = rotation_fsp_to_club_about_shaft(phi)
        m_fsp = np.array(
            [ILLUSTRATIVE_M_SHAFT_NM, ILLUSTRATIVE_M_OUT_OF_PLANE_NM, ILLUSTRATIVE_M_IN_PLANE_NM]
        )
        recovered = rot.T @ (rot @ m_fsp)
        self.assertTrue(np.allclose(recovered, m_fsp, atol=1e-9))

    def test_norm_invariant_across_roll_sweep(self) -> None:
        """Spatial couple norm is unchanged under roll re-expression."""
        norm_fsp = couple_spatial_norm_nm(
            ILLUSTRATIVE_M_SHAFT_NM,
            ILLUSTRATIVE_M_OUT_OF_PLANE_NM,
            ILLUSTRATIVE_M_IN_PLANE_NM,
        )
        for phi_deg in (0.0, 30.0, 45.0, 61.93, 90.0, 120.0):
            phi = math.radians(phi_deg)
            gamma, beta, alpha = couple_vector_fsp_to_club(
                ILLUSTRATIVE_M_SHAFT_NM,
                ILLUSTRATIVE_M_OUT_OF_PLANE_NM,
                ILLUSTRATIVE_M_IN_PLANE_NM,
                phi,
            )
            norm_club = math.sqrt(gamma**2 + beta**2 + alpha**2)
            self.assertAlmostEqual(norm_club, norm_fsp, places=6)

    def test_signed_zero_crossing_at_61_93_deg(self) -> None:
        """Illustrative inputs cross zero alpha projection at phi* = 61.93 deg."""
        phi_star = illustrative_alpha_zero_crossing_deg(
            ILLUSTRATIVE_M_IN_PLANE_NM,
            ILLUSTRATIVE_M_OUT_OF_PLANE_NM,
        )
        self.assertAlmostEqual(phi_star, 61.93, places=2)
        alpha_at_star = alpha_couple_in_club_frame(
            ILLUSTRATIVE_M_IN_PLANE_NM,
            ILLUSTRATIVE_M_OUT_OF_PLANE_NM,
            math.radians(phi_star),
        )
        self.assertAlmostEqual(alpha_at_star, 0.0, places=6)

    def test_alpha_at_zero_and_ninety_degrees(self) -> None:
        """Zero roll matches M_in; 90 deg roll matches M_out for illustrative inputs."""
        self.assertAlmostEqual(
            alpha_couple_in_club_frame(
                ILLUSTRATIVE_M_IN_PLANE_NM,
                ILLUSTRATIVE_M_OUT_OF_PLANE_NM,
                0.0,
            ),
            ILLUSTRATIVE_M_IN_PLANE_NM,
            places=9,
        )
        self.assertAlmostEqual(
            alpha_couple_in_club_frame(
                ILLUSTRATIVE_M_IN_PLANE_NM,
                ILLUSTRATIVE_M_OUT_OF_PLANE_NM,
                math.pi / 2.0,
            ),
            ILLUSTRATIVE_M_OUT_OF_PLANE_NM,
            places=9,
        )


class TestAlphaWarDraftRollFrameProse(unittest.TestCase):
    """Draft must separate shaft tangent e_t from velocity tangent v_M (#5461)."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load alpha-war-v1.md once."""
        cls.draft_text = (ALPHA_WAR_DIR / "draft" / "alpha-war-v1.md").read_text(encoding="utf-8")

    def test_fsp_frame_distinguishes_shaft_tangent_from_grip_velocity(self) -> None:
        """§2.3 FSP axes prose must not equate e_t with hub velocity tangent."""
        section = self.draft_text.split("### 2. Functional Swing Plane Frame")[1].split("### 3.")[0]
        self.assertIn("shaft tangential axis", section)
        self.assertIn("not** the same vector", section)
        self.assertIn("\\leftarrow\\text{FSP}", self.draft_text)
        self.assertIn("rotation matrix transforming coordinates", self.draft_text)

    def test_box_2_1_zero_degree_step_matches_plus_sine_formula(self) -> None:
        """Box 2.1 numeric demo at phi=0 must use M_in cos + M_out sin, not minus on M_out."""
        box = self.draft_text.split("Box 2.1:")[1].split(":::")[0]
        self.assertIn("M_{\\text{in}}\\cos 0^\\circ + M_{\\text{out}}\\sin 0^\\circ", box)
        self.assertNotIn("-15.0(1.0) - 8.0(0.0)", box)
        self.assertIn("\\operatorname{atan2}\\bigl(-M_{\\text{in}}, M_{\\text{out}}\\bigr)", box)


if __name__ == "__main__":
    unittest.main()
