"""Visualization functions for the Wrist Universal Joint model.

This module contains all matplotlib-based plotting and diagram functions:
- Forearm-hand-club anatomical diagram
- Torque vs time plots
- Angular acceleration vs time plots
- Transmission ratio sweep plots
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.patches import Ellipse, Polygon

from .constants import EPSILON
from .torque_calculator import (
    distribute_torque_by_grip_angle,
    universal_joint_transmission_ratio,
)

if TYPE_CHECKING:
    from matplotlib.figure import Figure


# ⚡ Bolt Optimization: Cache figure generation to prevent expensive redraws
# Limit entries to prevent OOM when sliding through many angles
@st.cache_resource(max_entries=20)
def draw_diagram(
    grip_angle_deg: float,
    wrist_angle_deg: float,
) -> Figure:
    """Draw the forearm-hand-club diagram."""
    fig, ax = plt.subplots(figsize=(12, 4))

    theta_grip_rad = np.radians(grip_angle_deg)
    phi_wrist_rad = np.radians(wrist_angle_deg)

    # Coordinate system: club is always horizontal, clubhead on left pointing up
    wrist_x = 0.4
    wrist_y = 0.5

    # Club shaft: always horizontal, extends left from hand midpoint (wrist)
    shaft_length = 1.05  # 3x longer
    hand_length = 0.2
    hand_dir_x = np.cos(theta_grip_rad)
    hand_dir_y = np.sin(theta_grip_rad)
    shaft_attach_x = wrist_x
    shaft_attach_y = wrist_y
    shaft_end_x = shaft_attach_x - shaft_length
    shaft_end_y = shaft_attach_y

    # Draw club shaft (horizontal)
    ax.plot(
        [shaft_end_x, shaft_attach_x],
        [shaft_end_y, shaft_attach_y],
        "k-",
        linewidth=8,
        solid_capstyle="round",
        label="Club Shaft",
        zorder=3,
    )

    # Clubhead: on left end, pointing up, trapezoid shape, tilted 30 degrees
    clubhead_width_base = 0.08
    clubhead_width_bottom = clubhead_width_base / 3
    clubhead_width_top = clubhead_width_base * 4 / 3
    clubhead_height = 0.24
    clubhead_angle_deg = 30
    clubhead_angle_rad = np.radians(clubhead_angle_deg)

    clubhead_base_x = shaft_end_x
    clubhead_base_y = shaft_end_y

    corners = np.array(
        [
            [-clubhead_width_bottom / 2, 0],
            [clubhead_width_bottom / 2, 0],
            [clubhead_width_top / 2, clubhead_height],
            [-clubhead_width_top / 2, clubhead_height],
        ],
    )

    cos_a = np.cos(clubhead_angle_rad)
    sin_a = np.sin(clubhead_angle_rad)
    rotation_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
    rotated_corners = corners @ rotation_matrix.T

    rotated_corners[:, 0] += clubhead_base_x
    rotated_corners[:, 1] += clubhead_base_y

    clubhead = Polygon(
        rotated_corners,
        facecolor="silver",
        alpha=0.9,
        edgecolor="gray",
        linewidth=2,
        zorder=4,
    )
    ax.add_patch(clubhead)

    # Hand: attached at midpoint to wrist, rotated by grip angle
    hand_width = 0.12
    hand_center_x = wrist_x
    hand_center_y = wrist_y

    hand = Ellipse(
        (hand_center_x, hand_center_y),
        hand_length,
        hand_width,
        angle=np.degrees(theta_grip_rad),
        facecolor="tan",
        alpha=0.8,
        edgecolor="saddlebrown",
        linewidth=2,
        zorder=6,
    )
    ax.add_patch(hand)

    # Draw 4 fingers on hand
    _draw_fingers(ax, hand_center_x, hand_center_y, hand_dir_x, hand_dir_y)

    # Forearm: attached to hand at long axis endpoints
    _draw_forearm(
        ax,
        wrist_x,
        wrist_y,
        hand_length,
        hand_dir_x,
        hand_dir_y,
        theta_grip_rad,
        phi_wrist_rad,
    )

    # Draw wrist joint
    ax.plot(wrist_x, wrist_y, "ko", markersize=12, zorder=10)
    ax.text(
        wrist_x,
        wrist_y - 0.1,
        "Wrist Joint",
        ha="center",
        fontsize=10,
        fontweight="bold",
        zorder=11,
    )

    # Draw grip angle arc (θ_grip)
    _draw_grip_angle_arc(ax, wrist_x, wrist_y, theta_grip_rad)

    # Draw wrist angle arc (φ)
    hand_endpoint_forearm_x = wrist_x + (hand_length / 2) * hand_dir_x
    hand_endpoint_forearm_y = wrist_y + (hand_length / 2) * hand_dir_y
    _draw_wrist_angle_arc(
        ax,
        hand_endpoint_forearm_x,
        hand_endpoint_forearm_y,
        theta_grip_rad,
        phi_wrist_rad,
    )

    ax.set_xlim(-1.5, 0.8)
    ax.set_ylim(-0.2, 1.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Forearm-Hand-Club Diagram", fontsize=12, fontweight="bold", pad=20)

    plt.tight_layout()
    return fig


def _draw_fingers(
    ax: Any,
    hand_center_x: float,
    hand_center_y: float,
    hand_dir_x: float,
    hand_dir_y: float,
) -> None:
    """Draw 4 fingers on the hand."""
    finger_length = 0.12
    finger_width = 0.015
    finger_dir_x = -hand_dir_x
    finger_dir_y = -hand_dir_y

    perp_to_hand_x = -hand_dir_y
    perp_to_hand_y = hand_dir_x
    finger_spacing = 0.03
    finger_positions = [-1.2, -0.4, 0.4, 1.2]

    for pos in finger_positions:
        base_x = hand_center_x + pos * finger_spacing * perp_to_hand_x
        base_y = hand_center_y + pos * finger_spacing * perp_to_hand_y
        tip_x = base_x + finger_length * finger_dir_x
        tip_y = base_y + finger_length * finger_dir_y
        finger_mid_x = (base_x + tip_x) / 2
        finger_mid_y = (base_y + tip_y) / 2
        finger_angle = np.rad2deg(np.arctan2(finger_dir_y, finger_dir_x))
        finger = Ellipse(
            (finger_mid_x, finger_mid_y),
            finger_length,
            finger_width,
            angle=finger_angle,
            facecolor="tan",
            alpha=0.9,
            edgecolor="saddlebrown",
            linewidth=1,
            zorder=7,
        )
        ax.add_patch(finger)


def _draw_forearm(
    ax: Any,
    wrist_x: float,
    wrist_y: float,
    hand_length: float,
    hand_dir_x: float,
    hand_dir_y: float,
    theta_grip_rad: float,
    phi_wrist_rad: float,
) -> None:
    """Draw the forearm attached to the hand."""
    forearm_angle_rad = theta_grip_rad + phi_wrist_rad + np.pi
    forearm_length = 0.35
    forearm_width = 0.1

    hand_endpoint_forearm_x = wrist_x + (hand_length / 2) * hand_dir_x
    hand_endpoint_forearm_y = wrist_y + (hand_length / 2) * hand_dir_y

    forearm_dir_x = np.cos(forearm_angle_rad)
    forearm_dir_y = np.sin(forearm_angle_rad)
    forearm_center_x = hand_endpoint_forearm_x - (forearm_length / 2) * forearm_dir_x
    forearm_center_y = hand_endpoint_forearm_y - (forearm_length / 2) * forearm_dir_y

    forearm = Ellipse(
        (forearm_center_x, forearm_center_y),
        forearm_length,
        forearm_width,
        angle=np.degrees(forearm_angle_rad),
        facecolor="tan",
        alpha=0.8,
        edgecolor="saddlebrown",
        linewidth=2,
        zorder=5,
    )
    ax.add_patch(forearm)


def _draw_grip_angle_arc(
    ax: Any,
    wrist_x: float,
    wrist_y: float,
    theta_grip_rad: float,
) -> None:
    """Draw the grip angle arc annotation."""
    arc_center_x = wrist_x - 0.05
    arc_center_y = wrist_y
    arc_radius = 0.12
    arc_theta = np.linspace(0, theta_grip_rad, 30)
    arc_x = arc_center_x + arc_radius * np.cos(arc_theta)
    arc_x = cast("np.ndarray[Any, Any]", arc_x)
    arc_y = arc_center_y + arc_radius * np.sin(arc_theta)
    arc_y = cast("np.ndarray[Any, Any]", arc_y)
    ax.plot(arc_x, arc_y, "g-", linewidth=2.5, zorder=8)

    ax.arrow(
        arc_center_x,
        arc_center_y,
        arc_radius,
        0,
        head_width=0.012,
        head_length=0.018,
        fc="k",
        ec="k",
        linewidth=2,
        zorder=8,
    )
    ax.arrow(
        arc_center_x,
        arc_center_y,
        arc_radius * np.cos(theta_grip_rad),
        arc_radius * np.sin(theta_grip_rad),
        head_width=0.012,
        head_length=0.018,
        fc="r",
        ec="r",
        linewidth=2,
        zorder=8,
    )

    label_x = arc_center_x + arc_radius * np.cos(theta_grip_rad / 2) * 0.7
    label_y = arc_center_y + arc_radius * np.sin(theta_grip_rad / 2) * 0.7
    ax.text(
        label_x,
        label_y + 0.02,
        r"$\theta_{grip}$",
        color="g",
        fontsize=13,
        ha="center",
        fontweight="bold",
        zorder=9,
    )


def _draw_wrist_angle_arc(
    ax: Any,
    wrist_arc_center_x: float,
    wrist_arc_center_y: float,
    theta_grip_rad: float,
    phi_wrist_rad: float,
) -> None:
    """Draw the wrist deviation angle arc annotation."""
    center_x = wrist_arc_center_x - 0.05
    center_y = wrist_arc_center_y
    radius = 0.12

    hand_axis_angle = theta_grip_rad
    forearm_axis_angle = theta_grip_rad + phi_wrist_rad

    wrist_arc_theta = np.linspace(hand_axis_angle, forearm_axis_angle, 30)
    w_arc_x = center_x + radius * np.cos(wrist_arc_theta)
    w_arc_x = cast("np.ndarray[Any, Any]", w_arc_x)
    w_arc_y = center_y + radius * np.sin(wrist_arc_theta)
    w_arc_y = cast("np.ndarray[Any, Any]", w_arc_y)
    ax.plot(w_arc_x, w_arc_y, "b-", linewidth=2.5, alpha=0.8, zorder=8)

    ax.arrow(
        center_x,
        center_y,
        radius * np.cos(hand_axis_angle),
        radius * np.sin(hand_axis_angle),
        head_width=0.012,
        head_length=0.018,
        fc="r",
        ec="r",
        linewidth=2,
        zorder=8,
    )
    ax.arrow(
        center_x,
        center_y,
        radius * np.cos(forearm_axis_angle),
        radius * np.sin(forearm_axis_angle),
        head_width=0.012,
        head_length=0.018,
        fc="b",
        ec="b",
        linewidth=2,
        zorder=8,
    )

    phi_mid = (hand_axis_angle + forearm_axis_angle) / 2
    phi_label_x = center_x + radius * np.cos(phi_mid) * 0.7
    phi_label_y = center_y + radius * np.sin(phi_mid) * 0.7
    ax.text(
        phi_label_x,
        phi_label_y + 0.02,
        r"$\phi$",
        color="b",
        fontsize=13,
        ha="center",
        fontweight="bold",
        zorder=9,
    )


# ⚡ Bolt Optimization: Cache figure generation
# Limit entries to prevent OOM when sliding through many angles
@st.cache_resource(max_entries=20)
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
            label="τ_α (higher MOI axis)",
            color="red",
            linewidth=2,
        )
    if show_gamma:
        ax.plot(
            t,
            torque_gamma,
            label="τ_γ (lowest MOI axis)",
            color="blue",
            linewidth=2,
        )

    ax.set_title(
        f"Torque vs Time (Grip: {grip_angle_deg:.0f}°, Wrist: {wrist_angle_deg:.0f}°)",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("Time (s)", fontsize=10)
    ax.set_ylabel("Torque (N·m)", fontsize=10)
    ax.grid(visible=True, alpha=0.3)
    ax.legend(loc="best", fontsize=9)

    plt.tight_layout()
    return fig


# ⚡ Bolt Optimization: Cache figure generation
# Limit entries to prevent OOM when sliding through many angles
@st.cache_resource(max_entries=20)
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
            label=f"α_α (I_α={i_alpha:.4f})",
            color="red",
            linewidth=2,
            linestyle="--",
        )
    if show_gamma:
        ax.plot(
            t,
            accel_gamma,
            label=f"α_γ (I_γ={i_gamma:.4f})",
            color="blue",
            linewidth=2,
            linestyle="--",
        )

    ax.set_title(
        f"Angular Acceleration vs Time (Grip: {grip_angle_deg:.0f}°, "
        f"Wrist: {wrist_angle_deg:.0f}°)",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("Time (s)", fontsize=10)
    ax.set_ylabel("Angular Acceleration (rad/s²)", fontsize=10)
    ax.grid(visible=True, alpha=0.3)
    ax.legend(loc="best", fontsize=9)

    plt.tight_layout()
    return fig


# ⚡ Bolt Optimization: Cache figure generation
# Limit entries to prevent OOM when sliding through many angles
@st.cache_resource(max_entries=20)
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
    fig, ax = plt.subplots(figsize=(10, 6))

    theta_grip_rad = np.radians(grip_angle_deg)
    phi_sweep = np.linspace(-60, 60, 200)
    phi_sweep_rad = np.radians(phi_sweep)

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

    tau_ratios = np.array(tau_ratios_list)
    omega_ratios = np.array(omega_ratios_list)
    accel_alpha_ratios = np.array(accel_alpha_ratios_list)
    accel_gamma_ratios = np.array(accel_gamma_ratios_list)

    if show_transmission:
        ax.plot(
            phi_sweep,
            tau_ratios,
            label="Torque Transmission Ratio (τ_out/τ_in)",
            color="purple",
            linewidth=2.5,
        )
    if show_velocity:
        ax.plot(
            phi_sweep,
            omega_ratios,
            label="Velocity Ratio (ω_out/ω_in)",
            color="orange",
            linewidth=2,
            linestyle="--",
        )
    if show_accel_alpha:
        ax.plot(
            phi_sweep,
            accel_alpha_ratios,
            label="Accel_α ratio (rad/s²)/(N·m)",
            color="red",
            linewidth=1.5,
            alpha=0.7,
        )
    if show_accel_gamma:
        ax.plot(
            phi_sweep,
            accel_gamma_ratios,
            label="Accel_γ ratio (rad/s²)/(N·m)",
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
        label=f"Current wrist angle ({wrist_angle_deg:.0f}°)",
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
        f"Universal Joint Transmission vs Wrist Deviation Angle (Grip={grip_angle_deg:.0f}°)",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("Wrist Deviation Angle (degrees)", fontsize=10)
    ax.set_ylabel("Transmission Ratio", fontsize=10)
    ax.grid(visible=True, alpha=0.3)
    ax.legend(loc="best", fontsize=9)

    plt.tight_layout()
    return fig
