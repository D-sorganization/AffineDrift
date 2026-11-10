"""Appendix B.1 double-pendulum regression tests (#5460)."""

from __future__ import annotations

import math
import re
import sys
import unittest
from pathlib import Path

import numpy as np

CALCS_DIR = Path(__file__).resolve().parent
DRAFT = CALCS_DIR.parent / "draft"
if str(CALCS_DIR) not in sys.path:
    sys.path.insert(0, str(CALCS_DIR))

from alpha_war_double_pendulum import (  # noqa: E402
    DoublePendulumParams,
    PendulumState,
    free_hinge_theta2_accel,
    hinge_angle,
    kinetic_energy,
    kinetic_energy_from_com_kinematics,
    mass_matrix,
    mass_matrix_from_kinetic_hessian,
    passive_release_accel_formula,
    wrist_torque,
)

DEFAULT_PARAMS = DoublePendulumParams(
    i1_o=2.0,
    m1=4.0,
    m2=0.45,
    l1=0.55,
    r_g2=0.42,
    i_g2=0.08,
)

FIG_SHOULDER_O = (120.0, 240.0)
FIG_WRIST = (260.0, 130.0)
FIG_CLUB_TIP = (420.0, 70.0)
FIG_ARM_TIP = (260.0, 130.0)


def _svg_path_endpoint(path_d: str) -> tuple[float, float]:
    """Parse the terminal x,y coordinates from a compact M…A… SVG path."""
    tokens = path_d.replace(",", " ").split()
    return float(tokens[-2]), float(tokens[-1])


