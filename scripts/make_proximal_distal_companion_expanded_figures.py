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
    ROOT,
    VIOLET,
    _save,
    _style,
)
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

WRIST_NODE_X = 98 / 10


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


def _boundary_draw_header(ax: plt.Axes) -> None:
    """Draw title and interaction header on axes."""
    ax.text(
        5.25,
        5.8,
        "Choose the Boundary Before Naming the Transfer",
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold",
        color=INK,
    )
    ax.text(
        0.5,
        4.75,
        "Interaction /\nConversion",
        ha="left",
        va="center",
        fontsize=11.5,
        fontweight="bold",
        color=INK,
    )
    ax.plot([0.5, 2.7], [4.3, 4.3], color=GRAY, linewidth=1.5)


def _boundary_draw_cards(ax: plt.Axes, cards_x: list[float], card_w: float) -> None:
    """Draw colored inventory card boxes, headers, and row dividers."""
    headers = ["Club", "Golfer + Club", "Golfer + Club\n+ Earth"]
    colors = [ORANGE, BLUE, GREEN]
    for head, col, cx in zip(headers, colors, cards_x, strict=True):
        card = FancyBboxPatch(
            (cx, 1.35),
            card_w,
            3.85,
            boxstyle="round,pad=0.0,rounding_size=0.15",
            facecolor="white",
            edgecolor=col,
            linewidth=2.0,
        )
        ax.add_patch(card)
        ax.text(
            cx + card_w / 2,
            4.75,
            head,
            ha="center",
            va="center",
            fontsize=11.5,
            fontweight="bold",
            color=col,
        )
        ax.plot([cx + 0.15, cx + card_w - 0.15], [4.3, 4.3], color=col, linewidth=1.5)
        for y_div in [3.585, 2.855, 2.125]:
            ax.plot(
                [cx + 0.15, cx + card_w - 0.15],
                [y_div, y_div],
                color=GRAY,
                linewidth=0.8,
                linestyle=":",
                alpha=0.6,
            )


def _boundary_draw_rows(ax: plt.Axes, cards_x: list[float], card_w: float) -> None:
    """Draw row labels and classification values across inventory cards."""
    rows = [
        ("Hand Contact", ["External", "Internal", "Internal"]),
        ("Foot-Ground", ["Outside Inventory", "External", "Internal"]),
        ("Gravity from Earth", ["External Force", "External Force", "Internal Interaction"]),
        ("Muscle Conversion", ["Outside Inventory", "Internal", "Internal"]),
    ]
    row_y = [3.95, 3.22, 2.49, 1.76]

    for y, (label, vals) in zip(row_y, rows, strict=True):
        ax.text(0.5, y, label, ha="left", va="center", fontsize=11, fontweight="bold", color=INK)
        for cx, val in zip(cards_x, vals, strict=True):
            ax.text(
                cx + card_w / 2,
                y,
                val,
                ha="center",
                va="center",
                fontsize=10.5,
                color=INK,
            )


def _boundary_draw_notes(ax: plt.Axes) -> None:
    """Draw clarifying notes at bottom of diagram."""
    ax.text(
        0.5,
        0.85,
        "Effective Gravitational Potential Can Represent an External Field",
        ha="left",
        va="center",
        fontsize=10,
        color=INK,
    )
    ax.text(
        0.5,
        0.45,
        "Interaction Classification Does Not Determine Work",
        ha="left",
        va="center",
        fontsize=10,
        color=INK,
    )


def make_system_boundaries() -> None:
    """Create colored inventory cards comparing three explicit body inventories."""
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    _clean(ax, (0, 10.5), (0, 6.2))

    _boundary_draw_header(ax)

    cards_x = [2.9, 5.4, 7.9]
    card_w = 2.3

    _boundary_draw_cards(ax, cards_x, card_w)
    _boundary_draw_rows(ax, cards_x, card_w)
    _boundary_draw_notes(ax)

    _save(fig, "fig_companion_system_boundaries")


