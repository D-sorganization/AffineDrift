"""Regenerate the numbers and figures of "Slack Take-Up as a Witness" (#5136).

Run from the repository root with:
python -m scripts.build_slack_takeup_witness
"""

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from src.tools import slack_takeup_counting as counting
from src.tools import slack_takeup_first_order as first_order
from src.tools import slack_takeup_witness as witness

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/slack_takeup_witness/results.json"
FIGURE_DIR = ROOT / "articles/figures/slack_takeup_witness"
REGIMES = ("known", "uncertain", "preloaded", "smooth")
LABELS = ("Split", "Lead Gap", "Trail Gap", "Lead State", "Trail State", "Lead k", "Trail k")


def compute() -> dict[str, Any]:
    """Run every study in a fixed order from one seeded generator."""
    rng = np.random.default_rng(witness.SEED)
    train = {
        name: witness.train_order_accuracy(rng, 400, taut)
        for name, taut in (("uncertain", False), ("taut", True))
    }
    hands = {regime: witness.classify_regime(rng, regime) for regime in REGIMES}
    jacobian = counting.scaled_jacobian(counting.nominal_vector())
    pair = counting.matched_pair()
    club = counting.pair_traces(pair["lead_split"], pair["nuisance"])["positions"][:, :, 1]
    pair["max_club_difference"] = float(np.max(np.abs(club[:, 0] - club[:, 1])))
    return {
        "schema_version": 1,
        "train": train,
        "hands": hands,
        "jacobian": jacobian.tolist(),
        "split_visibility": counting.split_visibility(jacobian),
        "matched_pair": pair,
        "first_order": first_order.first_order_summary(),
        "grasp": counting.grasp_visibility(),
    }


def _save(figure: Figure, path: Path) -> None:
    """Write deterministic SVG without a date stamp."""
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        figure.savefig(stream, format="svg", metadata={"Date": None})
    plt.close(figure)


def _train_figure() -> Figure:
    """Coupler stretch of a nominal train driven at the front, then at the rear."""
    ones = np.ones((2, witness.TRAIN_CARS - 1))
    forces = np.zeros((2, witness.TRAIN_CARS))
    forces[0, 0] = forces[1, -1] = witness.TRAIN_DRIVE
    chain = witness.Chain(
        np.ones(witness.TRAIN_CARS),
        forces,
        ones * witness.TRAIN_GAP,
        ones * witness.TRAIN_STIFFNESS,
        0.0 * ones,
        witness.TRAIN_DAMPING,
    )
    events, history = witness.simulate_traced(chain, witness.TRAIN_CLOCK)
    time = np.arange(history.shape[0]) * witness.TRAIN_CLOCK.step
    figure, axes = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True, layout="constrained")
    for trial, (axis, title) in enumerate(
        zip(axes, ("Drive at the Front Car", "Drive at the Rear Car"), strict=True)
    ):
        stretch = history[:, trial, :-1] - history[:, trial, 1:]
        for coupler in range(stretch.shape[1]):
            (line,) = axis.plot(time, stretch[:, coupler], label=f"Coupler {coupler + 1}")
            axis.axvline(events[trial, coupler], color=line.get_color(), linestyle=":")
        for edge in (-witness.TRAIN_GAP, witness.TRAIN_GAP):
            axis.axhline(edge, color="gray", linewidth=0.8, linestyle="--")
        axis.set(title=title, xlabel="Time (Manufactured Units)", xlim=(0, 12))
        axis.grid(alpha=0.25)
    axes[0].set_ylabel("Coupler Stretch")
    axes[1].legend(loc="center right", fontsize=9)
    return figure


def _blind_counts(results: dict[str, Any]) -> tuple[list[tuple[str, int, int]], ...]:
    """(label, blind directions, unknowns) rows for Toy B and for Toy C."""
    split, flow = results["split_visibility"], results["first_order"]
    toy_b = [
        ("Rigid Grip", 1, 1),
        ("Slack, Nuisance Known", 1 - min(1, split["rank_all"]), 1),
        ("Slack, Nuisance Free", split["unknowns"] - split["rank_all"], split["unknowns"]),
        ("First-Order Take-Up", flow["unknowns"] - flow["rank"], flow["unknowns"]),
    ]
    toy_c = [(row["channel"].title(), row["nullity"], 6) for row in results["grasp"]]
    return toy_b, toy_c


