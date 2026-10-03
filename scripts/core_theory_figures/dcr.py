"""DCR figures for declared mathematical examples, without golfer calibration.

Legacy builder names and publication URLs are retained. All coordinates and times
are normalized; the speed panel samples separate states, not a swing trajectory.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Ellipse
from numpy.typing import NDArray

from scripts.core_theory_figures.common import (
    ACCENT_ORANGE,
    GRID_COLOR,
    PRIMARY_BLUE,
    SAGE_GREEN,
    SLATE_GRAY,
    TEXT_COLOR,
    _clean_svg,
)

# Stipulated fixed-state example: W=I, epsilon=0, and ||u||_2 <= 1.
EXAMPLE_DRIFT = (2.0, 0.5)
EXAMPLE_INPUT_SCALES = (1.0, 0.5)
EXAMPLE_USED_INPUT = (-0.5, 0.5)
PLOT_STYLE = matplotlib.RcParams(
    {
        "font.size": 11,
        "svg.fonttype": "path",
        "text.color": TEXT_COLOR,
        "axes.labelcolor": TEXT_COLOR,
        "axes.edgecolor": SLATE_GRAY,
        "xtick.color": TEXT_COLOR,
        "ytick.color": TEXT_COLOR,
    }
)


def _save_figure(figure: Figure, output_path: Path) -> None:
    """Save deterministic SVG bytes and close only this figure."""
    try:
        figure.savefig(output_path, metadata={"Date": None, "Creator": "AffineDrift"})
    finally:
        plt.close(figure)
    _clean_svg(output_path)


def _style_axes(axis: Axes) -> None:
    axis.grid(True, color=GRID_COLOR, linestyle="--", linewidth=0.6, alpha=0.7)
    axis.spines[["top", "right"]].set_visible(False)
    axis.set_axisbelow(True)


def _draw_acceleration_sets(axis: Axes) -> None:
    width, height = 2 * np.asarray(EXAMPLE_INPUT_SCALES)
    specifications = (
        ((0.0, 0.0), PRIMARY_BLUE, "--", r"Input Effects $B_a\mathcal{U}$"),
        (EXAMPLE_DRIFT, SAGE_GREEN, "-", r"Total Set $a_d+B_a\mathcal{U}$"),
    )
    for center, color, style, label in specifications:
        axis.add_patch(
            Ellipse(
                center,
                width,
                height,
                facecolor="none",
                edgecolor=color,
                linewidth=2,
                linestyle=style,
                label=label,
            )
        )


def _example_vectors() -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    drift = np.asarray(EXAMPLE_DRIFT)
    used_input = np.asarray(EXAMPLE_USED_INPUT)
    if np.linalg.norm(used_input) > 1.0:
        raise ValueError("The declared example input must belong to the unit disk")
    return drift, np.diag(EXAMPLE_INPUT_SCALES) @ used_input


def _draw_acceleration_vectors(axis: Axes) -> None:
    drift, contribution = _example_vectors()
    specifications = (
        (np.zeros(2), drift, SLATE_GRAY, r"Drift $a_d$"),
        (drift, contribution, ACCENT_ORANGE, r"Input Contribution $B_a u$"),
        (np.zeros(2), drift + contribution, SAGE_GREEN, r"Total Acceleration $a$"),
    )
    for origin, vector, color, label in specifications:
        axis.quiver(
            *origin,
            *vector,
            angles="xy",
            scale_units="xy",
            scale=1,
            width=0.008,
            color=color,
            label=label,
            zorder=4,
        )
    axis.plot(0, 0, "o", color=TEXT_COLOR, markersize=4)
    axis.text(-0.05, -0.18, "Zero Acceleration", ha="center", fontsize=11)


def build_dcr_vector_decomposition(output_path: Path) -> None:
    """Plot input-only and drift-translated acceleration sets at one fixed state."""
    with plt.rc_context({**PLOT_STYLE, "svg.hashsalt": "dcr-acceleration-sets-v2"}):
        figure, axis = plt.subplots(figsize=(7.4, 5.6))
        figure.subplots_adjust(left=0.14, right=0.96, bottom=0.26, top=0.73)
        figure.suptitle("Fixed-State Acceleration Sets", fontsize=14)
        _style_axes(axis)
        _draw_acceleration_sets(axis)
        _draw_acceleration_vectors(axis)
        axis.set(
            xlim=(-1.3, 3.3),
            ylim=(-0.65, 1.15),
            aspect="equal",
            xlabel=r"Normalized Acceleration $a_1$",
            ylabel=r"Normalized Acceleration $a_2$",
        )
        axis.legend(
            loc="lower center", bbox_to_anchor=(0.5, 1.04), ncol=2, fontsize=10.5, frameon=False
        )
        figure.text(
            0.5,
            0.09,
            r"$a_d=(2,0.5),\ B_a=\mathrm{diag}(1,0.5),\ \|u\|_2\leq1$",
            ha="center",
            fontsize=11,
        )
        figure.text(
            0.5,
            0.035,
            r"Used Input $u=(-0.5,0.5)$; $W=I$, $\varepsilon=0$",
            ha="center",
            fontsize=11,
        )
        _save_figure(figure, output_path)


def _two_panels(title: str, declaration: str) -> tuple[Figure, tuple[Axes, Axes]]:
    figure, axes = plt.subplots(2, 1, figsize=(7.4, 6.2), sharex=True)
    figure.subplots_adjust(left=0.16, right=0.96, bottom=0.13, top=0.79, hspace=0.24)
    figure.suptitle(title, fontsize=14, y=0.98)
    figure.text(0.5, 0.855, declaration, ha="center", va="center", fontsize=11)
    for axis in axes:
        _style_axes(axis)
    return figure, (axes[0], axes[1])


def build_dcr_swing_phases(output_path: Path) -> None:
    """Plot the article's nonmonotone manufactured speed-state family at q=0."""
    with plt.rc_context({**PLOT_STYLE, "svg.hashsalt": "dcr-speed-states-v2"}):
        speeds = np.linspace(0.0, 3.0, 301)
        # Euler-Lagrange for I=e^(2q), U=-e^(2q)/2: qdd=1-v^2+e^(-2q)u.
        drift_magnitude = np.abs(1.0 - speeds**2)
        capacity = np.ones_like(speeds)  # q=0, |u|<=1, W=1, epsilon=0.
        figure, (upper, lower) = _two_panels(
            "Quadratic Velocity Dependence\nDoes Not Imply Monotone DCR",
            r"Separate States at $q=0$; $|u|\leq1$, $W=1$, $\varepsilon=0$",
        )
        upper.plot(speeds, drift_magnitude, color=PRIMARY_BLUE, label="Drift Magnitude")
        upper.plot(
            speeds, capacity, color=ACCENT_ORANGE, linestyle="--", label="Available Capacity"
        )
        upper.set_ylabel("Normalized\nAcceleration")
        lower.plot(speeds, drift_magnitude / capacity, color=SAGE_GREEN, label="DCR")
        sample_speeds = np.arange(4, dtype=float)
        lower.scatter(sample_speeds, np.abs(1 - sample_speeds**2), color=SAGE_GREEN, zorder=3)
        lower.set(xlabel=r"Speed Parameter $\nu$", ylabel="DCR\n(Dimensionless)")
        for axis in (upper, lower):
            axis.set_ylim(-0.35, 8.7)
            axis.legend(loc="upper left", frameon=False)
        _save_figure(figure, output_path)


