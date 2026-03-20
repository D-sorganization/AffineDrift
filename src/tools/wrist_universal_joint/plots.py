"""Time-series plot functions for the Wrist Universal Joint model.

This module contains matplotlib-based plotting functions:
- Torque vs time plots
- Angular acceleration vs time plots
- Transmission ratio sweep plots
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from src.core.contracts import check_positive, check_range

from .constants import EPSILON
from .torque_calculator import (
    distribute_torque_by_grip_angle,
    universal_joint_transmission_ratio,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from matplotlib.figure import Figure


# Cache figure generation to prevent expensive redraws
# Limit entries to prevent OOM when sliding through many angles
@st.cache_resource(max_entries=20)  # type: ignore[untyped-decorator]
def plot_torque(
    t: np.ndarray[Any, Any],
    input_torque: np.ndarray[Any, Any],
    grip_angle_deg: float,
    wrist_angle_deg: float,
    i_alpha: float,
    i_gamma: float,
    show_input: bool,
    show_transmitted: bool,
    show_alpha: bool,
    show_gamma: bool,
) -> Figure:
    """Plot torque vs time."""
    check_range(grip_angle_deg, 0, 90, "grip_angle_deg")
    check_range(wrist_angle_deg, -60, 60, "wrist_angle_deg")
    check_positive(i_alpha, "i_alpha")
    check_positive(i_gamma, "i_gamma")

    fig, ax = plt.subplots(figsize=(10, 6))

    theta_grip_rad = np.radians(grip_angle_deg)
    phi_wrist_rad = np.radians(wrist_angle_deg)

    _omega_ratio, tau_ratio = universal_joint_transmission_ratio(
        phi_wrist_rad,
        theta_grip_rad,
    )
    torque_transmitted = input_torque * tau_ratio
    torque_alpha, torque_gamma = distribute_torque_by_grip_angle(
        torque_transmitted,
        theta_grip_rad,
    )

    if show_input:
        ax.plot(
            t,
            input_torque,
            label="Input Torque (forearm)",
            color="gray",
            alpha=0.7,
            linewidth=1.5,
        )
    if show_transmitted:
        ax.plot(
            t,
            torque_transmitted,
            label=f"Transmitted (ratio={tau_ratio:.3f})",
            color="purple",
            linewidth=2,
        )
    if show_alpha:
        ax.plot(
            t,
            torque_alpha,
            label="\u03c4_\u03b1 (higher MOI axis)",
            color="red",
            linewidth=2,
        )
    if show_gamma:
        ax.plot(
            t,
            torque_gamma,
            label="\u03c4_\u03b3 (lowest MOI axis)",
            color="blue",
            linewidth=2,
        )

    ax.set_title(
        f"Torque vs Time (Grip: {grip_angle_deg:.0f}\u00b0, Wrist: {wrist_angle_deg:.0f}\u00b0)",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("Time (s)", fontsize=10)
    ax.set_ylabel("Torque (N\u00b7m)", fontsize=10)
    ax.grid(visible=True, alpha=0.3)
    ax.legend(loc="best", fontsize=9)

    plt.tight_layout()
    return fig


# Cache figure generation to prevent expensive redraws
# Limit entries to prevent OOM when sliding through many angles
@st.cache_resource(max_entries=20)  # type: ignore[untyped-decorator]
def plot_acceleration(
    t: np.ndarray[Any, Any],
    input_torque: np.ndarray[Any, Any],
    grip_angle_deg: float,
    wrist_angle_deg: float,
    i_alpha: float,
    i_gamma: float,
    show_alpha: bool,
    show_gamma: bool,
) -> Figure:
    """Plot angular acceleration vs time."""
    check_range(grip_angle_deg, 0, 90, "grip_angle_deg")
    check_range(wrist_angle_deg, -60, 60, "wrist_angle_deg")
    check_positive(i_alpha, "i_alpha")
    check_positive(i_gamma, "i_gamma")

    fig, ax = plt.subplots(figsize=(10, 6))

    theta_grip_rad = np.radians(grip_angle_deg)
    phi_wrist_rad = np.radians(wrist_angle_deg)

    _omega_ratio, tau_ratio = universal_joint_transmission_ratio(
        phi_wrist_rad,
        theta_grip_rad,
    )
    torque_transmitted = input_torque * tau_ratio
    torque_alpha, torque_gamma = distribute_torque_by_grip_angle(
        torque_transmitted,
        theta_grip_rad,
    )
    accel_alpha = torque_alpha / i_alpha if i_alpha > EPSILON else np.zeros_like(torque_alpha)
    accel_gamma = torque_gamma / i_gamma if i_gamma > EPSILON else np.zeros_like(torque_gamma)

    if show_alpha:
        ax.plot(
            t,
            accel_alpha,
            label=f"\u03b1_\u03b1 (I_\u03b1={i_alpha:.4f})",
            color="red",
            linewidth=2,
            linestyle="--",
        )
    if show_gamma:
        ax.plot(
            t,
            accel_gamma,
            label=f"\u03b1_\u03b3 (I_\u03b3={i_gamma:.4f})",
            color="blue",
            linewidth=2,
            linestyle="--",
        )

    ax.set_title(
        f"Angular Acceleration vs Time (Grip: {grip_angle_deg:.0f}\u00b0, "
        f"Wrist: {wrist_angle_deg:.0f}\u00b0)",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("Time (s)", fontsize=10)
    ax.set_ylabel("Angular Acceleration (rad/s\u00b2)", fontsize=10)
    ax.grid(visible=True, alpha=0.3)
    ax.legend(loc="best", fontsize=9)

    plt.tight_layout()
    return fig


def _compute_transmission_sweep(
    phi_sweep_deg: np.ndarray[Any, Any],
    theta_grip_rad: float,
    i_alpha: float,
    i_gamma: float,
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any], np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """Compute transmission ratios across a wrist angle sweep.

    Args:
        phi_sweep_deg: Array of wrist deviation angles in degrees.
        theta_grip_rad: Grip angle in radians.
        i_alpha: Moment of inertia about the alpha axis.
        i_gamma: Moment of inertia about the gamma axis.

    Returns:
        Tuple of (tau_ratios, omega_ratios, accel_alpha_ratios, accel_gamma_ratios).
    """
    phi_sweep_rad = np.radians(phi_sweep_deg)
    omega_ratios_list: list[float] = []
    tau_ratios_list: list[float] = []
    accel_alpha_ratios_list: list[float] = []
    accel_gamma_ratios_list: list[float] = []

    for phi_rad in phi_sweep_rad:
        omega_r, tau_r = universal_joint_transmission_ratio(phi_rad, theta_grip_rad)
        omega_ratios_list.append(omega_r)
        tau_ratios_list.append(tau_r)

        torque_trans = 1.0 * tau_r
        t_alpha, t_gamma = distribute_torque_by_grip_angle(torque_trans, theta_grip_rad)
        t_alpha_val = float(t_alpha) if isinstance(t_alpha, float | int) else t_alpha.item()
        t_gamma_val = float(t_gamma) if isinstance(t_gamma, float | int) else t_gamma.item()

        accel_alpha_ratios_list.append(t_alpha_val / i_alpha if i_alpha > EPSILON else 0.0)
        accel_gamma_ratios_list.append(t_gamma_val / i_gamma if i_gamma > EPSILON else 0.0)

    return (
        np.array(tau_ratios_list),
        np.array(omega_ratios_list),
        np.array(accel_alpha_ratios_list),
        np.array(accel_gamma_ratios_list),
    )


# Cache figure generation to prevent expensive redraws
# Limit entries to prevent OOM when sliding through many angles
@st.cache_resource(max_entries=20)  # type: ignore[untyped-decorator]
def plot_transmission_sweep(
    grip_angle_deg: float,
    wrist_angle_deg: float,
    i_alpha: float,
    i_gamma: float,
    show_transmission: bool,
    show_velocity: bool,
    show_accel_alpha: bool,
    show_accel_gamma: bool,
) -> Figure:
    """Plot transmission ratio vs wrist angle sweep."""
    check_range(grip_angle_deg, 0, 90, "grip_angle_deg")
    check_range(wrist_angle_deg, -60, 60, "wrist_angle_deg")
    check_positive(i_alpha, "i_alpha")
    check_positive(i_gamma, "i_gamma")

    fig, ax = plt.subplots(figsize=(10, 6))

    theta_grip_rad = np.radians(grip_angle_deg)
    phi_sweep = np.linspace(-60, 60, 200)

    tau_ratios, omega_ratios, accel_alpha_ratios, accel_gamma_ratios = _compute_transmission_sweep(
        phi_sweep, theta_grip_rad, i_alpha, i_gamma
    )

    if show_transmission:
        ax.plot(
            phi_sweep,
            tau_ratios,
            label="Torque Transmission Ratio (\u03c4_out/\u03c4_in)",
            color="purple",
            linewidth=2.5,
        )
    if show_velocity:
        ax.plot(
            phi_sweep,
            omega_ratios,
            label="Velocity Ratio (\u03c9_out/\u03c9_in)",
            color="orange",
            linewidth=2,
            linestyle="--",
        )
    if show_accel_alpha:
        ax.plot(
            phi_sweep,
            accel_alpha_ratios,
            label="Accel_\u03b1 ratio (rad/s\u00b2)/(N\u00b7m)",
            color="red",
            linewidth=1.5,
            alpha=0.7,
        )
    if show_accel_gamma:
        ax.plot(
            phi_sweep,
            accel_gamma_ratios,
            label="Accel_\u03b3 ratio (rad/s\u00b2)/(N\u00b7m)",
            color="blue",
            linewidth=1.5,
            alpha=0.7,
        )

    # Mark current wrist angle
    current_idx = np.argmin(np.abs(phi_sweep - wrist_angle_deg))
    ax.axvline(
        wrist_angle_deg,
        color="green",
        linestyle=":",
        linewidth=2,
        label=f"Current wrist angle ({wrist_angle_deg:.0f}\u00b0)",
    )
    if show_transmission:
        ax.plot(
            wrist_angle_deg,
            tau_ratios[current_idx],
            "go",
            markersize=10,
            markerfacecolor="lime",
        )

    ax.axhline(1.0, color="gray", linestyle="--", alpha=0.5, linewidth=1)

    ax.set_title(
        f"Universal Joint Transmission vs Wrist Deviation Angle (Grip={grip_angle_deg:.0f}\u00b0)",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("Wrist Deviation Angle (degrees)", fontsize=10)
    ax.set_ylabel("Transmission Ratio", fontsize=10)
    ax.grid(visible=True, alpha=0.3)
    ax.legend(loc="best", fontsize=9)

    plt.tight_layout()
    return fig