def _nullity_figure(results: dict[str, Any]) -> Figure:
    """Noise-free blind-direction counts, Toy B and Toy C on separate panels."""
    figure, axes = plt.subplots(2, 1, figsize=(8, 5.2), layout="constrained")
    titles = ("Toy B: One Rotation Axis", "Toy C: Six-Dimensional Grasp Kernel")
    for axis, rows, title, color in zip(
        axes, _blind_counts(results), titles, ("#4c72b0", "#dd8452"), strict=True
    ):
        names, blind, unknowns = zip(*rows[::-1], strict=True)
        axis.barh(names, unknowns, color="none", edgecolor=color, label="Unknowns")
        axis.barh(names, blind, color=color, label="Blind After Observation")
        for index, (value, total) in enumerate(zip(blind, unknowns, strict=True)):
            axis.text(total + 0.08, index, f"{value} of {total}", va="center")
        axis.set(title=title, xlim=(0, 8))
        axis.grid(axis="x", alpha=0.25)
    axes[0].legend(loc="lower right", fontsize=8)
    axes[1].set_xlabel("Directions (Noise-Free Rank Count)")
    return figure


def _sensitivity_figure(results: dict[str, Any]) -> Figure:
    """Scaled event-time sensitivities: split against the six nuisance parameters."""
    matrix = np.asarray(results["jacobian"])
    figure, axis = plt.subplots(figsize=(8, 2.8), layout="constrained")
    image = axis.imshow(matrix, cmap="RdBu_r", vmin=-8, vmax=8, aspect="auto")
    for (row, column), value in np.ndenumerate(matrix):
        axis.text(column, row, f"{value:.2f}", ha="center", va="center", fontsize=9)
    axis.set_xticks(range(len(LABELS)), LABELS)
    axis.set_yticks((0, 1), ("Lead Take-Up", "Trail Take-Up"))
    axis.set_title("Event-Time Shift per Prior Half-Range, in Units of Timing Noise")
    figure.colorbar(image, ax=axis, shrink=0.9)
    return figure


def _pair_figure(results: dict[str, Any]) -> Figure:
    """Coupler stretch and club angle for the matched opposite-source pair."""
    pair = results["matched_pair"]
    traces = counting.pair_traces(pair["lead_split"], pair["nuisance"])
    time, positions = traces["time"] * 1e3, traces["positions"]
    figure, axes = plt.subplots(1, 2, figsize=(9, 3.6), layout="constrained")
    for trial, (style, who) in enumerate((("-", "Lead-Led"), ("--", "Trail-Led"))):
        offset = (
            np.asarray(counting.nominal_vector()[3:5])
            if trial == 0
            else np.asarray(pair["nuisance"][1:])
        )
        lead = positions[:, trial, 0] - positions[:, trial, 1] + offset[0]
        trail = positions[:, trial, 1] - positions[:, trial, 2] + offset[1]
        axes[0].plot(time, lead, style, color="#4c72b0", label=f"{who}, Lead Coupler")
        axes[0].plot(time, trail, style, color="#dd8452", label=f"{who}, Trail Coupler")
        axes[1].plot(time, positions[:, trial, 1], style, color="black", label=who)
    for moment in pair["target_times"] + pair["matched_times"]:
        axes[0].axvline(moment * 1e3, color="gray", linewidth=0.8, linestyle=":")
    edges = ((witness.HAND_GAP, "--", "Band Edge"), (pair["nuisance"][0], "-.", "Wide Trail Edge"))
    for edge, style, label in edges:
        axes[0].axhline(edge, color="gray", linewidth=0.8, linestyle=style, label=label)
        axes[0].axhline(-edge, color="gray", linewidth=0.8, linestyle=style)
    axes[0].set(
        xlabel="Time (ms)",
        ylabel="Coupler Stretch (rad)",
        xlim=(0, 20),
        title="Take-Up Times Within Noise, Opposite Source",
    )
    axes[1].set(xlabel="Time (ms)", ylabel="Club Angle (rad)", title="Net Club Rotation")
    for axis in axes:
        axis.grid(alpha=0.25)
    axes[0].legend(fontsize=7, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.2))
    axes[1].legend(fontsize=8)
    return figure


def build(data_path: Path = DATA_PATH, figure_dir: Path = FIGURE_DIR) -> dict[str, Any]:
    """Compute the results, write the JSON and the four SVG figures, and return the results."""
    results = compute()
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    figure_dir.mkdir(parents=True, exist_ok=True)
    with plt.rc_context({"font.size": 10, "svg.fonttype": "none", "svg.hashsalt": "stw-v1"}):
        _save(_train_figure(), figure_dir / "train-takeup-order.svg")
        _save(_nullity_figure(results), figure_dir / "nullity-counts.svg")
        _save(_sensitivity_figure(results), figure_dir / "event-time-sensitivity.svg")
        _save(_pair_figure(results), figure_dir / "matched-pair.svg")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--figures", type=Path, default=FIGURE_DIR)
    arguments = parser.parse_args()
    build(arguments.data, arguments.figures)
