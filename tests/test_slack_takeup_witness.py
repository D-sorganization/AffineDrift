"""Contract tests for the "Slack Take-Up as a Witness" study, its data and figures (#5136)."""

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from src.tools import slack_takeup_counting as counting
from src.tools import slack_takeup_witness as witness

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ("train-takeup-order",)


@pytest.fixture(scope="module")
def rebuilt(tmp_path_factory: pytest.TempPathFactory) -> tuple[dict[str, Any], Path]:
    """Run the builder once into a temporary directory."""
    from scripts.build_slack_takeup_witness import build

    target = tmp_path_factory.mktemp("stw")
    return build(target / "results.json", target), target


def test_first_takeup_of_a_front_driven_train_matches_the_closed_form() -> None:
    """Before any coupler engages, the front car under force F closes gap g at sqrt(2 m g / F)."""
    ones = np.ones((1, witness.TRAIN_CARS - 1))
    forces = np.zeros((1, witness.TRAIN_CARS))
    forces[0, 0] = witness.TRAIN_DRIVE
    chain = witness.Chain(
        np.ones(witness.TRAIN_CARS),
        forces,
        ones * witness.TRAIN_GAP,
        ones * witness.TRAIN_STIFFNESS,
        0.0 * ones,
        witness.TRAIN_DAMPING,
    )
    events, _ = witness.simulate(chain, witness.TRAIN_CLOCK)
    expected = math.sqrt(2 * witness.TRAIN_GAP / witness.TRAIN_DRIVE)
    assert events[0, 0] == pytest.approx(expected, rel=5e-3)
    assert np.all(np.diff(events[0]) > 0)


def test_invalid_chains_are_rejected() -> None:
    """Shapes and signs are checked before integration."""
    good = witness.Chain(np.ones(2), np.ones((1, 2)), np.ones((1, 1)), np.ones((1, 1)),
                         np.zeros((1, 1)), 0.0)  # fmt: skip
    with pytest.raises(ValueError, match="stiffness"):
        witness.simulate(witness.Chain(**{**good.__dict__, "stiffness": -np.ones((1, 1))}),
                         witness.TRAIN_CLOCK)  # fmt: skip
    with pytest.raises(ValueError, match="step"):
        witness.simulate(good, witness.Clock(step=2.0, horizon=1.0))
    assert witness.wilson_interval(8, 10) == pytest.approx((0.4902, 0.9433), abs=1e-4)


def test_grasp_channel_counts_are_exact() -> None:
    """Couple-axis slack misses only axial squeeze; force-axis slack misses the three couples."""
    table = {row["channel"]: row for row in counting.grasp_visibility()}
    assert table["couple-axis slack, both hands"]["hidden"] == ["axial squeeze"]
    assert table["force-axis slack, both hands"]["hidden"] == list(counting.SPLIT_NAMES[3:])
    assert [row["nullity"] for row in table.values()] == [6, 3, 1, 5, 1, 0]
    couples = table["couple-axis slack, both hands"]
    assert couples["column_norms"][0] == 0.0
    assert couples["norm_spread"] == pytest.approx(1 / counting.GRIP_HALF_SEPARATION)


def _assert_close(expected: Any, actual: Any, path: str = "") -> None:
    """Recursive equality with a roundoff tolerance on floats."""
    if isinstance(expected, dict):
        assert expected.keys() == actual.keys(), path
        for key in expected:
            _assert_close(expected[key], actual[key], f"{path}.{key}")
    elif isinstance(expected, list):
        assert len(expected) == len(actual), path
        for index, (left, right) in enumerate(zip(expected, actual, strict=True)):
            _assert_close(left, right, f"{path}[{index}]")
    elif isinstance(expected, float):
        assert actual == pytest.approx(expected, rel=1e-9, abs=1e-12), path
    else:
        assert expected == actual, path


def test_committed_results_and_figures_regenerate(rebuilt: tuple[dict[str, Any], Path]) -> None:
    """The JSON matches a fresh run numerically and every SVG is byte-identical."""
    results, target = rebuilt
    committed = json.loads((ROOT / "data/slack_takeup_witness/results.json").read_text())
    _assert_close(committed, json.loads(json.dumps(results)))
    for name in FIGURES:
        published = ROOT / f"articles/figures/slack_takeup_witness/{name}.svg"
        assert (
            target / f"{name}.svg"
        ).read_bytes() == published.read_bytes(), (
            f"{name}.svg is stale; run python -m scripts.build_slack_takeup_witness"
        )