def make_moment_arm() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8))
    for axis, angle, title in zip(
        axes, (np.pi / 6, np.pi / 2), ("Shorter Moment Arm", "Perpendicular Force"), strict=True
    ):
        _clean(axis, (-0.6, 5), (-2.2, 2.5))
        axis.set_aspect("equal")
        axis.plot([0, 4.2], [0, 0], lw=9, color=ORANGE, solid_capstyle="round")
        axis.scatter(0, 0, s=100, color=INK)
        contact = np.array([3.2, 0.0])
        direction = np.array([np.cos(angle), np.sin(angle)])
        foot = contact - (contact @ direction) * direction
        force_line = np.stack([contact - 4 * direction, contact + 1.8 * direction])
        axis.plot(*force_line.T, ls="--", color=GRAY, gid="force-line-of-action")
        axis.plot([0, foot[0]], [0, foot[1]], color=GREEN, lw=3, gid="perpendicular-moment-arm")
        _edge(axis, tuple(contact), tuple(contact + 1.5 * direction), BLUE)
        axis.text(-0.25, 0.25, "O", color=INK, fontweight="bold")
        axis.text(3.45, -0.38, "H", color=INK, ha="center")
        label = contact + 1.65 * direction + 0.14 * np.array([-direction[1], direction[0]])
        axis.text(*label, "F", color=BLUE, fontweight="bold")
        axis.text(foot[0] / 2, foot[1] / 2 - 0.4, "h", color=GREEN, fontweight="bold")
        axis.set_title(title, color=INK, fontweight="bold")
    fig.suptitle(
        "Moment About O: Force Magnitude × Perpendicular Distance h",
        color=INK,
        fontweight="bold",
        fontsize=14,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    _save(fig, "fig_companion_moment_arm_geometry")


def make_constraint_reaction() -> None:
    """Save a circular-guide schematic separating force from release velocity."""
    fig, axis = plt.subplots(figsize=(8, 5.5))
    _clean(axis, (-3.5, 4.5), (-3, 3.5))
    axis.set_aspect("equal")
    radius = 2.1  # Schematic plotting units, not measured golf geometry.
    axis.add_patch(Circle((0, 0), radius, fill=False, ls="--", color=GRAY, lw=2))
    point = radius * np.array([1.0, 1.0]) / np.sqrt(2)
    tangent = np.array([1.0, -1.0]) / np.sqrt(2)
    axis.scatter(*point, s=180, color=ORANGE)
    _edge(axis, tuple(point), tuple(0.1 * point), BLUE)
    _edge(axis, tuple(point), tuple(point + 2.0 * tangent), GREEN)
    release = np.vstack([point + 2.05 * tangent, point + 3.5 * tangent])
    axis.plot(release[:, 0], release[:, 1], ls=":", color=RED, lw=3)
    axis.text(-1.1, 2.4, "Constraint Reaction", color=BLUE, fontweight="bold", ha="center")
    axis.text(3.1, 1.6, "Instantaneous\nVelocity", color=GREEN, fontweight="bold", ha="center")
    axis.text(2.8, -1.35, "Release Tangent", color=RED, ha="center")
    axis.set_title(
        "Connection Force and Release Velocity",
        color=INK,
        fontweight="bold",
        fontsize=15,
    )
    _save(fig, "fig_companion_constraint_reaction")


def make_sequence_overlap() -> None:
    time = np.linspace(0, 1, 400)
    fig, axis = plt.subplots(figsize=(10, 5))
    for center, width, color, style, label in (
        (0.36, 0.16, GRAY, "-", "Pelvis"),
        (0.48, 0.15, BLUE, "--", "Trunk"),
        (0.61, 0.13, GREEN, "-.", "Hand"),
        (0.78, 0.11, ORANGE, ":", "Club"),
    ):
        # Chosen curves illustrate order only, with no measured amplitude ratios.
        curve = np.exp(-0.5 * ((time - center) / width) ** 2)
        axis.plot(time, curve, lw=3, color=color, linestyle=style, label=label)
    axis.set(
        xlabel="Normalized Schematic Time",
        ylabel="Angular Speed / Own Peak (Normalized)",
        title="Schematic Peak Ordering: Chosen Curves, Not Measurements",
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
    """Plot the pinned finite-preparation experiment, including transmitted torque."""
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    programs = (
        ("persistent_arm_drive", (10, -4), "Persistent Command Directions"),
        ("wrist_to_arm_role_reversal", (-4, 10), "Complete Role Reversal"),
    )
    with np.load(ROOT / "data/illustrations/preload_transmission_study.npz") as data:
        for axis, (program, preparation, title) in zip(axes, programs, strict=True):
            prefix = "continuous_" + program
            time = data[prefix + "_time_s"]
            for name, color, before, after in zip(
                ("arm", "wrist"), (BLUE, ORANGE), preparation, (16, -6), strict=True
            ):
                transmitted = data[prefix + "_transmitted_" + name + "_torque_nm"]
                desired = np.where(time < 0, before, after)
                axis.plot(
                    time * 1000,
                    transmitted,
                    color=color,
                    lw=2.5,
                    label=name.title() + " Transmitted",
                )
                axis.step(
                    time * 1000,
                    desired,
                    where="post",
                    color=color,
                    ls="--",
                    lw=1.2,
                    label=name.title() + " Command",
                )
            axis.axvline(0, color=INK, ls=":")
            axis.axhline(0, color=GRAY, lw=0.8)
            axis.set(ylabel="Torque (N m)", title=title)
    axes[0].legend(frameon=False, ncol=2, loc="upper left")
    axes[1].set_xlabel("Time Relative to Transition (ms)")
    fig.suptitle("Synthetic Transmission: Commands and Continuous State", color=INK)
    fig.tight_layout()
    _save(fig, "fig_companion_preload_role_reversal")


def make_ground_ledger() -> None:
    fig, axis = plt.subplots(figsize=(10, 5.3))
    _clean(axis, (-1, 11.5), (-1, 5.5))
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
        "Modeled Net Reaction Does Not Uniquely Specify Foot Allocation",
        color=INK,
        fontweight="bold",
        fontsize=15,
    )
    _save(fig, "fig_companion_ground_reaction_ledger")


def make_moving_base() -> None:
    fig, axes = plt.subplots(2, 1, figsize=(5.5, 7), layout="constrained")
    panels = (
        (axes[0], "Prescribed Path", "Trajectory is specified\nReport reaction and power"),
        (
            axes[1],
            "Finite-Mass Base",
            "Force and inertia set motion\nClub load can change the path",
        ),
    )
    for axis, title, description in panels:
        _clean(axis, (-3.0, 3.0), (-2.2, 2.7))
        axis.add_patch(Rectangle((-0.8, 1.4), 1.6, 0.45, color=BLUE, alpha=0.6))
        axis.plot([0, 1.4, 2.3], [1.4, 0.5, -0.7], lw=5, color=ORANGE)
        _edge(axis, (1.2, 0.15), (0, 1.4), RED)
        _edge(axis, (-1.2, 2.15), (1.2, 2.15), INK)
        _edge(axis, (1.2, 2.15), (-1.2, 2.15), INK)
        axis.text(-2.7, 0.1, "Club\nload", color=RED, fontsize=14, fontweight="bold")
        axis.text(-2.7, -1.3, description, color=INK, fontsize=14)
        axis.set_title(title, color=INK, fontsize=17, fontweight="bold")
    _save(fig, "fig_companion_prescribed_vs_moving_base")


def make_solver_loop() -> None:
    fig, axis = plt.subplots(figsize=(10, 5.2))
    _clean(axis, (-0.5, 11.5), (-1, 5.5))
    nodes = (
        (1.0, 3.9, "Complete State\n+ Inputs", BLUE),
        (4.0, 3.9, "Fixed-Mode KKT\n+ Reactions", VIOLET),
        (7.0, 3.9, "Acceleration\n+ Integration", ORANGE),
        (10.0, 3.9, "Candidate\nNext State", GREEN),
        (5.5, 1.2, "Closure + Work + Projection Checks", RED),
    )
    for x, y, text, color in nodes:
        _node(axis, x, y, text, color, 2.2 if y > 2 else 6.8)
    for left, right in ((1.0, 4.0), (4.0, 7.0), (7.0, 10.0)):
        _edge(axis, (left + 1.1, 3.9), (right - 1.1, 3.9))
    _edge(axis, (10.0, 3.5), (8.9, 1.55), GRAY)
    _edge(axis, (2.1, 1.2), (1.0, 3.5), RED)
    axis.text(
        5.5,
        -0.4,
        "Schematic: Fixed Bilateral Mode; Refinement Compares Separate Runs",
        ha="center",
        color=GRAY,
        fontsize=10,
    )
    axis.set_title(
        "A Forward Model Advances State\nand Audits Its Approximation",
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
    """Keep conceptual observation nodes fully visible inside both panels."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6))
    for axis in axes:
        _clean(axis, (-1, 6), (-1, 5))
    for y, label, color in (
        (3.8, "Torque", BLUE),
        (2.5, "Stiffness", ORANGE),
        (1.2, "Delay", VIOLET),
    ):
        _node(axes[0], 1.0, y, label, color, 1.7)
        _edge(axes[0], (1.9, y), (3.42, 2.5), color)
    _node(axes[0], 4.4, 2.5, "Outcome", GREEN, 1.8)
    axes[0].set_title("Sensitivity: What Moves the Outcome?", color=INK, fontweight="bold")
    for y, label, color in (
        (3.8, "Recipe A", BLUE),
        (2.5, "Recipe B", ORANGE),
        (1.2, "Recipe C", VIOLET),
    ):
        _node(axes[1], 1.0, y, label, color, 1.7)
        _edge(axes[1], (1.9, y), (3.42, 2.5), color)
    _node(axes[1], 4.4, 2.5, "Same\nObservation", GREEN, 1.8)
    axes[1].set_title("Identifiability: Can We Recover the Recipe?", color=INK, fontweight="bold")
    fig.tight_layout()
    _save(fig, "fig_companion_sensitivity_identifiability")


def make_human_evidence() -> None:
    """Separate observations and conditional inferences without a certainty ladder."""
    fig, axis = plt.subplots(figsize=(5.5, 6.5))
    _clean(axis, (0, 8), (-0.4, 6.4))
    levels = (
        ("Calibrated Observations", "Motion, external loads,\nelectrical activity", BLUE),
        ("Mechanical Inference", "Frames, inertias,\ncontact assumptions", GREEN),
        ("Anatomical Inference", "Multiple muscle allocations\ncan remain", ORANGE),
        ("Prospective Tests", "Frozen predictions;\nrelevant new data", RED),
    )
    for index, (label, detail, color) in enumerate(levels):
        y = 4.9 - index * 1.3
        axis.add_patch(Rectangle((0.3, y), 7.4, 1.15, color=color, alpha=0.16, ec=color, lw=2))
        axis.text(
            4,
            y + 0.87,
            label,
            ha="center",
            va="center",
            color=color,
            fontweight="bold",
            fontsize=17,
        )
        axis.text(4, y + 0.35, detail, ha="center", va="center", color=INK, fontsize=14)
    axis.text(
        4,
        0.35,
        "Measurements constrain explanations.\nA unique mechanism is not guaranteed.",
        ha="center",
        va="center",
        color=INK,
        fontsize=13,
    )
    axis.set_title(
        "Observations, Inferences, and Tests",
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
        (WRIST_NODE_X, "Wrist", RED),
    ):
        _node(axis, x, 4.6, text, color, 1.7)
        _edge(axis, (x, 4.2), (5.4, 2.6), color)
    _node(axis, 5.4, 2.1, "Resultant Grip Wrench", INK, 3.0)
    for x, text in (
        (2.3, "Load May Differ"),
        (5.4, "Stiffness May Differ"),
        (8.5, "Effort May Differ"),
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
