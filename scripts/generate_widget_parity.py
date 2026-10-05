"""Generate or verify widget parity fixtures (``affinedrift/widget-parity/v1``).

ADR 0002 section 6: each browser widget that mirrors ``src/`` code is checked
against golden vectors computed by the Python reference. This script owns those
files under ``tests/fixtures/widgets/``; ``--check`` fails when a committed
fixture differs from a fresh in-memory regeneration.

Usage::

    python -m scripts.generate_widget_parity          # rewrite every fixture
    python -m scripts.generate_widget_parity --check  # fail if any is stale
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from src.affine_control.double_pendulum_affine import (
    DoublePendulumParams,
    affine_split,
    generalized_torque,
    simulate,
    tip_acceleration_split,
)

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "widgets"
SCHEMA = "affinedrift/widget-parity/v1"
GENERATOR = "python -m scripts.generate_widget_parity"
#: ADR 0002 tolerance policy: closed-form ports 1e-12, integrated results 1e-9.
CLOSED_FORM = {"abs": 1e-12, "rel": 1e-12}
INTEGRATED = {"abs": 1e-9, "rel": 1e-9}


@dataclass(frozen=True)
class WidgetSpec:
    """One widget: its id, cited Python source, and case builder."""

    widget: str
    source_path: str
    source_function: str
    build_cases: Callable[[], list[dict[str, Any]]]


def _floats(values: Any) -> Any:
    """Convert numpy scalars and arrays to plain JSON numbers."""
    return np.asarray(values, dtype=float).tolist()


# --------------------------------------------------------------------------
# drift-control-sandbox (WEB-06.3, #4533)
# --------------------------------------------------------------------------

#: Declared illustrative parameters shared with js/drift-control-sandbox.js.
SANDBOX_PARAMS = {"m1": 7.0, "m2": 0.6, "l1": 0.75, "l2": 1.1, "gravity": 9.81}
SANDBOX_HORIZON = 0.5
SANDBOX_STEPS = 500
SANDBOX_SAMPLE_EVERY = 25
#: Widget presets: start at rest at the top of a declared downswing.
SANDBOX_PRESETS = {
    "zero-torque": {"shoulder": 0.0, "wrist": 0.0},
    "shoulder-drive": {"shoulder": -20.0, "wrist": 0.0},
    "shoulder-and-wrist": {"shoulder": -20.0, "wrist": -3.0},
}
SANDBOX_Q0 = [2.6, 4.2]
SANDBOX_QD0 = [0.0, 0.0]
SPLIT_STATES = [
    {"q": [2.3, 3.6], "qd": [-1.5, 2.0], "shoulder": -25.0, "wrist": 3.0},
    {"q": [0.4, -0.2], "qd": [3.0, -4.5], "shoulder": 10.0, "wrist": -2.0},
]


def _sandbox_split_case(case_id: str, state: dict[str, Any]) -> dict[str, Any]:
    params = DoublePendulumParams(**SANDBOX_PARAMS)
    torque = generalized_torque(state["shoulder"], state["wrist"])
    drift, input_qdd = affine_split(state["q"], state["qd"], torque, params)
    tip_drift, tip_input = tip_acceleration_split(state["q"], state["qd"], drift, input_qdd, params)
    return {
        "id": case_id,
        "inputs": {"params": SANDBOX_PARAMS, **state},
        "expected": {
            "torque": _floats(torque),
            "drift_qdd": _floats(drift),
            "input_qdd": _floats(input_qdd),
            "tip_drift": _floats(tip_drift),
            "tip_input": _floats(tip_input),
        },
    }


def _sandbox_trajectory_case(preset: str) -> dict[str, Any]:
    params = DoublePendulumParams(**SANDBOX_PARAMS)
    joints = SANDBOX_PRESETS[preset]
    torque = generalized_torque(joints["shoulder"], joints["wrist"])
    samples = simulate(params, SANDBOX_Q0, SANDBOX_QD0, torque, SANDBOX_HORIZON, SANDBOX_STEPS)
    kept = samples[::SANDBOX_SAMPLE_EVERY]
    return {
        "id": f"preset-{preset}",
        "tolerance": INTEGRATED,
        "inputs": {
            "params": SANDBOX_PARAMS,
            "q0": SANDBOX_Q0,
            "qd0": SANDBOX_QD0,
            **joints,
            "horizon": SANDBOX_HORIZON,
            "steps": SANDBOX_STEPS,
            "sample_every": SANDBOX_SAMPLE_EVERY,
        },
        "expected": {
            "t": [s.t for s in kept],
            "q": [_floats(s.q) for s in kept],
            "qd": [_floats(s.qd) for s in kept],
            "drift_qdd": [_floats(s.drift_qdd) for s in kept],
            "input_qdd": [_floats(s.input_qdd) for s in kept],
        },
    }


def _sandbox_cases() -> list[dict[str, Any]]:
    cases = [_sandbox_split_case(f"split-{i}", state) for i, state in enumerate(SPLIT_STATES)]
    return cases + [_sandbox_trajectory_case(preset) for preset in SANDBOX_PRESETS]


WIDGETS: tuple[WidgetSpec, ...] = (
    WidgetSpec(
        widget="drift-control-sandbox",
        source_path="src/affine_control/double_pendulum_affine.py",
        source_function="simulate",
        build_cases=_sandbox_cases,
    ),
)


# --------------------------------------------------------------------------
# Rendering and checking
# --------------------------------------------------------------------------


def fixture_path(spec: WidgetSpec, root: Path = REPO_ROOT) -> Path:
    """Committed location of ``spec``'s fixture."""
    return root / "tests" / "fixtures" / "widgets" / f"{spec.widget}.parity.json"


def render_fixture(spec: WidgetSpec, root: Path = REPO_ROOT) -> str:
    """Return the fixture text for ``spec``, generated from current ``src/``."""
    source = root / spec.source_path
    document = {
        "schema": SCHEMA,
        "widget": spec.widget,
        "source": f"{spec.source_path}::{spec.source_function}",
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "generator": GENERATOR,
        "tolerance": CLOSED_FORM,
        "cases": spec.build_cases(),
    }
    return json.dumps(document, indent=2) + "\n"


def stale_fixtures(root: Path = REPO_ROOT) -> list[str]:
    """Return the widget ids whose committed fixture is missing or stale."""
    stale = []
    for spec in WIDGETS:
        path = fixture_path(spec, root)
        if not path.is_file() or path.read_text(encoding="utf-8") != render_fixture(spec, root):
            stale.append(spec.widget)
    return stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if any fixture is stale")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    if args.check:
        stale = stale_fixtures()
        if stale:
            logger.error("Stale widget parity fixtures (run %s): %s", GENERATOR, stale)
            return 1
        logger.info("Widget parity fixtures are current.")
        return 0
    for spec in WIDGETS:
        path = fixture_path(spec)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_fixture(spec), encoding="utf-8", newline="\n")
        logger.info("Wrote %s", path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
