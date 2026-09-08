"""Checked local charts and planar kinematics for the configuration-space chapter."""

import numpy as np
from numpy.typing import NDArray

type Array = NDArray[np.float64]
ROUND_OFF_TOLERANCE = 1e-12


def _chain(lengths: Array, angles: Array) -> tuple[Array, Array]:
    """Normalize a nonempty planar serial chain with positive finite lengths."""
    lengths, angles = np.asarray(lengths, dtype=float), np.asarray(angles, dtype=float)
    if lengths.ndim != 1 or not lengths.size or lengths.shape != angles.shape:
        raise ValueError("lengths and angles must be matching nonempty vectors")
    if not np.isfinite(lengths).all() or not np.isfinite(angles).all() or np.any(lengths <= 0):
        raise ValueError("lengths must be positive and all coordinates finite")
    return lengths, np.cumsum(angles)


def planar_pose(lengths: Array, angles: Array) -> Array:
    """Return endpoint x, y and an unwrapped local final-link angle.

    Args:
        lengths: Positive link lengths in metres.
        angles: Relative revolute joint angles in radians.

    Returns:
        A planar pose coordinate vector; angle equivalence is modulo 2*pi.
    """
    lengths, absolute = _chain(lengths, angles)
    return np.array([lengths @ np.cos(absolute), lengths @ np.sin(absolute), absolute[-1]])


def planar_jacobian(lengths: Array, angles: Array) -> Array:
    """Return the local derivative of planar_pose, with shape (3, number of joints).

    Args:
        lengths: Positive link lengths in metres.
        angles: Relative joint angles in radians.

    Returns:
        Position rows in metres per radian and an angular-rate row of ones.
        Singular values mixing these rows require an explicit task metric.
    """
    lengths, absolute = _chain(lengths, angles)
    x_derivative = -np.cumsum((lengths * np.sin(absolute))[::-1])[::-1]
    y_derivative = np.cumsum((lengths * np.cos(absolute))[::-1])[::-1]
    return np.vstack((x_derivative, y_derivative, np.ones(lengths.size)))


def inverse_two_link(lengths: Array, target: Array) -> tuple[Array, Array]:
    """Return both inverse branches of an unlimited planar 2R position task.

    Args:
        lengths: Two positive link lengths in metres.
        target: Desired endpoint position (x, y) in metres.

    Returns:
        Elbow-positive and elbow-negative branches, coinciding modulo 2*pi at
        ordinary workspace boundaries. Equal links at the origin instead raise
        ValueError because the inverse is a continuous family.
    """
    lengths, _ = _chain(lengths, np.zeros(2))
    target = np.asarray(target, dtype=float)
    if target.shape != (2,) or not np.isfinite(target).all():
        raise ValueError("target must be a finite planar position")
    if np.linalg.norm(target) == 0 and lengths[0] == lengths[1]:
        raise ValueError("equal links at the origin have a continuous inverse family")
    cosine = (target @ target - lengths @ lengths) / (2 * lengths[0] * lengths[1])
    if abs(cosine) > 1 + ROUND_OFF_TOLERANCE:
        raise ValueError("target is unreachable for the stated link lengths")
    cosine = float(np.clip(cosine, -1, 1))
    sine = np.sqrt(max(0.0, 1 - cosine**2))
    heading = np.arctan2(target[1], target[0])
    solutions = []
    for signed_sine in (sine, -sine):
        elbow = np.arctan2(signed_sine, cosine)
        shoulder = heading - np.arctan2(lengths[1] * signed_sine, lengths[0] + lengths[1] * cosine)
        solutions.append(np.array([shoulder, elbow]))
    return solutions[0], solutions[1]


def circle_point(coordinate: float, omitted_pole: int) -> Array:
    """Map a stereographic coordinate to the unit circle.

    Args:
        coordinate: Finite chart coordinate.
        omitted_pole: +1 omits (0, 1); -1 omits (0, -1).

    Returns:
        Circle point (x, y). Very large coordinates approach the omitted pole;
        floating-point roundoff can then prevent accurate inverse recovery.
    """
    if omitted_pole not in (-1, 1) or not np.isfinite(coordinate):
        raise ValueError("use a finite coordinate and omitted pole +1 or -1")
    # Reciprocal scaling avoids overflow from squaring a large coordinate.
    if abs(coordinate) > 1:
        reciprocal = 1 / coordinate
        return np.array([2 * reciprocal, omitted_pole * (1 - reciprocal**2)]) / (1 + reciprocal**2)
    return np.array([2 * coordinate, omitted_pole * (coordinate**2 - 1)]) / (1 + coordinate**2)


def circle_coordinate(point: Array, omitted_pole: int) -> float:
    """Project a unit-circle point away from the specified pole.

    Args:
        point: Finite Cartesian point (x, y) on the unit circle.
        omitted_pole: +1 for x/(1-y), -1 for x/(1+y).

    Returns:
        Local chart coordinate; an omitted pole or off-circle point is rejected.
    """
    point = np.asarray(point, dtype=float)
    if point.shape != (2,) or not np.isfinite(point).all() or omitted_pole not in (-1, 1):
        raise ValueError("use a finite planar point and pole +1 or -1")
    if not np.isclose(point @ point, 1, atol=ROUND_OFF_TOLERANCE, rtol=0):
        raise ValueError("point must lie on the unit circle")
    denominator = 1 - omitted_pole * point[1]
    if denominator <= 0:
        raise ValueError("the omitted pole has no coordinate in this chart")
    return float(point[0] / denominator)


def unicycle_step(state: Array, speed: float, turn_rate: float, duration: float) -> Array:
    """Integrate the ideal independently driven unicycle for constant inputs.

    Args:
        state: Planar x, y and unwrapped heading.
        speed: Signed forward speed.
        turn_rate: Independently commanded heading rate.
        duration: Nonnegative step duration.

    Returns:
        Exact constant-input endpoint up to floating-point error. This kinematic
        model omits car steering limits, acceleration limits and contact forces.
    """
    state = np.asarray(state, dtype=float)
    if state.shape != (3,) or not np.isfinite(state).all():
        raise ValueError("state must be a finite three-vector")
    if not np.isfinite([speed, turn_rate, duration]).all() or duration < 0:
        raise ValueError("inputs must be finite and duration nonnegative")
    angle = turn_rate * duration
    distance = speed * duration * np.sinc(angle / (2 * np.pi))
    midpoint = state[2] + angle / 2
    return state + np.array([distance * np.cos(midpoint), distance * np.sin(midpoint), angle])
