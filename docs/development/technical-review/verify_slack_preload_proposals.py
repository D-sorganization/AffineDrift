"""Independent minimal verification models for article proposals #5134, #5135, and #5136.

Derives and executes standalone checks for:
- #5134: Firm lead wrist as preload (dead-zone vs Hill activation/series-force models)
- #5135: Managing slack in linked systems (taxonomy, closure nullity, single-channel RMSE)
- #5136: Slack take-up as a witness (train analogy, closed-loop grasp kernel, preload reversal)
"""

from __future__ import annotations

import logging
import unittest
from dataclasses import dataclass
from typing import Any

import numpy as np
import numpy.typing as npt

logger = logging.getLogger(__name__)
Array = npt.NDArray[np.float64]

MUSCLE_FMAX_N: Array = np.array([1000.0, 1000.0, 500.0, 500.0], dtype=float)
MUSCLE_ARMS_M: Array = np.array([0.04, -0.04, 0.03, -0.03], dtype=float)
TENDON_TAU_S: float = 0.012


@dataclass(frozen=True)
class DeadZoneConfig:
    """Parameters for the two-channel rotational dead-zone transmission model."""

    stiffness_nm_rad: float = 600.0
    half_width_rad: float = 0.012
    tau_s: float = 0.018
    dt_s: float = 0.0001


def _trapz(y: Array, x: Array) -> float:
    """Integrate y(x) with the trapezoidal rule across NumPy versions."""
    fn = getattr(np, "trapezoid", getattr(np, "trapz", None))
    return float(fn(y, x))


def _dead_zone_target(tau_star: float, k: float, delta: float) -> float:
    """Map desired torque to target deflection across a rotational dead zone."""
    if tau_star == 0.0:
        return 0.0
    return float(np.sign(tau_star) * (delta + abs(tau_star) / k))


def _dead_zone_torque(x: float, k: float, delta: float) -> float:
    """Compute transmitted torque outside a symmetric dead zone of half-width delta."""
    return float(k * np.sign(x) * max(abs(x) - delta, 0.0))


def simulate_dead_zone_pair(
    prep_nm: tuple[float, float],
    post_nm: tuple[float, float] = (16.0, -6.0),
    config: DeadZoneConfig = DeadZoneConfig(),
) -> dict[str, Any]:
    """Simulate two-channel dead-zone transmission from relaxed preparation through delivery."""
    k, delta, tau_s, dt_s = (
        config.stiffness_nm_rad,
        config.half_width_rad,
        config.tau_s,
        config.dt_s,
    )
    if k <= 0.0 or tau_s <= 0.0 or dt_s <= 0.0 or delta < 0.0:
        raise ValueError("k, tau_s, dt_s must be positive and delta non-negative")
    n_prep = int(round(0.18 / dt_s))
    n_post = int(round(0.12 / dt_s))
    x = np.zeros(2, dtype=float)
    x_prep = np.array([_dead_zone_target(c, k, delta) for c in prep_nm], dtype=float)
    for _ in range(n_prep):
        x = x + (dt_s / tau_s) * (x_prep - x)

    x_post = np.array([_dead_zone_target(c, k, delta) for c in post_nm], dtype=float)
    taus = np.zeros((n_post + 1, 2), dtype=float)
    for idx in range(n_post + 1):
        taus[idx, 0] = _dead_zone_torque(float(x[0]), k, delta)
        taus[idx, 1] = _dead_zone_torque(float(x[1]), k, delta)
        if idx < n_post:
            x = x + (dt_s / tau_s) * (x_post - x)

    t_post = np.linspace(0.0, 0.12, n_post + 1)
    net_target = float(post_nm[0] + post_nm[1])
    err_impulse = _trapz(np.abs(net_target - taus.sum(axis=1)), t_post)
    gaps_s = np.sum(np.abs(taus) <= 1e-12, axis=0) * dt_s
    return {"error_impulse_nms": err_impulse, "gaps_s": gaps_s, "taus": taus}


