"""Planar triple-pendulum #5187: Φ, FTLE, event Jacobian, and Monte Carlo."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

from src.affine_control.golf_model import GolfModel
from src.affine_control.swing_analysis import synthetic_swing

logger = logging.getLogger(__name__)

type Float64Matrix = NDArray[np.float64]
type Float64Vector = NDArray[np.float64]

IMPACT_PLANE_Y_M = 0.0


@dataclass(frozen=True)
class Planar5187Config:
    """Manufactured #5187 example parameters."""

    duration_s: float = 0.30
    dt_s: float = 2.5e-3
    fd_grad: float = 1e-5
    impact_bisect_steps: int = 50
    monte_carlo_samples: int = 128
    monte_carlo_seed: int = 5187
    sigma0_joint_rad: float = 0.01
    sigma0_joint_rad_s: float = 0.05
    torque_noise_std: float = 0.08


@dataclass(frozen=True)
class TrajectoryBundle:
    """Nominal trajectory samples for the planar #5187 pipeline."""

    times_s: Float64Vector
    states: Float64Matrix
    torques: Float64Matrix
    model: GolfModel


@dataclass(frozen=True)
class VariationalSlice:
    """Variational summaries (Phi, FTLE, sigma_max) at one time sample."""

    time_s: float
    phi: Float64Matrix
    sigma_max: float
    ftle_s_inv: float


@dataclass(frozen=True)
class ImpactState:
    """State and segment bookkeeping at the nominal ground-plane impact."""

    time_s: float
    state: Float64Vector
    segment_index: int


@dataclass(frozen=True)
class Planar5187PipelineResult:
    """End-to-end outputs for the planar triple-pendulum #5187 Monte Carlo study."""

    config: Planar5187Config
    bundle: TrajectoryBundle
    slices: tuple[VariationalSlice, ...]
    impact: ImpactState
    phi_nominal_to_event: Float64Matrix
    j_event: Float64Matrix
    j_fixed: Float64Matrix
    sigma_y: Float64Matrix
    rho_linear: float
    cos_m: float
    mc: dict[str, Any]


def _dim() -> int:
    """Return the planar 3-link state dimension (3 angles + 3 rates)."""
    return 6


def _pack(q: Float64Vector, qd: Float64Vector) -> Float64Vector:
    """Stack generalized coordinates and velocities into a state vector."""
    return np.concatenate([q, qd])


def _unpack(x: Float64Vector) -> tuple[Float64Vector, Float64Vector]:
    """Split a state vector into ``(q, qdot)`` halves."""
    return x[:3].copy(), x[3:].copy()


def _ode_rhs(model: GolfModel, x: Float64Vector, tau: Float64Vector) -> Float64Vector:
    """Evaluate $\\dot x = f(x,u)$ for the planar triple pendulum."""
    q, qd = _unpack(x)
    return np.concatenate([qd, model.forced_acceleration(q, qd, tau)])


def _rk4(model: GolfModel, x: Float64Vector, tau: Float64Vector, dt: float) -> Float64Vector:
    """Advance one RK4 step on the continuous-time ODE."""
    k1 = _ode_rhs(model, x, tau)
    k2 = _ode_rhs(model, x + 0.5 * dt * k1, tau)
    k3 = _ode_rhs(model, x + 0.5 * dt * k2, tau)
    k4 = _ode_rhs(model, x + dt * k3, tau)
    return x + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def _heun(model: GolfModel, x: Float64Vector, tau: Float64Vector, dt: float) -> Float64Vector:
    """Two-stage integrator for Monte Carlo only (faster than RK4)."""
    k1 = _ode_rhs(model, x, tau)
    k2 = _ode_rhs(model, x + dt * k1, tau)
    return x + 0.5 * dt * (k1 + k2)


def _jacobian_x(
    model: GolfModel, x: Float64Vector, tau: Float64Vector, eps: float
) -> Float64Matrix:
    """Finite-difference Jacobian $\\partial f / \\partial x$ at ``(x, tau)``."""

    def col(i: int) -> Float64Vector:
        """Return one column of the Jacobian (central differences)."""
        b = np.zeros(_dim())
        b[i] = 1.0
        return cast(
            Float64Vector,
            (_ode_rhs(model, x + eps * b, tau) - _ode_rhs(model, x - eps * b, tau)) / (2.0 * eps),
        )

    return np.column_stack([col(i) for i in range(_dim())])


