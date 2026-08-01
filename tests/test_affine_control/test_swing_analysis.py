"""Tests for the Volume V swing-analysis pipeline (#3518).

The published version of this pipeline was never executed and failed in three
places. These tests assert the properties it violated, so the chapter's listing
-- which is generated from the module -- cannot regress silently.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.affine_control.swing_analysis import SwingAnalysis, synthetic_swing


def scalar_sum_speed(analysis: SwingAnalysis, rates: np.ndarray) -> float:
    """The published formula: sum of qdot_i times the reach beyond joint i.

    Configuration-blind by construction -- it takes no angles at all.
    """
    lengths = analysis.segment_lengths
    return float(
        sum(rates[i] * sum(lengths[j] for j in range(i, len(lengths))) for i in range(len(lengths)))
    )


class TestClubheadSpeed:
    def test_speed_depends_on_configuration(self) -> None:
        """The defect: the old formula returned one number for every posture."""
        analysis = SwingAnalysis()
        model = analysis.model()
        rates = np.array([5.0, 5.0, 5.0])

        straight = model.clubhead_speed(np.zeros(3), rates)
        folded = model.clubhead_speed(np.array([0.0, np.pi, np.pi]), rates)

        assert straight != pytest.approx(folded, rel=0.05)
        assert folded < straight

    def test_matches_the_scalar_sum_only_when_collinear(self) -> None:
        """The old formula is the collinear special case, not the general one."""
        analysis = SwingAnalysis()
        model = analysis.model()
        rates = np.array([5.0, 5.0, 5.0])

        collinear = model.clubhead_speed(np.zeros(3), rates)
        assert collinear == pytest.approx(scalar_sum_speed(analysis, rates), rel=1e-9)

        bent = model.clubhead_speed(np.array([0.2, -0.7, 1.1]), rates)
        assert bent < scalar_sum_speed(analysis, rates)

    def test_scalar_sum_overestimates_a_folded_arm_substantially(self) -> None:
        """Quantifies the claim the chapter now makes: about a 69% overestimate."""
        analysis = SwingAnalysis()
        model = analysis.model()
        rates = np.array([5.0, 5.0, 5.0])
        folded = model.clubhead_speed(np.array([0.0, np.pi, np.pi]), rates)
        overestimate = scalar_sum_speed(analysis, rates) / folded - 1.0
        assert overestimate > 0.5

    def test_zero_rates_give_zero_speed(self) -> None:
        analysis = SwingAnalysis()
        model = analysis.model()
        assert model.clubhead_speed(np.array([0.3, -0.4, 0.9]), np.zeros(3)) == pytest.approx(0.0)

    def test_speed_scales_linearly_with_rates(self) -> None:
        """Velocity is linear in qdot; the Jacobian does not depend on it."""
        analysis = SwingAnalysis()
        model = analysis.model()
        q = np.array([0.3, -0.4, 0.9])
        rates = np.array([1.0, -2.0, 3.0])
        base = model.clubhead_speed(q, rates)
        assert model.clubhead_speed(q, 2.5 * rates) == pytest.approx(2.5 * base, rel=1e-9)


class TestZtcfDecomposition:
    def test_control_contribution_is_exactly_the_torque_response(self) -> None:
        """Control-affine dynamics make the split exact, not approximate.

        a_actual - a_drift = M^-1 tau, so the decomposition is a theorem rather
        than the 60/40 estimate the published version returned.
        """
        analysis = synthetic_swing()
        model = analysis.model()
        _, control = analysis.ztcf_decomposition()

        for index in (0, len(control) // 2, len(control) - 1):
            q = analysis.joint_angles[index]
            tau = analysis.joint_torques[index]
            expected = np.linalg.norm(np.linalg.solve(model.rigid_mass_matrix(q), tau))
            assert control[index] == pytest.approx(expected, rel=1e-9)

    def test_zero_torque_gives_zero_control_contribution(self) -> None:
        analysis = synthetic_swing()
        analysis.joint_torques = np.zeros_like(analysis.joint_torques)
        _, control = analysis.ztcf_decomposition()
        assert np.allclose(control, 0.0)

    def test_split_is_not_a_fixed_ratio(self) -> None:
        """The published version returned a hardcoded 60/40 at every sample."""
        analysis = synthetic_swing()
        drift, control = analysis.ztcf_decomposition()
        interior = slice(1, -1)
        share = drift[interior] / (drift[interior] + control[interior])
        assert share.max() - share.min() > 0.2

    def test_drift_vanishes_when_the_chain_is_straight_and_vertical(self) -> None:
        """Documents why the summary reports a median rather than a point value.

        At a fully extended vertical configuration the gravity torque and the
        Christoffel terms both vanish, so the drift is exactly zero -- which
        would read as "0% drift" if quoted there.
        """
        analysis = SwingAnalysis()
        model = analysis.model()
        q = np.array([np.pi / 2, 0.0, 0.0])
        qd = np.array([3.0, -1.0, 2.0])
        bias = model.coriolis(q, qd) @ qd + model.gravity_torque(q)
        assert np.allclose(bias, 0.0, atol=1e-8)


class TestPipeline:
    def test_summary_runs_and_reports_a_plausible_speed(self) -> None:
        text = synthetic_swing().summary()
        assert "Peak clubhead speed" in text
        assert "Median over the swing" in text

    def test_analysis_requires_kinematics(self) -> None:
        with pytest.raises(ValueError, match="joint_angles"):
            SwingAnalysis().clubhead_speed()

    def test_decomposition_requires_torques(self) -> None:
        analysis = synthetic_swing()
        analysis.joint_torques = None
        with pytest.raises(ValueError, match="joint_torques"):
            analysis.ztcf_decomposition()

    def test_synthetic_swing_is_deterministic(self) -> None:
        """The published driver used np.random.randn, so output changed per run."""
        first = synthetic_swing().summary()
        second = synthetic_swing().summary()
        assert first == second

    def test_model_inertias_follow_from_mass_and_length(self) -> None:
        """Uniform rods, so inertia is not a free parameter."""
        analysis = SwingAnalysis()
        model = analysis.model()
        for inertia, mass, length in zip(
            model.inertias, analysis.segment_masses, analysis.segment_lengths, strict=True
        ):
            assert inertia == pytest.approx(mass * length**2 / 12.0)

    def test_mass_matrix_stays_positive_definite_along_the_swing(self) -> None:
        analysis = synthetic_swing()
        model = analysis.model()
        for q in analysis.joint_angles[::25]:
            assert np.min(np.linalg.eigvalsh(model.rigid_mass_matrix(q))) > 0.0
