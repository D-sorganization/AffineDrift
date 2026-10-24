"""Dead-zone and reduced-muscle preload models for the firm-lead-wrist article (#5134).

A self-contained port of two UpstreamDrift studies at 3fd2a59e390523169df846a3bbb395a6203c382c:
``scripts/research/proximal_distal_energy/torque_allocation_preload.py`` (a two-channel
transmission with a rotational dead zone) and ``advanced_biological_bridge.py`` (identical at the site-pinned b700e589; Hill-type
activation and series-force dynamics). Both compare a *persistent-direction* program, in which
the arm channel stays positive and the wrist channel stays negative, with a *complete role
reversal* that reaches the same net torque. The comparison metric ``error_impulse_nms`` keeps the
upstream name but is the integrated absolute (L1) tracking error of the net torque after the
transition, ``J = integral |desired - transmitted| dt`` in N m s. It is not an angular impulse
and not work.

At optimal fibre length and zero fibre velocity the upstream Hill force law reduces exactly to
``F = F_max * a``, which is what this port uses. Every parameter is a declared synthetic value,
not an identified tissue or grip property.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]

RESULTS_PATH = Path(__file__).resolve().parents[2] / "data/lead_wrist_preload/results.json"

ZERO_TORQUE_TOLERANCE_NM = 1e-12
EQUIVALENCE_TOLERANCE_NMS = 1e-10
PREPARATION_S = 0.18
DELIVERY_S = 0.12
DEAD_ZONE_STEP_S = 1e-4
MUSCLE_STEP_S = 2e-4
MAX_MUSCLE_STEP_S = 1e-3
AUDIT_STEPS_S = (1e-3, 5e-4, 2e-4, 1e-4, 5e-5)
LIMIT_STEPS_S = (2e-5, 1e-5)
SENSITIVITY_DEAD_ZONES_RAD = (0.0, 0.004, 0.012, 0.024)
SENSITIVITY_TIME_CONSTANTS_S = (0.008, 0.018, 0.035)
# Muscle bridge: arm channel 40 N m capacity at 0.04 m; wrist 15 N m at 0.03 m.
MOMENT_ARMS_M = np.array([0.04, -0.04, 0.03, -0.03])
MAX_FORCES_N = np.array([1000.0, 1000.0, 500.0, 500.0])
CAPACITIES_NM = (40.0, 15.0)
BASELINE_ACTIVATION = 0.08
MIN_ACTIVATION = 0.001
ACTIVATION_RATIO_LEVELS = (MIN_ACTIVATION, BASELINE_ACTIVATION, 1.0)
TAU_ACTIVATION_S = 0.010
TAU_DEACTIVATION_S = 0.040
TAU_TENDON_S = 0.012
# Heavy-hit article's assumed steel shaft: E = 210 GPa, rho = 7850 kg/m^3, length 1.15 m.
STEEL_YOUNGS_MODULUS_PA = 210e9
STEEL_DENSITY_KG_M3 = 7850.0
SHAFT_LENGTH_M = 1.15


@dataclass(frozen=True)
class DeadZoneChannel:
    """Series transmission: dead zone of half-width ``dead_zone_rad``, stiffness, lag."""

    stiffness_nm_rad: float
    dead_zone_rad: float
    time_constant_s: float

    def __post_init__(self) -> None:
        """Validate channel parameters at construction."""
        if not self.stiffness_nm_rad > 0.0:
            raise ValueError("stiffness_nm_rad must be positive")
        if not self.dead_zone_rad >= 0.0:
            raise ValueError("dead_zone_rad must be non-negative")
        if not self.time_constant_s > 0.0:
            raise ValueError("time_constant_s must be positive")


@dataclass(frozen=True)
class Program:
    """Desired arm and wrist torque (N m) before and after the transition at t = 0."""

    name: str
    arm_pre_nm: float
    wrist_pre_nm: float
    arm_post_nm: float
    wrist_post_nm: float


DEAD_ZONE_CHANNEL = DeadZoneChannel(600.0, 0.012, 0.018)
PERSISTENT = Program("persistent_direction", 10.0, -4.0, 16.0, -6.0)
REVERSAL = Program("complete_role_reversal", -4.0, 10.0, 16.0, -6.0)
PERSISTENT_LARGE = Program("persistent_direction_net_14", 10.0, -4.0, 20.0, -6.0)
REVERSAL_LARGE = Program("complete_role_reversal_net_14", -4.0, 10.0, 20.0, -6.0)


def _command_deflection(torque: FloatArray, channel: DeadZoneChannel) -> FloatArray:
    """Map commanded torque to shaft deflection including the dead zone."""
    magnitude = channel.dead_zone_rad + np.abs(torque) / channel.stiffness_nm_rad
    return np.where(torque == 0.0, 0.0, np.sign(torque) * magnitude)


def _engaged_torque(deflection: FloatArray, channel: DeadZoneChannel) -> FloatArray:
    """Return transmitted torque after slack is taken up in the dead zone."""
    slack = np.maximum(np.abs(deflection) - channel.dead_zone_rad, 0.0)
    return channel.stiffness_nm_rad * np.sign(deflection) * slack


def _tracking_error(desired: object, transmitted: object, time: object) -> float:
    """Integrate absolute net-torque tracking error over time (N m s)."""
    shortfall = np.asarray(desired, dtype=float) - np.asarray(transmitted, dtype=float)
    return float(np.trapezoid(np.abs(shortfall), np.asarray(time, dtype=float)))


def simulate_dead_zone(
    program: Program, channel: DeadZoneChannel, *, preloaded: bool, step_s: float = DEAD_ZONE_STEP_S
) -> dict[str, Any]:
    """Integrate both channels for the delivery window after the transition.

    Preconditions: ``step_s`` divides ``DELIVERY_S``. With ``preloaded`` the channels start at
    their loaded pre-transition equilibrium; otherwise at zero deflection.
    """
    steps = int(round(DELIVERY_S / step_s))
    if not np.isclose(steps * step_s, DELIVERY_S, rtol=0.0, atol=1e-12):
        raise ValueError("step_s must divide the delivery window")
    time = np.arange(steps + 1) * step_s
    pre = np.array([program.arm_pre_nm, program.wrist_pre_nm])
    post = np.array([program.arm_post_nm, program.wrist_post_nm])
    target = _command_deflection(post, channel)
    deflection = np.empty((steps + 1, 2))
    deflection[0] = _command_deflection(pre, channel) if preloaded else 0.0
    for index in range(steps):
        lag = (target - deflection[index]) / channel.time_constant_s
        deflection[index + 1] = deflection[index] + step_s * lag
    torque = _engaged_torque(deflection, channel)
    gaps = np.count_nonzero(np.abs(torque) <= ZERO_TORQUE_TOLERANCE_NM, axis=0) * step_s
    return {
        "time_s": time,
        "desired_net_nm": np.full_like(time, post.sum()),
        "transmitted_net_nm": torque.sum(axis=1),
        "error_impulse_nms": _tracking_error(post.sum(), torque.sum(axis=1), time),
        "arm_gap_s": float(gaps[0]),
        "wrist_gap_s": float(gaps[1]),
        "net_gap_s": float(
            np.count_nonzero(np.abs(torque.sum(axis=1)) <= ZERO_TORQUE_TOLERANCE_NM) * step_s
        ),
    }


def _activation_targets(arm_nm: float, wrist_nm: float) -> FloatArray:
    """Excitation for (arm+, arm-, wrist+, wrist-) above a shared baseline."""
    targets = np.full(4, BASELINE_ACTIVATION)
    for pair, (torque, capacity) in enumerate(zip((arm_nm, wrist_nm), CAPACITIES_NM, strict=True)):
        targets[2 * pair + (0 if torque >= 0.0 else 1)] += abs(torque) / capacity
    if np.any(targets > 1.0):
        raise ValueError("torque target exceeds activation capacity")
    return targets


def activation_time_constants(activation: npt.ArrayLike) -> tuple[FloatArray, FloatArray]:
    """Rise and decay time constants (s); both scale with the current activation."""
    scale = 0.5 + 1.5 * np.asarray(activation, dtype=float)
    return TAU_ACTIVATION_S * scale, TAU_DEACTIVATION_S / scale


def switch_time_constants_ms(program: Program = REVERSAL) -> dict[str, float]:
    """Activation time constant (ms) of each muscle at t = 0, rising or decaying as commanded.

    Assumes the preparation window has settled each activation at its pre-switch target, which
    holds for the published programs. Muscle order is (arm+, arm-, wrist+, wrist-).
    """
    pre = _activation_targets(program.arm_pre_nm, program.wrist_pre_nm)
    post = _activation_targets(program.arm_post_nm, program.wrist_post_nm)
    rise, decay = activation_time_constants(pre)
    tau_ms = 1e3 * np.where(post > pre, rise, decay)
    names = ("arm_positive", "arm_negative", "wrist_positive", "wrist_negative")
    rows = zip(names, post > pre, tau_ms, np.isclose(post, pre), strict=True)
    return {
        f"{name}_{'rise' if rising else 'decay'}": float(tau)
        for name, rising, tau, unchanged in rows
        if not unchanged
    }


def _activation_step(excitation: FloatArray, activation: FloatArray, step_s: float) -> FloatArray:
    """One Euler step of first-order activation with faster rise than decay."""
    rise, decay = activation_time_constants(activation)
    tau = np.where(excitation > activation, rise, decay)
    return np.clip(activation + step_s * (excitation - activation) / tau, MIN_ACTIVATION, 1.0)


def simulate_muscle(program: Program, *, step_s: float = MUSCLE_STEP_S) -> dict[str, Any]:
    """Run relaxed preparation then delivery with continuous muscle and tendon state.

    Preconditions: ``0 < step_s <= 1 ms`` (activation stability) and ``step_s`` divides both
    windows. Nothing is reset at t = 0; only the desired torques change.
    """
    if not 0.0 < step_s <= MAX_MUSCLE_STEP_S:
        raise ValueError("step_s must lie in (0, 1 ms]")
    time = np.arange(-round(PREPARATION_S / step_s), round(DELIVERY_S / step_s) + 1) * step_s
    pre = _activation_targets(program.arm_pre_nm, program.wrist_pre_nm)
    post = _activation_targets(program.arm_post_nm, program.wrist_post_nm)
    activation = np.full(4, MIN_ACTIVATION)
    tendon = np.zeros(4)
    moments = np.empty((time.size, 4))
    for index, instant in enumerate(time):
        activation = _activation_step(pre if instant < 0.0 else post, activation, step_s)
        tendon = tendon + step_s / TAU_TENDON_S * (MAX_FORCES_N * activation - tendon)
        moments[index] = MOMENT_ARMS_M * tendon
    desired = np.where(
        time < 0.0,
        program.arm_pre_nm + program.wrist_pre_nm,
        program.arm_post_nm + program.wrist_post_nm,
    )
    transmitted = moments.sum(axis=1)
    after = time >= 0.0
    peak = int(np.argmax(np.where(after, transmitted, -np.inf)))
    return {
        "peak_net_nm": float(transmitted[peak]),
        "peak_time_s": float(time[peak]),
        "time_s": time,
        "desired_net_nm": desired,
        "transmitted_net_nm": transmitted,
        "error_impulse_nms": _tracking_error(desired[after], transmitted[after], time[after]),
        "signed_error_nms": float(np.trapezoid((desired - transmitted)[after], time[after])),
        "shortfall_nms": float(
            np.trapezoid(np.maximum(desired - transmitted, 0.0)[after], time[after])
        ),
        "overshoot_nms": float(
            np.trapezoid(np.maximum(transmitted - desired, 0.0)[after], time[after])
        ),
    }


def muscle_step_audit(
    programs: tuple[Program, Program] = (PERSISTENT, REVERSAL),
) -> dict[str, Any]:
    """Tracking error of both programs over the published step grid and a fine-step limit.

    The limit is a Richardson extrapolation of the first-order Euler results at
    ``LIMIT_STEPS_S``: ``2 J(h/2) - J(h)``.
    """

    def errors(step: float) -> list[float]:
        """Return persistent and reversal tracking errors at the given step size."""
        return [simulate_muscle(program, step_s=step)["error_impulse_nms"] for program in programs]

    grid = np.array([errors(step) for step in AUDIT_STEPS_S])
    coarse, fine = (np.array(errors(step)) for step in LIMIT_STEPS_S)
    limit = 2.0 * fine - coarse
    return {
        "step_s": list(AUDIT_STEPS_S),
        "persistent_nms": grid[:, 0].tolist(),
        "reversal_nms": grid[:, 1].tolist(),
        "difference_nms": (grid[:, 1] - grid[:, 0]).tolist(),
        "limit_persistent_nms": float(limit[0]),
        "limit_reversal_nms": float(limit[1]),
        "limit_relative_difference": float((limit[1] - limit[0]) / limit[0]),
    }


def dead_zone_sensitivity() -> dict[str, Any]:
    """Classify the dead-zone by time-constant grid from loaded starts."""
    differences = []
    for dead_zone in SENSITIVITY_DEAD_ZONES_RAD:
        for time_constant in SENSITIVITY_TIME_CONSTANTS_S:
            channel = DeadZoneChannel(600.0, dead_zone, time_constant)
            persistent, reversal = (
                simulate_dead_zone(program, channel, preloaded=True)["error_impulse_nms"]
                for program in (PERSISTENT, REVERSAL)
            )
            differences.append(reversal - persistent)
    delta = np.array(differences)
    return {
        "difference_nms": delta.reshape(len(SENSITIVITY_DEAD_ZONES_RAD), -1).tolist(),
        "persistent_favored": int(np.sum(delta > EQUIVALENCE_TOLERANCE_NMS)),
        "equivalent": int(np.sum(np.abs(delta) <= EQUIVALENCE_TOLERANCE_NMS)),
        "reversal_favored": int(np.sum(delta < -EQUIVALENCE_TOLERANCE_NMS)),
    }


def shaft_round_trip_s() -> float:
    """Axial round-trip time 2L/c with c = sqrt(E/rho) for the assumed steel shaft."""
    return 2.0 * SHAFT_LENGTH_M / float(np.sqrt(STEEL_YOUNGS_MODULUS_PA / STEEL_DENSITY_KG_M3))


def _scalar_summary(trace: dict[str, Any]) -> dict[str, float]:
    """Keep only float-valued entries from a simulation trace."""
    return {key: value for key, value in trace.items() if isinstance(value, float)}


def build_results() -> dict[str, Any]:
    """Return every number the article quotes, as a JSON-serializable document."""
    dead_zone = {
        f"{program.name}_{'preloaded' if preloaded else 'relaxed'}": _scalar_summary(
            simulate_dead_zone(program, DEAD_ZONE_CHANNEL, preloaded=preloaded)
        )
        for program in (PERSISTENT, REVERSAL)
        for preloaded in (True, False)
    }
    muscle = {
        program.name: _scalar_summary(simulate_muscle(program))
        for program in (PERSISTENT, REVERSAL, PERSISTENT_LARGE, REVERSAL_LARGE)
    }
    return {
        "schema_version": 1,
        "metric": "integrated absolute net-torque tracking error after t = 0 (N m s)",
        "dead_zone": dead_zone,
        "dead_zone_sensitivity": dead_zone_sensitivity(),
        "muscle": muscle,
        "muscle_step_audit": muscle_step_audit(),
        "muscle_step_audit_net_14": muscle_step_audit((PERSISTENT_LARGE, REVERSAL_LARGE)),
        "shaft_round_trip_s": shaft_round_trip_s(),
        "switch_time_constants_ms": switch_time_constants_ms(),
        "decay_to_rise_ratio": {
            f"activation_{level:g}": float(ratio)
            for level, ratio in zip(
                ACTIVATION_RATIO_LEVELS,
                np.divide(*activation_time_constants(ACTIVATION_RATIO_LEVELS)[::-1]),
                strict=True,
            )
        },
    }


def write_results(path: Path = RESULTS_PATH) -> None:
    """Write ``build_results()`` as indented JSON; run ``python3 -m src.tools.lead_wrist_preload_models``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_results(), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    write_results()
