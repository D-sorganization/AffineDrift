"""Tests for the slack-representation model and studies behind #5135."""

from __future__ import annotations

import numpy as np
import pytest

from scripts.build_null_space_exploration_examples import render_document
from scripts.build_slack_management_data import DATA, build_document
from src.tools.slack_management_studies import (
    PUBLISHED_IMPULSES_NMS,
    REPRESENTATIONS,
    reproduction_section,
    unequal_lag_section,
)
from src.tools.slack_transmission import (
    PERSISTENT,
    ROLE_REVERSAL,
    Horizon,
    Program,
    Representation,
    Shape,
    channel_torque,
    command_deflection,
    play_operator,
    preparation_split,
    relative_advantage,
    simulate,
)

DEAD_ZONE = Representation("dead_zone", Shape.DEAD_ZONE, 0.012)
SMOOTH = Representation("smooth", Shape.SMOOTH, 0.012)
PUBLISHED_WINDOW = Horizon(duration_s=0.12)


def test_reproduces_published_dead_zone_impulses() -> None:
    section = reproduction_section()
    assert section["max_abs_deviation_nms"] < 1e-12
    assert section["reproduced_nms"].keys() == PUBLISHED_IMPULSES_NMS.keys()
    verdicts = {"persistent_favoured": 9, "equivalent": 3, "reversal_favoured": 0}
    assert section["grid_verdicts"] == verdicts


def test_reproduces_published_zero_transmission_and_delays() -> None:
    trace = simulate(ROLE_REVERSAL, DEAD_ZONE, grid=PUBLISHED_WINDOW)
    assert trace.zero_transmission_s == pytest.approx((0.0115, 0.0220), abs=1e-12)
    assert trace.recovery_delay_s == pytest.approx((0.0157, 0.0311), abs=1e-12)
    persistent = simulate(PERSISTENT, DEAD_ZONE, grid=PUBLISHED_WINDOW)
    assert persistent.zero_transmission_s == (0.0, 0.0)


@pytest.mark.parametrize("activation_lag", [0.0, 0.004, 0.010, 0.030])
@pytest.mark.parametrize("time_constant", [0.008, 0.018, 0.035])
def test_shared_linear_channels_cannot_separate_programs(
    activation_lag: float, time_constant: float
) -> None:
    rep = Representation("linear", Shape.DEAD_ZONE, 0.0, time_constant, 600.0, activation_lag)
    assert abs(relative_advantage(rep)) < 1e-12


def test_unequal_lags_separate_programs_without_any_gap() -> None:
    section = unequal_lag_section()
    assert section["exact_min_difference_nm"] == pytest.approx(-3.5, abs=1e-12)
    assert section["exact_min_time_s"] == pytest.approx(0.036 * np.log(2.0), abs=1e-15)
    assert section["simulated_min_difference_nm"] == pytest.approx(-3.5, abs=0.01)
    assert relative_advantage(REPRESENTATIONS[-1]) > 1.0


def test_dead_zone_and_smooth_both_favour_persistent_direction() -> None:
    assert relative_advantage(DEAD_ZONE) > 1.0
    assert relative_advantage(SMOOTH) > 1.0
    smooth_reversal = simulate(ROLE_REVERSAL, SMOOTH)
    assert smooth_reversal.zero_transmission_s == (0.0, 0.0)


def test_smooth_characteristic_is_odd_monotone_and_soft_at_zero() -> None:
    deflection = np.linspace(-0.05, 0.05, 2001)
    torque = channel_torque(deflection, SMOOTH)
    np.testing.assert_allclose(torque, -torque[::-1], atol=1e-12)
    assert np.all(np.diff(torque) > 0.0)
    small = channel_torque(np.array([1e-6]), SMOOTH)[0]
    assert small / 1e-6 < 1e-3 * SMOOTH.stiffness_nm_rad


@pytest.mark.parametrize("rep", [DEAD_ZONE, SMOOTH, REPRESENTATIONS[0]])
@pytest.mark.parametrize("torque", [-16.0, -0.5, 0.0, 3.0, 30.0])
def test_command_deflection_inverts_characteristic(rep: Representation, torque: float) -> None:
    deflection = command_deflection(torque, rep)
    assert channel_torque(np.array([deflection]), rep)[0] == pytest.approx(torque, abs=1e-9)


def test_play_operator_has_memory_and_reduces_to_identity_without_gap() -> None:
    position = np.array([0.0, 0.02, 0.0, -0.02, 0.0])
    output = play_operator(position, 0.01)
    assert (
        output[0] == 0.0 and output[2] == pytest.approx(0.01) and output[4] == pytest.approx(-0.01)
    )
    np.testing.assert_array_equal(play_operator(position, 0.0), position)
    with pytest.raises(ValueError):
        play_operator(position, -1.0)


def test_preparation_split_keeps_net_and_recovers_persistent_program() -> None:
    assert preparation_split(0.0).pre_nm == ROLE_REVERSAL.pre_nm
    assert preparation_split(14.0).pre_nm == PERSISTENT.pre_nm
    assert all(sum(preparation_split(c).pre_nm) == 6.0 for c in np.arange(0.0, 25.0))


def test_overshoot_appears_only_when_the_reversing_channel_starts_unloaded() -> None:
    assert simulate(preparation_split(8.0), DEAD_ZONE).peak_overshoot_nm > 1.0
    assert simulate(PERSISTENT, DEAD_ZONE).peak_overshoot_nm == 0.0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"name": "", "shape": Shape.DEAD_ZONE, "dead_zone_rad": 0.0},
        {"name": "x", "shape": Shape.DEAD_ZONE, "dead_zone_rad": -0.1},
        {"name": "x", "shape": Shape.DEAD_ZONE, "dead_zone_rad": 0.0, "time_constant_s": 0.0},
        {"name": "x", "shape": Shape.SMOOTH, "dead_zone_rad": 0.0, "stiffness_nm_rad": np.inf},
        {"name": "x", "shape": Shape.SMOOTH, "dead_zone_rad": 0.0, "wrist_time_constant_s": -1.0},
    ],
)
def test_representation_rejects_invalid_parameters(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        Representation(**kwargs)  # type: ignore[arg-type]


def test_program_and_horizon_reject_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        Program("bad", (np.nan, 0.0), (0.0, 0.0))
    with pytest.raises(ValueError):
        Horizon(duration_s=0.01, step_s=0.1)


def test_committed_results_match_a_fresh_build() -> None:
    committed = DATA.read_text(encoding="utf-8")
    assert render_document(build_document()) == committed
