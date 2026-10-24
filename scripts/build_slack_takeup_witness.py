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
from src.tools import slack_takeup_witness as witness

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/slack_takeup_witness/results.json"
FIGURE_DIR = ROOT / "articles/figures/slack_takeup_witness"


def compute() -> dict[str, Any]:
    """Run every study in a fixed order from one seeded generator."""
    rng = np.random.default_rng(witness.SEED)
    train = {
        name: witness.train_order_accuracy(rng, 400, taut)
        for name, taut in (("uncertain", False), ("taut", True))
    }
    return {
        "schema_version": 1,
        "train": train,
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


def build(data_path: Path = DATA_PATH, figure_dir: Path = FIGURE_DIR) -> dict[str, Any]:
    """Compute the results, write the JSON and the SVG figures, and return the results."""
    results = compute()
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    figure_dir.mkdir(parents=True, exist_ok=True)
    with plt.rc_context({"font.size": 10, "svg.fonttype": "none", "svg.hashsalt": "stw-v1"}):
        _save(_train_figure(), figure_dir / "train-takeup-order.svg")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--figures", type=Path, default=FIGURE_DIR)
    arguments = parser.parse_args()
    build(arguments.data, arguments.figures)
