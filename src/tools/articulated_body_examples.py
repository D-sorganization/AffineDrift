"""Inspectable fixed-base tree dynamics for the articulated-body chapter.

Inputs are prepared at one configuration. Motion is angular-first; each
transform maps parent-frame motion coordinates into the child frame. External
wrenches are moment-first, about and expressed in each child frame. These
smooth rigid-tree calculations do not solve contact, impacts or closed loops.
"""

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from src.affine_control.dynamics import force_cross, motion_cross
from src.core.constants import GRAVITY_M_S2

type Array = NDArray[np.float64]
SYMMETRY_TOLERANCE = 1e-10
SPATIAL_DIMENSION = 6


def _finite(value: Array, shape: tuple[int, ...], name: str) -> Array:
    """Validate a finite array at the calculation boundary."""
    array = np.asarray(value, dtype=float)
    if array.shape != shape or not np.isfinite(array).all():
        raise ValueError(f"{name} must have finite shape {shape}")
    return array


@dataclass(frozen=True)
class PreparedTree:
    """One-DOF joints in parent-before-child order, with -1 denoting the base.

    Args:
        parents: Topologically ordered parent indices.
        transform: Rigid spatial motion transforms, shape (N, 6, 6).
        subspace: Constant local joint motion directions, shape (N, 6).
        inertia: Positive-definite rigid-body spatial inertias, shape (N, 6, 6).

    Physical rigid-body inertias and rigid coordinate transforms are model
    preconditions; shape, symmetry and positive definiteness are checked here.
    A configuration-dependent joint subspace needs additional joint-bias terms
    and is outside this deliberately restricted example.
    """

    parents: tuple[int, ...]
    transform: Array
    subspace: Array
    inertia: Array

    def __post_init__(self) -> None:
        """Reject unordered trees, invalid arrays and singular body inertias."""
        count = len(self.parents)
        if count == 0 or any(not -1 <= parent < child for child, parent in enumerate(self.parents)):
            raise ValueError("parents must precede children; use -1 for a fixed-base joint")
        for name in ("transform", "inertia"):
            value = _finite(getattr(self, name), (count, 6, 6), name)
            object.__setattr__(self, name, value.copy())
        directions = _finite(self.subspace, (count, 6), "subspace")
        if np.any(np.linalg.norm(directions, axis=1) == 0):
            raise ValueError("joint subspaces must be nonzero")
        object.__setattr__(self, "subspace", directions.copy())
        if not np.allclose(
            self.inertia, self.inertia.transpose(0, 2, 1), atol=SYMMETRY_TOLERANCE, rtol=0
        ):
            raise ValueError("body inertias must be symmetric")
        if np.any(np.linalg.eigvalsh(self.inertia) <= 0):
            raise ValueError("body inertias must be positive definite")


@dataclass(frozen=True)
class DynamicsLoads:
    """Joint rates and actuator torques, plus optional SI load parameters.

    Args:
        velocity: Relative joint rates, shape (N,).
        torque: Applied actuator generalized forces, shape (N,).
        external: Body-frame external wrenches; omitted means zero.
        gravity: Physical gravity in the base frame.
        damping: Nonnegative joint viscous coefficients; omitted means zero.
        armature: Nonnegative diagonal reflected joint inertias; omitted means zero.

    Armature denotes the ideal kinetic term sum(a_i*qdot_i**2)/2. It does not
    model general rotor/body inertial coupling or gearbox compliance.
    """

    velocity: Array
    torque: Array
    external: Array | None = None
    gravity: Array = field(default_factory=lambda: np.array([0, -GRAVITY_M_S2, 0]))
    damping: Array | None = None
    armature: Array | None = None


@dataclass(frozen=True)
class _Loads:
    velocity: Array
    effective_torque: Array
    external: Array
    base_acceleration: Array
    damping_force: Array
    armature: Array


def _loads(loads: DynamicsLoads, count: int) -> _Loads:
    """Normalize optional loads and keep force-level damping explicit."""
    velocity = _finite(loads.velocity, (count,), "velocity")
    torque = _finite(loads.torque, (count,), "torque")
    external = np.zeros((count, 6)) if loads.external is None else loads.external
    external = _finite(external, (count, 6), "external")
    gravity = _finite(loads.gravity, (3,), "gravity")
    passive = []
    for name in ("damping", "armature"):
        value = getattr(loads, name)
        parameter = _finite(np.zeros(count) if value is None else value, (count,), name)
        if np.any(parameter < 0):
            raise ValueError(f"{name} must be nonnegative")
        passive.append(parameter)
    damping_force = passive[0] * velocity
    return _Loads(
        velocity,
        torque - damping_force,
        external,
        np.concatenate((np.zeros(3), -gravity)),
        damping_force,
        passive[1],
    )


@dataclass
class ABAResult:
    """Joint accelerations and intermediate arrays for inspecting all three passes.

    Spatial accelerations use the fictitious base acceleration that accounts
    for gravity; they are not ordinary Cartesian accelerometer readings.
    Inertia and bias contain each subtree before its own joint is eliminated.
    """

    joint_acceleration: Array
    velocity: Array
    spatial_acceleration: Array
    inertia: Array
    bias: Array
    pivot: Array
    effort: Array
    direction: Array


