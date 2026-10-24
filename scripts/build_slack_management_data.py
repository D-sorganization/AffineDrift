"""Regenerate the data and figures for "Managing Slack in Linked Systems" (#5135).

Run from the repository root with ``python3 -m scripts.build_slack_management_data``.  Writes
``data/slack_management/results.json`` and four SVG figures under
``articles/figures/slack_management/``.  Output is deterministic.
"""

import argparse
from collections.abc import Callable
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from scripts.build_null_space_exploration_examples import render_document
from src.tools.slack_management_studies import (
    DECLARED_GAP_RAD,
    EQUIVALENCE_MARGINS,
    REPRESENTATIONS,
    STUDY_HORIZON,
    flip_section,
    muscle_margin_section,
    representation_section,
    reproduction_section,
    split_section,
    unequal_lag_section,
)
from src.tools.slack_transmission import (
    PERSISTENT,
    ROLE_REVERSAL,
    channel_torque,
    play_operator,
    simulate,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/slack_management/results.json"
FIGURES = ROOT / "articles/figures/slack_management"
SCHEMA_VERSION = 1
MRAD = 1000.0
MS = 1000.0
TRACE_WINDOW_S = 0.08
PLAY_SAMPLES = 400
REFERENCE_PERIOD = "18ms"
INSET_BOUNDS = (0.55, 0.07, 0.42, 0.36)  # Axes fraction: empty lower right.
INSET_YLIM_PERCENT = 15.0
SPLIT_METRICS = ("error_impulse_nms", "channel_error_impulse_nms", "peak_overshoot_nm")
LABELS = {
    "rigid": "No Slack (Stiff Spring)",
    "dead_zone": "Dead Zone",
    "smooth_stiffening": "Smooth Stiffening Spring",
    "series_elastic_activation": "Spring + Second Linear Lag",
    "rigid_unequal_lags": "No Slack, Unequal Lags (18 / 36 ms)",
}

SECTIONS: dict[str, Callable[[], dict[str, Any]]] = {
    "reproduction": reproduction_section,
    "representations": representation_section,
    "flip": flip_section,
    "split": split_section,
    "unequal_lags": unequal_lag_section,
    "muscle_margin": muscle_margin_section,
}


def build_document() -> dict[str, Any]:
    """Run every study and wrap the results in the schema envelope."""
    return {"schema_version": SCHEMA_VERSION, "sections": {k: f() for k, f in SECTIONS.items()}}


def _ladder() -> Figure:
    figure, (left, right) = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    deflection = np.linspace(-0.04, 0.04, 801)
    for rep in REPRESENTATIONS[:3]:
        left.plot(deflection * MRAD, channel_torque(deflection, rep), label=LABELS[rep.name])
    left.set(xlabel="Deflection (mrad)", ylabel="Transmitted Torque (N m)")
    left.set_title("Memoryless Characteristics")
    phase = np.linspace(0.0, 4.0 * np.pi, PLAY_SAMPLES)
    position = 0.03 * np.sin(phase)
    right.plot(position * MRAD, play_operator(position, DECLARED_GAP_RAD) * MRAD, label="Play")
    right.plot(position * MRAD, position * MRAD, ":", color="gray", label="No Gap")
    right.set(xlabel="Input Position (mrad)", ylabel="Output Position (mrad)")
    right.set_title("Backlash (Play) Remembers Its Last Contact")
    for axis in (left, right):
        axis.grid(alpha=0.25)
        axis.legend(fontsize=9)
    return figure


def _traces() -> Figure:
    figure, axes = plt.subplots(2, 3, figsize=(13, 6.5), sharex=True, sharey=True)
    axes.flat[-1].set_visible(False)
    for axis, rep in zip(axes.flat, REPRESENTATIONS, strict=False):
        for program, style in ((PERSISTENT, "-"), (ROLE_REVERSAL, "--")):
            trace = simulate(program, rep, grid=STUDY_HORIZON)
            keep = trace.time_s <= TRACE_WINDOW_S
            net = trace.transmitted_nm.sum(axis=1)[keep]
            label = program.name.replace("_", " ").title()
            axis.plot(trace.time_s[keep] * MS, net, style, label=label)
        axis.axhline(sum(PERSISTENT.post_nm), color="black", lw=0.8, label="Desired Net")
        axis.set_title(LABELS[rep.name], fontsize=11)
        axis.grid(alpha=0.25)
    axes[0, 2].tick_params(labelbottom=True)
    for axis in (*axes[1], axes[0, 2]):
        axis.set_xlabel("Time After Transition (ms)")
    for axis in axes[:, 0]:
        axis.set_ylabel("Net Transmitted Torque (N m)")
    axes[0, 0].legend(fontsize=9)
    figure.set_layout_engine("constrained")
    return figure


def _flip(flip: dict[str, Any]) -> Figure:
    figure, (left, right) = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    gap = np.asarray(flip["gap_grid_rad"]) * MRAD
    for key, curve in flip["curves"].items():
        shape, period = key.rsplit("_", 1)
        style = "-" if shape == "dead_zone" else "--"
        label = f"{LABELS.get(shape, 'Smooth Stiffening Spring')}, T = {period[:-2]} ms"
        if period == REFERENCE_PERIOD:
            left.plot(gap, 100 * np.asarray(curve["relative_advantage"]), style, label=label)
        right.plot(gap, np.asarray(curve["max_zero_transmission_s"]) * MS, style, label=label)
    for margin in EQUIVALENCE_MARGINS:
        left.axhline(100 * margin, color="gray", lw=0.7, ls=":")
    left.set(xlabel="Gap or Softening Length (mrad)", ylabel="Persistent Advantage (%)")
    left.set_title("Tracking-Error Advantage")
    _margin_inset(left, flip)
    right.set(xlabel="Gap or Softening Length (mrad)", ylabel="Longest Zero Transmission (ms)")
    right.set_title("Zero-Transmission Time (Role Reversal)")
    for axis in (left, right):
        axis.grid(alpha=0.25)
        axis.legend(fontsize=8, loc="upper left")
    return figure


def _margin_inset(axis: Any, flip: dict[str, Any]) -> None:
    zoom = axis.inset_axes(INSET_BOUNDS)
    gap = np.asarray(flip["inset_gap_grid_rad"]) * MRAD
    for index, curve in enumerate(flip["inset_relative_advantage"].values()):
        zoom.plot(gap, 100 * np.asarray(curve), ("-", "--")[index], color=f"C{index}")
    for margin in EQUIVALENCE_MARGINS:
        zoom.axhline(100 * margin, color="gray", lw=0.7, ls=":")
        zoom.annotate(f"{margin:.0%}", (gap[-1], 100 * margin), fontsize=7, va="bottom", ha="right")
    zoom.set_ylim(0.0, INSET_YLIM_PERCENT)
    zoom.set_title("Margins Near Zero", fontsize=8)
    zoom.tick_params(labelsize=7)


def _split(split: dict[str, Any]) -> Figure:
    figure, axes = plt.subplots(3, 1, figsize=(8, 8.5), sharex=True, layout="constrained")
    pair = np.asarray(split["internal_pair_grid_nm"])
    for name, row in split["representations"].items():
        for axis, key in zip(axes, SPLIT_METRICS, strict=True):
            axis.plot(pair, row[key], marker="o", ms=3, label=LABELS[name])
    axes[2].plot(pair, split["preparation_torque_norm_nm"], color="black", label="Preparation Norm")
    for axis in axes:
        axis.axvline(0.0, color="gray", ls=":")
        axis.axvline(split["persistent_internal_pair_nm"], color="gray", ls=":")
        axis.grid(alpha=0.25)
        axis.legend(fontsize=9)
    axes[0].set(ylabel="Net Error (N m s)", title="Shifting the Preparation Split")
    axes[1].set(ylabel="Per-Channel Error (N m s)")
    axes[2].set(xlabel="Internal Pair c (N m)", ylabel="Overshoot or Norm (N m)")
    return figure


def _save(figure: Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("w", encoding="utf-8", newline="\n") as stream:
            figure.savefig(stream, format="svg", metadata={"Date": None})
    finally:
        plt.close(figure)


def write_outputs(data_path: Path = DATA, figure_dir: Path = FIGURES) -> dict[str, Any]:
    """Write the JSON document and every figure; return the document."""
    document = build_document()
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_bytes(render_document(document).encode("utf-8"))
    sections = document["sections"]
    with plt.rc_context({"font.size": 11, "svg.fonttype": "none", "svg.hashsalt": "slack-v1"}):
        _save(_ladder(), figure_dir / "fig_representation_ladder.svg")
        _save(_traces(), figure_dir / "fig_transmission_by_representation.svg")
        _save(_flip(sections["flip"]), figure_dir / "fig_conclusion_flip_map.svg")
        _save(_split(sections["split"]), figure_dir / "fig_preparation_split.svg")
    return document


def main() -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--figures", type=Path, default=FIGURES)
    arguments = parser.parse_args()
    write_outputs(arguments.data, arguments.figures)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