def _tip_y(model: GolfModel, q: Float64Vector) -> float:
    """Club-tip vertical position in the world frame (y-component)."""
    return float(model.joint_positions(q)[-1, 1])


def _tip_vel(model: GolfModel, q: Float64Vector, qd: Float64Vector) -> Float64Vector:
    """Planar club-tip velocity from joint kinematics."""
    th = model.link_angles(q)
    vx = vy = 0.0
    for link in range(3):
        rate = float(np.sum(qd[: link + 1]))
        ell = model.lengths[link]
        vx += rate * ell * (-np.sin(th[link]))
        vy += rate * ell * (np.cos(th[link]))
    return np.array([vx, vy], dtype=np.float64)


def _speed(model: GolfModel, q: Float64Vector, qd: Float64Vector) -> float:
    """Scalar clubhead speed (Euclidean norm of tip velocity)."""
    return float(np.linalg.norm(_tip_vel(model, q, qd)))


def _path_rad(model: GolfModel, q: Float64Vector, qd: Float64Vector) -> float:
    """In-plane path direction proxy (heading angle of tip velocity)."""
    vx, vy = _tip_vel(model, q, qd)
    return float(np.arctan2(vy, vx))


def _interp_x_tau(
    bundle: TrajectoryBundle, t: float, seg_hi: int
) -> tuple[Float64Vector, Float64Vector]:
    """Linearly interpolate state and torque between grid points for time ``t``."""
    t0, t1 = float(bundle.times_s[seg_hi - 1]), float(bundle.times_s[seg_hi])
    alpha = (t - t0) / max(t1 - t0, 1.0e-15)
    x = (1.0 - alpha) * bundle.states[seg_hi - 1] + alpha * bundle.states[seg_hi]
    tau = (1.0 - alpha) * bundle.torques[seg_hi - 1] + alpha * bundle.torques[seg_hi]
    return x, tau


def build_nominal_bundle(cfg: Planar5187Config) -> TrajectoryBundle:
    """Integrate the manufactured torque program to a nominal state trajectory."""
    analysis = synthetic_swing(duration=cfg.duration_s, dt=cfg.dt_s)
    model = analysis.model()
    ts = np.asarray(analysis.time, dtype=np.float64)
    taus = np.asarray(analysis.joint_torques, dtype=np.float64)
    xs = np.zeros((len(ts), _dim()))
    xs[0] = _pack(analysis.joint_angles[0], analysis.joint_velocities[0])
    for k in range(1, len(ts)):
        dt = float(ts[k] - ts[k - 1])
        xs[k] = _rk4(model, xs[k - 1], taus[k - 1], dt)
    return TrajectoryBundle(times_s=ts, states=xs, torques=taus, model=model)


def propagate_phi(bundle: TrajectoryBundle, eps: float) -> tuple[VariationalSlice, ...]:
    """Explicit-Euler propagation of $\\Phi$ with SVD growth and FTLE estimates."""
    model = bundle.model
    phi = np.eye(_dim())
    out: list[VariationalSlice] = []
    prev_t = float(bundle.times_s[0])
    sig = np.linalg.svd(phi, compute_uv=False)
    out.append(
        VariationalSlice(time_s=prev_t, phi=phi.copy(), sigma_max=float(sig[0]), ftle_s_inv=0.0)
    )
    for k in range(1, len(bundle.times_s)):
        dt = float(bundle.times_s[k] - bundle.times_s[k - 1])
        a_mat = _jacobian_x(model, bundle.states[k - 1], bundle.torques[k - 1], eps)
        phi = cast(Float64Matrix, phi + dt * (a_mat @ phi))
        t = float(bundle.times_s[k])
        sig = np.linalg.svd(phi, compute_uv=False)
        smax = float(sig[0])
        horizon = max(t - prev_t, 1.0e-12)
        ftle = float(np.log(max(smax, 1.0e-300)) / horizon)
        prev_t = t
        out.append(VariationalSlice(time_s=t, phi=phi.copy(), sigma_max=smax, ftle_s_inv=ftle))
    return tuple(out)


