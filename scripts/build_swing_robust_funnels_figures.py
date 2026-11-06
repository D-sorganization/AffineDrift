#!/usr/bin/env python3
"""Generate SVG figures for ``articles/swing-robust-funnels-ucm.qmd`` (#5187).

Run from the repository root::

    python3 scripts/build_swing_robust_funnels_figures.py

Writes under ``articles/swing-robust-funnels-figures/`` and updates
``planar-5187-results.json`` with pinned numerics for the prose.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow `python scripts/...` from any cwd without setting PYTHONPATH.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.patches import Ellipse  # noqa: E402

ROOT = _REPO_ROOT
OUTPUT_DIR = ROOT / "articles" / "swing-robust-funnels-figures"
RESULTS_JSON = OUTPUT_DIR / "planar-5187-results.json"

# Display windowing (matches article narrative).
LAST_WINDOW_S = 0.15
LATENCY_BAND_S = (0.100, 0.150)


def _run_pipeline() -> object:
    from src.affine_control.planar_5187 import run_planar_5187_pipeline

    return run_planar_5187_pipeline()


def _covariance_ellipse(
    ax: plt.Axes, cov: np.ndarray, mean: np.ndarray, n_sigma: float, **kwargs: object
) -> None:
    vals, vecs = np.linalg.eigh(cov)
    order = np.argsort(vals)[::-1]
    vals, vecs = vals[order], vecs[:, order]
    width, height = 2.0 * n_sigma * np.sqrt(np.maximum(vals, 0.0))
    angle_deg = float(np.degrees(np.arctan2(vecs[1, 0], vecs[0, 0])))
    ellipse = Ellipse(
        xy=(mean[0], mean[1]),
        width=width,
        height=height,
        angle=angle_deg,
        fill=False,
        **kwargs,
    )
    ax.add_patch(ellipse)


def _figure_sigma_max(result: object) -> Figure:
    slices = result.slices
    impact_t = result.impact.time_s
    times = np.array([s.time_s for s in slices])
    sigmas = np.array([s.sigma_max for s in slices])
    window_left = max(0.0, impact_t - LAST_WINDOW_S)

    fig, ax = plt.subplots(figsize=(8.5, 4.0), layout="constrained")
    ax.plot(times * 1000.0, sigmas, color="C0", label=r"$\sigma_{\max}(\Phi)$")
    ax.axvspan(window_left * 1000.0, impact_t * 1000.0, color="C1", alpha=0.18, label="Last 150 ms")
    lat_lo = max(0.0, impact_t - LATENCY_BAND_S[1]) * 1000.0
    lat_hi = max(0.0, impact_t - LATENCY_BAND_S[0]) * 1000.0
    ax.axvspan(lat_lo, lat_hi, color="C2", alpha=0.12, label="Example latency band (100–150 ms)")
    ax.axvline(
        impact_t * 1000.0, color="gray", linestyle="--", linewidth=1.0, label="Nominal impact"
    )
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel(r"$\sigma_{\max}(\Phi)$")
    ax.set_title("Variational Growth on the Manufactured Planar Triple-Pendulum Example (#5187)")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper left", fontsize=9)
    return fig


def _figure_ellipse(result: object) -> Figure:
    sigma_y = np.asarray(result.sigma_y)
    mc = result.mc
    v_nom = float(mc["clubhead_speed_m_s"])
    psi_nom = float(mc["path_angle_rad"])
    rho = float(mc["rho_linear"])
    fig, ax = plt.subplots(figsize=(5.5, 5.0), layout="constrained")
    mean = np.array([v_nom, psi_nom])
    _covariance_ellipse(
        ax, sigma_y, mean, n_sigma=2.0, edgecolor="C0", linewidth=1.5, label="Linear ±2σ"
    )
    ax.plot(mean[0], mean[1], "o", color="C0", label="Nominal (linearization point)")
    ax.set_xlabel(r"Clubhead speed $v$ (m/s)")
    ax.set_ylabel(r"In-plane path angle $\psi$ (rad)")
    ax.set_title(rf"Linear $\Sigma_y$ at impact; $\rho$ = {rho:.3f}")
    ax.grid(alpha=0.25)
    ax.legend(loc="best", fontsize=9)
    return fig


def _figure_sens_compare(result: object) -> Figure:
    j_ev = np.asarray(result.j_event)
    j_fx = np.asarray(result.j_fixed)
    labels = (r"$\|\nabla v\|$", r"$\|\nabla\psi\|$")
    x = np.arange(2)
    width = 0.35
    fig, ax = plt.subplots(figsize=(6.5, 4.0), layout="constrained")
    ax.bar(
        x - width / 2,
        [np.linalg.norm(j_ev[0]), np.linalg.norm(j_ev[1])],
        width,
        label="Event time",
        color="C0",
    )
    ax.bar(
        x + width / 2,
        [np.linalg.norm(j_fx[0]), np.linalg.norm(j_fx[1])],
        width,
        label="Fixed grid time",
        color="C1",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Gradient norm (mixed units)")
    ax.set_title("Speed vs Path Sensitivity: Event Map vs Fixed Clock Time")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    return fig


def _figure_monte_carlo(result: object) -> Figure:
    from src.affine_control.planar_5187 import (
        Planar5187Config,
        _integrate_to_impact,
        _path_rad,
        _speed,
        _unpack,
    )

    cfg: Planar5187Config = result.config
    bundle = result.bundle
    rng = np.random.default_rng(cfg.monte_carlo_seed)
    x_nom = bundle.states[0].copy()
    v_pts = []
    p_pts = []
    for _ in range(min(500, cfg.monte_carlo_samples)):
        z = rng.standard_normal(6)
        delta = np.array(
            [
                z[0] * cfg.sigma0_joint_rad,
                z[1] * cfg.sigma0_joint_rad,
                z[2] * cfg.sigma0_joint_rad,
                z[3] * cfg.sigma0_joint_rad_s,
                z[4] * cfg.sigma0_joint_rad_s,
                z[5] * cfg.sigma0_joint_rad_s,
            ]
        )
        noise = rng.normal(scale=cfg.torque_noise_std, size=bundle.torques.shape)
        _te, xf = _integrate_to_impact(
            bundle.model, x_nom + delta, bundle.times_s, bundle.torques + noise
        )
        qf, qdf = _unpack(xf)
        v_pts.append(_speed(bundle.model, qf, qdf))
        p_pts.append(_path_rad(bundle.model, qf, qdf))

    v_pts = np.asarray(v_pts)
    p_pts = np.asarray(p_pts)

    mc = result.mc
    v_nom = float(mc["clubhead_speed_m_s"])
    psi_nom = float(mc["path_angle_rad"])
    sigma_y = np.asarray(result.sigma_y)

    fig, ax = plt.subplots(figsize=(6.0, 5.2), layout="constrained")
    ax.scatter(v_pts, p_pts, s=6, alpha=0.35, c="C1", label="Nonlinear Monte Carlo")
    mean = np.array([v_nom, psi_nom])
    _covariance_ellipse(
        ax, sigma_y, mean, n_sigma=2.0, edgecolor="C0", linewidth=1.5, label="Linear ±2σ"
    )
    ax.plot(mean[0], mean[1], "o", color="C0")
    rho_mc = float(mc["rho_monte_carlo"])
    rho_lin = float(mc["rho_linear"])
    ax.set_xlabel(r"Clubhead speed $v$ (m/s)")
    ax.set_ylabel(r"Path angle $\psi$ (rad)")
    ax.set_title("Linear vs Monte Carlo at impact " f"(rho_lin={rho_lin:.3f}, rho_MC={rho_mc:.3f})")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.25)
    return fig


def _results_dict(result: object) -> dict[str, object]:
    cfg = result.config
    mc = result.mc
    return {
        "config": {
            "duration_s": cfg.duration_s,
            "dt_s": cfg.dt_s,
            "fd_grad": cfg.fd_grad,
            "monte_carlo_samples": cfg.monte_carlo_samples,
            "monte_carlo_seed": cfg.monte_carlo_seed,
            "sigma0_joint_rad": cfg.sigma0_joint_rad,
            "sigma0_joint_rad_s": cfg.sigma0_joint_rad_s,
            "torque_noise_std": cfg.torque_noise_std,
        },
        "mc": mc,
        "gradient_norms": {
            "event_speed": float(np.linalg.norm(result.j_event[0])),
            "event_path": float(np.linalg.norm(result.j_event[1])),
            "fixed_speed": float(np.linalg.norm(result.j_fixed[0])),
            "fixed_path": float(np.linalg.norm(result.j_fixed[1])),
        },
    }


def build_figures(result: object, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with plt.rc_context(
        {"font.size": 11, "svg.fonttype": "none", "svg.hashsalt": "swing-robust-5187"}
    ):
        for name, builder in (
            ("fig-sigma-max.svg", _figure_sigma_max),
            ("fig-cov-ellipse.svg", _figure_ellipse),
            ("fig-event-vs-fixed.svg", _figure_sens_compare),
            ("fig-mc-linear.svg", _figure_monte_carlo),
        ):
            fig = builder(result)
            try:
                out = output_dir / name
                with out.open("w", encoding="utf-8", newline="\n") as stream:
                    fig.savefig(stream, format="svg", metadata={"Date": None})
            finally:
                plt.close(fig)
    results_path = output_dir / "planar-5187-results.json"
    results_path.write_text(json.dumps(_results_dict(result), indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory for SVG and JSON output",
    )
    args = parser.parse_args()
    result = _run_pipeline()
    build_figures(result, args.output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