class TestAlphaWarDoublePendulum(unittest.TestCase):
    """Lock B.1 inertia matrix, tau2=0 substitution, and conditional release prose."""

    def test_mass_matrix_matches_kinetic_energy_hessian(self) -> None:
        """M(phi) must equal the velocity Hessian of T."""
        state = PendulumState(0.9, 2.1, 11.0, 14.0)
        phi = hinge_angle(state)
        m_analytic = mass_matrix(DEFAULT_PARAMS, phi)
        m_numeric = mass_matrix_from_kinetic_hessian(DEFAULT_PARAMS, state)
        np.testing.assert_allclose(m_analytic, m_numeric, rtol=1e-4, atol=1e-6)

    def test_independent_com_kinematics_matches_draft_kinetic_energy(self) -> None:
        """Two independent T constructions must agree (position vs draft split)."""
        state = PendulumState(0.75, 1.95, 8.5, 12.0)
        t_draft = kinetic_energy(DEFAULT_PARAMS, state)
        t_com = kinetic_energy_from_com_kinematics(DEFAULT_PARAMS, state)
        self.assertAlmostEqual(t_draft, t_com, places=9)

    def test_mass_matrix_from_com_kinematics_hessian(self) -> None:
        """Hessian of COM-kinematics T matches analytic M for random velocities."""
        state = PendulumState(1.1, 2.4, 5.0, -3.0)
        phi = hinge_angle(state)
        m_analytic = mass_matrix(DEFAULT_PARAMS, phi)

        def _t_com(v1: float, v2: float) -> float:
            """Kinetic energy at perturbed velocities for numeric Hessian sampling."""
            return kinetic_energy_from_com_kinematics(
                DEFAULT_PARAMS, PendulumState(state.theta1, state.theta2, v1, v2)
            )

        eps = 1e-4
        v1, v2 = state.theta1_dot, state.theta2_dot
        t0 = _t_com(v1, v2)
        m22 = (_t_com(v1, v2 + eps) - 2.0 * t0 + _t_com(v1, v2 - eps)) / (eps * eps)
        m11 = (_t_com(v1 + eps, v2) - 2.0 * t0 + _t_com(v1 - eps, v2)) / (eps * eps)
        m12 = (
            _t_com(v1 + eps, v2 + eps)
            - _t_com(v1 + eps, v2 - eps)
            - _t_com(v1 - eps, v2 + eps)
            + _t_com(v1 - eps, v2 - eps)
        ) / (4.0 * eps * eps)
        m_numeric = np.array([[m11, m12], [m12, m22]], dtype=np.float64)
        np.testing.assert_allclose(m_analytic, m_numeric, rtol=1e-4, atol=1e-6)

    def test_zero_arm_speed_limiting_centrifugal_coupling(self) -> None:
        """At dot theta1 = 0 the centrifugal sin(phi) term vanishes in row 2."""
        state = PendulumState(1.0, 2.2, 0.0, 4.0)
        phi = hinge_angle(state)
        self.assertAlmostEqual(
            DEFAULT_PARAMS.m2
            * DEFAULT_PARAMS.l1
            * DEFAULT_PARAMS.r_g2
            * state.theta1_dot**2
            * math.sin(phi),
            0.0,
            places=12,
        )

    def test_tau2_zero_row_matches_passive_coupling_plus_gravity(self) -> None:
        """Substituting tau2=0 in row 2 matches the full free-hinge solve."""
        state = PendulumState(1.05, 2.35, 12.0, 9.0)
        theta1_ddot = -18.0
        dd_full = free_hinge_theta2_accel(DEFAULT_PARAMS, state, theta1_ddot)
        dd_passive = passive_release_accel_formula(DEFAULT_PARAMS, state, theta1_ddot)
        self.assertAlmostEqual(
            wrist_torque(DEFAULT_PARAMS, state, theta1_ddot, dd_full), 0.0, places=6
        )
        self.assertNotAlmostEqual(dd_full, dd_passive, places=3)

    def test_passive_formula_matches_row2_without_gravity(self) -> None:
        """Interaction-only pass-through equals row-2 tau2=0 when G2 is zeroed."""
        state = PendulumState(1.05, 2.35, 12.0, 9.0)
        params = DoublePendulumParams(
            i1_o=DEFAULT_PARAMS.i1_o,
            m1=DEFAULT_PARAMS.m1,
            m2=DEFAULT_PARAMS.m2,
            l1=DEFAULT_PARAMS.l1,
            r_g2=DEFAULT_PARAMS.r_g2,
            i_g2=DEFAULT_PARAMS.i_g2,
            g=0.0,
        )
        theta1_ddot = -18.0
        dd_passive = passive_release_accel_formula(params, state, theta1_ddot)
        dd_full = free_hinge_theta2_accel(params, state, theta1_ddot)
        self.assertAlmostEqual(dd_passive, dd_full, places=9)

    def test_negative_hinge_torque_not_universal_at_near_zero_speed(self) -> None:
        """Small arm speed does not force large negative muscular tau2."""
        state = PendulumState(1.2, 2.0, 0.4, 0.2)
        tau = wrist_torque(DEFAULT_PARAMS, state, theta1_ddot=-2.0, theta2_ddot=0.5)
        self.assertGreater(tau, -5.0)

    def test_draft_references_b1_diagram(self) -> None:
        """B.1 must cite the pendulum convention figure."""
        text = (DRAFT / "alpha-war-v1.md").read_text(encoding="utf-8")
        b1 = text.split("### B.1")[1].split("### B.2")[0]
        self.assertIn("figures/fig-double-pendulum-b1.svg", b1)
        self.assertIn("unconditional mathematical necessity", b1.lower())

    def test_section_33_includes_moving_grip_acceleration(self) -> None:
        """§3.3 angular-rate ODE must retain the moving-grip acceleration term."""
        text = (DRAFT / "alpha-war-v1.md").read_text(encoding="utf-8")
        s33 = text.split("## 3.3")[1].split("## 3.4")[0]
        self.assertIn("a_{g,\\perp}", s33)
        self.assertIn("m_c\\,d_{G/M}\\,a_{g,\\perp}", s33)

    def test_b1_diagram_file_exists_with_labels(self) -> None:
        """Schematic documents absolute angles at O, hinge phi, and torque arrows."""
        svg = (DRAFT / "figures" / "fig-double-pendulum-b1.svg").read_text(encoding="utf-8")
        for element_id in (
            "theta1-arc-from-horizontal",
            "theta2-arc-from-horizontal",
            "phi-hinge-arc",
            "tau1-arrow",
            "tau2-arrow",
        ):
            self.assertIn(f'id="{element_id}"', svg)
        self.assertIn('marker-end="url(#arrow-ccw)"', svg)
        self.assertIn("theta1", svg)
        self.assertIn("theta2", svg)

    def test_b1_theta2_arc_matches_club_direction_from_shoulder(self) -> None:
        """theta2 arc endpoint must match the absolute O-to-club direction."""
        svg = (DRAFT / "figures" / "fig-double-pendulum-b1.svg").read_text(encoding="utf-8")
        match = re.search(r'id="theta2-arc-from-horizontal" d="([^"]+)"', svg)
        self.assertIsNotNone(match)
        path_d = match.group(1) if match else ""
        ex, ey = _svg_path_endpoint(path_d)
        ox, oy = FIG_SHOULDER_O
        cx, cy = FIG_CLUB_TIP
        expected = math.atan2(oy - cy, cx - ox)
        drawn = math.atan2(oy - ey, ex - ox)
        self.assertAlmostEqual(drawn, expected, places=2)

    def test_b1_theta1_arc_matches_arm_direction_from_shoulder(self) -> None:
        """theta1 arc endpoint must match the absolute O-to-arm direction."""
        svg = (DRAFT / "figures" / "fig-double-pendulum-b1.svg").read_text(encoding="utf-8")
        match = re.search(r'id="theta1-arc-from-horizontal" d="([^"]+)"', svg)
        self.assertIsNotNone(match)
        path_d = match.group(1) if match else ""
        ex, ey = _svg_path_endpoint(path_d)
        ox, oy = FIG_SHOULDER_O
        ax, ay = FIG_ARM_TIP
        expected = math.atan2(oy - ay, ax - ox)
        drawn = math.atan2(oy - ey, ex - ox)
        self.assertAlmostEqual(drawn, expected, places=2)

    def test_b1_tau2_arrow_bulges_outward_for_ccw_uncocking(self) -> None:
        """tau2 arc start should lie on the club side, outside the hinge, for +CCW."""
        svg = (DRAFT / "figures" / "fig-double-pendulum-b1.svg").read_text(encoding="utf-8")
        match = re.search(r'id="tau2-arrow" d="([^"]+)"', svg)
        self.assertIsNotNone(match)
        tokens = (match.group(1) if match else "").replace(",", " ").split()
        start_x, start_y = float(tokens[1]), float(tokens[2])
        wx, wy = FIG_WRIST
        self.assertGreater(start_x, wx + 20.0)
        self.assertLess(start_y, wy)


if __name__ == "__main__":
    unittest.main()