def locate_impact(bundle: TrajectoryBundle, cfg: Planar5187Config) -> ImpactState:
    """Bisect for the first upward crossing of the impact guard (tip $y=0$)."""
    ys = np.array([_tip_y(bundle.model, _unpack(x)[0]) for x in bundle.states])
    for idx in range(1, len(ys)):
        if ys[idx - 1] <= IMPACT_PLANE_Y_M < ys[idx]:
            lo_t = float(bundle.times_s[idx - 1])
            hi_t = float(bundle.times_s[idx])
            x_lo = bundle.states[idx - 1].copy()
            tau_seg = bundle.torques[idx - 1].copy()
            for _ in range(cfg.impact_bisect_steps):
                mid = 0.5 * (lo_t + hi_t)
                dt_try = mid - float(bundle.times_s[idx - 1])
                x_try = _rk4(bundle.model, bundle.states[idx - 1], tau_seg, dt_try)
                y_try = _tip_y(bundle.model, _unpack(x_try)[0])
                if y_try <= IMPACT_PLANE_Y_M:
                    lo_t, x_lo = mid, x_try.copy()
                else:
                    hi_t = mid
            return ImpactState(time_s=lo_t, state=x_lo, segment_index=idx)
    raise RuntimeError("Nominal trajectory never crosses the impact plane (tip y upward).")


def phi_at_time(
    bundle: TrajectoryBundle,
    slices: tuple[VariationalSlice, ...],
    t_event: float,
    seg_index: int,
    eps: float,
) -> Float64Matrix:
    """Φ(t_event, t0) via one explicit-Euler substep from the last grid before *t_event*."""
    k = seg_index - 1
    dt_sub = t_event - float(bundle.times_s[k])
    if dt_sub < 1.0e-15:
        return slices[k].phi.copy()
    model = bundle.model
    phi_k = slices[k].phi.copy()
    a_mat = _jacobian_x(model, bundle.states[k], bundle.torques[k], eps)
    return cast(Float64Matrix, phi_k + dt_sub * (a_mat @ phi_k))


def _grad_scalar(fn: Any, x: Float64Vector, eps: float) -> Float64Vector:
    """Central-difference gradient of a scalar map on $\\mathbb{R}^6$."""
    g = np.zeros(_dim())
    for i in range(_dim()):
        b = np.zeros(_dim())
        b[i] = 1.0
        g[i] = (fn(x + eps * b) - fn(x - eps * b)) / (2.0 * eps)
    return g


def _grad_h(model: GolfModel, x: Float64Vector, eps: float) -> Float64Vector:
    """Gradient of the impact guard ``h =`` club-tip $y$-coordinate."""

    def hval(state: Float64Vector) -> float:
        """Guard value at full state ``state``."""
        return _tip_y(model, _unpack(state)[0])

    return _grad_scalar(hval, x, eps)


def _task_jacobian(model: GolfModel, x: Float64Vector, eps: float) -> Float64Matrix:
    """Stacked task Jacobian [speed; path angle] for the planar proxy outputs."""

    def speed(xv: Float64Vector) -> float:
        """Clubhead speed as a function of full state."""
        q, qd = _unpack(xv)
        return _speed(model, q, qd)

    def pth(xv: Float64Vector) -> float:
        """Path-angle proxy as a function of full state."""
        q, qd = _unpack(xv)
        return _path_rad(model, q, qd)

    return np.vstack([_grad_scalar(speed, x, eps), _grad_scalar(pth, x, eps)])


def event_sensitivity_phi(
    model: GolfModel,
    x_event: Float64Vector,
    tau_event: Float64Vector,
    phi: Float64Matrix,
    eps: float,
) -> Float64Matrix:
    """Φ_e = Φ + f (∂t_e/∂x0) with ∂t_e/∂x0 = −(dh/dx Φ)/(dh/dt)."""
    dh_dx = _grad_h(model, x_event, eps).reshape(1, _dim())
    fvec = _ode_rhs(model, x_event, tau_event).reshape(_dim(), 1)
    h_dot = float(np.squeeze(dh_dx @ fvec))
    if abs(h_dot) < 1.0e-8:
        logger.warning(
            "Small |dh/dt|=%s at impact; event-time scaling may be ill-conditioned.", h_dot
        )
    row_te = -(dh_dx @ phi) / h_dot
    return cast(Float64Matrix, phi + fvec @ row_te)


