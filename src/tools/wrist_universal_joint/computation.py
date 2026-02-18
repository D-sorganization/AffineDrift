"""Shared computation pipelines for the Wrist Universal Joint model.

This module consolidates duplicated transmission/torque computation
patterns used across plots.py and streamlit_app.py.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from .constants import EPSILON
from .torque_calculator import (
    distribute_torque_by_grip_angle,
    universal_joint_transmission_ratio,
)


def compute_transmission_pipeline(
    grip_angle_deg: float,
    wrist_angle_deg: float,
    input_torque: float | np.ndarray[Any, Any],
) -> dict[str, Any]:
    """Compute full transmission pipeline from angles to distributed torques.

    Args:
        grip_angle_deg: Grip angle in degrees.
        wrist_angle_deg: Wrist deviation angle in degrees.
        input_torque: Input torque value(s) in N·m.

    Returns:
        Dictionary with keys: theta_grip_rad, phi_wrist_rad, omega_ratio,
        tau_ratio, torque_transmitted, torque_alpha, torque_gamma.
    """
    theta_grip_rad = np.radians(grip_angle_deg)
    phi_wrist_rad = np.radians(wrist_angle_deg)
    omega_ratio, tau_ratio = universal_joint_transmission_ratio(phi_wrist_rad, theta_grip_rad)
    torque_transmitted = input_torque * tau_ratio
    torque_alpha, torque_gamma = distribute_torque_by_grip_angle(torque_transmitted, theta_grip_rad)
    return {
        "theta_grip_rad": theta_grip_rad,
        "phi_wrist_rad": phi_wrist_rad,
        "omega_ratio": omega_ratio,
        "tau_ratio": tau_ratio,
        "torque_transmitted": torque_transmitted,
        "torque_alpha": torque_alpha,
        "torque_gamma": torque_gamma,
    }


def compute_angular_accelerations(
    torque_alpha: float | np.ndarray[Any, Any],
    torque_gamma: float | np.ndarray[Any, Any],
    i_alpha: float,
    i_gamma: float,
) -> tuple[np.ndarray[Any, Any] | float, np.ndarray[Any, Any] | float]:
    """Compute angular accelerations from torques and moments of inertia.

    Args:
        torque_alpha: Torque about alpha axis (N·m).
        torque_gamma: Torque about gamma axis (N·m).
        i_alpha: Moment of inertia about alpha axis (kg·m²).
        i_gamma: Moment of inertia about gamma axis (kg·m²).

    Returns:
        Tuple of (accel_alpha, accel_gamma) in rad/s².
    """
    accel_alpha = torque_alpha / i_alpha if i_alpha > EPSILON else np.zeros_like(torque_alpha)
    accel_gamma = torque_gamma / i_gamma if i_gamma > EPSILON else np.zeros_like(torque_gamma)
    return accel_alpha, accel_gamma


def format_plot_axes(
    ax: Any,
    title: str,
    xlabel: str,
    ylabel: str,
) -> None:
    """Apply consistent axis formatting to a matplotlib axes.

    Args:
        ax: Matplotlib axes object.
        title: Plot title.
        xlabel: X-axis label.
        ylabel: Y-axis label.
    """
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.grid(visible=True, alpha=0.3)
    ax.legend(loc="best", fontsize=9)
