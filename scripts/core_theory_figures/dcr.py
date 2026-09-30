"""Controllability-Drift Ratio (DCR) figure generators."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

from scripts.core_theory_figures.common import (
    ACCENT_ORANGE,
    GRID_COLOR,
    LIGHT_BG,
    PRIMARY_BLUE,
    SAGE_GREEN,
    SLATE_GRAY,
    TEXT_COLOR,
    _clean_svg,
)


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