def _cos_m(
    model: GolfModel, j_speed: Float64Vector, j_path: Float64Vector, q: Float64Vector
) -> float:
    """Mass-weighted cosine between speed and path task rows (velocity block)."""
    gs = j_speed[3:6]
    gp = j_path[3:6]
    minv = np.linalg.inv(model.rigid_mass_matrix(q))
    num = float(gs @ minv @ gp)
    den = float(np.sqrt(max(gs @ minv @ gs, 0.0) * max(gp @ minv @ gp, 0.0)) + 1.0e-30)
    return num / den


def _integrate_to_impact(
    model: GolfModel,
    x0: Float64Vector,
    ts: Float64Vector,
    taus: Float64Matrix,
) -> tuple[float, Float64Vector]:
    """Simulate forward with Heun steps; bisect the segment that crosses impact."""
    x = x0.copy()
    y_prev = _tip_y(model, _unpack(x)[0])
    for k in range(1, len(ts)):
        dt = float(ts[k] - ts[k - 1])
        x_next = _heun(model, x, taus[k - 1], dt)
        y_next = _tip_y(model, _unpack(x_next)[0])
        if y_prev <= IMPACT_PLANE_Y_M < y_next:
            lo, hi = 0.0, dt
            x_a = x.copy()
            for _ in range(40):
                mid = 0.5 * (lo + hi)
                x_m = _heun(model, x, taus[k - 1], mid)
                y_m = _tip_y(model, _unpack(x_m)[0])
                if y_m <= IMPACT_PLANE_Y_M:
                    lo, x_a = mid, x_m.copy()
                else:
                    hi = mid
            return float(ts[k - 1]) + lo, x_a
        x, y_prev = x_next, y_next
    raise RuntimeError("Perturbed trajectory did not reach impact plane.")


def _initial_state_covariance(cfg: Planar5187Config) -> Float64Matrix:
    """Diagonal covariance on joint angles and rates for analysis."""
    return np.diag(
        np.array(
            [
                cfg.sigma0_joint_rad**2,
                cfg.sigma0_joint_rad**2,
                cfg.sigma0_joint_rad**2,
                cfg.sigma0_joint_rad_s**2,
                cfg.sigma0_joint_rad_s**2,
                cfg.sigma0_joint_rad_s**2,
            ],
            dtype=np.float64,
        )
    )


def _linear_task_stats(
    phi_event: Float64Matrix, sigma0: Float64Matrix, j_event: Float64Matrix
) -> tuple[Float64Matrix, float, float, float, float]:
    """Push $\\Sigma_0$ through $\\Phi_e$ and return $\\Sigma_y$ and Pearson $\\rho$."""
    sig_state = phi_event @ sigma0 @ phi_event.T
    sigma_y = j_event @ sig_state @ j_event.T
    v11, v12 = float(sigma_y[0, 0]), float(sigma_y[0, 1])
    v22 = float(sigma_y[1, 1])
    rho = float(v12 / max(np.sqrt(max(v11, 1.0e-30) * max(v22, 1.0e-30)), 1.0e-30))
    return sigma_y, v11, v12, v22, rho