def _velocity_bias(tree: PreparedTree, loads: _Loads) -> tuple[Array, Array, Array]:
    """Propagate motion, then form gyroscopic and known external wrenches."""
    velocity = np.zeros((len(tree.parents), SPATIAL_DIMENSION))
    joint_bias, wrench_bias = np.zeros_like(velocity), np.zeros_like(velocity)
    for body, parent in enumerate(tree.parents):
        joint_motion = tree.subspace[body] * loads.velocity[body]
        inherited = np.zeros(SPATIAL_DIMENSION) if parent == -1 else velocity[parent]
        velocity[body] = tree.transform[body] @ inherited + joint_motion
        joint_bias[body] = motion_cross(velocity[body]) @ joint_motion
        momentum = tree.inertia[body] @ velocity[body]
        wrench_bias[body] = force_cross(velocity[body]) @ momentum - loads.external[body]
    return velocity, joint_bias, wrench_bias


def _eliminate_joints(
    tree: PreparedTree, loads: _Loads, joint_bias: Array, result: ABAResult
) -> None:
    """Eliminate each joint acceleration while preserving its effect on the parent."""
    for body in reversed(range(len(tree.parents))):
        direction = result.inertia[body] @ tree.subspace[body]
        pivot = float(tree.subspace[body] @ direction + loads.armature[body])
        if not np.isfinite(pivot) or pivot <= 0:
            raise ValueError("articulated pivot is nonpositive or nonfinite")
        effort = loads.effective_torque[body] - tree.subspace[body] @ result.bias[body]
        result.direction[body], result.pivot[body], result.effort[body] = direction, pivot, effort
        parent = tree.parents[body]
        if parent == -1:
            continue
        remainder = result.inertia[body] - np.outer(direction, direction) / pivot
        transmitted = result.bias[body] + remainder @ joint_bias[body] + direction * effort / pivot
        transform = tree.transform[body]
        result.inertia[parent] += transform.T @ remainder @ transform
        result.bias[parent] += transform.T @ transmitted


def _recover_acceleration(
    tree: PreparedTree, loads: _Loads, joint_bias: Array, result: ABAResult
) -> None:
    """Recover eliminated accelerations in parent-before-child order."""
    for body, parent in enumerate(tree.parents):
        inherited = loads.base_acceleration if parent == -1 else result.spatial_acceleration[parent]
        inherited = tree.transform[body] @ inherited + joint_bias[body]
        result.joint_acceleration[body] = (
            result.effort[body] - result.direction[body] @ inherited
        ) / result.pivot[body]
        result.spatial_acceleration[body] = (
            inherited + tree.subspace[body] * result.joint_acceleration[body]
        )


def forward_dynamics(tree: PreparedTree, loads: DynamicsLoads) -> ABAResult:
    """Solve the smooth fixed-base tree using linear work in its joint count.

    Args:
        tree: Prepared rigid tree at the requested configuration.
        loads: Known rates and forces, expressed in the declared frames.

    Returns:
        Accelerations and the complete scalar-joint elimination intermediates.
    """
    normalized = _loads(loads, len(tree.parents))
    velocity, joint_bias, wrench_bias = _velocity_bias(tree, normalized)
    result = ABAResult(
        np.zeros(len(tree.parents)),
        velocity,
        np.zeros_like(velocity),
        tree.inertia.copy(),
        wrench_bias,
        np.zeros(len(tree.parents)),
        np.zeros(len(tree.parents)),
        np.zeros_like(velocity),
    )
    _eliminate_joints(tree, normalized, joint_bias, result)
    _recover_acceleration(tree, normalized, joint_bias, result)
    return result


def inverse_dynamics(tree: PreparedTree, loads: DynamicsLoads, acceleration: Array) -> Array:
    """Return actuator torques for prescribed joint acceleration via Newton-Euler.

    Args:
        tree: Prepared rigid tree at one configuration.
        loads: Rates, gravity, external loads and passive parameters; torque is ignored.
        acceleration: Prescribed relative joint accelerations, shape (N,).

    Returns:
        Actuator torques including compensation for viscous damping and armature.
    """
    count = len(tree.parents)
    normalized = _loads(loads, count)
    acceleration = _finite(acceleration, (count,), "acceleration")
    _, joint_bias, wrench = _velocity_bias(tree, normalized)
    spatial = np.zeros_like(wrench)
    torque = normalized.damping_force + normalized.armature * acceleration
    for body, parent in enumerate(tree.parents):
        inherited = normalized.base_acceleration if parent == -1 else spatial[parent]
        spatial[body] = (
            tree.transform[body] @ inherited
            + joint_bias[body]
            + tree.subspace[body] * acceleration[body]
        )
        wrench[body] += tree.inertia[body] @ spatial[body]
    for body in reversed(range(count)):
        torque[body] += tree.subspace[body] @ wrench[body]
        parent = tree.parents[body]
        if parent != -1:
            wrench[parent] += tree.transform[body].T @ wrench[body]
    return torque
