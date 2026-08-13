"""Generate reviewer-path, synthesis, and energy-ledger companion figures."""

from __future__ import annotations

import matplotlib.pyplot as plt
from make_proximal_distal_companion_expanded_figures import _clean, _edge, _node
from make_proximal_distal_companion_figures import (
    BLUE,
    GRAY,
    GREEN,
    INK,
    ORANGE,
    RED,
    VIOLET,
    _save,
)


def make_reviewer_path() -> None:
    fig, axis = plt.subplots(figsize=(11, 4.7))
    _clean(axis, (-0.5, 12.5), (-1, 4.5))
    labels = (
        (0.7, "Claim", BLUE),
        (2.8, "Figure", GREEN),
        (4.9, "Data", ORANGE),
        (7.0, "Script", VIOLET),
        (9.1, "Test", RED),
        (11.2, "Manifest", INK),
    )
    for x, label, color in labels:
        _node(axis, x, 2.2, label, color, 1.5)
    for left, right in zip(labels[:-1], labels[1:], strict=True):
        _edge(axis, (left[0] + 0.75, 2.2), (right[0] - 0.75, 2.2))
    axis.text(
        6,
        0.6,
        "A reviewer can walk backward from prose to reproducible evidence.",
        ha="center",
        color=GRAY,
    )
    axis.set_title(
        "The Publication Is an Entry Point, Not the Evidence Boundary",
        color=INK,
        fontweight="bold",
        fontsize=16,
    )
    _save(fig, "fig_companion_reviewer_path")


def make_synthesis() -> None:
    fig, axis = plt.subplots(figsize=(10, 6))
    _clean(axis, (-5.5, 5.5), (-4, 4))
    _node(axis, 0, 0, "A Testable\nMechanism", INK, 2.3)
    items = (
        (0, 2.8, "Energy Ledger", BLUE),
        (3.7, 1.6, "Geometry", GREEN),
        (3.7, -1.6, "Timing", ORANGE),
        (0, -2.8, "Robustness", VIOLET),
        (-3.7, -1.6, "Human Evidence", RED),
        (-3.7, 1.6, "Falsification", GRAY),
    )
    for x, y, text, color in items:
        _node(axis, x, y, text, color, 2.0)
        _edge(axis, (x * 0.72, y * 0.72), (x * 0.25, y * 0.25), color)
    axis.set_title(
        "The Framework Connects Mechanisms Without Selecting One Technique",
        color=INK,
        fontweight="bold",
        fontsize=16,
    )
    _save(fig, "fig_companion_synthesis_map")


def make_energy_ledger() -> None:
    fig, axis = plt.subplots(figsize=(9.5, 4.8))
    labels = ("Hand Work", "Gravity", "Shaft Storage", "Damping", "Kinetic Gain")
    values = (50, 3, -8, -5, 40)
    colors = (BLUE, GREEN, VIOLET, RED, ORANGE)
    axis.bar(labels, values, color=colors)
    axis.axhline(0, color=INK, lw=1)
    axis.set(
        ylabel="Energy Change (J)",
        title="A Closed Ledger Names Supply, Storage, Loss, and Remaining Kinetic Energy",
    )
    for index, value in enumerate(values):
        axis.text(
            index, value + (1.3 if value >= 0 else -2.5), f"{value:+d} J", ha="center", color=INK
        )
    fig.tight_layout()
    _save(fig, "fig_companion_energy_ledger")
