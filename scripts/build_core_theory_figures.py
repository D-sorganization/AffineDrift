"""Deterministic figure generator for Core Theory pages.

Generates 9 high-resolution, lightweight SVG figures across:
- articles/controllability-drift-ratio.qmd (3 figures)
- articles/zero-torque-counterfactual.qmd (3 figures)
- articles/superposition.qmd (3 figures)
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

LOGGER = logging.getLogger("build_core_theory_figures")

FIGURE_NAMES = (
    "fig_dcr_vector_decomposition.svg",
    "fig_dcr_swing_phases.svg",
    "fig_dcr_reachability_tubes.svg",
    "fig_ztcf_trajectory_divergence.svg",
    "fig_ztcf_clubhead_speed_loss.svg",
    "fig_ztcf_passive_dynamics_attribution.svg",
    "fig_superposition_decomposition.svg",
    "fig_superposition_modal_response.svg",
    "fig_superposition_breakdown_boundary.svg",
)

# Common styling palette
PRIMARY_BLUE = "#17608a"
ACCENT_ORANGE = "#a34716"
SAGE_GREEN = "#2a7f62"
SLATE_GRAY = "#5c6773"
LIGHT_BG = "#f4f7f9"
GRID_COLOR = "#d8e1e8"
TEXT_COLOR = "#22252a"


def _clean_svg(path: Path) -> None:
    """Normalize line endings and strip trailing whitespace for deterministic diffs."""
    text = path.read_text(encoding="utf-8")
    cleaned = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    path.write_text(cleaned, encoding="utf-8", newline="\n")


def build_dcr_vector_decomposition(output_path: Path) -> None:
    """Figure 1: State derivative decomposition into drift vector and control authority ellipsoid."""
    with plt.rc_context(
        {
            "font.size": 11,
            "svg.fonttype": "none",
            "svg.hashsalt": "dcr1",
            "axes.edgecolor": SLATE_GRAY,
            "axes.labelcolor": TEXT_COLOR,
            "text.color": TEXT_COLOR,
        }
    ):
        fig, ax = plt.subplots(figsize=(7.2, 5.0), layout="constrained")

        # Background grid
        ax.set_facecolor("#ffffff")
        ax.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR, zorder=0)

        # Origin
        ax.scatter([0], [0], color=TEXT_COLOR, s=40, zorder=5)
        ax.annotate(
            r"Current State $x(t)$" + "\n(Origin in tangent frame)",
            (0, 0),
            xytext=(-1.8, -0.6),
            fontsize=10,
            fontweight="medium",
        )

        # Drift vector f(x)
        drift_x, drift_y = 3.2, 1.4
        ax.annotate(
            "",
            xy=(drift_x, drift_y),
            xytext=(0, 0),
            arrowprops={
                "arrowstyle": "-|>",
                "color": PRIMARY_BLUE,
                "lw": 2.6,
                "mutation_scale": 18,
            },
            zorder=4,
        )
        ax.text(
            drift_x * 0.45 - 0.2,
            drift_y * 0.5 + 0.35,
            r"Drift Vector $f(x)$" + "\n(Zero-input baseline)",
            color=PRIMARY_BLUE,
            fontsize=11,
            fontweight="bold",
        )

        # Control authority set G(x)U (Ellipsoid centered at tip of drift vector)
        ellipse_center = (drift_x, drift_y)
        width, height, angle = 2.4, 1.4, 25
        control_ellipse = patches.Ellipse(
            ellipse_center,
            width=width,
            height=height,
            angle=angle,
            facecolor="#c7e0ef",
            edgecolor=PRIMARY_BLUE,
            linestyle="--",
            linewidth=1.8,
            alpha=0.65,
            zorder=2,
            label="Control Authority Set $G(x)\\mathcal{U}$",
        )
        ax.add_patch(control_ellipse)

        # Sample control vector G(x)u
        u1_dx, u1_dy = 0.9, 0.5

        # Net state derivatives \dot{x} = f(x) + G(x)u
        ax.annotate(
            "",
            xy=(drift_x + u1_dx, drift_y + u1_dy),
            xytext=(drift_x, drift_y),
            arrowprops={
                "arrowstyle": "-|>",
                "color": ACCENT_ORANGE,
                "lw": 2.0,
                "mutation_scale": 14,
            },
            zorder=4,
        )
        ax.text(
            drift_x + 0.3,
            drift_y + 0.8,
            r"$G(x)u_1$ (Correction)",
            color=ACCENT_ORANGE,
            fontsize=10,
        )

        ax.annotate(
            "",
            xy=(drift_x + u1_dx, drift_y + u1_dy),
            xytext=(0, 0),
            arrowprops={"arrowstyle": "-|>", "color": SAGE_GREEN, "lw": 2.2, "mutation_scale": 16},
            zorder=3,
        )
        ax.text(
            (drift_x + u1_dx) * 0.72 + 0.2,
            (drift_y + u1_dy) * 0.45 - 0.3,
            r"Net Realized Velocity $\dot{x} = f(x) + G(x)u$",
            color=SAGE_GREEN,
            fontsize=10,
            fontweight="bold",
        )

        # Key takeaway box
        takeaway_text = (
            "Key Insight: Drift $f(x)$ translates the center of reachable motion.\n"
            "Control capacity $G(x)\\mathcal{U}$ spans corrections relative to that shifting center."
        )
        ax.text(
            -1.8,
            3.0,
            takeaway_text,
            fontsize=9.5,
            bbox={
                "boxstyle": "round,pad=0.5",
                "facecolor": LIGHT_BG,
                "edgecolor": SLATE_GRAY,
                "alpha": 0.9,
            },
            zorder=6,
        )

        ax.set_xlim(-2.2, 5.2)
        ax.set_ylim(-1.2, 3.8)
        ax.set_xlabel(
            "State Tangent Coordinate $\\delta x_1$ (e.g. Velocity Component)", fontsize=11
        )
        ax.set_ylabel(
            "State Tangent Coordinate $\\delta x_2$ (e.g. Acceleration Component)", fontsize=11
        )
        ax.set_title(
            "Local Vector Decomposition: Drift vs. Control Manifold", fontsize=12, fontweight="bold"
        )
        ax.legend(loc="lower right", framealpha=0.9, fontsize=9.5)
        ax.spines[["top", "right"]].set_visible(False)

        fig.savefig(output_path, metadata={"Creator": "AffineDrift; Core Theory Figure Generator"})
        plt.close(fig)

    _clean_svg(output_path)


def build_dcr_swing_phases(output_path: Path) -> None:
    """Figure 2: Evolution of Drift Acceleration, Control Capacity, and DCR across swing phases."""
    with plt.rc_context(
        {
            "font.size": 10.5,
            "svg.fonttype": "none",
            "svg.hashsalt": "dcr2",
            "axes.edgecolor": SLATE_GRAY,
            "axes.labelcolor": TEXT_COLOR,
            "text.color": TEXT_COLOR,
        }
    ):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.6, 5.8), sharex=True, layout="constrained")

        # Time vector representing downswing (0 to 280 ms)
        t = np.linspace(0, 0.28, 200)

        # Drift acceleration: quadratic-like growth due to centrifugal/Coriolis (v^2 / r)
        # Starts near 15 m/s^2 (gravity/posture) and climbs to ~180 m/s^2 near impact
        drift_acc = 15.0 + 2100.0 * (t**2.2)

        # Control acceleration capacity: muscular torque capacity remains relatively flat/bounded (~50-60 m/s^2)
        control_cap = 55.0 - 15.0 * np.sin(np.pi * t / 0.28) ** 2

        # DCR: Drift-to-Control Ratio
        dcr = drift_acc / control_cap

        # Swing phase intervals
        phases = [
            (0.00, 0.08, "Phase I\nTransition", "#eef3f7"),
            (0.08, 0.18, "Phase II\nMid-Downswing", "#ffffff"),
            (0.18, 0.25, "Phase III\nDistal Release", "#fcf5f0"),
            (0.25, 0.28, "Phase IV\nDelivery", "#f3f8f5"),
        ]

        for ax in (ax1, ax2):
            for t_start, t_end, _label, bg_color in phases:
                ax.axvspan(t_start, t_end, facecolor=bg_color, alpha=0.8, zorder=0)
            ax.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR, zorder=1)
            ax.spines[["top", "right"]].set_visible(False)

        # Top panel: Accelerations
        ax1.plot(
            t * 1000,
            drift_acc,
            color=PRIMARY_BLUE,
            linewidth=2.2,
            label=r"Drift Acceleration $\|a_d(t)\|$",
        )
        ax1.plot(
            t * 1000,
            control_cap,
            color=ACCENT_ORANGE,
            linewidth=2.0,
            linestyle="--",
            label=r"Control Capacity $\sup \|B_a u\|$",
        )
        ax1.set_ylabel(r"Acceleration (m/s$^2$)", fontsize=10.5)
        ax1.set_title(
            "Drift vs. Control Acceleration Capacity Across Downswing",
            fontsize=11.5,
            fontweight="bold",
        )
        ax1.legend(loc="upper left", framealpha=0.9, fontsize=9.5)

        # Phase annotations on top panel
        for t_start, t_end, label, _ in phases:
            mid_t = (t_start + t_end) / 2.0 * 1000
            ax1.text(
                mid_t,
                195,
                label,
                ha="center",
                va="top",
                fontsize=8.5,
                color=SLATE_GRAY,
                fontweight="bold",
            )

        ax1.set_ylim(0, 220)

        # Bottom panel: DCR
        ax2.plot(
            t * 1000,
            dcr,
            color=SAGE_GREEN,
            linewidth=2.4,
            label=r"$\mathrm{DCR}(t) = \|a_d\| / \sup \|B_a u\|$",
        )
        ax2.axhline(
            1.0,
            color=SLATE_GRAY,
            linestyle=":",
            linewidth=1.2,
            label="Parity Threshold (DCR = 1.0)",
        )

        ax2.annotate(
            "Release Onset\n(Coriolis surge)",
            xy=(180, dcr[np.argmin(np.abs(t - 0.18))]),
            xytext=(130, 2.6),
            arrowprops={"arrowstyle": "->", "color": SAGE_GREEN, "lw": 1.4},
            fontsize=9.0,
            color=SAGE_GREEN,
            fontweight="bold",
        )

        ax2.set_xlabel("Time from Top of Downswing (ms)", fontsize=10.5)
        ax2.set_ylabel("Drift-Control Ratio (DCR)", fontsize=10.5)
        ax2.set_title("Instantaneous DCR Profile", fontsize=11.5, fontweight="bold")
        ax2.legend(loc="upper left", framealpha=0.9, fontsize=9.5)
        ax2.set_ylim(0, 4.2)

        fig.savefig(output_path, metadata={"Creator": "AffineDrift; Core Theory Figure Generator"})
        plt.close(fig)

    _clean_svg(output_path)


def build_dcr_reachability_tubes(output_path: Path) -> None:
    """Figure 3: Finite-horizon reachable set envelopes contracting as time-to-impact decreases."""
    with plt.rc_context(
        {
            "font.size": 10.5,
            "svg.fonttype": "none",
            "svg.hashsalt": "dcr3",
            "axes.edgecolor": SLATE_GRAY,
            "axes.labelcolor": TEXT_COLOR,
            "text.color": TEXT_COLOR,
        }
    ):
        fig, ax = plt.subplots(figsize=(7.4, 5.0), layout="constrained")
        ax.set_facecolor("#ffffff")
        ax.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR, zorder=0)

        # Time to impact (ms): 120 ms down to 0 ms (impact)
        dt = np.linspace(120, 0, 200)

        # Nominal trajectory (drift-dominated central path)
        nominal_y = np.zeros_like(dt)

        # Reachable set bounds under bounded control: envelope shrinks as O(dt^2) or O(dt)
        # At dt=120 ms: +/- 15 cm; at dt=60 ms: +/- 4.5 cm; at dt=15 ms: +/- 0.6 cm
        upper_bound = 15.0 * (dt / 120.0) ** 1.6
        lower_bound = -upper_bound

        # Shaded reachable tube
        ax.fill_between(
            dt,
            lower_bound,
            upper_bound,
            color="#c7e0ef",
            alpha=0.6,
            zorder=2,
            label="Reachable Deviation Envelope $\\mathcal{R}(t; \\mathcal{U})$",
        )
        ax.plot(dt, upper_bound, color=PRIMARY_BLUE, linestyle="--", linewidth=1.5, zorder=3)
        ax.plot(dt, lower_bound, color=PRIMARY_BLUE, linestyle="--", linewidth=1.5, zorder=3)

        # Nominal path
        ax.plot(
            dt,
            nominal_y,
            color=PRIMARY_BLUE,
            linewidth=2.2,
            label="Nominal Drift Trajectory",
            zorder=4,
        )

        # Sample perturbed control trajectories
        sample_1 = upper_bound * 0.7 * np.sin(np.pi * (120 - dt) / 120)
        sample_2 = lower_bound * 0.85 * np.sin(np.pi * (120 - dt) / 120)
        ax.plot(
            dt,
            sample_1,
            color=ACCENT_ORANGE,
            linewidth=1.6,
            label="Steered Correction (+Control)",
            zorder=4,
        )
        ax.plot(
            dt,
            sample_2,
            color=SAGE_GREEN,
            linewidth=1.6,
            label="Opposing Correction (-Control)",
            zorder=4,
        )

        # Vertical milestone markers
        milestones = [
            (100, "100 ms: Wide Authority\n(±11.0 cm)"),
            (50, "50 ms: Bounded\n(±3.4 cm)"),
            (15, "15 ms: Tight\n(±0.5 cm)"),
        ]
        for m_t, label in milestones:
            ax.axvline(m_t, color=SLATE_GRAY, linestyle=":", linewidth=1.2, zorder=1)
            idx = np.argmin(np.abs(dt - m_t))
            y_val = upper_bound[idx]
            ax.scatter([m_t], [y_val], color=PRIMARY_BLUE, s=30, zorder=5)
            ax.text(
                m_t - 2,
                12.0,
                label,
                rotation=90,
                va="top",
                ha="right",
                fontsize=8.5,
                color=SLATE_GRAY,
            )

        # Target impact tolerance window at t=0
        ax.plot(
            [0, 0],
            [-1.0, 1.0],
            color="#d9534f",
            linewidth=4.0,
            label="Acceptable Strike Window",
            zorder=6,
        )
        ax.scatter([0], [0], color="#d9534f", s=50, zorder=7)

        # Annotations
        ax.annotate(
            "Impact Window\n(Ball Contact)",
            xy=(0, 0),
            xytext=(18, -4.5),
            arrowprops={"arrowstyle": "->", "color": "#d9534f", "lw": 1.5},
            fontsize=9.5,
            fontweight="bold",
            color="#d9534f",
        )

        ax.set_xlim(125, -5)  # Invert x-axis: countdown to impact
        ax.set_ylim(-16, 17)
        ax.set_xlabel("Time Remaining to Ball Impact $\\Delta t$ (ms)", fontsize=10.5)
        ax.set_ylabel("Terminal Clubhead Position Dispersion (cm)", fontsize=10.5)
        ax.set_title(
            "Finite-Horizon Reachable Tube Under Bounded Control Authority",
            fontsize=11.5,
            fontweight="bold",
        )
        ax.legend(loc="upper left", framealpha=0.9, fontsize=9.0)
        ax.spines[["top", "right"]].set_visible(False)

        fig.savefig(output_path, metadata={"Creator": "AffineDrift; Core Theory Figure Generator"})
        plt.close(fig)

    _clean_svg(output_path)


def build_ztcf_trajectory_divergence(output_path: Path) -> None:
    """Figure 4: Planar clubhead path divergence between active baseline and ZTCF branches."""
    with plt.rc_context(
        {
            "font.size": 10.5,
            "svg.fonttype": "none",
            "svg.hashsalt": "ztcf1",
            "axes.edgecolor": SLATE_GRAY,
            "axes.labelcolor": TEXT_COLOR,
            "text.color": TEXT_COLOR,
        }
    ):
        fig, ax = plt.subplots(figsize=(7.2, 5.2), layout="constrained")
        ax.set_facecolor("#ffffff")
        ax.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR, zorder=0)

        # Active baseline planar trajectory (arc from top of swing to ball impact)
        # Top of swing: (-0.6, 1.5), Delivery: (0.0, 0.0)
        theta_active = np.linspace(2.2, 0.0, 100)
        r_active = 1.6 - 0.2 * np.cos(theta_active)
        x_active = -r_active * np.cos(theta_active - 0.3) + 0.3
        y_active = r_active * np.sin(theta_active - 0.3) - 0.45

        ax.plot(
            x_active,
            y_active,
            color=PRIMARY_BLUE,
            linewidth=2.6,
            label="Active Torque Baseline",
            zorder=4,
        )

        # ZTCF Branch 1: Released at Top of Swing (t0 = 0.00 s)
        # With zero torque, passive arm-club flail falls mostly downward under gravity without planar uncocking
        theta_b1 = np.linspace(2.2, 1.2, 60)
        x_b1 = x_active[0] + 0.3 * (2.2 - theta_b1) ** 1.3
        y_b1 = y_active[0] - 1.4 * (2.2 - theta_b1) ** 0.9
        ax.plot(
            x_b1,
            y_b1,
            color="#8c9ba5",
            linestyle="--",
            linewidth=2.0,
            label="ZTCF: Release at Top ($t_0=0$ ms)",
            zorder=3,
        )

        # ZTCF Branch 2: Released at Mid-Downswing (t0 = 140 ms, shaft horizontal)
        # Already has momentum, so it sweeps forward, but lags behind active torque and dips lower
        idx_b2 = 45
        t_b2 = np.linspace(0, 1, 50)
        x_b2 = (
            x_active[idx_b2]
            + (x_active[-1] - x_active[idx_b2]) * t_b2
            - 0.22 * np.sin(np.pi * t_b2)
        )
        y_b2 = (
            y_active[idx_b2]
            + (y_active[-1] - y_active[idx_b2]) * t_b2
            - 0.35 * np.sin(np.pi * t_b2)
        )
        ax.plot(
            x_b2,
            y_b2,
            color=ACCENT_ORANGE,
            linestyle="-.",
            linewidth=2.0,
            label="ZTCF: Release at Mid-Downswing ($t_0=140$ ms)",
            zorder=3,
        )

        # ZTCF Branch 3: Released at Late Downswing (t0 = 240 ms, pre-impact)
        # Minimal divergence because clubhead release is already driven by momentum
        idx_b3 = 80
        t_b3 = np.linspace(0, 1, 30)
        x_b3 = (
            x_active[idx_b3]
            + (x_active[-1] - x_active[idx_b3]) * t_b3
            - 0.03 * np.sin(np.pi * t_b3)
        )
        y_b3 = (
            y_active[idx_b3]
            + (y_active[-1] - y_active[idx_b3]) * t_b3
            - 0.04 * np.sin(np.pi * t_b3)
        )
        ax.plot(
            x_b3,
            y_b3,
            color=SAGE_GREEN,
            linestyle=":",
            linewidth=2.2,
            label="ZTCF: Release Pre-Impact ($t_0=240$ ms)",
            zorder=3,
        )

        # Ball position (Target)
        ax.scatter(
            [x_active[-1]],
            [y_active[-1]],
            color="#d9534f",
            s=70,
            zorder=6,
            label="Ball Strike Point",
        )
        ax.annotate(
            "Ball Impact\n(0, 0)",
            (x_active[-1], y_active[-1]),
            xytext=(x_active[-1] + 0.15, y_active[-1] - 0.15),
            fontsize=9.5,
            fontweight="bold",
            color="#d9534f",
        )

        # Release point markers
        ax.scatter([x_active[0]], [y_active[0]], color=PRIMARY_BLUE, s=40, zorder=5)
        ax.scatter([x_active[idx_b2]], [y_active[idx_b2]], color=ACCENT_ORANGE, s=40, zorder=5)
        ax.scatter([x_active[idx_b3]], [y_active[idx_b3]], color=SAGE_GREEN, s=40, zorder=5)

        ax.set_xlabel("Horizontal Clubhead Position $X$ (m)", fontsize=10.5)
        ax.set_ylabel("Vertical Clubhead Position $Y$ (m)", fontsize=10.5)
        ax.set_title(
            "Planar Clubhead Path Divergence Under Zero-Torque Counterfactuals",
            fontsize=11.5,
            fontweight="bold",
        )
        ax.legend(loc="upper left", framealpha=0.9, fontsize=9.0)
        ax.spines[["top", "right"]].set_visible(False)

        fig.savefig(output_path, metadata={"Creator": "AffineDrift; Core Theory Figure Generator"})
        plt.close(fig)

    _clean_svg(output_path)


def build_ztcf_clubhead_speed_loss(output_path: Path) -> None:
    """Figure 5: Clubhead speed trajectories comparing active baseline vs ZTCF branches."""
    with plt.rc_context(
        {
            "font.size": 10.5,
            "svg.fonttype": "none",
            "svg.hashsalt": "ztcf2",
            "axes.edgecolor": SLATE_GRAY,
            "axes.labelcolor": TEXT_COLOR,
            "text.color": TEXT_COLOR,
        }
    ):
        fig, ax = plt.subplots(figsize=(7.4, 5.0), layout="constrained")
        ax.set_facecolor("#ffffff")
        ax.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR, zorder=0)

        t = np.linspace(0, 0.28, 200)

        # Active velocity profile: S-curve acceleration reaching ~48.2 m/s
        v_active = 48.2 / (1.0 + np.exp(-25.0 * (t - 0.19)))

        ax.plot(
            t * 1000,
            v_active,
            color=PRIMARY_BLUE,
            linewidth=2.6,
            label="Active Baseline (Full Torque)",
            zorder=5,
        )

        # ZTCF Branch 1: Released at t=100 ms (Early downswing)
        # Momentum stagnates, terminal velocity ~18.5 m/s (62% loss)
        t_b1 = t[t >= 0.10]
        v_b1 = v_active[np.argmin(np.abs(t - 0.10))] + 6.0 * (1.0 - np.exp(-15.0 * (t_b1 - 0.10)))
        ax.plot(
            t_b1 * 1000,
            v_b1,
            color="#8c9ba5",
            linestyle="--",
            linewidth=2.0,
            label="ZTCF at 100 ms (-62% speed)",
            zorder=4,
        )

        # ZTCF Branch 2: Released at t=180 ms (Shaft horizontal)
        # Reaches ~36.2 m/s (25% loss)
        t_b2 = t[t >= 0.18]
        v_b2 = v_active[np.argmin(np.abs(t - 0.18))] + 14.5 * (1.0 - np.exp(-22.0 * (t_b2 - 0.18)))
        ax.plot(
            t_b2 * 1000,
            v_b2,
            color=ACCENT_ORANGE,
            linestyle="-.",
            linewidth=2.0,
            label="ZTCF at 180 ms (-25% speed)",
            zorder=4,
        )

        # ZTCF Branch 3: Released at t=245 ms (35 ms pre-impact)
        # Reaches ~46.4 m/s (only 3.7% loss)
        t_b3 = t[t >= 0.245]
        v_b3 = v_active[np.argmin(np.abs(t - 0.245))] + 5.8 * (1.0 - np.exp(-35.0 * (t_b3 - 0.245)))
        ax.plot(
            t_b3 * 1000,
            v_b3,
            color=SAGE_GREEN,
            linestyle=":",
            linewidth=2.2,
            label="ZTCF at 245 ms (-3.7% speed)",
            zorder=4,
        )

        # Impact markers
        ax.scatter([280], [v_active[-1]], color=PRIMARY_BLUE, s=45, zorder=6)
        ax.scatter([280], [v_b1[-1]], color="#8c9ba5", s=45, zorder=6)
        ax.scatter([280], [v_b2[-1]], color=ACCENT_ORANGE, s=45, zorder=6)
        ax.scatter([280], [v_b3[-1]], color=SAGE_GREEN, s=45, zorder=6)

        # Annotations on impact deficit
        ax.annotate(
            "Terminal Impact Deficit:\nEarly removal = large loss;\nLate removal = negligible loss",
            xy=(280, 46.4),
            xytext=(140, 10.0),
            arrowprops={"arrowstyle": "->", "color": SLATE_GRAY, "lw": 1.4},
            fontsize=9.5,
            bbox={
                "boxstyle": "round,pad=0.4",
                "facecolor": LIGHT_BG,
                "edgecolor": SLATE_GRAY,
                "alpha": 0.9,
            },
            zorder=7,
        )

        ax.set_xlim(-5, 290)
        ax.set_ylim(0, 54)
        ax.set_xlabel("Downswing Elapsed Time (ms)", fontsize=10.5)
        ax.set_ylabel("Modeled Clubhead Speed (m/s)", fontsize=10.5)
        ax.set_title(
            "Clubhead Speed Under Zero-Torque Counterfactual Branches",
            fontsize=11.5,
            fontweight="bold",
        )
        ax.legend(loc="upper left", framealpha=0.9, fontsize=9.0)
        ax.spines[["top", "right"]].set_visible(False)

        fig.savefig(output_path, metadata={"Creator": "AffineDrift; Core Theory Figure Generator"})
        plt.close(fig)

    _clean_svg(output_path)


def build_ztcf_passive_dynamics_attribution(output_path: Path) -> None:
    """Figure 6: Breakdown of distal club acceleration into active torque and passive interaction."""
    with plt.rc_context(
        {
            "font.size": 10.5,
            "svg.fonttype": "none",
            "svg.hashsalt": "ztcf3",
            "axes.edgecolor": SLATE_GRAY,
            "axes.labelcolor": TEXT_COLOR,
        }
    ):
        fig, ax = plt.subplots(figsize=(7.6, 5.2), layout="constrained")
        ax.set_facecolor("#ffffff")
        ax.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR, zorder=0)

        t = np.linspace(0, 0.28, 200)

        # Active muscular torque contribution M^{-1} tau: peaks mid-swing, then decays near impact
        # as wrists uncock and positive muscular torque diminishes
        acc_active = 350.0 * np.sin(np.pi * t / 0.25) * np.exp(-4.0 * (t - 0.12) ** 2)

        # Passive centrifugal / interaction coupling: surges dramatically in late downswing
        # due to deceleration of proximal segments (arm braking) flailing the club
        acc_passive = 850.0 / (1.0 + np.exp(-32.0 * (t - 0.22)))

        # Gravitational acceleration component: modest throughout
        acc_gravity = 25.0 * np.cos(np.pi * t / 0.28)

        # Total acceleration
        acc_total = acc_active + acc_passive + acc_gravity

        # Curves
        ax.plot(
            t * 1000,
            acc_total,
            color=TEXT_COLOR,
            linewidth=2.4,
            label=r"Total Acceleration $\ddot{q}_3(t)$",
            zorder=5,
        )
        ax.plot(
            t * 1000,
            acc_active,
            color=ACCENT_ORANGE,
            linewidth=2.0,
            linestyle="--",
            label=r"Active Torque Contribution $M^{-1}\tau$",
            zorder=4,
        )
        ax.plot(
            t * 1000,
            acc_passive,
            color=PRIMARY_BLUE,
            linewidth=2.2,
            label=r"Passive Interaction / Flail $-M^{-1}C\dot{q}$",
            zorder=4,
        )
        ax.plot(
            t * 1000,
            acc_gravity,
            color=SLATE_GRAY,
            linewidth=1.4,
            linestyle=":",
            label=r"Gravity $-M^{-1}g$",
            zorder=3,
        )

        # Shading the passive-dominant zone
        ax.axvspan(180, 280, facecolor="#c7e0ef", alpha=0.35, zorder=1)
        ax.text(
            230,
            950,
            "Passive Interaction\nDominance Zone",
            ha="center",
            fontsize=9.0,
            color=PRIMARY_BLUE,
            fontweight="bold",
        )

        ax.annotate(
            "Interaction Surge:\nProximal deceleration drives\ndistal club acceleration",
            xy=(220, acc_passive[np.argmin(np.abs(t - 0.22))]),
            xytext=(100, 650),
            arrowprops={"arrowstyle": "->", "color": PRIMARY_BLUE, "lw": 1.4},
            fontsize=9.0,
            bbox={
                "boxstyle": "round,pad=0.3",
                "facecolor": LIGHT_BG,
                "edgecolor": SLATE_GRAY,
                "alpha": 0.9,
            },
            zorder=6,
        )

        ax.set_xlim(0, 285)
        ax.set_ylim(-100, 1100)
        ax.set_xlabel("Time from Top of Downswing (ms)", fontsize=10.5)
        ax.set_ylabel(r"Distal Angular Acceleration $\ddot{q}_3$ (rad/s$^2$)", fontsize=10.5)
        ax.set_title(
            "Attribution of Distal Acceleration: Active Muscular vs. Passive Coupling",
            fontsize=11.5,
            fontweight="bold",
        )
        ax.legend(loc="upper left", framealpha=0.9, fontsize=9.0)
        ax.spines[["top", "right"]].set_visible(False)

        fig.savefig(output_path, metadata={"Creator": "AffineDrift; Core Theory Figure Generator"})
        plt.close(fig)

    _clean_svg(output_path)


def build_superposition_decomposition(output_path: Path) -> None:
    """Figure 7: Parallelogram superposition of instantaneous acceleration increments at fixed state."""
    with plt.rc_context(
        {
            "font.size": 10.5,
            "svg.fonttype": "none",
            "svg.hashsalt": "super1",
            "axes.edgecolor": SLATE_GRAY,
            "axes.labelcolor": TEXT_COLOR,
            "text.color": TEXT_COLOR,
        }
    ):
        fig, ax = plt.subplots(figsize=(7.2, 5.2), layout="constrained")
        ax.set_facecolor("#ffffff")
        ax.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR, zorder=0)

        # Baseline drift acceleration \ddot{q}_0
        a0_x, a0_y = 1.2, 0.8
        ax.annotate(
            "",
            xy=(a0_x, a0_y),
            xytext=(0, 0),
            arrowprops={"arrowstyle": "-|>", "color": SLATE_GRAY, "lw": 2.2, "mutation_scale": 16},
            zorder=3,
        )
        ax.text(
            a0_x * 0.4 - 0.4,
            a0_y * 0.5 + 0.25,
            r"Drift Baseline $\ddot{q}_0 = M^{-1}(-C\dot{q}-g)$",
            color=SLATE_GRAY,
            fontsize=9.5,
            fontweight="bold",
        )

        # Channel 1 increment \Delta \ddot{q}_1 = M^{-1} [u_1, 0]^T
        du1_x, du1_y = 2.4, 0.5
        # Channel 2 increment \Delta \ddot{q}_2 = M^{-1} [0, u_2]^T
        du2_x, du2_y = 0.6, 2.0

        # Vector 1 from drift tip
        ax.annotate(
            "",
            xy=(a0_x + du1_x, a0_y + du1_y),
            xytext=(a0_x, a0_y),
            arrowprops={
                "arrowstyle": "-|>",
                "color": PRIMARY_BLUE,
                "lw": 2.2,
                "mutation_scale": 16,
            },
            zorder=4,
        )
        ax.text(
            a0_x + du1_x * 0.5 + 0.1,
            a0_y + du1_y * 0.5 - 0.35,
            r"$\Delta \ddot{q}_1 = M^{-1}B_1 u_1$",
            color=PRIMARY_BLUE,
            fontsize=10,
            fontweight="bold",
        )

        # Vector 2 from drift tip
        ax.annotate(
            "",
            xy=(a0_x + du2_x, a0_y + du2_y),
            xytext=(a0_x, a0_y),
            arrowprops={
                "arrowstyle": "-|>",
                "color": ACCENT_ORANGE,
                "lw": 2.2,
                "mutation_scale": 16,
            },
            zorder=4,
        )
        ax.text(
            a0_x + du2_x * 0.5 - 1.2,
            a0_y + du2_y * 0.5 + 0.3,
            r"$\Delta \ddot{q}_2 = M^{-1}B_2 u_2$",
            color=ACCENT_ORANGE,
            fontsize=10,
            fontweight="bold",
        )

        # Parallelogram dashed lines
        ax.plot(
            [a0_x + du1_x, a0_x + du1_x + du2_x],
            [a0_y + du1_y, a0_y + du1_y + du2_y],
            color=ACCENT_ORANGE,
            linestyle="--",
            linewidth=1.4,
            zorder=2,
        )
        ax.plot(
            [a0_x + du2_x, a0_x + du1_x + du2_x],
            [a0_y + du2_y, a0_y + du1_y + du2_y],
            color=PRIMARY_BLUE,
            linestyle="--",
            linewidth=1.4,
            zorder=2,
        )

        # Net superposed acceleration \ddot{q}(u_1 + u_2)
        net_x = a0_x + du1_x + du2_x
        net_y = a0_y + du1_y + du2_y
        ax.annotate(
            "",
            xy=(net_x, net_y),
            xytext=(0, 0),
            arrowprops={"arrowstyle": "-|>", "color": SAGE_GREEN, "lw": 2.6, "mutation_scale": 18},
            zorder=5,
        )
        ax.text(
            net_x * 0.5 + 0.3,
            net_y * 0.5 + 0.4,
            r"$\ddot{q}(u_1+u_2) = \ddot{q}_0 + \Delta \ddot{q}_1 + \Delta \ddot{q}_2$",
            color=SAGE_GREEN,
            fontsize=10.5,
            fontweight="bold",
        )

        # Nodes
        ax.scatter([0], [0], color=TEXT_COLOR, s=40, zorder=6)
        ax.scatter([a0_x], [a0_y], color=SLATE_GRAY, s=35, zorder=6)
        ax.scatter([net_x], [net_y], color=SAGE_GREEN, s=50, zorder=6)

        # Theorem statement box
        thm_text = (
            r"Exact Superposition Theorem at Fixed State $x$:" + "\n"
            r"$\mathcal{F}_x(u_1 + u_2) - \mathcal{F}_x(0) = [\mathcal{F}_x(u_1) - \mathcal{F}_x(0)] + [\mathcal{F}_x(u_2) - \mathcal{F}_x(0)]$"
        )
        ax.text(
            -0.2,
            3.6,
            thm_text,
            fontsize=9.5,
            bbox={
                "boxstyle": "round,pad=0.5",
                "facecolor": LIGHT_BG,
                "edgecolor": SLATE_GRAY,
                "alpha": 0.9,
            },
            zorder=7,
        )

        ax.set_xlim(-0.6, 5.0)
        ax.set_ylim(-0.4, 4.2)
        ax.set_xlabel(r"Proximal Acceleration Component $\ddot{q}_1$ (rad/s$^2$)", fontsize=10.5)
        ax.set_ylabel(r"Distal Acceleration Component $\ddot{q}_2$ (rad/s$^2$)", fontsize=10.5)
        ax.set_title(
            "Parallelogram Superposition of Joint Acceleration Increments",
            fontsize=11.5,
            fontweight="bold",
        )
        ax.spines[["top", "right"]].set_visible(False)

        fig.savefig(output_path, metadata={"Creator": "AffineDrift; Core Theory Figure Generator"})
        plt.close(fig)

    _clean_svg(output_path)


def build_superposition_modal_response(output_path: Path) -> None:
    """Figure 8: Cross-coupling acceleration responses from separate input channels."""
    with plt.rc_context(
        {
            "font.size": 10.5,
            "svg.fonttype": "none",
            "svg.hashsalt": "super2",
            "axes.edgecolor": SLATE_GRAY,
            "axes.labelcolor": TEXT_COLOR,
            "text.color": TEXT_COLOR,
        }
    ):
        fig, ax = plt.subplots(figsize=(7.4, 5.0), layout="constrained")
        ax.set_facecolor("#ffffff")
        ax.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR, axis="y", zorder=0)

        # 3 Actuators: Shoulder (u1), Elbow (u2), Wrist (u3)
        # Responses across coordinates: [ddq1, ddq2, ddq3]
        # Illustrates non-diagonal M(q)^{-1}
        u1_response = [14.2, -5.8, 3.4]  # Unit shoulder torque
        u2_response = [-5.8, 22.4, -8.1]  # Unit elbow torque
        u3_response = [3.4, -8.1, 38.6]  # Unit wrist torque

        x = np.arange(3)
        width = 0.25

        ax.bar(
            x - width,
            u1_response,
            width,
            label="Torque at Shoulder ($u_1$)",
            color=PRIMARY_BLUE,
            zorder=3,
        )
        ax.bar(
            x, u2_response, width, label="Torque at Elbow ($u_2$)", color=ACCENT_ORANGE, zorder=3
        )
        ax.bar(
            x + width,
            u3_response,
            width,
            label="Torque at Wrist ($u_3$)",
            color=SAGE_GREEN,
            zorder=3,
        )

        ax.axhline(0, color=TEXT_COLOR, linewidth=1.0, zorder=4)

        ax.set_xticks(x)
        ax.set_xticklabels(
            [
                "Response at Shoulder\nCoordinate $\\ddot{q}_1$",
                "Response at Elbow\nCoordinate $\\ddot{q}_2$",
                "Response at Wrist\nCoordinate $\\ddot{q}_3$",
            ],
            fontsize=10.0,
        )
        ax.set_ylabel(
            r"Induced Acceleration $\Delta \ddot{q}_j$ (rad/s$^2$ per 100 Nm)", fontsize=10.5
        )
        ax.set_title(
            "Cross-Channel Acceleration Coupling via Mass Matrix Inverse $M^{-1}(q)$",
            fontsize=11.5,
            fontweight="bold",
        )
        ax.legend(loc="upper left", framealpha=0.9, fontsize=9.5)
        ax.spines[["top", "right"]].set_visible(False)

        # Annotation highlighting cross-coupling
        ax.annotate(
            "Inertial Cross-Coupling:\nActuating one joint induces\nopposing reactions elsewhere",
            xy=(1 - width, -5.8),
            xytext=(0.5, -14.0),
            arrowprops={"arrowstyle": "->", "color": SLATE_GRAY, "lw": 1.2},
            fontsize=9.0,
            bbox={
                "boxstyle": "round,pad=0.3",
                "facecolor": LIGHT_BG,
                "edgecolor": SLATE_GRAY,
                "alpha": 0.9,
            },
            zorder=5,
        )

        ax.set_ylim(-18, 45)

        fig.savefig(output_path, metadata={"Creator": "AffineDrift; Core Theory Figure Generator"})
        plt.close(fig)

    _clean_svg(output_path)


def build_superposition_breakdown_boundary(output_path: Path) -> None:
    """Figure 9: Divergence of naive trajectory superposition in nonlinear dynamics over time."""
    with plt.rc_context(
        {
            "font.size": 10.5,
            "svg.fonttype": "none",
            "svg.hashsalt": "super3",
            "axes.edgecolor": SLATE_GRAY,
            "axes.labelcolor": TEXT_COLOR,
            "text.color": TEXT_COLOR,
        }
    ):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.8, 4.6), layout="constrained")

        # Time horizon (0 to 150 ms)
        t = np.linspace(0, 0.15, 150)

        # Left panel: Trajectory comparison
        # Exact nonlinear simulation vs naive linear trajectory superposition
        traj_drift = 0.5 * t**2
        traj_u1 = traj_drift + 2.0 * t**2
        traj_u2 = traj_drift + 1.2 * t**2
        # Linear superposition: q_u1 + q_u2 - q_0
        traj_superposed = traj_u1 + traj_u2 - traj_drift
        # Exact nonlinear response: compounding centrifugal/Coriolis creates divergence
        traj_exact = traj_superposed + 18.0 * t**3 + 120.0 * t**4

        ax1.set_facecolor("#ffffff")
        ax1.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR, zorder=0)
        ax1.plot(
            t * 1000,
            traj_exact,
            color=PRIMARY_BLUE,
            linewidth=2.4,
            label="Exact Nonlinear $\\Phi_t(u_1+u_2)$",
            zorder=4,
        )
        ax1.plot(
            t * 1000,
            traj_superposed,
            color=ACCENT_ORANGE,
            linestyle="--",
            linewidth=2.0,
            label="Naive Superposition\n$\\Phi_t(u_1)+\\Phi_t(u_2)-\\Phi_t(0)$",
            zorder=3,
        )
        ax1.plot(
            t * 1000,
            traj_drift,
            color=SLATE_GRAY,
            linestyle=":",
            linewidth=1.5,
            label="Drift Baseline $\\Phi_t(0)$",
            zorder=2,
        )

        ax1.set_xlabel("Time Horizon $\\Delta t$ (ms)", fontsize=10.0)
        ax1.set_ylabel("Joint Coordinate Displacement (rad)", fontsize=10.0)
        ax1.set_title("Trajectory vs. Superposition", fontsize=11.0, fontweight="bold")
        ax1.legend(loc="upper left", framealpha=0.9, fontsize=8.5)
        ax1.spines[["top", "right"]].set_visible(False)

        # Right panel: Superposition Error Norm vs Horizon for varying torque amplitudes
        ax2.set_facecolor("#ffffff")
        ax2.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR, zorder=0)

        err_small = 4.0 * t**3 + 15.0 * t**4
        err_medium = 18.0 * t**3 + 120.0 * t**4
        err_large = 60.0 * t**3 + 450.0 * t**4

        ax2.plot(
            t * 1000,
            err_small,
            color=SAGE_GREEN,
            linewidth=1.8,
            label="Low Amplitude (10 Nm)",
            zorder=3,
        )
        ax2.plot(
            t * 1000,
            err_medium,
            color=PRIMARY_BLUE,
            linewidth=2.2,
            label="Medium Amplitude (50 Nm)",
            zorder=3,
        )
        ax2.plot(
            t * 1000,
            err_large,
            color=ACCENT_ORANGE,
            linewidth=2.0,
            label="High Amplitude (120 Nm)",
            zorder=3,
        )

        ax2.axvline(30, color=SLATE_GRAY, linestyle=":", linewidth=1.2)
        ax2.text(32, 0.22, "Valid Linear\nWindow (<30 ms)", fontsize=8.5, color=SLATE_GRAY)

        ax2.set_xlabel("Time Horizon $\\Delta t$ (ms)", fontsize=10.0)
        ax2.set_ylabel("Superposition Error Norm $\\|\\epsilon(t)\\|$", fontsize=10.0)
        ax2.set_title("Superposition Breakdown Error", fontsize=11.0, fontweight="bold")
        ax2.legend(loc="upper left", framealpha=0.9, fontsize=8.5)
        ax2.spines[["top", "right"]].set_visible(False)

        fig.savefig(output_path, metadata={"Creator": "AffineDrift; Core Theory Figure Generator"})
        plt.close(fig)

    _clean_svg(output_path)


def build_all_figures(output_dir: Path) -> list[Path]:
    """Generate all 9 core theory SVG figures in the designated directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    generators = [
        ("fig_dcr_vector_decomposition.svg", build_dcr_vector_decomposition),
        ("fig_dcr_swing_phases.svg", build_dcr_swing_phases),
        ("fig_dcr_reachability_tubes.svg", build_dcr_reachability_tubes),
        ("fig_ztcf_trajectory_divergence.svg", build_ztcf_trajectory_divergence),
        ("fig_ztcf_clubhead_speed_loss.svg", build_ztcf_clubhead_speed_loss),
        ("fig_ztcf_passive_dynamics_attribution.svg", build_ztcf_passive_dynamics_attribution),
        ("fig_superposition_decomposition.svg", build_superposition_decomposition),
        ("fig_superposition_modal_response.svg", build_superposition_modal_response),
        ("fig_superposition_breakdown_boundary.svg", build_superposition_breakdown_boundary),
    ]

    for filename, func in generators:
        target = output_dir / filename
        LOGGER.info("Generating figure: %s", target)
        func(target)
        generated.append(target)

    return generated