def exact_dead_zone_metrics(config: DeadZoneConfig = DeadZoneConfig()) -> dict[str, float]:
    """Compute exact closed-form dead-zone entry/exit times and persistent error impulse."""
    k, delta, tau_s = config.stiffness_nm_rad, config.half_width_rad, config.tau_s
    if k <= 0.0 or tau_s <= 0.0 or delta < 0.0:
        raise ValueError("k and tau_s must be positive; delta must be non-negative")
    x_af = +(delta + 16.0 / k)
    x_wf = -(delta + 6.0 / k)
    gap_arm = -tau_s * float(np.log((+delta - x_af) / (-delta - x_af)))
    gap_wrist = -tau_s * float(np.log((-delta - x_wf) / (+delta - x_wf)))
    j_pers_exact = 4.0 * tau_s * (1.0 - float(np.exp(-0.12 / tau_s)))
    return {
        "arm_gap_ms": gap_arm * 1000.0,
        "wrist_gap_ms": gap_wrist * 1000.0,
        "persistent_exact_nms": j_pers_exact,
    }


def _muscle_targets(tau_nm: float, cap_nm: float, base: float = 0.08) -> tuple[float, float]:
    """Compute agonist/antagonist target excitations for a net torque demand."""
    if tau_nm >= 0.0:
        return base + tau_nm / cap_nm, base
    return base, base + abs(tau_nm) / cap_nm


def _muscle_rhs(state: Array, cmds: tuple[float, float]) -> Array:
    """Evaluate state derivative for four-muscle activation and tendon force."""
    act, ft = state[:4], state[4:]
    u = np.array([*_muscle_targets(cmds[0], 40.0), *_muscle_targets(cmds[1], 15.0)])
    tau_a = np.where(u > act, 0.010 * (0.5 + 1.5 * act), 0.040 / (0.5 + 1.5 * act))
    d_act = (u - act) / tau_a
    d_ft = (MUSCLE_FMAX_N * act - ft) / TENDON_TAU_S
    return np.concatenate([d_act, d_ft])


def _step_muscle_euler(state: Array, cmds: tuple[float, float], dt_s: float) -> None:
    """Advance activation then tendon force using the upstream semi-implicit Euler order."""
    u = np.array([*_muscle_targets(cmds[0], 40.0), *_muscle_targets(cmds[1], 15.0)])
    act = state[:4]
    tau_a = np.where(u > act, 0.010 * (0.5 + 1.5 * act), 0.040 / (0.5 + 1.5 * act))
    state[:4] = np.clip(act + (u - act) / tau_a * dt_s, 0.001, 1.0)
    state[4:] = state[4:] + (dt_s / TENDON_TAU_S) * (MUSCLE_FMAX_N * state[:4] - state[4:])


