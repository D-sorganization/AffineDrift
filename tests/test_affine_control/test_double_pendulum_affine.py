"""Contract for the double-pendulum drift/input split behind the WEB-06.3 sandbox (#4533).

The sandbox widget shows ``qdd = f(x) + G(x) u`` for the point-mass double
pendulum of :func:`src.affine_control.dynamics.double_pendulum_mass_matrix`.
These tests pin the physics the widget mirrors: the potential must match the
mass matrix (energy is conserved without torque), the drift must not depend on
the input, the input term must be linear in it, and the Cartesian tip split must
add up to the acceleration of the integrated trajectory.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.affine_control.double_pendulum_affine import (
    DoublePendulumParams,
    affine_split,
    generalized_torque,
    grad_potential,
    potential,
    simulate,
    tip_acceleration_split,
    tip_position,
)
from src.affine_control.dynamics import double_pendulum_mass_matrix

PARAMS = DoublePendulumParams(m1=7.0, m2=0.6, l1=0.75, l2=1.1, gravity=9.81)
Q = np.array([2.3, 3.6])
QD = np.array([-1.5, 2.0])


def test_params_reject_nonphysical_values() -> None:
    for bad in ({"m1": 0.0}, {"l2": -1.0}, {"gravity": float("nan")}, {"m2": float("inf")}):
        values = {"m1": 1.0, "m2": 1.0, "l1": 1.0, "l2": 1.0, "gravity": 9.81} | bad
        with pytest.raises(ValueError):
            DoublePendulumParams(**values)


def test_grad_potential_is_the_gradient_of_the_potential() -> None:
    step = 1e-6
    numeric = np.array(
        [
            (potential(Q + step * e, PARAMS) - potential(Q - step * e, PARAMS)) / (2 * step)
            for e in np.eye(2)
        ]
    )
    np.testing.assert_allclose(grad_potential(Q, PARAMS), numeric, rtol=1e-8, atol=1e-8)


def test_potential_matches_the_mass_matrix_so_unforced_energy_is_conserved() -> None:
    samples = simulate(PARAMS, Q, QD, np.zeros(2), horizon=1.0, steps=2000)

    def energy(q: np.ndarray, qd: np.ndarray) -> float:
        mass = double_pendulum_mass_matrix(q, PARAMS.m1, PARAMS.m2, PARAMS.l1, PARAMS.l2)
        return float(0.5 * qd @ mass @ qd + potential(q, PARAMS))

    energies = [energy(s.q, s.qd) for s in samples]
    assert max(energies) - min(energies) < 1e-6 * max(1.0, abs(energies[0]))


def test_drift_does_not_depend_on_the_input_and_input_term_is_linear() -> None:
    drift_a, input_a = affine_split(Q, QD, np.array([10.0, -2.0]), PARAMS)
    drift_b, input_b = affine_split(Q, QD, np.array([-40.0, 5.0]), PARAMS)
    np.testing.assert_array_equal(drift_a, drift_b)
    _, input_sum = affine_split(Q, QD, np.array([-30.0, 3.0]), PARAMS)
    np.testing.assert_allclose(input_a + input_b, input_sum, rtol=1e-12, atol=1e-12)
    _, input_zero = affine_split(Q, QD, np.zeros(2), PARAMS)
    np.testing.assert_array_equal(input_zero, np.zeros(2))


def test_split_sums_to_the_equation_of_motion() -> None:
    torque = np.array([25.0, -3.0])
    drift, input_qdd = affine_split(Q, QD, torque, PARAMS)
    mass = double_pendulum_mass_matrix(Q, PARAMS.m1, PARAMS.m2, PARAMS.l1, PARAMS.l2)
    k = 0.5 * PARAMS.m2 * PARAMS.l1 * PARAMS.l2 * np.sin(Q[0] - Q[1])
    coriolis_qd = np.array([k * QD[1] ** 2, -k * QD[0] ** 2])
    residual = mass @ (drift + input_qdd) + coriolis_qd + grad_potential(Q, PARAMS) - torque
    np.testing.assert_allclose(residual, 0.0, atol=1e-10)


def test_tip_split_adds_up_to_the_trajectory_tip_acceleration() -> None:
    torque = np.array([30.0, 2.0])
    dt = 1e-4
    samples = simulate(PARAMS, Q, QD, torque, horizon=2 * dt, steps=2)
    middle = samples[1]
    tips = [tip_position(s.q, PARAMS) for s in samples]
    numeric = (tips[2] - 2 * tips[1] + tips[0]) / dt**2
    drift, input_qdd = affine_split(middle.q, middle.qd, torque, PARAMS)
    tip_drift, tip_input = tip_acceleration_split(middle.q, middle.qd, drift, input_qdd, PARAMS)
    np.testing.assert_allclose(tip_drift + tip_input, numeric, rtol=1e-4, atol=1e-3)


def test_simulate_samples_carry_the_split_at_each_state() -> None:
    torque = np.array([12.0, 0.0])
    samples = simulate(PARAMS, Q, QD, torque, horizon=0.5, steps=50)
    assert len(samples) == 51
    assert samples[0].t == 0.0 and samples[-1].t == pytest.approx(0.5)
    for sample in (samples[0], samples[25], samples[-1]):
        drift, input_qdd = affine_split(sample.q, sample.qd, torque, PARAMS)
        np.testing.assert_array_equal(sample.drift_qdd, drift)
        np.testing.assert_array_equal(sample.input_qdd, input_qdd)


def test_joint_torques_map_to_generalized_forces_with_matching_power() -> None:
    """A wrist torque acts between the links, so it enters as ``(-tau_w, tau_w)``."""
    shoulder, wrist = 40.0, -6.0
    generalized = generalized_torque(shoulder, wrist)
    np.testing.assert_array_equal(generalized, np.array([shoulder - wrist, wrist]))
    power_generalized = generalized @ QD
    power_joints = shoulder * QD[0] + wrist * (QD[1] - QD[0])
    assert power_generalized == pytest.approx(power_joints, rel=1e-15)


def test_simulate_rejects_bad_horizon_and_steps() -> None:
    with pytest.raises(ValueError):
        simulate(PARAMS, Q, QD, np.zeros(2), horizon=0.0, steps=10)
    with pytest.raises(ValueError):
        simulate(PARAMS, Q, QD, np.zeros(2), horizon=1.0, steps=0)