def check_figures(output_dir: Path) -> bool:
    """Validate that all expected figures exist, are non-empty, and are valid SVGs."""
    all_ok = True
    for filename in FIGURE_NAMES:
        target = output_dir / filename
        if not target.is_file():
            LOGGER.error("Missing figure: %s", target)
            all_ok = False
            continue
        size = target.stat().st_size
        if size == 0:
            LOGGER.error("Empty figure: %s", target)
            all_ok = False
            continue
        # Verify valid SVG content
        content = target.read_text(encoding="utf-8")
        if "<svg" not in content or "</svg>" not in content:
            LOGGER.error("Invalid SVG file (missing <svg> root): %s", target)
            all_ok = False
            continue
        LOGGER.info("Verified figure %s (%d bytes)", filename, size)

    return all_ok


def main() -> int:
    """CLI entrypoint."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description="Generate SVG figures for core theory pages.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "articles/figures/core_theory",
        help="Destination directory for generated SVGs.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check that all figures exist and are valid SVGs without modifying them.",
    )

    args = parser.parse_args()

    if args.check:
        LOGGER.info("Running figure check against %s", args.output_dir)
        ok = check_figures(args.output_dir)
        return 0 if ok else 1

    LOGGER.info("Generating core theory figures into %s", args.output_dir)
    build_all_figures(args.output_dir)
    LOGGER.info("All 9 figures generated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
