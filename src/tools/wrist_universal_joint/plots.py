"""Time-series plot functions for the Wrist Universal Joint model.

This module contains matplotlib-based plotting functions:
- Torque vs time plots
- Angular acceleration vs time plots
- Transmission ratio sweep plots
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
from matplotlib.figure import Figure

from src.core.contracts import check_positive, check_range

from .enhanced_model_kinematics import (
    compute_acceleration_signals as _compute_acceleration_signals_core,
)
from .enhanced_model_kinematics import (
    compute_torque_signals as _compute_torque_signals_core,
)
from .enhanced_model_kinematics import (
    compute_transmission_sweep as _compute_transmission_sweep_core,
)

logger = logging.getLogger(__name__)


def _compute_torque_signals(
    input_torque: np.ndarray[Any, Any],
    grip_angle_deg: float,
    wrist_angle_deg: float,
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any], np.ndarray[Any, Any], float]:
    """Compute torque signal components for the given angles."""
    signals = _compute_torque_signals_core(input_torque, grip_angle_deg, wrist_angle_deg)
    return (
        signals.torque_transmitted,
        signals.torque_alpha,
        signals.torque_gamma,
        signals.tau_ratio,
    )


def _plot_torque_lines(
    ax: Any,
    t: np.ndarray[Any, Any],
    input_torque: np.ndarray[Any, Any],
    torque_transmitted: np.ndarray[Any, Any],
    torque_alpha: np.ndarray[Any, Any],
    torque_gamma: np.ndarray[Any, Any],
    tau_ratio: float,
    show_input: bool,
    show_transmitted: bool,
    show_alpha: bool,
    show_gamma: bool,
) -> None:
    """Draw torque signal lines on the given axes."""
    if show_input:
        ax.plot(
            t, input_torque, label="Input Torque (forearm)", color="gray", alpha=0.7, linewidth=1.5
        )  # noqa: E501
    if show_transmitted:
        ax.plot(
            t,
            torque_transmitted,
            label=f"Transmitted (ratio={tau_ratio:.3f})",
            color="purple",
            linewidth=2,
        )  # noqa: E501
    if show_alpha:
        ax.plot(t, torque_alpha, label="\u03c4_\u03b1 (higher MOI axis)", color="red", linewidth=2)
    if show_gamma:
        ax.plot(t, torque_gamma, label="\u03c4_\u03b3 (lowest MOI axis)", color="blue", linewidth=2)


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

    fig = Figure(figsize=(10, 6))
    ax = fig.subplots()
    torque_transmitted, torque_alpha, torque_gamma, tau_ratio = _compute_torque_signals(
        input_torque, grip_angle_deg, wrist_angle_deg
    )
    _plot_torque_lines(
        ax,
        t,
        input_torque,
        torque_transmitted,
        torque_alpha,
        torque_gamma,
        tau_ratio,
        show_input,
        show_transmitted,
        show_alpha,
        show_gamma,
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
    fig.tight_layout()
    return fig


def _compute_acceleration_signals(
    input_torque: np.ndarray[Any, Any],
    grip_angle_deg: float,
    wrist_angle_deg: float,
    i_alpha: float,
    i_gamma: float,
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """Compute angular acceleration signals for both axes."""
    signals = _compute_acceleration_signals_core(
        input_torque,
        grip_angle_deg,
        wrist_angle_deg,
        i_alpha,
        i_gamma,
    )
    return signals.accel_alpha, signals.accel_gamma


def _plot_acceleration_series(
    ax: Any,
    t: np.ndarray[Any, Any],
    accel_alpha: np.ndarray[Any, Any],
    accel_gamma: np.ndarray[Any, Any],
    i_alpha: float,
    i_gamma: float,
    show_alpha: bool,
    show_gamma: bool,
) -> None:
    """Draw the alpha/gamma acceleration curves that are enabled for display."""
    if show_alpha:
        ax.plot(
            t,
            accel_alpha,
            label=f"\u03b1_\u03b1 (I_\u03b1={i_alpha:.4f})",
            color="red",
            linewidth=2,
            linestyle="--",
        )  # noqa: E501
    if show_gamma:
        ax.plot(
            t,
            accel_gamma,
            label=f"\u03b1_\u03b3 (I_\u03b3={i_gamma:.4f})",
            color="blue",
            linewidth=2,
            linestyle="--",
        )  # noqa: E501


def _style_acceleration_axes(ax: Any, grip_angle_deg: float, wrist_angle_deg: float) -> None:
    """Apply title, labels, grid, and legend to an acceleration plot axes object."""
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

    fig = Figure(figsize=(10, 6))
    ax = fig.subplots()
    accel_alpha, accel_gamma = _compute_acceleration_signals(
        input_torque, grip_angle_deg, wrist_angle_deg, i_alpha, i_gamma
    )
    _plot_acceleration_series(
        ax, t, accel_alpha, accel_gamma, i_alpha, i_gamma, show_alpha, show_gamma
    )
    _style_acceleration_axes(ax, grip_angle_deg, wrist_angle_deg)
    fig.tight_layout()
    return fig


def _compute_transmission_sweep(
    phi_sweep_deg: np.ndarray[Any, Any],
    theta_grip_rad: float,
    i_alpha: float,
    i_gamma: float,
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any], np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """Compute transmission ratios across a wrist angle sweep."""
    del phi_sweep_deg
    sweep = _compute_transmission_sweep_core(np.degrees(theta_grip_rad), 0.0, i_alpha, i_gamma)
    return (
        sweep.tau_ratios,
        sweep.omega_ratios,
        sweep.accel_alpha_ratios,
        sweep.accel_gamma_ratios,
    )


def _plot_transmission_series(
    ax: Any,
    phi_sweep: np.ndarray[Any, Any],
    tau_ratios: np.ndarray[Any, Any],
    omega_ratios: np.ndarray[Any, Any],
    accel_alpha_ratios: np.ndarray[Any, Any],
    accel_gamma_ratios: np.ndarray[Any, Any],
    show_transmission: bool,
    show_velocity: bool,
    show_accel_alpha: bool,
    show_accel_gamma: bool,
) -> None:
    """Draw transmission ratio series lines on the given axes."""
    if show_transmission:
        ax.plot(
            phi_sweep,
            tau_ratios,
            label="Torque Transmission Ratio (\u03c4_out/\u03c4_in)",
            color="purple",
            linewidth=2.5,
        )  # noqa: E501
    if show_velocity:
        ax.plot(
            phi_sweep,
            omega_ratios,
            label="Velocity Ratio (\u03c9_out/\u03c9_in)",
            color="orange",
            linewidth=2,
            linestyle="--",
        )  # noqa: E501
    if show_accel_alpha:
        ax.plot(
            phi_sweep,
            accel_alpha_ratios,
            label="Accel_\u03b1 ratio (rad/s\u00b2)/(N\u00b7m)",
            color="red",
            linewidth=1.5,
            alpha=0.7,
        )  # noqa: E501
    if show_accel_gamma:
        ax.plot(
            phi_sweep,
            accel_gamma_ratios,
            label="Accel_\u03b3 ratio (rad/s\u00b2)/(N\u00b7m)",
            color="blue",
            linewidth=1.5,
            alpha=0.7,
        )  # noqa: E501


def _annotate_current_wrist_angle(
    ax: Any,
    phi_sweep: np.ndarray[Any, Any],
    wrist_angle_deg: float,
    tau_ratios: np.ndarray[Any, Any],
    show_transmission: bool,
) -> None:
    """Annotate the current wrist angle with a vertical line and optional dot."""
    current_idx = np.argmin(np.abs(phi_sweep - wrist_angle_deg))
    ax.axvline(
        wrist_angle_deg,
        color="green",
        linestyle=":",
        linewidth=2,
        label=f"Current wrist angle ({wrist_angle_deg:.0f}\u00b0)",
    )  # noqa: E501
    if show_transmission:
        ax.plot(
            wrist_angle_deg, tau_ratios[current_idx], "go", markersize=10, markerfacecolor="lime"
        )  # noqa: E501
    ax.axhline(1.0, color="gray", linestyle="--", alpha=0.5, linewidth=1)


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

    fig = Figure(figsize=(10, 6))
    ax = fig.subplots()
    tau_ratios, omega_ratios, accel_alpha_ratios, accel_gamma_ratios = _compute_transmission_sweep(
        np.linspace(-60, 60, 200), np.radians(grip_angle_deg), i_alpha, i_gamma
    )
    phi_sweep = np.linspace(-60, 60, len(tau_ratios))
    _plot_transmission_series(
        ax,
        phi_sweep,
        tau_ratios,
        omega_ratios,
        accel_alpha_ratios,
        accel_gamma_ratios,
        show_transmission,
        show_velocity,
        show_accel_alpha,
        show_accel_gamma,
    )
    _annotate_current_wrist_angle(ax, phi_sweep, wrist_angle_deg, tau_ratios, show_transmission)
    ax.set_title(
        f"Universal Joint Transmission vs Wrist Deviation Angle (Grip={grip_angle_deg:.0f}\u00b0)",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("Wrist Deviation Angle (degrees)", fontsize=10)
    ax.set_ylabel("Transmission Ratio", fontsize=10)
    ax.grid(visible=True, alpha=0.3)
    ax.legend(loc="best", fontsize=9)
    fig.tight_layout()
    return fig
