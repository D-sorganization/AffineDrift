"""Reproduce Chapter 4 physical loads and instantaneous attribution examples."""

import json
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DP = import_module("docs.development.technical-review.build_double_pendulum_figures")
ROOT = Path(__file__).resolve().parents[3]
GRAVITY_VECTOR = np.array([0.0, -DP.AFFINE.GRAVITY_M_S2])
EXAMPLE_ANGLES = np.deg2rad([0.0, -5.0])
EXAMPLE_RATES = np.array([10.0, 9.0])
EXAMPLE_ACCELERATION = np.array([20.0, -30.0])


@dataclass(frozen=True)
class RotatingState:
    """Planar transport data expressed in coincident axes at the evaluation time."""

    relative_position: np.ndarray
    relative_velocity: np.ndarray
    relative_acceleration: np.ndarray
    angular_rate: float
    angular_acceleration: float
    origin_acceleration: np.ndarray


def cross_plane(first: np.ndarray, second: np.ndarray) -> float:
    """Return the out-of-plane moment of two planar vectors."""
    return float(first[0] * second[1] - first[1] * second[0])


def transport_acceleration(state: RotatingState) -> np.ndarray:
    """Apply moving-origin, Euler, centripetal and positive Coriolis transport terms."""
    quarter_turn = np.array([[0, -1], [1, 0]])
    return (
        state.origin_acceleration
        + state.relative_acceleration
        + state.angular_acceleration * quarter_turn @ state.relative_position
        - state.angular_rate**2 * state.relative_position
        + 2 * state.angular_rate * quarter_turn @ state.relative_velocity
    )


def shift_moment(moment: np.ndarray, force: np.ndarray, old_to_new: np.ndarray) -> np.ndarray:
    """Shift a wrench reference by old_to_new while retaining the same spatial axes."""
    return moment - np.cross(old_to_new, force)


def body_kinematics(q: np.ndarray, rates: np.ndarray, acceleration: np.ndarray) -> dict:
    """Locate both COMs and hinge H using the declared two-link geometry."""
    radial = np.array([DP.radial(q[0]), DP.radial(q.sum())])
    tangent = np.array([DP.tangent(q[0]), DP.tangent(q.sum())])
    absolute_rates = np.array([rates[0], rates.sum()])
    absolute_acceleration = np.array([acceleration[0], acceleration.sum()])
    distances = np.array([[DP.AFFINE.COM_FIRST, 0], [DP.AFFINE.LENGTH_FIRST, DP.AFFINE.COM_SECOND]])
    return {
        "com_position": distances @ radial,
        "com_velocity": distances @ (absolute_rates[:, None] * tangent),
        "com_acceleration": distances
        @ (absolute_acceleration[:, None] * tangent - absolute_rates[:, None] ** 2 * radial),
        "hinge_position": DP.AFFINE.LENGTH_FIRST * radial[0],
        "hinge_velocity": DP.AFFINE.LENGTH_FIRST * rates[0] * tangent[0],
    }


def body_loads(q: np.ndarray, rates: np.ndarray, acceleration: np.ndarray) -> dict:
    """Recover hinge/base forces and actuator moments from independent body balances."""
    data = body_kinematics(q, rates, acceleration)
    centers, com_acceleration = data["com_position"], data["com_acceleration"]
    hinge = data["hinge_position"]
    hinge_force = DP.AFFINE.MASS_SECOND * (com_acceleration[1] - GRAVITY_VECTOR)
    base_force = DP.AFFINE.MASS_FIRST * (com_acceleration[0] - GRAVITY_VECTOR) + hinge_force
    distal_torque = DP.AFFINE.INERTIA_SECOND * acceleration.sum()
    distal_torque -= cross_plane(hinge - centers[1], hinge_force)
    proximal_torque = DP.AFFINE.INERTIA_FIRST * acceleration[0] + distal_torque
    proximal_torque -= cross_plane(-centers[0], base_force)
    proximal_torque -= cross_plane(hinge - centers[0], -hinge_force)
    hinge_power = float(hinge_force @ data["hinge_velocity"])
    gravity_power = np.array([DP.AFFINE.MASS_FIRST, DP.AFFINE.MASS_SECOND])
    gravity_power *= data["com_velocity"] @ GRAVITY_VECTOR
    actuator_body_power = np.array(
        [(proximal_torque - distal_torque) * rates[0], distal_torque * rates.sum()]
    )
    data.update(
        hinge_force=hinge_force,
        base_force=base_force,
        torque=np.array([proximal_torque, distal_torque]),
        interface_force_power=np.array([-hinge_power, hinge_power]),
        body_power=np.array([-hinge_power, hinge_power]) + gravity_power + actuator_body_power,
        gravity_power=gravity_power,
        actuator_body_power=actuator_body_power,
    )
    return data


