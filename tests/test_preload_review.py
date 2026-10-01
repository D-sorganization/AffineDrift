"""Numerical checks for the declared synthetic Chapter 14 experiment."""

import importlib
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "data/illustrations/preload_transmission_study.npz"


def test_figure_displays_transmitted_history_not_only_commands(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    module = importlib.import_module("make_proximal_distal_companion_expanded_figures")
    figures = []
    monkeypatch.setattr(module, "_save", lambda figure, stem: figures.append(figure))
    module.make_preload()
    try:
        axis = figures[0].axes[0]
        arm = next(line for line in axis.lines if line.get_label() == "Arm Transmitted")
        assert len(arm.get_ydata()) == 3001
        assert arm.get_ydata()[0] == 0
        assert arm.get_ydata()[1800] == pytest.approx(10, abs=0.001)
        assert arm.get_ydata()[-1] == pytest.approx(16, abs=0.01)
        assert axis.get_ylabel() == "Torque (N m)"
    finally:
        plt.close("all")


@pytest.mark.parametrize(
    ("program", "error", "gap", "delay"),
    [
        ("persistent_arm_drive", 0.07171505681942013, [0, 0], [0, 0]),
        ("wrist_to_arm_role_reversal", 0.1954089217169282, [0.0115, 0.022], [0.0157, 0.0311]),
    ],
)
def test_archived_continuous_trace_reproduces_reported_metrics(
    program: str, error: float, gap: list[float], delay: list[float]
) -> None:
    with np.load(ARCHIVE, allow_pickle=False) as data:
        prefix = "continuous_" + program
        time = data[prefix + "_time_s"]
        post = time >= 0
        transmitted = np.column_stack(
            [data[prefix + "_transmitted_" + name + "_torque_nm"] for name in ("arm", "wrist")]
        )
        desired = data[prefix + "_desired_net_torque_nm"]
        assert np.trapezoid(abs(desired[post] - transmitted[post].sum(axis=1)), time[post]) == (
            pytest.approx(error, abs=1e-12)
        )
        np.testing.assert_allclose(
            np.count_nonzero(abs(transmitted[post]) <= 1e-12, axis=0) * 0.0001, gap
        )
        reached = (transmitted[post] * np.array([1, -1])) >= np.array([1.6, 0.6])
        np.testing.assert_allclose(time[post][np.argmax(reached, axis=0)], delay)


def test_same_time_constant_is_required_for_allocation_independent_net_response() -> None:
    time = np.linspace(0, 0.12, 1201)[:, None]
    target = np.array([16, -6])
    persistent = np.array([10, -4])
    reversal = np.array([-4, 10])
    common = np.exp(-time / 0.018)
    first = target + (persistent - target) * common
    second = target + (reversal - target) * common
    np.testing.assert_allclose(first.sum(axis=1), second.sum(axis=1), atol=1e-14)
    unequal = np.exp(-time / np.array([0.018, 0.036]))
    difference = ((persistent - reversal) * unequal).sum(axis=1)
    assert abs(difference[180]) > 3.3
    assert np.max(abs(first - second)) == pytest.approx(14)


def test_same_moment_does_not_imply_same_force_or_work() -> None:
    positions = np.array([[0.1, 0, 0], [-0.1, 0, 0]])
    couple = np.array([[0, 40, 0], [0, -40, 0]])
    plus_common_force = couple + np.array([0, 10, 0])
    for forces in (couple, plus_common_force):
        np.testing.assert_allclose(np.cross(positions, forces).sum(axis=0), [0, 0, 8])
    np.testing.assert_allclose(couple.sum(axis=0), [0, 0, 0])
    np.testing.assert_allclose(plus_common_force.sum(axis=0), [0, 20, 0])
    assert plus_common_force.sum(axis=0) @ np.array([0, 1, 0]) == 20


def test_zero_net_torque_can_retain_positive_restoring_stiffness() -> None:
    # Two opposed, preloaded linear torsional elements near theta=0.
    theta = np.array([-0.001, 0, 0.001])
    first = 5 - 100 * theta
    second = -5 - 100 * theta
    net = first + second
    assert net[1] == 0
    assert np.all(abs(first) > 4.8) and np.all(abs(second) > 4.8)
    np.testing.assert_allclose(-np.gradient(net, theta), 200)
