"""Appendix A wrench ordering and power invariance regression tests (#5459)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

CALCS_DIR = Path(__file__).resolve().parent
if str(CALCS_DIR) not in sys.path:
    sys.path.insert(0, str(CALCS_DIR))

from alpha_war_spatial_wrench import (  # noqa: E402
    dual_pairing_matrix,
    force_first_wrench_transport_matrix,
    mechanical_power,
    poinsot_moment_transport,
    transport_wrench,
    triple_product_lhs,
    triple_product_rhs,
    twist_adjoint,
    twist_adjoint_inverse_transpose,
)


class TestAlphaWarSpatialWrenchPower(unittest.TestCase):
    """Lock dual wrench/twist power pairing and Poinsot transport."""

    def test_force_first_pairing_differs_from_naive_dot_product(self) -> None:
        """Naive W.T @ V permutes slots; dual power is W.T @ P @ V = R.v + M.omega."""
        force = np.array([0.0, 1.0, 0.0])
        moment = np.array([2.0, 0.0, 0.0])
        omega = np.array([0.0, 0.0, 1.0])
        vel = np.array([3.0, 0.0, 0.0])
        wrench = np.concatenate([force, moment])
        twist = np.concatenate([omega, vel])
        naive = float(wrench @ twist)
        pairing = dual_pairing_matrix()
        dual = float(wrench @ pairing @ twist)
        self.assertAlmostEqual(mechanical_power(wrench, twist), dual)
        self.assertAlmostEqual(dual, force @ vel + moment @ omega)
        self.assertNotAlmostEqual(naive, dual)

    def test_force_first_transport_equals_p_ad_inv_t_p(self) -> None:
        """Force-first transport is P Ad^{-T} P, not Ad^{-T} on [R;M] alone."""
        r_ba = np.array([0.12, -0.03, 0.08])
        p = dual_pairing_matrix()
        expected = p @ twist_adjoint_inverse_transpose(r_ba) @ p
        np.testing.assert_allclose(force_first_wrench_transport_matrix(r_ba), expected)
        self.assertFalse(np.allclose(twist_adjoint_inverse_transpose(r_ba), expected))

    def test_issue_5459_concrete_triple_product_regression(self) -> None:
        """Lock the concrete triple-product values from issue #5459."""
        r = np.array([1.0, 0.0, 0.0])
        force = np.array([0.0, 1.0, 0.0])
        omega = np.array([0.0, 0.0, 1.0])
        self.assertAlmostEqual(triple_product_rhs(r, force, omega), 1.0)
        self.assertAlmostEqual(triple_product_lhs(r, force, omega), 1.0)

    def test_moment_transport_matches_poinsot(self) -> None:
        """Transported wrench moment matches the Poinsot formula."""
        r_ba = np.array([0.12, -0.03, 0.08])
        force = np.array([4.0, -1.5, 2.0])
        moment_a = np.array([0.5, 1.2, -0.4])
        moment_b = poinsot_moment_transport(moment_a, force, r_ba)
        wrench_a = np.concatenate([force, moment_a])
        wrench_b = transport_wrench(wrench_a, r_ba)
        np.testing.assert_allclose(wrench_b[0:3], force)
        np.testing.assert_allclose(wrench_b[3:6], moment_b)

    def test_power_invariant_under_change_of_reference_point(self) -> None:
        """W_A.T P V_A equals W_B.T P V_B under Ad twist and force-first wrench transport."""
        pairing = dual_pairing_matrix()
        rng = np.random.default_rng(5459)
        for _ in range(32):
            force = rng.normal(size=3)
            moment = rng.normal(size=3)
            omega = rng.normal(size=3)
            vel_a = rng.normal(size=3)
            r_ba = rng.normal(size=3)
            twist_a = np.concatenate([omega, vel_a])
            twist_b = twist_adjoint(r_ba) @ twist_a
            wrench_a = np.concatenate([force, moment])
            wrench_b = transport_wrench(wrench_a, r_ba)
            p_a = float(wrench_a @ pairing @ twist_a)
            p_b = float(wrench_b @ pairing @ twist_b)
            self.assertAlmostEqual(mechanical_power(wrench_a, twist_a), p_a)
            self.assertAlmostEqual(mechanical_power(wrench_b, twist_b), p_b)
            self.assertAlmostEqual(p_a, p_b, places=9)


if __name__ == "__main__":
    unittest.main()
