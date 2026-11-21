"""Zero-Torque Counterfactual (ZTCF) figure generators from pinned GolfModel runs."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from scripts.core_theory_figures.common import (
    ACCENT_ORANGE,
    GRID_COLOR,
    PRIMARY_BLUE,
    SAGE_GREEN,
    SLATE_GRAY,
    TEXT_COLOR,
    _clean_svg,
)
from src.affine_control.core_theory_simulations import ZtcfFigureSeries, ztcf_figure_series

_BRANCH_STYLE = {
    0: ("#8c9ba5", "--", "ZTCF at $t_0=0$ ms (model time)"),
    50: (ACCENT_ORANGE, "-.", "ZTCF at $t_0=50$ ms"),
    100: (SAGE_GREEN, ":", "ZTCF at $t_0=100$ ms"),
    150: ("#6f8f6a", (0, (3, 1, 1, 1)), "ZTCF at $t_0=150$ ms"),
}


def _style_axis(axis: Axes) -> None:
    axis.set_facecolor("#ffffff")
    axis.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR, zorder=0)
    axis.spines[["top", "right"]].set_visible(False)


def _save(fig: Figure, output_path: Path) -> None:
    fig.savefig(output_path, metadata={"Creator": "AffineDrift; Core Theory Figure Generator"})
    plt.close(fig)
    _clean_svg(output_path)


def _plot_branch_speeds(axis: Axes, series: ZtcfFigureSeries) -> None:
    axis.plot(
        series.time_s * 1000,
        series.actual_speed_m_s,
        color=PRIMARY_BLUE,
        linewidth=2.6,
        label="Constant-torque reference (pinned run)",
        zorder=5,
    )
    for step, speeds in series.branch_speeds_m_s.items():
        color, style, label = _BRANCH_STYLE.get(
            step, (SLATE_GRAY, "--", f"ZTCF branch step {step}")
        )
        time_ms = np.linspace(0, series.time_s[-1] * 1000, len(speeds))
        axis.plot(
            time_ms, speeds, color=color, linestyle=style, linewidth=2.0, label=label, zorder=4
        )


def build_ztcf_trajectory_divergence(output_path: Path) -> None:
    """Clubhead tip paths for the pinned constant-torque run and ZTCF branches."""
    series = ztcf_figure_series()
    with plt.rc_context({"font.size": 10.5, "svg.fonttype": "none", "svg.hashsalt": "ztcf1"}):
        fig, axis = plt.subplots(figsize=(7.2, 5.2), layout="constrained")
        _style_axis(axis)
        axis.plot(
            series.actual_tip_xy[:, 0],
            series.actual_tip_xy[:, 1],
            color=PRIMARY_BLUE,
            linewidth=2.6,
            label="Constant-torque reference",
            zorder=4,
        )
        for step, path in series.branch_tip_xy.items():
            color, style, label = _BRANCH_STYLE.get(step, (SLATE_GRAY, "--", f"Branch {step}"))
            axis.plot(
                path[:, 0], path[:, 1], color=color, linestyle=style, linewidth=2.0, label=label
            )
        axis.scatter(
            series.actual_tip_xy[-1, 0], series.actual_tip_xy[-1, 1], color="#d9534f", s=60
        )
        axis.set_xlabel("Club tip $x$ (m)")
        axis.set_ylabel("Club tip $y$ (m)")
        axis.set_title("Schematic: ZTCF Branch Paths From Pinned GolfModel Run", fontweight="bold")
        axis.legend(loc="best", fontsize=8.5)
        _save(fig, output_path)


def build_ztcf_clubhead_speed_loss(output_path: Path) -> None:
    """Clubhead speed under the reference run and branched ZTCF integrations."""
    series = ztcf_figure_series()
    with plt.rc_context({"font.size": 10.5, "svg.fonttype": "none", "svg.hashsalt": "ztcf2"}):
        fig, axis = plt.subplots(figsize=(7.4, 5.0), layout="constrained")
        _style_axis(axis)
        _plot_branch_speeds(axis, series)
        axis.set_xlabel("Model time (ms)")
        axis.set_ylabel("Clubhead speed (m/s)")
        axis.set_title("Pinned Three-Link Model: Reference vs. ZTCF Branches", fontweight="bold")
        axis.legend(loc="best", fontsize=8.5)
        _save(fig, output_path)


def build_ztcf_passive_dynamics_attribution(output_path: Path) -> None:
    """Distal joint drift vs. input acceleration along the pinned reference run."""
    series = ztcf_figure_series()
    total = series.distal_drift_qdd + series.distal_input_qdd
    with plt.rc_context({"font.size": 10.5, "svg.fonttype": "none", "svg.hashsalt": "ztcf3"}):
        fig, axis = plt.subplots(figsize=(7.6, 5.2), layout="constrained")
        _style_axis(axis)
        axis.plot(
            series.time_s * 1000,
            total,
            color=TEXT_COLOR,
            linewidth=2.2,
            label=r"$\ddot q_3$ (total)",
        )
        axis.plot(
            series.time_s * 1000,
            series.distal_input_qdd,
            color=ACCENT_ORANGE,
            linestyle="--",
            linewidth=2.0,
            label=r"Declared input $M^{-1}\tau$",
        )
        axis.plot(
            series.time_s * 1000,
            series.distal_drift_qdd,
            color=PRIMARY_BLUE,
            linewidth=2.0,
            label=r"Drift $-M^{-1}(C\dot q + g)$",
        )
        axis.set_xlabel("Model time (ms)")
        axis.set_ylabel(r"Distal $\ddot q_3$ (rad/s$^2$)")
        axis.set_title("Pointwise Split Along Pinned Constant-Torque Run", fontweight="bold")
        axis.legend(loc="best", fontsize=9.0)
        _save(fig, output_path)