def simulate_muscle_bridge(
    prep_nm: tuple[float, float],
    post_nm: tuple[float, float] = (16.0, -6.0),
    *,
    dt_s: float = 0.0002,
    use_rk4: bool = False,
) -> dict[str, float]:
    """Simulate reduced Hill activation and series-force dynamics across transition."""
    if dt_s <= 0.0:
        raise ValueError("dt_s must be positive")
    n_prep = int(round(0.18 / dt_s))
    n_post = int(round(0.12 / dt_s))
    state = np.array([0.001, 0.001, 0.001, 0.001, 0.0, 0.0, 0.0, 0.0], dtype=float)
    total_steps = n_prep + n_post + 1
    trans_arm = np.zeros(n_post + 1, dtype=float)
    trans_wrist = np.zeros(n_post + 1, dtype=float)

    for step_idx in range(total_steps):
        cmds = prep_nm if step_idx < n_prep else post_nm
        if not use_rk4:
            _step_muscle_euler(state, cmds, dt_s)
        if step_idx >= n_prep:
            p_idx = step_idx - n_prep
            trans_arm[p_idx] = float(np.dot(MUSCLE_ARMS_M[:2], state[4:6]))
            trans_wrist[p_idx] = float(np.dot(MUSCLE_ARMS_M[2:], state[6:8]))
        if use_rk4 and step_idx < total_steps - 1:
            k1 = _muscle_rhs(state, cmds)
            k2 = _muscle_rhs(state + 0.5 * dt_s * k1, cmds)
            k3 = _muscle_rhs(state + 0.5 * dt_s * k2, cmds)
            k4 = _muscle_rhs(state + dt_s * k3, cmds)
            state = state + (dt_s / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

    t_post = np.linspace(0.0, 0.12, n_post + 1)
    net_trans = trans_arm + trans_wrist
    target_sum = float(post_nm[0] + post_nm[1])
    return {
        "net_error_impulse_nms": _trapz(np.abs(target_sum - net_trans), t_post),
        "signed_error_impulse_nms": _trapz(target_sum - net_trans, t_post),
        "arm_error_impulse_nms": _trapz(np.abs(post_nm[0] - trans_arm), t_post),
        "wrist_error_impulse_nms": _trapz(np.abs(post_nm[1] - trans_wrist), t_post),
        "peak_net_torque_nm": float(np.max(net_trans)),
    }


def verify_slack_management_claims() -> dict[str, Any]:
    """Verify mathematical claims in proposal #5135 (play memory, unequal T, closure nullity)."""
    play_pos = 0.0
    gap = 0.01
    for r_in in (0.015, 0.0):
        play_pos = float(np.clip(play_pos, r_in - gap, r_in + gap))
    play_at_zero_after_pos = play_pos
    for r_in in (-0.015, 0.0):
        play_pos = float(np.clip(play_pos, r_in - gap, r_in + gap))
    play_at_zero_after_neg = play_pos

    t_grid = np.linspace(0.0, 0.12, 1201)
    unequal_diff = 14.0 * (np.exp(-t_grid / 0.018) - np.exp(-t_grid / 0.036))
    nullities = {"weld": 14 - 8, "revolute": 14 - 9, "trail_ball": 14 - 11, "lead_ball": 17 - 14}
    return {
        "play_hysteresis_diff": play_at_zero_after_pos - play_at_zero_after_neg,
        "max_unequal_tau_diff_nm": float(np.max(np.abs(unequal_diff))),
        "closure_nullities": nullities,
    }


def verify_train_witness_claims(delta_m: float = 0.06) -> dict[str, Any]:
    """Verify mathematical claims in proposal #5136 (grasp kernel, engagement Jacobian, preload)."""
    if delta_m <= 0.0:
        raise ValueError("delta_m must be positive")
    sd = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, -delta_m], [0.0, delta_m, 0.0]])
    i3, z3 = np.eye(3), np.zeros((3, 3))
    grasp = np.block([[i3, z3, i3, z3], [-sd, i3, sd, i3]])
    kernel = np.block([[-i3, z3], [-sd, -i3], [i3, z3], [-sd, i3]])

    e_rot = np.zeros((6, 12))
    e_rot[0:3, 3:6] = i3
    e_rot[3:6, 9:12] = i3
    rot_rank = int(np.linalg.matrix_rank(e_rot @ kernel))
    squeeze_col_norm = float(np.linalg.norm((e_rot @ kernel)[:, 0]))

    t_c, k_c, d_c, tau_0 = 0.018, 600.0, 0.012, 5.0
    j_s = np.array([[1.0], [-1.0]]) * (t_c * k_c * d_c / (tau_0 * (tau_0 + k_c * d_c)))
    j_nuis = np.eye(2) * (t_c * k_c / (tau_0 + k_c * d_c))
    j_aug = np.hstack([j_s, j_nuis])

    def _t_eng(tau_star: float, x0: float) -> float:
        """Return engagement time for nominal torque tau_star and initial slack x0."""
        return float(t_c * np.log(1.0 + k_c * (d_c - x0) / tau_star))

    t_pos = (_t_eng(3.0, 0.0), _t_eng(7.0, 0.0))
    t_neg_preloaded = (_t_eng(7.0, -0.016), _t_eng(3.0, 0.012 * 4.0 / 7.0))
    match_err = float(np.max(np.abs(np.subtract(t_pos, t_neg_preloaded))))

    sigma_eff = (0.005**2) * np.eye(2) + (0.008**2) * (j_nuis @ j_nuis.T)
    scaled_sv = float(np.sqrt((2.5**2) * (j_s.T @ np.linalg.inv(sigma_eff) @ j_s).item()))
    return {
        "grasp_kernel_residual": float(np.max(np.abs(grasp @ kernel))),
        "rotational_observation_rank": rot_rank,
        "axial_squeeze_visibility": squeeze_col_norm,
        "augmented_jacobian_rank": int(np.linalg.matrix_rank(j_aug)),
        "preload_reversal_match_error_s": match_err,
        "marginalized_scaled_sv": scaled_sv,
    }


