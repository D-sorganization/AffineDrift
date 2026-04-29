"""Kinematic helpers for the enhanced wrist universal joint Qt app."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .torque_calculator import (
    distribute_torque_by_grip_angle,
    universal_joint_transmission_ratio,
)

_EPSILON = 1e-6


@dataclass(frozen=True, slots=True)
class TorqueSignals:
    """Torque traces and ratios for a single wrist/grip configuration."""

    omega_ratio: float
    tau_ratio: float
    torque_transmitted: np.ndarray[Any, Any]
    torque_alpha: np.ndarray[Any, Any]
    torque_gamma: np.ndarray[Any, Any]


@dataclass(frozen=True, slots=True)
class AccelerationSignals:
    """Angular acceleration traces for the alpha and gamma axes."""

    accel_alpha: np.ndarray[Any, Any]
    accel_gamma: np.ndarray[Any, Any]


@dataclass(frozen=True, slots=True)
class TransmissionSweep:
    """Transmission ratios across a wrist-angle sweep."""

    wrist_angle_deg: np.ndarray[Any, Any]
    omega_ratios: np.ndarray[Any, Any]
    tau_ratios: np.ndarray[Any, Any]
    accel_alpha_ratios: np.ndarray[Any, Any]
    accel_gamma_ratios: np.ndarray[Any, Any]


def compute_torque_signals(
    input_torque: np.ndarray[Any, Any],
    grip_angle_deg: float,
    wrist_angle_deg: float,
) -> TorqueSignals:
    """Compute transmitted and distributed torque signals."""
    theta_grip_rad = np.radians(grip_angle_deg)
    phi_wrist_rad = np.radians(wrist_angle_deg)
    omega_ratio, tau_ratio = universal_joint_transmission_ratio(
        phi_rad=phi_wrist_rad,
        delta_rad=theta_grip_rad,
    )
    torque_transmitted = input_torque * tau_ratio
    torque_alpha, torque_gamma = distribute_torque_by_grip_angle(
        torque_transmitted,
        theta_grip_rad,
    )
    return TorqueSignals(
        omega_ratio=omega_ratio,
        tau_ratio=tau_ratio,
        torque_transmitted=np.asarray(torque_transmitted),
        torque_alpha=np.asarray(torque_alpha),
        torque_gamma=np.asarray(torque_gamma),
    )


def compute_acceleration_signals(
    input_torque: np.ndarray[Any, Any],
    grip_angle_deg: float,
    wrist_angle_deg: float,
    i_alpha: float,
    i_gamma: float,
) -> AccelerationSignals:
    """Compute angular acceleration traces for the configured inertias."""
    torque = compute_torque_signals(input_torque, grip_angle_deg, wrist_angle_deg)
    accel_alpha = (
        torque.torque_alpha / i_alpha if i_alpha > _EPSILON else np.zeros_like(torque.torque_alpha)
    )
    accel_gamma = (
        torque.torque_gamma / i_gamma if i_gamma > _EPSILON else np.zeros_like(torque.torque_gamma)
    )
    return AccelerationSignals(
        accel_alpha=np.asarray(accel_alpha),
        accel_gamma=np.asarray(accel_gamma),
    )


def compute_transmission_sweep(
    grip_angle_deg: float,
    wrist_angle_deg: float,
    i_alpha: float,
    i_gamma: float,
) -> TransmissionSweep:
    """Compute transmission metrics across a wrist-angle sweep."""
    del wrist_angle_deg  # Included for API symmetry with the live-configuration helpers.
    phi_sweep = np.linspace(-60, 60, 200)
    theta_grip_rad = np.radians(grip_angle_deg)
    omega_ratios: list[float] = []
    tau_ratios: list[float] = []
    accel_alpha_ratios: list[float] = []
    accel_gamma_ratios: list[float] = []

    for phi_rad in np.radians(phi_sweep):
        omega_ratio, tau_ratio = universal_joint_transmission_ratio(
            phi_rad=phi_rad,
            delta_rad=theta_grip_rad,
        )
        omega_ratios.append(omega_ratio)
        tau_ratios.append(tau_ratio)

        torque_alpha, torque_gamma = distribute_torque_by_grip_angle(tau_ratio, theta_grip_rad)
        accel_alpha_ratios.append(float(torque_alpha) / i_alpha if i_alpha > _EPSILON else 0.0)
        accel_gamma_ratios.append(float(torque_gamma) / i_gamma if i_gamma > _EPSILON else 0.0)

    return TransmissionSweep(
        wrist_angle_deg=phi_sweep,
        omega_ratios=np.asarray(omega_ratios),
        tau_ratios=np.asarray(tau_ratios),
        accel_alpha_ratios=np.asarray(accel_alpha_ratios),
        accel_gamma_ratios=np.asarray(accel_gamma_ratios),
    )


def build_info_html(
    grip_angle_deg: int,
    wrist_angle_deg: int,
) -> str:
    """Build the HTML summary shown in the info panel."""
    _omega_ratio, tau_ratio = universal_joint_transmission_ratio(
        phi_rad=np.radians(wrist_angle_deg),
        delta_rad=np.radians(grip_angle_deg),
    )
    return f"""
        <b>Current Configuration:</b><br>
        Grip={grip_angle_deg}°, Wrist={wrist_angle_deg}° → Transmission Ratio = {tau_ratio:.3f}<br>
        <br>
        <b>Key Insights:</b><br>
        • Transmission ratio <b>varies with wrist angle</b> (see transmission plot)<br>
        • At neutral wrist (φ≈0°): Maximum transmission efficiency<br>
        • At extreme radial/ulnar deviation: Reduced transmission<br>
        • Grip angle determines <b>which axes</b> receive transmitted torque<br>
        • Lower grip angle (fingers) → more torque to lowest MOI axis (γ) (stability)<br>
        • Higher grip angle (palm) → more torque to higher MOI axis (α) (face angle control)
        """
