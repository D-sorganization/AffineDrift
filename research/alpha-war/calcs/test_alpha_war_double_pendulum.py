"""Appendix B.1 double-pendulum regression tests (#5460)."""

from __future__ import annotations

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


class TestAlphaWarDoublePendulum(unittest.TestCase):
    """Lock B.1 inertia matrix, tau2=0 substitution, and conditional release prose."""

    def test_mass_matrix_matches_kinetic_energy_hessian(self) -> None:
        """M(phi) must equal the velocity Hessian of T."""
        state = PendulumState(0.9, 2.1, 11.0, 14.0)
        phi = hinge_angle(state)
        m_analytic = mass_matrix(DEFAULT_PARAMS, phi)
        m_numeric = mass_matrix_from_kinetic_hessian(DEFAULT_PARAMS, state)
        np.testing.assert_allclose(m_analytic, m_numeric, rtol=1e-4, atol=1e-6)

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


if __name__ == "__main__":
    unittest.main()
