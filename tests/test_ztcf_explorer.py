"""Python reference for the WEB-06.4 ZTCF counterfactual explorer (#4534).

The explorer integrates one declared torque-driven run from the registered
fixture state, branches a zero-torque counterfactual from the actual state at a
chosen intervention step, and reports the simulated terminal difference. Every
branch is replayed through ``execute_ztcf_intervention`` as a postcondition.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from src.affine_control.ztcf_contract import execute_ztcf_intervention
from src.affine_control.ztcf_explorer import (
    DECLARED_TORQUE,
    HORIZON,
    STEPS,
    branch_intervention,
    explore,
    load_fixture,
)


def test_declared_scenario_keeps_the_fixture_step_size() -> None:
    fixture = load_fixture()
    fixture_dt = (
        fixture.integration.end_time - fixture.integration.start_time
    ) / fixture.integration.steps
    assert math.isclose(HORIZON / STEPS, fixture_dt, rel_tol=1e-12)
    assert len(DECLARED_TORQUE) == 3


def test_branch_starts_from_the_actual_state_at_the_intervention() -> None:
    run = explore(intervention_step=50)
    t, q, qd, _ = run.actual[50]
    t0, q0, qd0, _ = run.branch[0]
    assert t0 == t
    assert np.array_equal(q0, q) and np.array_equal(qd0, qd)
    assert len(run.branch) == STEPS - 50 + 1
    assert math.isclose(run.branch[-1][0], HORIZON, rel_tol=1e-12)


def test_branch_record_is_a_valid_contract_replay_of_the_branch() -> None:
    run = explore(intervention_step=120)
    t_i, q_i, qd_i, _ = run.actual[120]
    _, q, qd, speed = run.branch[-1]
    record = run.record
    assert record.state.q == tuple(float(v) for v in q_i)
    assert record.state.qd == tuple(float(v) for v in qd_i)
    assert record.integration.start_time == t_i
    assert record.integration.end_time == HORIZON
    assert record.integration.steps == STEPS - 120
    terminal = execute_ztcf_intervention(record)
    assert terminal == record.expected
    assert terminal.q == tuple(float(v) for v in q)
    assert terminal.qd == tuple(float(v) for v in qd)
    assert terminal.clubhead_speed == speed


def test_branch_record_names_its_source_fixture() -> None:
    record = explore(intervention_step=10).record
    assert record.intervention_id.startswith(load_fixture().intervention_id)
    assert record.interpretation == load_fixture().interpretation


def test_branch_intervention_rejects_a_mismatched_expected_result() -> None:
    fixture = load_fixture()
    assert fixture.expected is not None
    with pytest.raises(ValueError, match="replay"):
        branch_intervention(fixture, 0, fixture.state.q, fixture.state.qd, fixture.expected)


def test_difference_is_actual_minus_counterfactual_at_the_horizon() -> None:
    run = explore(intervention_step=0)
    _, q_actual, qd_actual, speed_actual = run.actual[-1]
    _, q_branch, qd_branch, speed_branch = run.branch[-1]
    assert np.array_equal(run.difference.q, q_actual - q_branch)
    assert np.array_equal(run.difference.qd, qd_actual - qd_branch)
    assert run.difference.clubhead_speed == speed_actual - speed_branch


def test_zero_declared_torque_leaves_no_difference() -> None:
    run = explore(intervention_step=0, torque=(0.0, 0.0, 0.0))
    assert np.array_equal(run.difference.q, np.zeros(3))
    assert run.difference.clubhead_speed == 0.0


def test_fixture_replay_reproduces_the_registered_terminal_state() -> None:
    fixture = load_fixture()
    assert fixture.expected is not None
    terminal = execute_ztcf_intervention(fixture)
    tolerance = fixture.integration.absolute_tolerance
    assert np.allclose(terminal.q, fixture.expected.q, rtol=0.0, atol=tolerance)
    assert math.isclose(terminal.clubhead_speed, fixture.expected.clubhead_speed, abs_tol=tolerance)


@pytest.mark.parametrize("step", [-1, STEPS, 2.5])
def test_rejects_an_intervention_step_outside_the_run(step: int) -> None:
    with pytest.raises(ValueError, match="intervention_step"):
        explore(intervention_step=step)


def test_rejects_a_non_finite_or_misshapen_torque() -> None:
    with pytest.raises(ValueError, match="torque"):
        explore(intervention_step=0, torque=(float("nan"), 0.0, 0.0))
    with pytest.raises(ValueError, match="torque"):
        explore(intervention_step=0, torque=(1.0, 2.0))
