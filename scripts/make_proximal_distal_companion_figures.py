"""Generate the visual vocabulary for the proximal-distal companion book."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Arc, Circle, FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "articles/figures/proximal_distal_companion"
EVIDENCE = (
    ROOT
    / "data/proximal_distal_energy_transfer"
    / "transmission_robustness_companion_snapshot.json"
)

INK = "#17324D"
BLUE = "#2C7FB8"
GREEN = "#238B45"
ORANGE = "#D95F0E"
VIOLET = "#756BB1"
RED = "#B2182B"
GRAY = "#657786"
CREAM = "#F7F3EA"


def _style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 13,
            "axes.labelsize": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "savefig.bbox": "tight",
            "svg.hashsalt": "proximal-distal-companion-v1",
        }
    )


def _save(fig: Figure, stem: str) -> tuple[Path, Path]:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    svg = OUTPUT / f"{stem}.svg"
    pdf = OUTPUT / f"{stem}.pdf"
    fig.savefig(svg, metadata={"Date": None})
    fig.savefig(pdf, metadata={"CreationDate": None, "ModDate": None})
    svg.write_text(
        "\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n",
        encoding="utf-8",
    )
    plt.close(fig)
    return svg, pdf


def _arrow(
    axis: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    color: str,
    label: str = "",
) -> None:
    axis.add_patch(
        FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=15, lw=2.2, color=color)
    )
    if label:
        x = (start[0] + end[0]) / 2
        y = (start[1] + end[1]) / 2
        axis.text(x, y + 0.12, label, ha="center", color=color, fontweight="bold")


def _box(
    axis: plt.Axes, xy: tuple[float, float], text: str, color: str, width: float = 2.0
) -> None:
    x, y = xy
    axis.add_patch(
        FancyBboxPatch(
            (x, y),
            width,
            0.8,
            boxstyle="round,pad=0.08",
            facecolor=color,
            edgecolor=color,
            alpha=0.14,
            lw=2,
        )
    )
    axis.text(
        x + width / 2, y + 0.4, text, ha="center", va="center", color=color, fontweight="bold"
    )


def make_follow_energy() -> tuple[Path, Path]:
    fig, axis = plt.subplots(figsize=(10, 4.5))
    axis.set(xlim=(0, 11), ylim=(0, 4.5))
    axis.axis("off")
    labels = (
        (0.3, "Ground", GRAY),
        (2.7, "Body", BLUE),
        (5.1, "Hands", GREEN),
        (7.5, "Club", ORANGE),
        (9.5, "Ball", RED),
    )
    for x, label, color in labels:
        _box(axis, (x, 2.2), label, color, 1.3)
    for left, right in zip(labels[:-1], labels[1:], strict=True):
        _arrow(axis, (left[0] + 1.3, 2.6), (right[0], 2.6), INK)
    axis.text(
        5.5,
        3.65,
        "Follow the Transfer, Not Just the Speed Peaks",
        ha="center",
        fontsize=16,
        fontweight="bold",
        color=INK,
    )
    axis.text(
        5.5,
        0.8,
        "Each connection can carry power, store energy, dissipate energy, or redirect the load.",
        ha="center",
        color=GRAY,
    )
    return _save(fig, "fig_companion_follow_energy")


def make_state_map() -> tuple[Path, Path]:
    fig, axis = plt.subplots(figsize=(9, 5))
    axis.set(xlim=(0, 10), ylim=(0, 6))
    axis.axis("off")
    _box(axis, (0.4, 3.8), "Configuration\nWhere Things Are", BLUE, 2.3)
    _box(axis, (3.85, 3.8), "Velocity\nHow They Move", GREEN, 2.3)
    _box(axis, (7.3, 3.8), "Stored State\nWhat Is Loaded", VIOLET, 2.3)
    for x in (2.7, 6.15):
        _arrow(axis, (x, 4.2), (x + 1.15, 4.2), INK)
    _box(axis, (2.1, 1.25), "The Present State", INK, 5.8)
    for x in (1.55, 5.0, 8.45):
        _arrow(axis, (x, 3.75), (x + (5 - x) * 0.22, 2.1), GRAY)
    axis.text(
        5,
        0.55,
        "A model asks what happens next from this complete snapshot.",
        ha="center",
        color=GRAY,
    )
    return _save(fig, "fig_companion_state_snapshot")


def make_speed_energy() -> tuple[Path, Path]:
    speed = np.linspace(0, 2, 200)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.3))
    axes[0].plot(speed, speed, color=BLUE, lw=3, label="Speed")
    axes[0].plot(speed, speed**2, color=ORANGE, lw=3, label="Kinetic Energy")
    axes[0].set(
        xlabel="Relative Speed", ylabel="Relative Amount", title="Energy Grows With Speed Squared"
    )
    axes[0].legend(frameon=False)
    masses = ["Light Segment", "Heavy Segment"]
    axes[1].bar(masses, [1, 3], color=[GREEN, VIOLET])
    axes[1].set(
        ylabel="Relative Kinetic Energy at the Same Speed", title="Mass and Inertia Matter Too"
    )
    axes[1].text(
        0.5, 2.55, "Same speed\nDifferent energy", ha="center", color=INK, fontweight="bold"
    )
    fig.suptitle("A Speedometer Is Not an Energy Meter", fontsize=16, fontweight="bold", color=INK)
    fig.tight_layout()
    return _save(fig, "fig_companion_speed_is_not_energy")


def make_carry_release() -> tuple[Path, Path]:
    fig, axes = plt.subplots(1, 3, figsize=(11, 4))
    titles = ("1. Carry", "2. Reorient", "3. Handoff")
    angles = (2.2, 1.5, 0.45)
    for axis, title, angle in zip(axes, titles, angles, strict=True):
        shoulder = np.array([0.2, 0.2])
        hand = shoulder + 1.2 * np.array([np.cos(angle), np.sin(angle)])
        club = hand + 1.3 * np.array([np.cos(angle - 0.9), np.sin(angle - 0.9)])
        axis.plot(
            [shoulder[0], hand[0]], [shoulder[1], hand[1]], color=BLUE, lw=8, solid_capstyle="round"
        )
        axis.plot(
            [hand[0], club[0]], [hand[1], club[1]], color=ORANGE, lw=5, solid_capstyle="round"
        )
        axis.scatter(*shoulder, s=90, color=INK)
        axis.scatter(*hand, s=70, color=GREEN)
        axis.set_title(title, fontweight="bold", color=INK)
        axis.set_aspect("equal")
        axis.axis("off")
        axis.set(xlim=(-1.2, 1.8), ylim=(-1.4, 1.8))
    fig.suptitle(
        "The Distal Segment Is First Carried, Then Accelerated Relative to Its Base",
        fontsize=15,
        fontweight="bold",
        color=INK,
    )
    return _save(fig, "fig_companion_carry_then_handoff")


def make_force_projection() -> tuple[Path, Path]:
    fig, axis = plt.subplots(figsize=(8, 6))
    axis.set(xlim=(-1, 6), ylim=(-1, 5))
    axis.set_aspect("equal")
    axis.axis("off")
    hand = np.array([1.0, 1.0])
    head = np.array([4.8, 2.6])
    direction = (head - hand) / np.linalg.norm(head - hand)
    normal = np.array([-direction[1], direction[0]])
    axis.plot([*hand[[0]], head[0]], [hand[1], head[1]], color=ORANGE, lw=8, solid_capstyle="round")
    axis.scatter(*hand, s=100, color=GREEN)
    axis.scatter(*head, s=130, color=INK)
    _arrow(axis, tuple(hand), tuple(hand + 2.4 * direction), BLUE, "Along the Club")
    _arrow(axis, tuple(hand), tuple(hand + 2.1 * normal), RED, "Across the Club")
    axis.add_patch(
        Arc(
            tuple(hand),
            1.4,
            1.4,
            theta1=np.degrees(np.arctan2(direction[1], direction[0])),
            theta2=np.degrees(np.arctan2(normal[1], normal[0])),
            color=VIOLET,
            lw=2,
        )
    )
    axis.text(
        3.0,
        4.4,
        "Direction Changes What a Force Can Do",
        ha="center",
        fontsize=16,
        fontweight="bold",
        color=INK,
    )
    axis.text(
        3.0,
        -0.2,
        "The same force magnitude can pull, redirect, or turn depending on geometry.",
        ha="center",
        color=GRAY,
    )
    return _save(fig, "fig_companion_force_direction")


def make_two_hand_couple() -> tuple[Path, Path]:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for axis, separation in zip(axes, (0.8, 2.0), strict=True):
        axis.plot([-2.4, 2.4], [0, 0], color=ORANGE, lw=10, solid_capstyle="round")
        for x, sign in ((-separation / 2, 1), (separation / 2, -1)):
            axis.scatter(x, 0, s=120, color=GREEN)
            _arrow(axis, (x, 0), (x, 1.6 * sign), BLUE if sign > 0 else RED)
        axis.add_patch(Arc((0, 0), 2.4, 2.4, theta1=30, theta2=320, color=VIOLET, lw=3))
        axis.set_title("Narrow Grip" if separation < 1 else "Wider Separation", fontweight="bold")
        axis.set(xlim=(-3, 3), ylim=(-2, 2))
        axis.axis("off")
    fig.suptitle(
        "Opposing Hand Forces Can Form a Couple Without a Net Push",
        fontsize=15,
        fontweight="bold",
        color=INK,
    )
    return _save(fig, "fig_companion_two_hand_couple")


def make_sign_quadrants() -> tuple[Path, Path]:
    fig, axis = plt.subplots(figsize=(7, 6))
    axis.axhline(0, color=INK, lw=1.5)
    axis.axvline(0, color=INK, lw=1.5)
    axis.set(
        xlim=(-1, 1),
        ylim=(-1, 1),
        xlabel="Angular Velocity Sign",
        ylabel="Torque Sign",
        title="Power Depends on Torque and Motion Together",
    )
    labels = {
        (0.5, 0.5): ("Positive Power", GREEN),
        (-0.5, -0.5): ("Positive Power", GREEN),
        (-0.5, 0.5): ("Negative Power", RED),
        (0.5, -0.5): ("Negative Power", RED),
    }
    for (x, y), (label, color) in labels.items():
        axis.text(
            x, y, label, ha="center", va="center", color=color, fontweight="bold", fontsize=12
        )
    axis.text(
        0,
        -1.15,
        "A negative torque can add or remove energy; the velocity sign decides.",
        ha="center",
        color=GRAY,
    )
    return _save(fig, "fig_companion_torque_power_quadrants")


def make_shaft_spring() -> tuple[Path, Path]:
    t = np.linspace(0, 1, 300)
    load = np.exp(-(((t - 0.34) / 0.16) ** 2))
    stored = np.exp(-(((t - 0.48) / 0.19) ** 2))
    release = np.gradient(-stored, t)
    fig, axis = plt.subplots(figsize=(10, 4.5))
    axis.plot(t, load, color=BLUE, lw=3, label="Applied Loading")
    axis.plot(t, stored, color=VIOLET, lw=3, label="Stored Elastic Energy")
    axis.fill_between(
        t, np.maximum(release, 0) / 8, color=ORANGE, alpha=0.3, label="Illustrative Release Rate"
    )
    axis.set(
        xlabel="Illustrative Swing Phase",
        ylabel="Normalized Amount",
        title="A Flexible Shaft Is a Small, Timed Energy Account",
    )
    axis.legend(frameon=False, ncol=3)
    axis.set_xticks([0, 0.33, 0.66, 1], labels=["Early", "Loading", "Late", "Delivery"])
    return _save(fig, "fig_companion_shaft_storage")


def make_counterfactual_fork() -> tuple[Path, Path]:
    fig, axis = plt.subplots(figsize=(10, 5))
    axis.set(xlim=(0, 10), ylim=(0, 6))
    axis.axis("off")
    _box(axis, (0.6, 2.6), "Same State", INK, 1.8)
    _arrow(axis, (2.4, 3.0), (4.0, 4.4), BLUE, "Keep Input")
    _arrow(axis, (2.4, 3.0), (4.0, 1.6), RED, "Remove Input")
    _box(axis, (4.0, 4.0), "Pointwise\nAcceleration", BLUE, 2.1)
    _box(axis, (4.0, 1.2), "Pointwise\nDrift", RED, 2.1)
    _arrow(axis, (6.1, 4.4), (7.5, 4.4), BLUE)
    _arrow(axis, (6.1, 1.6), (7.5, 1.6), RED)
    _box(axis, (7.5, 4.0), "Forward\nTrajectory", BLUE, 1.8)
    _box(axis, (7.5, 1.2), "Forward\nCounterfactual", RED, 1.8)
    axis.text(
        5,
        5.55,
        "Two Questions That Must Not Be Confused",
        ha="center",
        fontsize=16,
        fontweight="bold",
        color=INK,
    )
    axis.text(
        5,
        0.35,
        "Pointwise: what is the acceleration now?  Forward: where does the changed system go?",
        ha="center",
        color=GRAY,
    )
    return _save(fig, "fig_companion_counterfactual_fork")


def make_clock_state() -> tuple[Path, Path]:
    x = np.linspace(0, 1, 300)
    states = [1 / (1 + np.exp(-18 * (x - c))) for c in (0.44, 0.52, 0.60)]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharey=True)
    for state, color in zip(states, (BLUE, GREEN, VIOLET), strict=True):
        axes[0].plot(x, state, color=color, lw=2)
        axes[1].plot(x, state, color=color, lw=2)
    axes[0].axvline(0.52, color=RED, ls="--", lw=2, label="Clock Trigger")
    axes[0].set_title("Clock: One Time for Every Run")
    for state, color in zip(states, (BLUE, GREEN, VIOLET), strict=True):
        idx = np.argmin(np.abs(state - 0.6))
        axes[1].scatter(x[idx], state[idx], color=color, s=70)
    axes[1].axhline(0.6, color=RED, ls="--", lw=2, label="State Threshold")
    axes[1].set_title("State: Trigger When the System Arrives")
    for axis in axes:
        axis.set(xlabel="Time", ylabel="Mechanical Progress")
        axis.legend(frameon=False)
    fig.suptitle(
        "A State Trigger Moves With the Realized Motion", fontsize=15, fontweight="bold", color=INK
    )
    return _save(fig, "fig_companion_clock_vs_state")


def make_speed_tradeoffs() -> tuple[Path, Path]:
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    summaries = data["program_summaries"]
    labels = {
        "clock_restrain_then_drive": "Clock",
        "state_triggered_handoff": "State",
        "state_triggered_higher_impedance": "State + Impedance",
        "early_drive": "Early Drive",
    }
    colors = (BLUE, GREEN, VIOLET, ORANGE)
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.7))
    for (program, label), color in zip(labels.items(), colors, strict=True):
        held = summaries[program]["held_out"]
        axes[0].scatter(
            held["delivery_speed_m_s"]["std"],
            held["delivery_speed_m_s"]["q10"],
            s=90,
            color=color,
            label=label,
        )
        axes[1].scatter(
            held["peak_hand_force_n"]["q90"],
            held["face_path_error_deg"]["mean"],
            s=90,
            color=color,
            label=label,
        )
    axes[0].set(
        xlabel="Speed Spread (m/s)",
        ylabel="Lower-Tail Delivery Speed (m/s)",
        title="Speed Floor Versus Repeatability",
    )
    axes[1].set(
        xlabel="High-Exposure Hand Force (N)",
        ylabel="Mean Planar Error (deg)",
        title="Accuracy Proxy Versus Loading",
    )
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle(
        "There Is No Single Winner When the Outcomes Disagree",
        fontsize=15,
        fontweight="bold",
        color=INK,
    )
    fig.tight_layout()
    return _save(fig, "fig_companion_tradeoff_map")


def make_task_null() -> tuple[Path, Path]:
    fig, axis = plt.subplots(figsize=(9, 5))
    axis.set(xlim=(0, 10), ylim=(0, 6))
    axis.axis("off")
    center = (7.6, 3)
    axis.add_patch(Circle(center, 0.65, facecolor=GREEN, edgecolor=GREEN, alpha=0.18, lw=3))
    axis.text(*center, "Delivery\nWindow", ha="center", va="center", fontweight="bold", color=GREEN)
    starts = ((0.7, 1.0), (0.8, 2.1), (0.6, 3.2), (0.9, 4.3), (0.7, 5.1))
    colors = (BLUE, VIOLET, ORANGE, RED, GRAY)
    for start, color in zip(starts, colors, strict=True):
        path = FancyArrowPatch(
            start,
            center,
            connectionstyle=f"arc3,rad={(start[1]-3)*.08}",
            arrowstyle="-|>",
            mutation_scale=13,
            lw=2.2,
            color=color,
        )
        axis.add_patch(path)
    axis.text(
        3.0,
        5.6,
        "Different Coordination Histories",
        ha="center",
        fontsize=14,
        fontweight="bold",
        color=INK,
    )
    axis.text(
        7.6,
        1.0,
        "Stable task outcome does not require\nidentical motion everywhere.",
        ha="center",
        color=GRAY,
    )
    return _save(fig, "fig_companion_many_paths_one_outcome")


def make_evidence_ladder() -> tuple[Path, Path]:
    fig, axis = plt.subplots(figsize=(10, 5.4))
    axis.set(xlim=(0, 11), ylim=(0, 6))
    axis.axis("off")
    levels = (
        (0.5, 0.6, "Equation\nIdentity", GRAY),
        (2.5, 1.55, "Reduced\nModel", BLUE),
        (4.5, 2.5, "Cross-Engine\nCheck", VIOLET),
        (6.5, 3.45, "Instrumented\nHuman Study", GREEN),
        (8.5, 4.4, "Replicated\nOutcome", ORANGE),
    )
    for x, y, label, color in levels:
        _box(axis, (x, y), label, color, 1.75)
    axis.plot([0.5, 10.25], [0.45, 5.25], color=INK, lw=1, alpha=0.3)
    axis.text(
        5.5,
        5.7,
        "Confidence Rises Only When the Evidence Changes Kind",
        ha="center",
        fontsize=16,
        fontweight="bold",
        color=INK,
    )
    axis.text(
        5.5,
        0.15,
        "A more detailed model is not automatically a human experiment.",
        ha="center",
        color=RED,
        fontweight="bold",
    )
    return _save(fig, "fig_companion_evidence_ladder")


def make_falsification_map() -> tuple[Path, Path]:
    fig, axis = plt.subplots(figsize=(10, 5.5))
    axis.set(xlim=(0, 11), ylim=(0, 6))
    axis.axis("off")
    _box(axis, (0.5, 2.6), "Claim", INK, 1.5)
    _arrow(axis, (2, 3), (3, 3), INK)
    _box(axis, (3, 2.6), "Prediction", BLUE, 1.8)
    _arrow(axis, (4.8, 3), (5.8, 3), INK)
    _box(axis, (5.8, 2.6), "Measurement", GREEN, 1.8)
    _arrow(axis, (7.6, 3), (8.6, 4.3), GREEN, "Agrees")
    _arrow(axis, (7.6, 3), (8.6, 1.5), RED, "Disagrees")
    _box(axis, (8.6, 3.9), "Narrower\nConfidence", GREEN, 1.8)
    _box(axis, (8.6, 1.1), "Revise or\nReject", RED, 1.8)
    axis.text(
        5.5,
        5.55,
        "A Scientific Story Must Include an Exit",
        ha="center",
        fontsize=16,
        fontweight="bold",
        color=INK,
    )
    axis.text(
        5.5,
        0.35,
        "A claim that survives every possible result has not risked enough.",
        ha="center",
        color=GRAY,
    )
    return _save(fig, "fig_companion_falsification_map")


BUILDERS: tuple[Callable[[], tuple[Path, Path]], ...] = (
    make_follow_energy,
    make_state_map,
    make_speed_energy,
    make_carry_release,
    make_force_projection,
    make_two_hand_couple,
    make_sign_quadrants,
    make_shaft_spring,
    make_counterfactual_fork,
    make_clock_state,
    make_speed_tradeoffs,
    make_task_null,
    make_evidence_ladder,
    make_falsification_map,
)


def main() -> None:
    _style()
    for builder in BUILDERS:
        for path in builder():
            print(path)


if __name__ == "__main__":
    main()