def acceleration_attribution(q: np.ndarray, rates: np.ndarray, torque: np.ndarray) -> dict:
    """Map fixed-state force terms and endpoint curvature to one inertial task frame."""
    mass, bias, gradient = DP.AFFINE.operators(q, rates)
    jacobian = DP.endpoint_jacobian(q)
    return {
        "input": jacobian @ np.linalg.solve(mass, torque),
        "velocity": -jacobian @ np.linalg.solve(mass, bias),
        "gravity": -jacobian @ np.linalg.solve(mass, gradient),
        "curvature": DP.endpoint_acceleration(q, rates, np.zeros(2)),
    }


def example_report() -> dict:
    """Compute declared inverse dynamics, body loads and task contributions in SI units."""
    data = body_loads(EXAMPLE_ANGLES, EXAMPLE_RATES, EXAMPLE_ACCELERATION)
    mass, bias, gradient = DP.AFFINE.operators(EXAMPLE_ANGLES, EXAMPLE_RATES)
    return {
        "authority": "Manufactured rigid planar model; not a measured golfer or collision",
        "angles_degrees": np.rad2deg(EXAMPLE_ANGLES).tolist(),
        "rates_rad_s": EXAMPLE_RATES.tolist(),
        "acceleration_rad_s2": EXAMPLE_ACCELERATION.tolist(),
        "inertia_term_N_m": (mass @ EXAMPLE_ACCELERATION).tolist(),
        "bias_N_m": bias.tolist(),
        "potential_gradient_N_m": gradient.tolist(),
        "body_loads_SI": {key: value.tolist() for key, value in data.items()},
        "endpoint_acceleration_contributions_m_s2": {
            key: value.tolist()
            for key, value in acceleration_attribution(
                EXAMPLE_ANGLES, EXAMPLE_RATES, data["torque"]
            ).items()
        },
        "input_power_W": float(data["torque"] @ EXAMPLE_RATES),
    }


def draw_contributions(axis: plt.Axes, values: np.ndarray, labels: list[str]) -> None:
    """Compare signed components in common units without implying positive assistance."""
    locations = np.arange(len(labels))
    axis.barh(locations - 0.16, values[:, 0], 0.3, label="First Component", color="#176a9a")
    axis.barh(locations + 0.16, values[:, 1], 0.3, label="Second Component", color="#994a1f")
    axis.set_yticks(locations, labels)
    axis.axvline(0, color="gray", linewidth=0.8)
    axis.invert_yaxis()
    axis.legend(fontsize=8)


def main() -> None:
    """Write shared vector plots and the complete numerical evidence record."""
    report = example_report()
    plt.rcParams.update({"svg.fonttype": "none", "svg.hashsalt": "forces-torques-4355"})
    figure, axes = plt.subplots(2, 1, figsize=(8, 8), constrained_layout=True)
    components = np.array(
        [report[key] for key in ("inertia_term_N_m", "bias_N_m", "potential_gradient_N_m")]
        + [report["body_loads_SI"]["torque"]]
    )
    draw_contributions(axes[0], components, ["Inertia M a", "Bias c", "Gradient g", "Input τ"])
    axes[0].set(
        title="Joint-Moment Accounting: Components Are Joints 1 and 2", xlabel="Moment (N m)"
    )
    task = report["endpoint_acceleration_contributions_m_s2"]
    values = np.array(list(task.values()) + [np.sum(list(task.values()), axis=0)])
    draw_contributions(axes[1], values, ["Input", "Velocity Bias", "Gravity", "Curvature", "Total"])
    axes[1].set(
        title="Endpoint Accounting: Components Are Horizontal and Vertical",
        xlabel="Acceleration (m/s²)",
    )
    figure.suptitle("One Declared State, Two Different Questions")
    folder = ROOT / "articles/The_Physics_of_Golf/figures"
    for extension in ("svg", "pdf"):
        figure.savefig(folder / f"forces_torques_verified.{extension}")
    plt.close(figure)
    (Path(__file__).parent / "forces-torques-numerics.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
