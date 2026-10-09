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
        assert "Joint acceleration norm medians" in text
        assert "rad/s^2" in text
        assert "%" not in text

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


@pytest.mark.parametrize("duration,step", [(0.3005, 0.007), (0.3, 1.0)])
def test_grid_includes_endpoints_without_exceeding_step(duration: float, step: float) -> None:
    analysis = synthetic_swing(duration, step)
    assert len(analysis.time) == int(np.ceil(duration / step)) + 1
    assert analysis.time[0] == 0.0
    assert analysis.time[-1] == duration
    assert np.all(np.diff(analysis.time) <= step * (1 + 1e-12))


def test_synthetic_rates_are_analytic_at_both_endpoints() -> None:
    duration = 0.31
    analysis = synthetic_swing(duration, 0.04)
    expected = np.array([[0, np.pi**2 / 3, 0], [2 * np.pi, -np.pi**2 / 3, np.pi**2 / 4]])
    np.testing.assert_allclose(analysis.joint_velocities[[0, -1]], expected / duration, atol=1e-12)


def test_inverse_torques_recover_prescribed_second_derivative() -> None:
    duration = 0.31
    analysis = synthetic_swing(duration, 0.04)
    fraction = analysis.time / duration
    expected = (
        np.column_stack(
            [
                np.full_like(fraction, 2 * np.pi),
                -np.pi**3 / 3 * np.sin(np.pi * fraction),
                np.pi**3 / 8 * np.cos(np.pi * fraction / 2),
            ]
        )
        / duration**2
    )
    drift, control = analysis.joint_acceleration_components()
    np.testing.assert_allclose(drift + control, expected, rtol=1e-10, atol=1e-8)


def test_signed_cancellation_does_not_partition_net_acceleration_norm() -> None:
    analysis = SwingAnalysis(
        time=np.array([4.0]),
        joint_angles=np.array([[0.1, -0.2, 0.3]]),
        joint_velocities=np.array([[0.5, 0.2, -0.4]]),
    )
    model = analysis.model()
    angles, rates = analysis.joint_angles[0], analysis.joint_velocities[0]
    analysis.joint_torques = (model.coriolis(angles, rates) @ rates + model.gravity_torque(angles))[
        None
    ]
    drift, control = analysis.joint_acceleration_components()
    assert drift.shape == control.shape == (1, 3)
    np.testing.assert_allclose(drift + control, 0, atol=1e-10)
    drift_norm, control_norm = analysis.ztcf_decomposition()
    np.testing.assert_allclose(drift_norm, np.linalg.norm(drift, axis=1))
    np.testing.assert_allclose(control_norm, np.linalg.norm(control, axis=1))
    assert drift_norm[0] + control_norm[0] > 1
    assert "%" not in analysis.summary()


def test_summary_duration_uses_elapsed_time() -> None:
    analysis = synthetic_swing(0.3, 0.05)
    analysis.time += 10
    assert "Duration: 0.300 s" in analysis.summary()


@pytest.mark.parametrize(
    "duration,step", [(0, 0.1), (-1, 0.1), (1, 0), (1, -1), (np.nan, 1), (1, np.inf)]
)
def test_synthetic_time_contract(duration: float, step: float) -> None:
    with pytest.raises(ValueError, match="duration|dt"):
        synthetic_swing(duration, step)


@pytest.mark.parametrize(
    "field,value",
    [
        ("time", np.array([])),
        ("time", np.array([0.0, 0.0])),
        ("time", np.array([0.0, np.nan])),
        ("time", np.array([[0.0, 0.1]])),
        ("joint_angles", np.zeros((2, 2))),
        ("joint_angles", np.full((2, 3), np.inf)),
        ("joint_velocities", np.zeros((1, 3))),
        ("joint_torques", np.zeros((2, 2))),
        ("joint_torques", np.full((2, 3), np.nan)),
        ("segment_lengths", np.array([1.0, 0.0, 1.0])),
        ("segment_masses", np.array([1.0, -1.0, 1.0])),
        ("segment_lengths", np.array([1.0, np.inf, 1.0])),
        ("segment_masses", np.ones(2)),
    ],
)
def test_analysis_rejects_invalid_arrays(field: str, value: np.ndarray) -> None:
    analysis = SwingAnalysis(
        time=np.array([0.0, 0.1]),
        joint_angles=np.zeros((2, 3)),
        joint_velocities=np.zeros((2, 3)),
        joint_torques=np.zeros((2, 3)),
    )
    setattr(analysis, field, value)
    with pytest.raises(ValueError, match=field):
        analysis.joint_acceleration_components()
