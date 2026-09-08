"""Independent checks of configuration charts, kinematics and reachable motion."""

import importlib

import numpy as np
import pytest


@pytest.fixture
def examples():
    """Load the chapter implementation after the independent expectations exist."""
    return importlib.import_module("src.tools.configuration_examples")


@pytest.mark.parametrize("angles", [(0.2, 0.8), (-1.0, -0.7), (0.0, 0.0)])
def test_inverse_recovers_both_physical_branches(examples, angles):
    """Inverse solutions close the triangle, including its extended boundary."""
    lengths = np.array([1.4, 0.8])
    first, second = angles
    target = lengths[0] * np.array([np.cos(first), np.sin(first)])
    target += lengths[1] * np.array([np.cos(first + second), np.sin(first + second)])
    solutions = examples.inverse_two_link(lengths, target)
    for solution in solutions:
        np.testing.assert_allclose(examples.planar_pose(lengths, solution)[:2], target, atol=1e-12)
    assert np.sign(solutions[0][1]) == -np.sign(solutions[1][1])


@pytest.mark.parametrize("target", [(3.1, 0.0), (0.2, 0.0)])
def test_unreachable_target_is_rejected(examples, target):
    """Neither side of the analytic reachable annulus can be ignored."""
    with pytest.raises(ValueError, match="unreachable"):
        examples.inverse_two_link(np.array([2.0, 1.0]), np.array(target))


def test_equal_link_origin_has_continuous_inverse_family(examples):
    """Two returned isolated branches would misrepresent a folded equal-link arm."""
    with pytest.raises(ValueError, match="continuous"):
        examples.inverse_two_link(np.ones(2), np.zeros(2))
    for shoulder in np.linspace(-np.pi, np.pi, 9):
        pose = examples.planar_pose(np.ones(2), np.array([shoulder, np.pi]))
        np.testing.assert_allclose(pose[:2], 0, atol=1e-14)
        assert pose[2] == pytest.approx(shoulder + np.pi)


@pytest.mark.parametrize("angles", [(0.2, 0.7, -0.3), (0.0, 0.0, 0.0)])
def test_planar_pose_jacobian_by_finite_differences(examples, angles):
    """Check the task derivative separately from its closed-form implementation."""
    lengths = np.array([1.0, 0.8, 0.5])
    angles = np.array(angles)
    step = 1e-6
    finite = np.column_stack(
        [
            (
                examples.planar_pose(lengths, angles + step * direction)
                - examples.planar_pose(lengths, angles - step * direction)
            )
            / (2 * step)
            for direction in np.eye(3)
        ]
    )
    np.testing.assert_allclose(examples.planar_jacobian(lengths, angles), finite, atol=1e-9)


def test_position_determinant_and_singular_direction(examples):
    """A straight arm loses radial velocity, not its configuration dimension."""
    lengths = np.array([2.0, 1.0])
    for elbow in [0.0, 0.3, -1.2, np.pi]:
        jacobian = examples.planar_jacobian(lengths, np.array([0.4, elbow]))[:2]
        assert np.linalg.det(jacobian) == pytest.approx(2 * np.sin(elbow), abs=1e-14)
    jacobian = examples.planar_jacobian(lengths, np.zeros(2))[:2]
    np.testing.assert_allclose(jacobian, [[0, 0], [3, 1]])
    assert np.linalg.matrix_rank(jacobian) == 1


@pytest.mark.parametrize("pole", [-1, 1])
@pytest.mark.parametrize("coordinate", [-3.0, -0.4, 0.0, 2.0])
def test_stereographic_chart_has_inverse_and_unit_norm(examples, pole, coordinate):
    """Both charts cover their omitted-pole complements with unique points."""
    point = examples.circle_point(coordinate, pole)
    assert point @ point == pytest.approx(1.0)
    assert examples.circle_coordinate(point, pole) == pytest.approx(coordinate)


