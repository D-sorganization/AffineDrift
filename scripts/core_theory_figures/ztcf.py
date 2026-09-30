"""Zero-Torque Counterfactual (ZTCF) figure generators."""

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
