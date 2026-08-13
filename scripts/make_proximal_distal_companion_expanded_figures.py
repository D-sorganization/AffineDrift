"""Generate the expanded lay-book figure set."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from make_proximal_distal_companion_figures import (
    BLUE,
    GRAY,
    GREEN,
    INK,
    ORANGE,
    RED,
    VIOLET,
    _save,
    _style,
)
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle


def _clean(axis: plt.Axes, xlim: tuple[float, float], ylim: tuple[float, float]) -> None:
    axis.set(xlim=xlim, ylim=ylim)
    axis.axis("off")


def _node(axis: plt.Axes, x: float, y: float, text: str, color: str, width: float = 2.1) -> None:
    patch = FancyBboxPatch(
        (x - width / 2, y - 0.35),
        width,
        0.7,
        boxstyle="round,pad=0.08",
        facecolor=color,
        edgecolor=color,
        alpha=0.15,
        lw=2,
    )
    axis.add_patch(patch)
    axis.text(x, y, text, ha="center", va="center", color=color, fontweight="bold")


def _edge(
    axis: plt.Axes, start: tuple[float, float], end: tuple[float, float], color: str = INK
) -> None:
    axis.add_patch(
        FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=14, lw=2, color=color)
    )


def make_system_boundaries() -> None:
    fig, axis = plt.subplots(figsize=(9, 5.4))
    _clean(axis, (-5, 5), (-3, 3))
    for radius, color, label in (
        (1.0, ORANGE, "Club"),
        (2.0, BLUE, "Golfer + Club"),
        (2.8, GREEN, "Golfer + Club + Earth"),
    ):
        axis.add_patch(Circle((0, 0), radius, fill=False, lw=3, color=color))
        axis.text(0, radius - 0.24, label, ha="center", color=color, fontweight="bold")
    _edge(axis, (-4.4, 0.9), (-2.9, 0.9), RED)
    axis.text(-3.7, 1.25, "Gravity / Ground", ha="center", color=RED)
    _edge(axis, (-2.0, -1.7), (-1.0, -0.8), VIOLET)
    axis.text(-2.5, -2.05, "Hand Work Changes Boundary Role", color=VIOLET)
    axis.set_title(
        "Choose the Boundary Before Naming the Transfer", color=INK, fontweight="bold", fontsize=16
    )
    _save(fig, "fig_companion_system_boundaries")


def make_moment_arm() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for axis, angle, title in zip(
        axes, (0.1, 1.35), ("Short Moment Arm", "Long Moment Arm"), strict=True
    ):
        _clean(axis, (-0.5, 5), (-1, 3.8))
        axis.plot([0, 4.2], [0, 0], lw=9, color=ORANGE, solid_capstyle="round")
        axis.scatter(0, 0, s=100, color=INK)
        force_end = (3.2 + 1.5 * np.cos(angle), 1.5 * np.sin(angle))
        _edge(axis, (3.2, 0), force_end, BLUE)
        axis.plot([0, force_end[0]], [0, force_end[1]], ls="--", color=GRAY)
        axis.set_title(title, color=INK, fontweight="bold")
    fig.suptitle(
        "The Same Force Can Produce a Different Turning Effect",
        color=INK,
        fontweight="bold",
        fontsize=16,
    )
    _save(fig, "fig_companion_moment_arm_geometry")


def make_constraint_reaction() -> None:
    fig, axis = plt.subplots(figsize=(8, 5.5))
    _clean(axis, (-3.5, 4.5), (-3, 3.5))
    axis.add_patch(Circle((0, 0), 2.1, fill=False, ls="--", color=GRAY, lw=2))
    point = np.array([1.5, 1.47])
    axis.scatter(*point, s=180, color=ORANGE)
    _edge(axis, tuple(point), (0.15, 0.15), BLUE)
    _edge(axis, tuple(point), (3.0, 0.0), GREEN)
    axis.plot([point[0], 4.0], [point[1], -0.9], ls=":", color=RED, lw=3)
    axis.text(-0.6, 0.8, "Constraint Reaction", color=BLUE, fontweight="bold")
    axis.text(2.7, 0.8, "Instantaneous Velocity", color=GREEN, fontweight="bold")
    axis.text(2.8, -1.35, "Unconstrained Tangent", color=RED)
    axis.set_title(
        "A Constraint Pushes Back to Preserve the Allowed Path",
        color=INK,
        fontweight="bold",
        fontsize=15,
    )
    _save(fig, "fig_companion_constraint_reaction")


def make_sequence_overlap() -> None:
    time = np.linspace(0, 1, 400)
    fig, axis = plt.subplots(figsize=(10, 5))
    for center, width, height, color, label in (
        (0.36, 0.16, 1.0, GRAY, "Pelvis"),
        (0.48, 0.15, 1.15, BLUE, "Trunk"),
        (0.61, 0.13, 1.3, GREEN, "Arm / Hands"),
        (0.78, 0.11, 1.7, ORANGE, "Club"),
    ):
        curve = height * np.exp(-0.5 * ((time - center) / width) ** 2)
        axis.plot(time, curve, lw=3, color=color, label=label)
    axis.axvspan(0.3, 0.9, color=VIOLET, alpha=0.07, label="Overlapping Coupling")
    axis.set(
        xlabel="Normalized Downswing Time",
        ylabel="Relative Speed",
        title="Ordered Peaks Do Not Mean Sequentially Isolated Segments",
    )
    axis.legend(frameon=False, ncol=2)
    _save(fig, "fig_companion_sequence_overlap")


def make_force_power() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(11, 4))
    for axis, force, title, color in zip(
        axes,
        ((1.7, 0), (-1.7, 0), (0, 1.7)),
        ("Positive Power", "Negative Power", "Zero Power"),
        (GREEN, RED, VIOLET),
        strict=True,
    ):
        _clean(axis, (-2.2, 2.2), (-1.5, 2.2))
        _edge(axis, (-1.4, 0), (1.5, 0), INK)
        _edge(axis, (0, 0), force, color)
        axis.text(0, 1.65, title, ha="center", color=color, fontweight="bold")
        axis.text(0, -0.8, "velocity →", ha="center", color=INK)
    fig.suptitle(
        "Power Depends on the Projection of Force Along Velocity",
        color=INK,
        fontweight="bold",
        fontsize=16,
    )
    _save(fig, "fig_companion_force_power_projection")


def make_preload() -> None:
    time = np.linspace(-0.18, 0.12, 500)
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    persistent_arm = np.where(time < 0, 8, 16)
    persistent_wrist = np.where(time < 0, -2, -6)
    reversal_arm = np.where(time < 0, -4, 16)
    reversal_wrist = np.where(time < 0, 10, -6)
    for axis, arm, wrist, title in (
        (axes[0], persistent_arm, persistent_wrist, "Persistent Loaded Directions"),
        (axes[1], reversal_arm, reversal_wrist, "Complete Role Reversal"),
    ):
        axis.plot(time * 1000, arm, color=BLUE, lw=3, label="Arm channel")
        axis.plot(time * 1000, wrist, color=ORANGE, lw=3, label="Wrist channel")
        axis.axvline(0, color=INK, ls="--")
        axis.axhline(0, color=GRAY, lw=1)
        axis.set(ylabel="Desired Torque", title=title)
    axes[0].legend(frameon=False, ncol=2)
    axes[1].set_xlabel("Time Relative to Transition (ms)")
    fig.tight_layout()
    _save(fig, "fig_companion_preload_role_reversal")


def make_ground_ledger() -> None:
    fig, axis = plt.subplots(figsize=(10, 5.3))
    _clean(axis, (-1, 11), (-1, 5.5))
    for x, text, color in (
        (1.0, "Gravity +\nConfiguration", GRAY),
        (4.0, "Velocity-Dependent\nDrift", BLUE),
        (7.0, "Controls", ORANGE),
        (10.0, "External Loads", VIOLET),
    ):
        _node(axis, x, 4.1, text, color, 2.2)
        _edge(axis, (x, 3.7), (5.5, 2.2), color)
    _node(axis, 5.5, 1.7, "Net Ground-Reaction Wrench", GREEN, 3.4)
    _edge(axis, (5.5, 1.3), (3.5, 0.2), INK)
    _edge(axis, (5.5, 1.3), (7.5, 0.2), INK)
    axis.text(3.0, -0.2, "Left Foot Allocation?", color=RED, ha="center")
    axis.text(8.0, -0.2, "Right Foot Allocation?", color=RED, ha="center")
    axis.set_title(
        "Net Reaction Can Be Decomposed While Contact Allocation Remains Hidden",
        color=INK,
        fontweight="bold",
        fontsize=15,
    )
    _save(fig, "fig_companion_ground_reaction_ledger")


def make_moving_base() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for axis, title, movable in (
        (axes[0], "Prescribed Base", False),
        (axes[1], "Coupled Finite-Mass Base", True),
    ):
        _clean(axis, (-2.5, 3.5), (-2, 3.5))
        axis.add_patch(Rectangle((-0.8, 1.6), 1.6, 0.45, color=BLUE, alpha=0.6))
        axis.plot([0, 1.5, 2.5], [1.6, 0.7, -0.8], lw=6, color=ORANGE)
        _edge(axis, (1.5, 0.7), (-0.2, 1.75), RED)
        if movable:
            _edge(axis, (-0.8, 1.2), (-1.8, 1.2), GREEN)
            axis.text(-1.2, 0.7, "Base responds", ha="center", color=GREEN)
        else:
            axis.plot([-1.8, 1.8], [1.55, 1.55], color=INK, lw=3)
        axis.set_title(title, color=INK, fontweight="bold")
    fig.suptitle(
        "Back-Reaction Is Hidden When the Driver Cannot Move",
        color=INK,
        fontweight="bold",
        fontsize=16,
    )
    _save(fig, "fig_companion_prescribed_vs_moving_base")


def make_solver_loop() -> None:
    fig, axis = plt.subplots(figsize=(10, 5.2))
    _clean(axis, (-1, 11), (-1, 5.5))
    nodes = (
        (1.0, 3.9, "Present State\n+ Controls", BLUE),
        (4.0, 3.9, "KKT Dynamics\n+ Reactions", VIOLET),
        (7.0, 3.9, "Acceleration\n+ Integration", ORANGE),
        (10.0, 3.9, "Next State", GREEN),
        (5.5, 1.2, "Constraint + Energy + Timestep Audits", RED),
    )
    for x, y, text, color in nodes:
        _node(axis, x, y, text, color, 2.2 if y > 2 else 4.0)
    for left, right in ((1.0, 4.0), (4.0, 7.0), (7.0, 10.0)):
        _edge(axis, (left + 1.1, 3.9), (right - 1.1, 3.9))
    _edge(axis, (10.0, 3.5), (6.8, 1.55), GRAY)
    _edge(axis, (4.2, 1.2), (1.0, 3.5), RED)
    axis.set_title(
        "A Forward Solver Predicts, Advances, and Checks Every Step",
        color=INK,
        fontweight="bold",
        fontsize=16,
    )
    _save(fig, "fig_companion_forward_solver_loop")


def make_planar_spatial() -> None:
    fig = plt.figure(figsize=(10, 4.8))
    left = fig.add_subplot(121)
    right = fig.add_subplot(122, projection="3d")
    _clean(left, (-2.5, 2.5), (-2.5, 2.8))
    left.plot([0, 1.1, 2.0], [2.0, 0.8, -1.0], lw=7, color=ORANGE)
    left.set_title("Planar Projection", color=INK, fontweight="bold")
    right.plot([0, 1.1, 2.0], [0, 0.8, -0.4], [2.0, 0.8, -1.0], lw=7, color=ORANGE)
    right.quiver(1.1, 0.8, 0.8, 0, 1.2, 0, color=VIOLET, linewidth=2)
    right.set_title("Spatial Wrench and Changing Axes", color=INK, fontweight="bold")
    right.set_axis_off()
    fig.suptitle(
        "A Plane Reveals One Projection and Hides Others", color=INK, fontweight="bold", fontsize=16
    )
    _save(fig, "fig_companion_planar_to_spatial")


def make_sensitivity() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6))
    for axis in axes:
        _clean(axis, (-1, 6), (-1, 5))
    for y, label, color in (
        (3.8, "Torque", BLUE),
        (2.5, "Stiffness", ORANGE),
        (1.2, "Delay", VIOLET),
    ):
        _node(axes[0], 1.0, y, label, color, 1.7)
        _edge(axes[0], (1.9, y), (4.0, 2.5), color)
    _node(axes[0], 5.0, 2.5, "Outcome", GREEN, 1.7)
    axes[0].set_title("Sensitivity: What Moves the Outcome?", color=INK, fontweight="bold")
    for y, label, color in (
        (3.8, "Recipe A", BLUE),
        (2.5, "Recipe B", ORANGE),
        (1.2, "Recipe C", VIOLET),
    ):
        _node(axes[1], 1.0, y, label, color, 1.7)
        _edge(axes[1], (1.9, y), (4.0, 2.5), color)
    _node(axes[1], 5.0, 2.5, "Same Observation", GREEN, 2.0)
    axes[1].set_title("Identifiability: Can We Recover the Recipe?", color=INK, fontweight="bold")
    fig.tight_layout()
    _save(fig, "fig_companion_sensitivity_identifiability")


def make_human_evidence() -> None:
    fig, axis = plt.subplots(figsize=(8, 5.5))
    _clean(axis, (-1, 9), (-0.5, 6))
    levels = (
        (0.7, 7.6, "Observed Motion", BLUE),
        (1.4, 6.2, "External + Net Joint Kinetics", GREEN),
        (2.1, 4.8, "Bilateral Contact + Shaft State", ORANGE),
        (2.8, 3.4, "Mechanistic Biological Identification", RED),
    )
    for index, (x, width, label, color) in enumerate(levels):
        y = 0.6 + index * 1.25
        axis.add_patch(Rectangle((x, y), width, 0.85, color=color, alpha=0.22, ec=color, lw=2))
        axis.text(
            x + width / 2, y + 0.42, label, ha="center", va="center", color=color, fontweight="bold"
        )
    axis.set_title(
        "Evidence Narrows as the Claim Becomes More Specific",
        color=INK,
        fontweight="bold",
        fontsize=16,
    )
    _save(fig, "fig_companion_human_evidence_pyramid")


def make_biological_redundancy() -> None:
    fig, axis = plt.subplots(figsize=(10, 5.5))
    _clean(axis, (-1, 11), (-1, 6))
    for x, text, color in (
        (1.0, "Scapula", BLUE),
        (3.2, "Shoulder", GREEN),
        (5.4, "Elbow", ORANGE),
        (7.6, "Forearm", VIOLET),
        (9.8, "Wrist", RED),
    ):
        _node(axis, x, 4.6, text, color, 1.7)
        _edge(axis, (x, 4.2), (5.4, 2.6), color)
    _node(axis, 5.4, 2.1, "Same Net Hand Wrench", INK, 3.0)
    for x, text in (
        (2.3, "Different Load"),
        (5.4, "Different Stiffness"),
        (8.5, "Different Effort"),
    ):
        _edge(axis, (5.4, 1.7), (x, 0.5), GRAY)
        axis.text(x, 0.1, text, ha="center", color=GRAY)
    axis.set_title(
        "Club Motion Does Not Uniquely Identify the Biological Allocation",
        color=INK,
        fontweight="bold",
        fontsize=15,
    )
    _save(fig, "fig_companion_biological_redundancy")


def main() -> None:
    from make_proximal_distal_companion_review_figures import (
        make_energy_ledger,
        make_reviewer_path,
        make_synthesis,
    )

    _style()
    makers = (
        make_system_boundaries,
        make_moment_arm,
        make_constraint_reaction,
        make_sequence_overlap,
        make_force_power,
        make_preload,
        make_ground_ledger,
        make_moving_base,
        make_solver_loop,
        make_planar_spatial,
        make_sensitivity,
        make_human_evidence,
        make_biological_redundancy,
        make_reviewer_path,
        make_synthesis,
        make_energy_ledger,
    )
    for maker in makers:
        maker()


if __name__ == "__main__":
    main()
