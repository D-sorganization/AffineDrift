"""Generate the visual vocabulary for the proximal-distal companion book."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Arc, Circle, FancyArrowPatch, FancyBboxPatch

from scripts.shaft_energy_illustration import prescribed_cycle

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "articles/figures/proximal_distal_companion"
EVIDENCE = ROOT / "data/illustrations/uncertainty_control_study.json"

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
    axis: Axes,
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


def _box(axis: Axes, xy: tuple[float, float], text: str, color: str, width: float = 2.0) -> None:
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
        "Follow the Interactions and the Energy Ledger",
        ha="center",
        fontsize=16,
        fontweight="bold",
        color=INK,
    )
    axis.text(
        5.5,
        0.8,
        "Ground contact can redirect momentum without supplying work.\n"
        "Other interfaces may transfer, store or dissipate mechanical energy.",
        ha="center",
        color=GRAY,
    )
    return _save(fig, "fig_companion_follow_energy")


def make_state_map() -> tuple[Path, Path]:
    """Separate components of state from the conditions needed for prediction."""
    fig, axis = plt.subplots(figsize=(9, 5))
    axis.set(xlim=(0, 10), ylim=(0, 6))
    axis.axis("off")
    _box(axis, (0.4, 3.8), "Configuration\nWhere Things Are", BLUE, 2.3)
    _box(axis, (3.85, 3.8), "Velocity\nHow They Move", GREEN, 2.3)
    _box(axis, (7.3, 3.8), "Internal Variables\nMemory and Mode", VIOLET, 2.3)
    _box(axis, (2.1, 1.25), "The Present State", INK, 5.8)
    for x in (1.55, 5.0, 8.45):
        _arrow(axis, (x, 3.75), (x + (5 - x) * 0.22, 2.1), GRAY)
    axis.text(
        5,
        0.55,
        "Prediction Also Requires the Model and Parameters,\n"
        "Future Inputs, Initial Time, and Well-Posed Evolution Rules.",
        ha="center",
        color=GRAY,
    )
    return _save(fig, "fig_companion_state_snapshot")


def make_speed_energy() -> tuple[Path, Path]:
    speed = np.linspace(0, 2, 200)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.3))
    axes[0].plot(speed, speed, color=BLUE, lw=3, label=r"Speed $v/v_0$")
    axes[0].plot(speed, speed**2, color=ORANGE, lw=3, label=r"Energy $K/K_0$")
    axes[0].set(
        xlabel=r"Speed Ratio $v/v_0$",
        ylabel="Dimensionless Ratio",
        title="Fixed Mass: $K_0 = m v_0^2/2$",
    )
    axes[0].legend(frameon=False)
    masses = [r"Mass $m_0$", r"Mass $3m_0$"]
    axes[1].bar(masses, [1, 3], color=[GREEN, VIOLET])
    axes[1].set(ylabel=r"Energy Ratio $K/K_0$", title="Translation at the Same Speed")
    axes[1].text(0, 2.35, "$K_0=m_0v^2/2$\nNo Rotation Included", ha="center", color=INK)
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
    """Separate a grip force's application point from its moment reference."""
    fig, axis = plt.subplots(figsize=(8, 6))
    axis.set(xlim=(-1, 6), ylim=(-1, 5))
    axis.set_aspect("equal")
    axis.axis("off")
    hand = np.array([1.0, 1.0])
    head = np.array([4.8, 2.6])
    # An illustrative straight-link COM, not a measured driver mass distribution.
    center = hand + 0.7 * (head - hand)
    direction = (head - hand) / np.linalg.norm(head - hand)
    normal = np.array([-direction[1], direction[0]])
    axis.plot([hand[0], head[0]], [hand[1], head[1]], color=ORANGE, lw=8, zorder=0.5)
    axis.scatter(hand[0], hand[1], s=100, color=GREEN, zorder=5)
    axis.scatter(head[0], head[1], s=130, color=INK)
    axis.scatter(center[0], center[1], s=90, color=VIOLET, zorder=5)
    axis.text(hand[0] - 0.6, hand[1] - 0.25, "$H$ (Hand)", color=GREEN)
    axis.text(center[0] - 0.3, center[1] + 0.8, "$G$ (Center of Mass)", color=VIOLET)
    _arrow(axis, tuple(hand), tuple(hand + 2.4 * direction), BLUE)
    axis.text(2.1, 1.9, "Along Shaft", color=BLUE, ha="center", fontweight="bold")
    _arrow(axis, tuple(hand), tuple(hand + 2.1 * normal), RED)
    axis.text(-0.2, 2.2, "Transverse", color=RED, ha="center", fontweight="bold")
    # Translate the free displacement vector below the shaft so it stays legible.
    _arrow(axis, tuple(center - 0.6 * normal), tuple(hand - 0.6 * normal), VIOLET, "$r_{GH}$")
    axis.text(
        3.0,
        4.4,
        "Direction and Reference Point Set the Moment",
        ha="center",
        fontsize=15,
        fontweight="bold",
        color=INK,
    )
    axis.text(
        2.5,
        -0.4,
        r"$M_H^{(F)}=0,\qquad M_G^{(F)}=r_{GH}\times F$",
        ha="center",
        fontsize=14,
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
    data = prescribed_cycle()
    time = data["time"]
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True, layout="constrained")
    energy, power = axes
    energy.plot(time, data["elastic"], color=VIOLET, label="Elastic Energy")
    energy.plot(time, data["kinetic"], color=BLUE, label="Kinetic Energy")
    energy.plot(time, data["elastic"] + data["kinetic"], color=INK, ls="--", label="Total")
    energy.set(ylabel="Energy (J)", title="A Prescribed Motion With a Closed Energy Account")
    power.plot(time, data["input_power"], color=BLUE, label="Signed Drive Power")
    power.plot(time, data["dissipation"], color=ORANGE, label="Damping Loss Rate")
    power.plot(time, data["energy_rate"], color=INK, ls="--", label="Stored-Energy Rate")
    power.axhline(0, color=GRAY, lw=0.7)
    power.set(xlabel="Time (s)", ylabel="Power (W)")
    for axis in axes:
        axis.legend(frameon=False, loc="upper right", fontsize=9)
    fig.supxlabel("Illustration Only: Prescribed Spring–Mass–Damper Motion", fontsize=10)
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
    """Plot the chapter's eight archived candidates without inventing a frontier."""
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    candidates = data["control_comparison"]["candidates"]
    with np.load(EVIDENCE.with_name(data["array_artifact"])) as archive:
        held = archive["held_out_outputs"].copy()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.6))
    for index, candidate in enumerate(candidates):
        label = f"{index + 1}. {candidate['name'].replace('_', ' ').title()}"
        color = plt.get_cmap("tab10")(index)
        speed = held[index, :, 0]
        first = (held[index, :, 1].mean(), np.quantile(speed, 0.1))
        second = (np.quantile(held[index, :, 2], 0.9), speed.std(ddof=1))
        axes[0].scatter(
            *first,
            s=65,
            color=color,
            label=label,
        )
        axes[1].scatter(*second, s=65, color=color)
        for axis, point in zip(axes, (first, second), strict=True):
            axis.annotate(str(index + 1), point, xytext=(5, 5), textcoords="offset points")
    axes[0].set(
        xlabel="Mean Planar Face–Path Error (deg)",
        ylabel="10th-Percentile Delivery Speed (m/s)",
        title="Speed Versus Planar Error",
    )
    axes[1].set(
        xlabel="90th-Percentile Peak Hand Force (N)",
        ylabel="Delivery-Speed Standard Deviation (m/s)",
        title="Force Versus Speed Spread",
    )
    for axis in axes:
        axis.margins(0.12)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=4, fontsize=8)
    fig.suptitle("Eight Preselected Programs: Six Held-Out Cases", fontweight="bold", color=INK)
    fig.tight_layout(rect=(0, 0.12, 1, 0.96))
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
            connectionstyle=f"arc3,rad={(start[1] - 3) * 0.08}",
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
