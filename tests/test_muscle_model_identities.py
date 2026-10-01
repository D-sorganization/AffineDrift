"""Mathematical contract verification tests for muscle-tendon and joint mechanics models."""

import math
from dataclasses import dataclass

import numpy as np
import pytest
from scipy.integrate import solve_ivp


def test_pennation_kinematics_and_transmitted_power() -> None:
    """Verify constant-thickness pennation kinematics, power, and dx/dl = 1/cos."""
    h = 0.02
    l_fiber = 0.1
    f_fiber = 200.0
    v_fiber = -0.05
    v_tendon = 0.01

    cos_alpha = math.sqrt(1.0 - (h / l_fiber) ** 2)
    f_tendon = f_fiber * cos_alpha
    v_mt = v_tendon + v_fiber / cos_alpha
    transmitted_power = f_tendon * (v_mt - v_tendon)

    assert transmitted_power == pytest.approx(-10.0, rel=1e-12)

    delta_l = 1e-6
    x_plus = math.sqrt((l_fiber + delta_l) ** 2 - h**2)
    x_minus = math.sqrt((l_fiber - delta_l) ** 2 - h**2)
    dx_dl_fd = (x_plus - x_minus) / (2.0 * delta_l)

    assert dx_dl_fd == pytest.approx(1.0 / cos_alpha, rel=1e-8)
    assert abs(dx_dl_fd - cos_alpha) > 0.01  # Confirms dx/dl is 1/cos, not cos


def _activation_ode(t: float, a: np.ndarray, u: float) -> np.ndarray:
    act = a[0]
    tau = 0.015 * (0.5 + 1.5 * act) if u > act else 0.05 / (0.5 + 1.5 * act)
    return np.array([(u - act) / tau])


@pytest.mark.parametrize(
    ("a0", "u", "target_a", "expected_t"),
    [
        (0.0, 1.0, 0.95, 0.0684969682),
        (1.0, 0.0, 0.05, 0.1749199855),
    ],
)
def test_activation_step_times(a0: float, u: float, target_a: float, expected_t: float) -> None:
    """Verify activation and deactivation step times against ODE numerical integration."""
    sol = solve_ivp(
        _activation_ode,
        t_span=(0.0, 0.25),
        y0=[a0],
        args=(u,),
        dense_output=True,
        rtol=1e-10,
        atol=1e-12,
    )
    assert sol.success and sol.sol is not None
    simulated_a = float(sol.sol(expected_t)[0])
    assert simulated_a == pytest.approx(target_a, abs=1e-8)


@dataclass(frozen=True)
class TendonConfig:
    f0: float = 4000.0
    slack: float = 0.25
    eps0: float = 0.04
    k: float = 35.0


def _tendon_force(eps: float, cfg: TendonConfig) -> float:
    return cfg.f0 * math.expm1(cfg.k * eps) / math.expm1(cfg.k * cfg.eps0)


def _tendon_energy(eps: float, cfg: TendonConfig) -> float:
    denom = math.expm1(cfg.k * cfg.eps0)
    return cfg.f0 * cfg.slack * (math.expm1(cfg.k * eps) / cfg.k - eps) / denom


@pytest.mark.parametrize("k", [10.0, 35.0])
def test_tendon_mechanics_and_energy(k: float) -> None:
    """Verify tendon force positivity, inversion, derivative, and dU/dlength = FT."""
    cfg = TendonConfig(k=k)

    for fraction in (0.5, 0.75, 1.0):
        eps_inv = math.log1p(fraction * math.expm1(cfg.k * cfg.eps0)) / cfg.k
        f_calc = _tendon_force(eps_inv, cfg)
        assert f_calc > 0.0
        assert f_calc == pytest.approx(fraction * cfg.f0, rel=1e-9)
        if fraction == 1.0:
            assert eps_inv == pytest.approx(cfg.eps0, rel=1e-12)

    eps = 0.03
    d_eps = 1e-6
    df_deps_fd = (_tendon_force(eps + d_eps, cfg) - _tendon_force(eps - d_eps, cfg)) / (2.0 * d_eps)
    df_deps_analytic = cfg.f0 * cfg.k * math.exp(cfg.k * eps) / math.expm1(cfg.k * cfg.eps0)
    assert df_deps_fd == pytest.approx(df_deps_analytic, rel=1e-7)

    length = cfg.slack * (1.0 + eps)
    dl = 1e-6
    u_plus = _tendon_energy((length + dl) / cfg.slack - 1.0, cfg)
    u_minus = _tendon_energy((length - dl) / cfg.slack - 1.0, cfg)
    du_dl_fd = (u_plus - u_minus) / (2.0 * dl)
    assert du_dl_fd == pytest.approx(_tendon_force(eps, cfg), rel=1e-7)


def test_joint_curved_path_and_stiffness() -> None:
    """Verify joint curved path torque and stiffness against finite difference -dtau/dq."""

    def length(q: float) -> float:
        return 0.3 + 0.04 * q + 0.01 * q**2

    def lprime(q: float) -> float:
        return 0.04 + 0.02 * q

    def force(l_val: float) -> float:
        return 100.0 + 500.0 * (l_val - 0.3)

    def torque(q: float) -> float:
        return -force(length(q)) * lprime(q)

    for q in (0.0, 0.5, 1.2):
        l_val = length(q)
        lp_val = lprime(q)
        f_val = force(l_val)
        k_analytic = 500.0 * (lp_val**2) + f_val * 0.02

        dq = 1e-6
        neg_dtau_dq_fd = -(torque(q + dq) - torque(q - dq)) / (2.0 * dq)
        assert neg_dtau_dq_fd == pytest.approx(k_analytic, rel=1e-7)
