"""Python parity with the shared momentum and energy ledger fixture (#5886).

Expected values are closed form. The browser mirror is checked by
``tests/momentum-energy-ledger-parity.test.js`` against this same file.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.affine_control.momentum_energy_ledger import (
    advance_constant_wrench,
    segment_ledger,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "momentum_energy_ledger_analytic.json"
FIXTURE = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
_SPINNING = FIXTURE["ledgers"][0]["state"]


def _close(actual: float, expected: float, tolerance: dict[str, float], label: str) -> None:
    bound = tolerance["abs"] + tolerance["rel"] * abs(expected)
    gap = abs(actual - expected)
    assert gap <= bound, f"{label}: |{actual} - {expected}| = {gap} > {bound}"


def _close_record(
    actual: dict[str, float],
    expected: dict[str, float],
    tolerance: dict[str, float],
    label: str,
) -> None:
    assert set(actual) == set(expected), label
    for key, value in expected.items():
        _close(actual[key], value, tolerance, f"{label}.{key}")


def test_fixture_declares_the_analytic_schema() -> None:
    assert FIXTURE["schema"] == "affinedrift/momentum-energy-ledger-analytic/v1"
    assert FIXTURE["tolerance"] == {"abs": 1e-12, "rel": 1e-12}


def test_analytic_ledgers_match_the_shared_fixture() -> None:
    tolerance = FIXTURE["tolerance"]
    for case in FIXTURE["ledgers"]:
        actual = segment_ledger(case["state"], FIXTURE["gravity"])
        _close_record(actual, case["expected"], tolerance, case["id"])


def test_analytic_intervals_match_the_shared_fixture() -> None:
    tolerance = FIXTURE["tolerance"]
    gravity = FIXTURE["gravity"]
    for case in FIXTURE["intervals"]:
        advanced = advance_constant_wrench(
            case["state"], case["wrench"], gravity, case["duration"]
        )
        label = case["id"]
        _close_record(advanced["final_state"], case["expected_state"], tolerance, label)
        final = segment_ledger(advanced["final_state"], gravity)
        _close_record(final, case["expected_ledger"], tolerance, f"{label}.ledger")
        _close_record(advanced["balance"], case["expected_balance"], tolerance, f"{label}.balance")


@pytest.mark.parametrize(
    ("state", "gravity", "message"),
    [
        ({**_SPINNING, "mass": 0.0}, 10.0, "mass must be positive"),
        ({**_SPINNING, "inertia_about_com": -0.1}, 10.0, "inertia_about_com must be non-negative"),
        (_SPINNING, -1.0, "gravity must be non-negative"),
        ({**_SPINNING, "mass": True}, 10.0, "state.mass must be a finite number"),
        ("segment", 10.0, "state must be an object"),
    ],
)
def test_ledger_rejects_invalid_inputs(state: object, gravity: float, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        segment_ledger(state, gravity)


def test_interval_rejects_zero_duration_and_torque_on_a_point_mass() -> None:
    point = FIXTURE["ledgers"][1]["state"]
    wrench = {"force_x": 0.0, "force_y": 0.0, "torque_about_com": 0.0}
    with pytest.raises(ValueError, match="duration must be positive"):
        advance_constant_wrench(point, wrench, FIXTURE["gravity"], 0.0)
    with pytest.raises(ValueError, match="torque_about_com requires positive inertia"):
        advance_constant_wrench(
            point,
            {**wrench, "torque_about_com": 1.0},
            FIXTURE["gravity"],
            0.2,
        )