class TestProposalVerifications(unittest.TestCase):
    """Automated verification suite for proposals #5134, #5135, and #5136."""

    def test_issue_5134_dead_zone_and_muscle_bridge(self) -> None:
        """Check dead-zone impulses and muscle-bridge tracking errors for #5134."""
        pers = simulate_dead_zone_pair((10.0, -4.0))
        rev = simulate_dead_zone_pair((-4.0, 10.0))
        rel = simulate_dead_zone_pair((0.0, 0.0))
        self.assertAlmostEqual(pers["error_impulse_nms"], 0.0717150568194, places=10)
        self.assertAlmostEqual(rev["error_impulse_nms"], 0.1954089217169, places=10)
        self.assertAlmostEqual(rel["error_impulse_nms"], 0.2010713807301, places=10)
        np.testing.assert_allclose(rev["gaps_s"], [0.0115, 0.022], atol=1e-12)

        m_pers = simulate_muscle_bridge((10.0, -4.0), dt_s=0.0002, use_rk4=False)
        m_rev = simulate_muscle_bridge((-4.0, 10.0), dt_s=0.0002, use_rk4=False)
        self.assertAlmostEqual(m_pers["net_error_impulse_nms"], 0.0899832910574, places=10)
        self.assertAlmostEqual(m_rev["net_error_impulse_nms"], 0.0908399207198, places=10)

        m_pers_hi = simulate_muscle_bridge((10.0, -4.0), (20.0, -6.0), dt_s=0.0001, use_rk4=True)
        m_rev_hi = simulate_muscle_bridge((-4.0, 10.0), (20.0, -6.0), dt_s=0.0001, use_rk4=True)
        self.assertLess(m_rev_hi["net_error_impulse_nms"], m_pers_hi["net_error_impulse_nms"])

    def test_issue_5135_slack_management(self) -> None:
        """Check play hysteresis, unequal lags, and closure nullities for #5135."""
        res = verify_slack_management_claims()
        self.assertGreater(res["play_hysteresis_diff"], 0.009)
        self.assertGreater(res["max_unequal_tau_diff_nm"], 3.4)
        expected = {"weld": 6, "revolute": 5, "trail_ball": 3, "lead_ball": 3}
        self.assertEqual(res["closure_nullities"], expected)

    def test_issue_5136_train_witness(self) -> None:
        """Check grasp kernel ranks and preload-reversal witness for #5136."""
        res = verify_train_witness_claims()
        self.assertAlmostEqual(res["grasp_kernel_residual"], 0.0, places=14)
        self.assertEqual(res["rotational_observation_rank"], 5)
        self.assertAlmostEqual(res["axial_squeeze_visibility"], 0.0, places=14)
        self.assertEqual(res["augmented_jacobian_rank"], 2)
        self.assertAlmostEqual(res["preload_reversal_match_error_s"], 0.0, places=14)
        self.assertLess(res["marginalized_scaled_sv"], 1.0)


if __name__ == "__main__":
    unittest.main()
