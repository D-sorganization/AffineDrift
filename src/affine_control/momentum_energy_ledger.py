"""Planar one-segment momentum and energy ledger.

``js/momentum-energy-ledger.js`` is the mirror. Both use
``tests/fixtures/momentum_energy_ledger_analytic.json``. y points up.
``gravity`` is downward acceleration. External force acts at the centre of mass.
"""

from __future__ import annotations

import math
from collections.abc import Mapping

_STATE_FIELDS = (
    "mass",
    "inertia_about_com",
    "com_x",
    "com_y",
    "com_vx",
    "com_vy",
    "angular_velocity",
)
_WRENCH_FIELDS = ("force_x", "force_y", "torque_about_com")
_IDENTITY_ABS_TOLERANCE = 1e-12
_HALF = 0.5


def _finite(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"{name} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be a finite number")
    return number


def _record(payload: object, fields: tuple[str, ...], label: str) -> dict[str, float]:
    if not isinstance(payload, Mapping):
        raise ValueError(f"{label} must be an object")
    for field in fields:
        if field not in payload:
            raise ValueError(f"{label} missing {field}")
    values = payload
    return {field: _finite(values[field], f"{label}.{field}") for field in fields}


def _segment(payload: object) -> dict[str, float]:
    state = _record(payload, _STATE_FIELDS, "state")
    if state["mass"] <= 0.0:
        raise ValueError("mass must be positive")
    if state["inertia_about_com"] < 0.0:
        raise ValueError("inertia_about_com must be non-negative")
    return state


def _gravity(gravity: object) -> float:
    value = _finite(gravity, "gravity")
    if value < 0.0:
        raise ValueError("gravity must be non-negative")
    return value


def _alpha(inertia: float, torque: float) -> float:
    if inertia == 0.0:
        if torque != 0.0:
            raise ValueError("torque_about_com requires positive inertia")
        return 0.0
    return torque / inertia


def segment_ledger(state: object, gravity: object) -> dict[str, float]:
    """Ledger for one segment: mass > 0, inertia >= 0, gravity >= 0.

    Mechanical energy is kinetic plus potential. Origin angular momentum is
    the centre-of-mass orbit plus spin. Kinetic energy uses König's split.
    """
    segment = _segment(state)
    weight = _gravity(gravity)
    mass = segment["mass"]
    momentum_x = mass * segment["com_vx"]
    momentum_y = mass * segment["com_vy"]
    spin = segment["inertia_about_com"] * segment["angular_velocity"]
    orbit = segment["com_x"] * momentum_y - segment["com_y"] * momentum_x
    speed_sq = segment["com_vx"] ** 2 + segment["com_vy"] ** 2
    kinetic = _HALF * (
        mass * speed_sq + segment["inertia_about_com"] * segment["angular_velocity"] ** 2
    )
    potential = mass * weight * segment["com_y"]
    if kinetic < -_IDENTITY_ABS_TOLERANCE:
        raise ValueError("kinetic_energy must be non-negative")
    return {
        "linear_momentum_x": momentum_x,
        "linear_momentum_y": momentum_y,
        "angular_momentum_about_com": spin,
        "angular_momentum_about_origin": orbit + spin,
        "kinetic_energy": kinetic,
        "potential_energy": potential,
        "mechanical_energy": kinetic + potential,
    }


def _motion(
    state: dict[str, float], wrench: dict[str, float], gravity: float, duration: float
) -> dict[str, float]:
    acceleration_x = wrench["force_x"] / state["mass"]
    acceleration_y = wrench["force_y"] / state["mass"] - gravity
    alpha = _alpha(state["inertia_about_com"], wrench["torque_about_com"])
    half_dt2 = _HALF * duration * duration
    return {
        "duration": duration,
        "com_x": state["com_x"] + state["com_vx"] * duration + acceleration_x * half_dt2,
        "com_y": state["com_y"] + state["com_vy"] * duration + acceleration_y * half_dt2,
        "com_vx": state["com_vx"] + acceleration_x * duration,
        "com_vy": state["com_vy"] + acceleration_y * duration,
        "angular_velocity": state["angular_velocity"] + alpha * duration,
        "delta_theta": state["angular_velocity"] * duration + alpha * half_dt2,
        "acceleration_x": acceleration_x,
        "acceleration_y": acceleration_y,
    }


def _integral(origin: float, rate: float, acceleration: float, duration: float) -> float:
    half_dt2 = _HALF * duration * duration
    return origin * duration + rate * half_dt2 + acceleration * duration * half_dt2 / 3.0


def _balance(
    state: dict[str, float], wrench: dict[str, float], gravity: float, motion: dict[str, float]
) -> dict[str, float]:
    duration = motion["duration"]
    total_force_x = wrench["force_x"]
    total_force_y = wrench["force_y"] - state["mass"] * gravity
    integral_x = _integral(state["com_x"], state["com_vx"], motion["acceleration_x"], duration)
    integral_y = _integral(state["com_y"], state["com_vy"], motion["acceleration_y"], duration)
    angular = total_force_y * integral_x - total_force_x * integral_y
    angular += wrench["torque_about_com"] * duration
    work = wrench["force_x"] * (motion["com_x"] - state["com_x"])
    work += wrench["force_y"] * (motion["com_y"] - state["com_y"])
    work += wrench["torque_about_com"] * motion["delta_theta"]
    return {
        "linear_impulse_x": total_force_x * duration,
        "linear_impulse_y": total_force_y * duration,
        "angular_impulse_about_origin": angular,
        "work_at_com": work,
    }


def _carried_state(state: dict[str, float], motion: dict[str, float]) -> dict[str, float]:
    carried = {field: motion[field] for field in _STATE_FIELDS if field in motion}
    carried["mass"] = state["mass"]
    carried["inertia_about_com"] = state["inertia_about_com"]
    return carried


def advance_constant_wrench(
    state: object, wrench: object, gravity: object, duration: object
) -> dict[str, dict[str, float]]:
    """Advance under a constant COM wrench. Duration > 0; a point mass has zero torque.

    Postcondition: reported impulses and work equal the ledger change.
    """
    segment = _segment(state)
    loads = _record(wrench, _WRENCH_FIELDS, "wrench")
    weight = _gravity(gravity)
    elapsed = _finite(duration, "duration")
    if elapsed <= 0.0:
        raise ValueError("duration must be positive")
    motion = _motion(segment, loads, weight, elapsed)
    final = _carried_state(segment, motion)
    balance = _balance(segment, loads, weight, motion)
    return {"final_state": final, "balance": balance}