def _monte_carlo_at_impact(
    bundle: TrajectoryBundle, config: Planar5187Config
) -> tuple[Float64Vector, Float64Vector, float]:
    """Sample joint and torque noise; return speed/path samples and Monte Carlo $\\rho$."""
    rng = np.random.default_rng(config.monte_carlo_seed)
    x_nom = bundle.states[0].copy()
    v_samples = np.zeros(config.monte_carlo_samples)
    p_samples = np.zeros(config.monte_carlo_samples)
    for sample_idx in range(config.monte_carlo_samples):
        z = rng.standard_normal(_dim())
        delta = np.array(
            [
                z[0] * config.sigma0_joint_rad,
                z[1] * config.sigma0_joint_rad,
                z[2] * config.sigma0_joint_rad,
                z[3] * config.sigma0_joint_rad_s,
                z[4] * config.sigma0_joint_rad_s,
                z[5] * config.sigma0_joint_rad_s,
            ],
            dtype=np.float64,
        )
        noise = rng.normal(scale=config.torque_noise_std, size=bundle.torques.shape)
        taup = bundle.torques + noise
        _te, xf = _integrate_to_impact(bundle.model, x_nom + delta, bundle.times_s, taup)
        qf, qdf = _unpack(xf)
        v_samples[sample_idx] = _speed(bundle.model, qf, qdf)
        p_samples[sample_idx] = _path_rad(bundle.model, qf, qdf)

    rho_mc = (
        float(np.corrcoef(v_samples, p_samples)[0, 1])
        if np.std(v_samples) > 0 and np.std(p_samples) > 0
        else float("nan")
    )
    return v_samples, p_samples, rho_mc


def run_planar_5187_pipeline(cfg: Planar5187Config | None = None) -> Planar5187PipelineResult:
    """Run nominal trajectory, variational growth, linear $\\Sigma_y$, and Monte Carlo."""
    config = cfg or Planar5187Config()
    eps = config.fd_grad
    bundle = build_nominal_bundle(config)
    slices = propagate_phi(bundle, eps)
    impact = locate_impact(bundle, config)

    phi_pre = phi_at_time(bundle, slices, impact.time_s, impact.segment_index, eps)
    x_evt, tau_evt = _interp_x_tau(bundle, impact.time_s, impact.segment_index)
    phi_event = event_sensitivity_phi(bundle.model, x_evt, tau_evt, phi_pre, eps)

    j_event = _task_jacobian(bundle.model, x_evt, eps)
    fixed_idx = int(np.searchsorted(bundle.times_s, impact.time_s, side="right") - 1)
    j_fixed = _task_jacobian(bundle.model, bundle.states[fixed_idx], eps)

    sigma0 = _initial_state_covariance(config)
    sigma_y, v11, _v12, v22, rho = _linear_task_stats(phi_event, sigma0, j_event)

    qe, _ = _unpack(x_evt)
    cos_m = _cos_m(bundle.model, j_event[0], j_event[1], qe)

    v_samples, p_samples, rho_mc = _monte_carlo_at_impact(bundle, config)

    s_event = np.linalg.svd(phi_event, compute_uv=False)
    sigma_max_event = float(s_event[0])
    sigma_max_global = max(float(s.sigma_max) for s in slices)

    qei, qdei = _unpack(x_evt)
    v_nom = _speed(bundle.model, qei, qdei)
    psi_nom = _path_rad(bundle.model, qei, qdei)

    mc = {
        "impact_time_s": impact.time_s,
        "clubhead_speed_m_s": v_nom,
        "path_angle_rad": psi_nom,
        "cos_m": cos_m,
        "n_samples": config.monte_carlo_samples,
        "speed_mean": float(np.mean(v_samples)),
        "speed_std": float(np.std(v_samples, ddof=1)),
        "path_std_rad": float(np.std(p_samples, ddof=1)),
        "rho_monte_carlo": rho_mc,
        "linear_sigma_v": float(np.sqrt(max(v11, 0.0))),
        "linear_sigma_path_rad": float(np.sqrt(max(v22, 0.0))),
        "rho_linear": rho,
        "sigma_max_phi_event": sigma_max_event,
        "sigma_max_global": sigma_max_global,
        "sigma_max_at_impact": float(slices[max(fixed_idx, 0)].sigma_max),
        "ftle_at_impact_per_s": float(slices[max(fixed_idx, 0)].ftle_s_inv),
    }

    return Planar5187PipelineResult(
        config=config,
        bundle=bundle,
        slices=slices,
        impact=impact,
        phi_nominal_to_event=phi_event,
        j_event=j_event,
        j_fixed=j_fixed,
        sigma_y=sigma_y,
        rho_linear=rho,
        cos_m=cos_m,
        mc=mc,
    )
