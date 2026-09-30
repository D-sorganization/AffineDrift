"""Superposition figure generators."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
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