def test_chart_transition_and_velocity_chain_rule(examples):
    """Coordinate velocities transform; their raw numbers need not agree."""
    coordinate, velocity = 0.7, 1.3
    point = examples.circle_point(coordinate, 1)
    other = examples.circle_coordinate(point, -1)
    assert other == pytest.approx(1 / coordinate)
    step = 1e-6
    before = examples.circle_coordinate(examples.circle_point(coordinate - step * velocity, 1), -1)
    after = examples.circle_coordinate(examples.circle_point(coordinate + step * velocity, 1), -1)
    assert (after - before) / (2 * step) == pytest.approx(-velocity / coordinate**2, rel=1e-9)


def test_omitted_pole_and_invalid_circle_inputs(examples):
    """An invalid chart must fail explicitly instead of masquerading as coordinates."""
    for point, pole in [(np.array([0.0, 1.0]), 1), (np.array([2.0, 0.0]), -1)]:
        with pytest.raises(ValueError):
            examples.circle_coordinate(point, pole)
    with pytest.raises(ValueError):
        examples.circle_point(1.0, 0)


def test_unicycle_commutator_sign_and_order(examples):
    """Exact motions give epsilon squared times [forward, rotation]."""
    initial = np.array([0.2, -0.3, 0.4])
    bracket = np.array([np.sin(initial[2]), -np.cos(initial[2]), 0.0])
    errors = []
    for step in [0.02, 0.01, 0.005]:
        state = initial.copy()
        for speed, turn in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            state = examples.unicycle_step(state, speed, turn, step)
        errors.append(np.linalg.norm((state - initial) / step**2 - bracket))
    assert errors[1] / errors[0] == pytest.approx(0.5, rel=0.001)
    assert errors[2] / errors[1] == pytest.approx(0.5, rel=0.001)


def test_constant_unicycle_turn_matches_circle_geometry(examples):
    """The exact integration includes simultaneous translation and rotation."""
    result = examples.unicycle_step(np.zeros(3), 2.0, 1.0, np.pi / 2)
    np.testing.assert_allclose(result, [2, 2, np.pi / 2], atol=1e-14)


def test_nonintegrability_does_not_imply_full_bracket_rank():
    """The R4 counterexample generates z motion but never changes w."""
    first = np.array([1.0, 0, 0, 0])
    second = np.array([0, 1.0, 0.7, 0])
    bracket = np.array([0, 0, 1.0, 0])
    assert np.linalg.matrix_rank(np.column_stack([first, second])) == 2
    assert np.linalg.matrix_rank(np.column_stack([first, second, bracket])) == 3
    assert np.all(np.column_stack([first, second, bracket])[3] == 0)


@pytest.mark.parametrize("lengths,angles", [([0, 1], [0, 0]), ([1, 1], [0]), ([], [])])
def test_invalid_link_model_is_rejected(examples, lengths, angles):
    """The model boundary requires positive lengths and matching finite coordinates."""
    with pytest.raises(ValueError):
        examples.planar_pose(np.array(lengths), np.array(angles))


@pytest.mark.parametrize("target", [np.zeros(3), np.array([np.nan, 0])])
def test_inverse_rejects_invalid_task_coordinates(examples, target):
    """A task with the wrong dimension or nonfinite entries is not an IK target."""
    with pytest.raises(ValueError, match="finite planar"):
        examples.inverse_two_link(np.ones(2), target)


@pytest.mark.parametrize("point,pole", [(np.zeros(3), 1), (np.ones(2), 0)])
def test_circle_projection_rejects_invalid_representation(examples, point, pole):
    """The chart boundary requires the declared ambient dimension and pole."""
    with pytest.raises(ValueError, match="finite planar"):
        examples.circle_coordinate(point, pole)


@pytest.mark.parametrize("state", [np.zeros(2), np.array([0, np.inf, 0])])
def test_unicycle_rejects_invalid_state(examples, state):
    """Invalid states must not propagate silent nonphysical trajectories."""
    with pytest.raises(ValueError, match="finite three-vector"):
        examples.unicycle_step(state, 1.0, 0.0, 0.1)


@pytest.mark.parametrize("speed,duration", [(np.inf, 0.1), (1.0, -0.1)])
def test_unicycle_rejects_invalid_input_interval(examples, speed, duration):
    """Signed speed is allowed; nonfinite inputs and negative elapsed time are not."""
    with pytest.raises(ValueError, match="duration nonnegative"):
        examples.unicycle_step(np.zeros(3), speed, 0.0, duration)
