"""Core torque transmission calculations for the Wrist Universal Joint model.

This module contains the physics and mathematics for:
- Moments of inertia calculation
- Universal joint (Hooke/Cardan) transmission ratios
- Grip-angle-based torque distribution
- Signal generation for input torque profiles
"""

from __future__ import annotations

from typing import Any

import numpy as np
from simpleeval import EvalWithCompoundTypes

from src.core.contracts import check_positive, ensure, require

from .constants import MAX_DELTA_DEGREES, rng


def calculate_moments_of_inertia(
    clubhead_weight_g: float,
    shaft_weight_g: float,
    club_length_m: float,
    cg_distance_m: float,
) -> tuple[float, float]:
    """Calculate moments of inertia for golf club about two axes.

    Args:
    ----
        clubhead_weight_g: Clubhead weight in grams.
        shaft_weight_g: Shaft weight in grams.
        club_length_m: Total club length in meters.
        cg_distance_m: Distance from grip to clubhead center of mass in meters.

    Returns:
    -------
        A tuple containing:
            - I_alpha: Moment of inertia about shaft axis (kg·m²) - higher MOI.
            - I_gamma: Moment of inertia about local gamma axis (kg·m²) - lowest MOI.

    """
    check_positive(clubhead_weight_g, "clubhead weight")
    check_positive(shaft_weight_g, "shaft weight")
    check_positive(club_length_m, "club length")
    check_positive(cg_distance_m, "CG distance")
    m_head = clubhead_weight_g / 1000.0  # kg
    m_shaft = shaft_weight_g / 1000.0  # kg

    # Shaft inertia (thin rod about end): I = (1/3) * m * L²
    i_shaft_alpha = (1 / 3) * m_shaft * club_length_m**2

    # Clubhead inertia about shaft axis (point mass)
    i_head_alpha = m_head * cg_distance_m**2

    # Total I_alpha (about shaft axis) - higher MOI axis
    i_alpha = i_shaft_alpha + i_head_alpha

    # I_gamma (lowest MOI axis) - typically 0.5x for golf clubs
    i_gamma = 0.5 * i_alpha

    ensure(i_alpha > 0, "I_alpha must be positive")
    ensure(i_gamma > 0, "I_gamma must be positive")
    return i_alpha, i_gamma


def universal_joint_transmission_ratio(
    phi_rad: float,
    delta_rad: float,
) -> tuple[float, float]:
    """Calculate transmission ratios for a universal (Hooke/Cardan) joint.

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
    # Avoid singularities at delta = 90°
    if np.abs(delta_rad) > np.radians(MAX_DELTA_DEGREES):
        delta_rad = np.sign(delta_rad) * np.radians(MAX_DELTA_DEGREES)

    sin_delta = np.sin(delta_rad)
    cos_delta = np.cos(delta_rad)
    sin_phi = np.sin(phi_rad)

    # Angular velocity ratio: ω_out/ω_in
    denominator = np.sqrt(1.0 - sin_delta**2 * sin_phi**2)
    omega_ratio = cos_delta / denominator

    # Torque ratio: τ_out/τ_in = 1/(ω_out/ω_in) from power conservation
    tau_ratio = denominator / cos_delta

    return omega_ratio, tau_ratio


def distribute_torque_by_grip_angle(
    torque_transmitted: float | np.ndarray[Any, Any],
    theta_grip_rad: float,
) -> tuple[float | np.ndarray[Any, Any], float | np.ndarray[Any, Any]]:
    """Distribute transmitted torque to club axes based on grip angle.

    Args:
    ----
        torque_transmitted: Torque transmitted through universal joint (N·m).
        theta_grip_rad: Grip angle in radians.

    Returns:
    -------
        A tuple containing:
            - torque_alpha: Torque to higher MOI axis (N·m).
            - torque_gamma: Torque to lowest MOI axis (N·m).

    """
    torque_alpha = torque_transmitted * np.sin(theta_grip_rad)
    torque_gamma = torque_transmitted * np.cos(theta_grip_rad)

    return torque_alpha, torque_gamma


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
        A tuple containing:
            - torque: Generated torque signal array.
            - error: Error message string, or None if successful.

    """
    require(len(t) > 0, "time array must not be empty")
    error: str | None = None
    torque: np.ndarray[Any, Any]

    if noise_type == "Golf-like Random":
        torque = rng.normal(0, 1, len(t))
        torque += np.exp(-50 * (t - 0.5) ** 2) * 8 * rng.standard_normal(len(t))
        torque = np.convolve(torque, np.ones(10) / 10, mode="same")
    elif noise_type == "Step":
        torque = np.zeros_like(t)
        torque[250:] = 3.0  # Step at midpoint
    elif noise_type == "Pulse":
        torque = np.zeros_like(t)
        pulse_start = 200
        pulse_end = 300
        torque[pulse_start:pulse_end] = 5.0 * rng.standard_normal(pulse_end - pulse_start)
    elif noise_type == "Burst":
        torque = np.zeros_like(t)
        burst_center = 250
        burst_width = 50
        burst_indices = np.arange(
            max(0, burst_center - burst_width),
            min(len(t), burst_center + burst_width),
        )
        torque[burst_indices] = rng.normal(0, 3, len(burst_indices))
    elif noise_type == "Sinusoidal":
        torque = 2.0 * np.sin(8 * np.pi * t)
    elif noise_type == "Random":
        torque = rng.normal(0, 1.5, len(t))
        torque = np.convolve(torque, np.ones(10) / 10, mode="same")
    elif noise_type == "Polynomial":
        torque, error = _evaluate_polynomial(t, polynomial_expression)
    else:
        # Default to golf-like
        torque = rng.normal(0, 1, len(t))
        torque += np.exp(-50 * (t - 0.5) ** 2) * 8 * rng.standard_normal(len(t))
        torque = np.convolve(torque, np.ones(10) / 10, mode="same")

    return torque, error


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
        A tuple containing:
            - torque: Evaluated result array.
            - error: Error message string, or None if successful.

    """
    try:
        evaluator = EvalWithCompoundTypes(
            names={
                "t": t,
                "pi": np.pi,
                "e": np.e,
            },
            functions={
                "sin": np.sin,
                "cos": np.cos,
                "exp": np.exp,
                "sqrt": np.sqrt,
                "log": np.log,
            },
        )
        result = evaluator.eval(expression)
        if isinstance(result, np.ndarray):
            if result.shape != t.shape:
                return (
                    t**2 - t,
                    f"Polynomial result shape {result.shape} does not match "
                    f"time array shape {t.shape}.",
                )
            return result, None
        return np.full_like(t, float(result)), None
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
