"""Core torque transmission calculations for the Wrist Universal Joint model.

This module contains the physics and mathematics for:
- Moments of inertia calculation
- Universal joint (Hooke/Cardan) transmission ratios
- Grip-angle-based torque distribution
- Signal generation for input torque profiles
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
from simpleeval import EvalWithCompoundTypes  # type: ignore[import-untyped]

from src.core.contracts import check_positive, ensure, require

from .constants import MAX_DELTA_DEGREES, rng

logger = logging.getLogger(__name__)


def _compute_i_alpha(
    m_head_kg: float,
    m_shaft_kg: float,
    club_length_m: float,
    cg_distance_m: float,
) -> float:
    """Compute transverse grip-point inertia for a thin rod and point head.

    Both components lie along the shaft in this approximation. The rotation
    axis passes through the grip and is perpendicular to the shaft. This
    formula cannot determine inertia about the shaft's longitudinal axis.

    Args:
        m_head_kg: Clubhead mass in kilograms.
        m_shaft_kg: Shaft mass in kilograms.
        club_length_m: Total club length in meters.
        cg_distance_m: Distance from grip to clubhead CG in meters.

    Returns:
        I_alpha in kg·m².
    """
    i_shaft = (1.0 / 3.0) * m_shaft_kg * club_length_m**2
    i_head = m_head_kg * cg_distance_m**2
    return i_shaft + i_head


def calculate_moments_of_inertia(
    clubhead_weight_g: float,
    shaft_weight_g: float,
    club_length_m: float,
    cg_distance_m: float,
    i_gamma_ratio: float = 0.5,
) -> tuple[float, float]:
    """Calculate moments of inertia for golf club about two axes.

    Args:
    ----
        clubhead_weight_g: Clubhead weight in grams.
        shaft_weight_g: Shaft weight in grams.
        club_length_m: Total club length in meters.
        cg_distance_m: Distance from grip to clubhead center of mass in meters.
        i_gamma_ratio: User-selected illustrative ratio of I_gamma to I_alpha.
            The compatibility default 0.5 is not a measured club property.

    Returns:
    -------
        A tuple of (I_alpha, I_gamma) in kg·m².

    """
    check_positive(clubhead_weight_g, "clubhead weight")
    check_positive(shaft_weight_g, "shaft weight")
    check_positive(club_length_m, "club length")
    check_positive(cg_distance_m, "CG distance")
    check_positive(i_gamma_ratio, "i_gamma_ratio")
    i_alpha = _compute_i_alpha(
        clubhead_weight_g / 1000.0, shaft_weight_g / 1000.0, club_length_m, cg_distance_m
    )
    i_gamma = i_gamma_ratio * i_alpha
    ensure(i_alpha > 0, "I_alpha must be positive")
    ensure(i_gamma > 0, "I_gamma must be positive")
    return i_alpha, i_gamma


def universal_joint_transmission_ratio(
    phi_rad: float,
    delta_rad: float,
) -> tuple[float, float]:
    """Calculate fixed-bend Cardan speed and ideal quasistatic torque ratios.

    The phase convention is psi = atan2(cos(delta)*sin(phi), cos(phi)),
    continued over revolutions. Differentiating gives dpsi/dphi, without a
    square root. Torque reciprocity assumes negligible joint energy storage
    and losses, fixed shaft supports and power-conjugate shaft torques.
    This one-DOF driveshaft mechanism is not a calibrated two-DOF wrist model.
    Finite bends beyond MAX_DELTA_DEGREES are clipped for legacy demo callers;
    their output describes the clipped angle, not the requested geometry.

    Args:
    ----
        phi_rad: Rotation angle of input shaft (radians).
        delta_rad: Bend angle between shafts (radians).

    Returns:
    -------
        A tuple containing:
            - omega_ratio: ω_out / ω_in (angular velocity ratio).
            - tau_ratio: τ_out / τ_in (torque transmission ratio).

    """
    if not np.isfinite(phi_rad) or not np.isfinite(delta_rad):
        raise ValueError("Cardan angles must be finite")

    # Legacy display limit; the 90-degree mechanism is outside this model.
    if np.abs(delta_rad) > np.radians(MAX_DELTA_DEGREES):
        delta_rad = np.sign(delta_rad) * np.radians(MAX_DELTA_DEGREES)

    sin_delta = np.sin(delta_rad)
    cos_delta = np.cos(delta_rad)
    sin_phi = np.sin(phi_rad)

    # Angular velocity ratio: ω_out/ω_in
    denominator = 1.0 - sin_delta**2 * sin_phi**2
    omega_ratio = cos_delta / denominator

    # Torque ratio: τ_out/τ_in = 1/(ω_out/ω_in) from power conservation
    tau_ratio = denominator / cos_delta

    return omega_ratio, tau_ratio


def distribute_torque_by_grip_angle(
    torque_transmitted: float | np.ndarray[Any, Any],
    theta_grip_rad: float,
) -> tuple[float | np.ndarray[Any, Any], float | np.ndarray[Any, Any]]:
    """Resolve a torque vector onto two orthogonal illustrative axes.

    This preserves vector magnitude, not energy by itself. Neither axis is
    automatically a face-angle or speed axis; that needs an orientation and
    inertia model. The angle is a coordinate projection, not a grip diagnosis.

    Args:
    ----
        torque_transmitted: Torque transmitted through universal joint (N·m).
        theta_grip_rad: Grip angle in radians.

    Returns:
    -------
        A tuple containing:
            - torque_alpha: Sine component (N·m).
            - torque_gamma: Cosine component (N·m).

    """
    torque_alpha = torque_transmitted * np.sin(theta_grip_rad)
    torque_gamma = torque_transmitted * np.cos(theta_grip_rad)

    return torque_alpha, torque_gamma


def _generate_golf_torque(t: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
    """Generate a golf-swing-like random torque signal."""
    torque = rng.normal(0, 1, len(t))
    torque += np.exp(-50 * (t - 0.5) ** 2) * 8 * rng.standard_normal(len(t))
    return np.convolve(torque, np.ones(10) / 10, mode="same")


def _generate_step_torque(t: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
    """Generate a step torque signal (step at midpoint)."""
    n = len(t)
    torque = np.zeros_like(t)
    midpoint = n // 2
    torque[midpoint:] = 3.0  # Step at midpoint
    return torque


def _generate_pulse_torque(t: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
    """Generate a pulse torque signal (random burst in the middle 20% of the array)."""
    n = len(t)
    torque = np.zeros_like(t)
    pulse_start = int(0.4 * n)
    pulse_end = int(0.6 * n)
    torque[pulse_start:pulse_end] = 5.0 * rng.standard_normal(pulse_end - pulse_start)
    return torque


def _generate_burst_torque(t: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
    """Generate a burst torque signal (Gaussian burst centered at midpoint)."""
    n = len(t)
    torque = np.zeros_like(t)
    burst_center = n // 2
    burst_width = max(1, n // 10)
    burst_indices = np.arange(
        max(0, burst_center - burst_width),
        min(n, burst_center + burst_width),
    )
    torque[burst_indices] = rng.normal(0, 3, len(burst_indices))
    return torque


def generate_sample_torque(
    noise_type: str,
    t: np.ndarray[Any, Any],
    polynomial_expression: str = "t**2 - t",
) -> tuple[np.ndarray[Any, Any], str | None]:
    """Generate a torque signal based on noise type.

    Args:
    ----
        noise_type: Type of signal to generate.
        t: Time array.
        polynomial_expression: Expression for polynomial mode.

    Returns:
    -------
        Tuple of (torque array, error string or None).

    """
    require(len(t) > 0, "time array must not be empty")
    error: str | None = None
    torque: np.ndarray[Any, Any]

    if noise_type == "Golf-like Random":
        torque = _generate_golf_torque(t)
    elif noise_type == "Step":
        torque = _generate_step_torque(t)
    elif noise_type == "Pulse":
        torque = _generate_pulse_torque(t)
    elif noise_type == "Burst":
        torque = _generate_burst_torque(t)
    elif noise_type == "Sinusoidal":
        torque = 2.0 * np.sin(8 * np.pi * t)
    elif noise_type == "Random":
        torque = rng.normal(0, 1.5, len(t))
        torque = np.convolve(torque, np.ones(10) / 10, mode="same")
    elif noise_type == "Polynomial":
        torque, error = _evaluate_polynomial(t, polynomial_expression)
    else:
        torque = _generate_golf_torque(t)

    return torque, error


def _build_polynomial_namespace(
    t: np.ndarray[Any, Any],
) -> Any:
    """Build a safe evaluator with allowed names and functions for polynomial expressions."""
    return EvalWithCompoundTypes(
        names={"t": t, "pi": np.pi, "e": np.e},
        functions={
            "sin": np.sin,
            "cos": np.cos,
            "exp": np.exp,
            "sqrt": np.sqrt,
            "log": np.log,
        },
    )


def _validate_polynomial_result(
    result: Any,
    t: np.ndarray[Any, Any],
) -> tuple[np.ndarray[Any, Any], str | None]:
    """Validate and coerce a polynomial evaluation result to match the time array shape."""
    if isinstance(result, np.ndarray):
        if result.shape != t.shape:
            return (
                t**2 - t,
                f"Polynomial result shape {result.shape} does not match "
                f"time array shape {t.shape}.",
            )
        return result, None
    return np.full_like(t, float(result)), None


def _evaluate_polynomial(
    t: np.ndarray[Any, Any],
    expression: str,
) -> tuple[np.ndarray[Any, Any], str | None]:
    """Safely evaluate a polynomial expression over a time array.

    Args:
    ----
        t: Time array.
        expression: Mathematical expression using 't' as variable.

    Returns:
    -------
        Tuple of (evaluated result array, error string or None).

    """
    try:
        evaluator = _build_polynomial_namespace(t)
        result = evaluator.eval(expression)
        return _validate_polynomial_result(result, t)
    except SyntaxError:
        return t**2 - t, "Invalid polynomial syntax. Please check your expression."
    except NameError:
        return (
            t**2 - t,
            "Invalid variable or function. Only 't', 'sin', 'cos', 'exp', "
            "'sqrt', 'log', 'pi', and 'e' are allowed.",
        )
    except (TypeError, ValueError) as e:
        return (
            t**2 - t,
            f"Error in polynomial expression: {type(e).__name__}. Please check your formula.",
        )
    except (ArithmeticError, OverflowError, ZeroDivisionError):
        return (
            t**2 - t,
            "Unexpected error evaluating polynomial expression. Please check your formula.",
        )
