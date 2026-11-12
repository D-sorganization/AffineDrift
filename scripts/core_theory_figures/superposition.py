"""Superposition figure generators from pinned AffineDrift dynamics runs."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from scripts.core_theory_figures.common import (
    ACCENT_ORANGE,
    GRID_COLOR,
    PRIMARY_BLUE,
    SAGE_GREEN,
    SLATE_GRAY,
    TEXT_COLOR,
    _clean_svg,
)
from src.affine_control.core_theory_simulations import (
    superposition_breakdown_series,
    superposition_instantaneous_vectors,
    superposition_modal_responses,
)


def _save(fig, output_path: Path) -> None:
    fig.savefig(output_path, metadata={"Creator": "AffineDrift; Core Theory Figure Generator"})
    plt.close(fig)
    _clean_svg(output_path)


def build_superposition_decomposition(output_path: Path) -> None:
    """Parallelogram of instantaneous joint accelerations at the pinned state."""
    vectors = superposition_instantaneous_vectors()
    a0 = vectors.baseline
    du1, du2, combined = vectors.delta_u1, vectors.delta_u2, vectors.combined
    with plt.rc_context({"font.size": 10.5, "svg.fonttype": "none", "svg.hashsalt": "super1"}):
        fig, axis = plt.subplots(figsize=(7.2, 5.2), layout="constrained")
        axis.set_facecolor("#ffffff")
        axis.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR, zorder=0)
        for start, delta, color, _label in (
            ((0, 0), a0, SLATE_GRAY, r"Drift $\ddot q_0$"),
            (a0, du1, PRIMARY_BLUE, r"$\Delta \ddot q_1$"),
            (a0, du2, ACCENT_ORANGE, r"$\Delta \ddot q_2$"),
            ((0, 0), combined, SAGE_GREEN, r"$\ddot q(\tau_1+\tau_2)$"),
        ):
            end = (start[0] + delta[0], start[1] + delta[1])
            axis.annotate(
                "",
                xy=end,
                xytext=start,
                arrowprops={"arrowstyle": "-|>", "color": color, "lw": 2.2, "mutation_scale": 16},
            )
        axis.set_xlim(
            min(0, a0[0], combined[0]) - 0.3, max(a0[0] + du1[0] + du2[0], combined[0]) + 0.4
        )
        axis.set_ylim(
            min(0, a0[1], combined[1]) - 0.5, max(a0[1] + du1[1] + du2[1], combined[1]) + 0.4
        )
        axis.set_xlabel(r"$\ddot q_1$ (rad/s$^2$)")
        axis.set_ylabel(r"$\ddot q_2$ (rad/s$^2$)")
        axis.set_title("Instantaneous Acceleration Superposition (Pinned State)", fontweight="bold")
        axis.spines[["top", "right"]].set_visible(False)
        _save(fig, output_path)


def build_superposition_modal_response(output_path: Path) -> None:
    """Unit-torque responses from ``M(q)^{-1}`` at the pinned GolfModel configuration."""
    bars = superposition_modal_responses()
    with plt.rc_context({"font.size": 10.5, "svg.fonttype": "none", "svg.hashsalt": "super2"}):
        fig, axis = plt.subplots(figsize=(7.4, 5.0), layout="constrained")
        axis.set_facecolor("#ffffff")
        axis.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR, axis="y", zorder=0)
        x = np.arange(3)
        width = 0.25
        colors = (PRIMARY_BLUE, ACCENT_ORANGE, SAGE_GREEN)
        for index in range(3):
            axis.bar(
                x + (index - 1) * width,
                bars.responses[index],
                width,
                label=rf"Unit torque at $q_{index + 1}$",
                color=colors[index],
            )
        axis.axhline(0, color=TEXT_COLOR, linewidth=1.0)
        axis.set_xticks(x)
        axis.set_xticklabels([rf"$\ddot q_{j}$ response" for j in (1, 2, 3)])
        axis.set_ylabel(r"$\Delta \ddot q_j$ (rad/s$^2$ per 100 N·m)")
        axis.set_title(r"Cross-Coupling via $M(q)^{-1}$ (Pinned Configuration)", fontweight="bold")
        axis.legend(loc="best", fontsize=8.5)
        axis.spines[["top", "right"]].set_visible(False)
        _save(fig, output_path)


def build_superposition_breakdown_boundary(output_path: Path) -> None:
    """Finite-horizon superposition error from pinned double-pendulum integration."""
    series = superposition_breakdown_series()
    with plt.rc_context({"font.size": 10.5, "svg.fonttype": "none", "svg.hashsalt": "super3"}):
        fig, (left, right) = plt.subplots(1, 2, figsize=(7.8, 4.6), layout="constrained")
        for axis in (left, right):
            axis.set_facecolor("#ffffff")
            axis.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR, zorder=0)
            axis.spines[["top", "right"]].set_visible(False)
        t_ms = series.time_s * 1000
        left.plot(
            t_ms, series.exact_q1, color=PRIMARY_BLUE, linewidth=2.2, label=r"$\Phi_t(u_1+u_2)$"
        )
        left.plot(
            t_ms,
            series.naive_q1,
            color=ACCENT_ORANGE,
            linestyle="--",
            linewidth=2.0,
            label="Naive sum",
        )
        left.plot(t_ms, series.drift_q1, color=SLATE_GRAY, linestyle=":", label=r"$\Phi_t(0)$")
        left.set_xlabel(r"Horizon $\Delta t$ (ms)")
        left.set_ylabel(r"$q_1$ (rad)")
        left.set_title("Trajectory vs. Superposition", fontweight="bold")
        left.legend(fontsize=8.0, loc="upper left")
        label_map = {0.2: "0.2× torques", 1.0: "1.0× torques", 2.0: "2.0× torques"}
        palette = (SAGE_GREEN, PRIMARY_BLUE, ACCENT_ORANGE)
        for scale, color in zip(series.torque_scales, palette, strict=True):
            right.plot(
                t_ms,
                series.scaled_position_error_norm[scale],
                color=color,
                linewidth=2.0,
                label=label_map[scale],
            )
        right.set_xlabel(r"Horizon $\Delta t$ (ms)")
        right.set_ylabel(r"$\|q_{u_1+u_2}-q_{u_1}-q_{u_2}+q_0\|$")
        right.set_title(r"Leading-Order $O(\Delta t^4)$ Position Error", fontweight="bold")
        right.legend(fontsize=8.0, loc="upper left")
        _save(fig, output_path)