def _plot_endpoint_projection(axis: Axes, horizons: NDArray[np.float64], name: str) -> None:
    half_width = horizons**2 / 2 if name == "Position" else horizons
    axis.plot(horizons, half_width, color=PRIMARY_BLUE, label=f"Upper {name} Bound")
    axis.plot(horizons, -half_width, color=ACCENT_ORANGE, label=f"Lower {name} Bound")
    axis.fill_between(horizons, -half_width, half_width, color=PRIMARY_BLUE, alpha=0.12)
    axis.legend(loc="upper left", frameon=False)


def build_dcr_reachability_tubes(output_path: Path) -> None:
    """Plot exact marginal endpoint intervals for qdot=v, vdot=u, |u|<=1."""
    with plt.rc_context({**PLOT_STYLE, "svg.hashsalt": "dcr-endpoint-projections-v2"}):
        horizons = np.linspace(0.0, 1.0, 101)
        figure, (position, velocity) = _two_panels(
            "Endpoint Projections of a Bounded Double Integrator",
            r"$\dot q=v,\ \dot v=u,\ |u|\leq1$; $q(0)=v(0)=0$" + "\nSeparate Marginal Projections",
        )
        _plot_endpoint_projection(position, horizons, "Position")
        _plot_endpoint_projection(velocity, horizons, "Velocity")
        position.set_ylabel("Normalized Endpoint\nDisplacement")
        velocity.set(xlabel=r"Independent Horizon $T$", ylabel="Normalized Endpoint\nVelocity")
        _save_figure(figure, output_path)
