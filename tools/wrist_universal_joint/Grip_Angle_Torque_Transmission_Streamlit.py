"""Enhanced Wrist Universal Joint Model - Streamlit Web App.

# mypy: disable-error-code="no-any-unimported"

This is a web-based version of the enhanced PyQt6 GUI that models the wrist as a
universal joint.
Host this on Streamlit Cloud (free) and embed via iframe in your HTML pages.

Features:
- Universal joint (Hooke/Cardan) transmission characteristics
- Wrist radial/ulnar deviation angle modeling
- Interactive diagram showing forearm, hand, and club
- Multiple plot types: torque, angular acceleration, transmission ratio
- Polynomial signal generator
- Real-time parameter updates
"""

from __future__ import annotations

from typing import Any, cast

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.figure import Figure
from matplotlib.patches import Ellipse, Polygon

# Page config
st.set_page_config(
    page_title="Enhanced Wrist Universal Joint Model",
    page_icon="🏌️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Default golf club properties
DEFAULT_CLUBHEAD_WEIGHT = 200.0  # grams
DEFAULT_SHAFT_WEIGHT = 100.0  # grams
DEFAULT_CLUB_LENGTH = 1.0  # meters
DEFAULT_CLUBHEAD_CG_DISTANCE = 0.85  # meters

# Initialize session state
if "polynomial_expression" not in st.session_state:
    st.session_state.polynomial_expression = "t**2 - t"
if "polynomial_error" not in st.session_state:
    st.session_state.polynomial_error = None


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
    if np.abs(delta_rad) > np.radians(89):
        delta_rad = np.sign(delta_rad) * np.radians(89)

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
) -> np.ndarray[Any, Any]:
    """Generate a torque signal based on noise type."""
    if noise_type == "Golf-like Random":
        torque = np.random.normal(0, 1, len(t))
        torque += np.exp(-50 * (t - 0.5) ** 2) * 8 * np.random.randn(len(t))
        torque = cast(np.ndarray[Any, Any], np.convolve(torque, np.ones(10) / 10, mode="same"))
    elif noise_type == "Step":
        torque = np.zeros_like(t)
        torque[250:] = 3.0  # Step at midpoint
    elif noise_type == "Pulse":
        torque = np.zeros_like(t)
        pulse_start = 200
        pulse_end = 300
        torque[pulse_start:pulse_end] = 5.0 * np.random.randn(pulse_end - pulse_start)
    elif noise_type == "Burst":
        torque = np.zeros_like(t)
        burst_center = 250
        burst_width = 50
        burst_indices = np.arange(
            max(0, burst_center - burst_width), min(len(t), burst_center + burst_width)
        )
        torque[burst_indices] = np.random.normal(0, 3, len(burst_indices))
    elif noise_type == "Sinusoidal":
        torque = 2.0 * np.sin(8 * np.pi * t)
    elif noise_type == "Random":
        torque = np.random.normal(0, 1.5, len(t))
        torque = cast(np.ndarray[Any, Any], np.convolve(torque, np.ones(10) / 10, mode="same"))
    elif noise_type == "Polynomial":
        # Evaluate polynomial expression using safer method
        try:
            safe_dict = {
                "t": t,
                "sin": np.sin,
                "cos": np.cos,
                "exp": np.exp,
                "sqrt": np.sqrt,
                "log": np.log,
                "pi": np.pi,
                "e": np.e,
            }
            code = compile(polynomial_expression, "<string>", "eval")
            result = eval(code, {"__builtins__": {}}, safe_dict)
            if isinstance(result, np.ndarray):
                if result.shape != t.shape:
                    st.session_state.polynomial_error = (
                        f"Polynomial result shape {result.shape} does not match "
                        f"time array shape {t.shape}."
                    )
                    torque = t**2 - t
                else:
                    torque = result
                    st.session_state.polynomial_error = (
                        None  # Only clear error on successful evaluation
                    )
            else:
                torque = np.full_like(t, float(result))
                st.session_state.polynomial_error = (
                    None  # Only clear error on successful evaluation
                )
        except SyntaxError:
            st.session_state.polynomial_error = (
                "Invalid polynomial syntax. Please check your expression."
            )
            torque = t**2 - t
        except NameError:
            st.session_state.polynomial_error = (
                "Invalid variable or function. Only 't', 'sin', 'cos', 'exp', "
                "'sqrt', 'log', 'pi', and 'e' are allowed."
            )
            torque = t**2 - t
        except (TypeError, ValueError) as e:
            st.session_state.polynomial_error = (
                f"Error in polynomial expression: {type(e).__name__}. " "Please check your formula."
            )
            torque = t**2 - t
        except (ArithmeticError, OverflowError, ZeroDivisionError):
            st.session_state.polynomial_error = (
                "Unexpected error evaluating polynomial expression. " "Please check your formula."
            )
            torque = t**2 - t
    else:
        # Default to golf-like
        torque = np.random.normal(0, 1, len(t))
        torque += np.exp(-50 * (t - 0.5) ** 2) * 8 * np.random.randn(len(t))
        torque = cast(np.ndarray[Any, Any], np.convolve(torque, np.ones(10) / 10, mode="same"))

    return torque


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
        ]
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

    # Forearm: attached to hand at long axis endpoints
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
    arc_center_x = wrist_x - 0.05
    arc_center_y = wrist_y
    arc_radius = 0.12
    arc_theta = np.linspace(0, theta_grip_rad, 30)
    arc_x = arc_center_x + arc_radius * np.cos(arc_theta)
    arc_y = arc_center_y + arc_radius * np.sin(arc_theta)
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

    # Draw wrist angle arc (φ)
    wrist_arc_center_x = hand_endpoint_forearm_x - 0.05
    wrist_arc_center_y = hand_endpoint_forearm_y
    wrist_arc_radius = 0.12

    # For arc visualization, use angles without π offset
    hand_axis_angle_for_arc = theta_grip_rad
    forearm_axis_angle_for_arc = theta_grip_rad + phi_wrist_rad

    wrist_arc_start = hand_axis_angle_for_arc
    wrist_arc_end = forearm_axis_angle_for_arc
    wrist_arc_theta = np.linspace(wrist_arc_start, wrist_arc_end, 30)
    wrist_arc_x = wrist_arc_center_x + wrist_arc_radius * np.cos(wrist_arc_theta)
    wrist_arc_y = wrist_arc_center_y + wrist_arc_radius * np.sin(wrist_arc_theta)
    ax.plot(wrist_arc_x, wrist_arc_y, "b-", linewidth=2.5, alpha=0.8, zorder=8)

    # Wrist angle arrows (for arc visualization)
    ax.arrow(
        wrist_arc_center_x,
        wrist_arc_center_y,
        wrist_arc_radius * np.cos(hand_axis_angle_for_arc),
        wrist_arc_radius * np.sin(hand_axis_angle_for_arc),
        head_width=0.012,
        head_length=0.018,
        fc="r",
        ec="r",
        linewidth=2,
        zorder=8,
    )
    ax.arrow(
        wrist_arc_center_x,
        wrist_arc_center_y,
        wrist_arc_radius * np.cos(forearm_axis_angle_for_arc),
        wrist_arc_radius * np.sin(forearm_axis_angle_for_arc),
        head_width=0.012,
        head_length=0.018,
        fc="b",
        ec="b",
        linewidth=2,
        zorder=8,
    )

    phi_mid = (wrist_arc_start + wrist_arc_end) / 2
    phi_label_x = wrist_arc_center_x + wrist_arc_radius * np.cos(phi_mid) * 0.7
    phi_label_y = wrist_arc_center_y + wrist_arc_radius * np.sin(phi_mid) * 0.7
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

    ax.set_xlim(-1.5, 0.8)
    ax.set_ylim(-0.2, 1.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Forearm-Hand-Club Diagram", fontsize=12, fontweight="bold", pad=20)

    plt.tight_layout()
    return fig


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

    omega_ratio, tau_ratio = universal_joint_transmission_ratio(
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

    omega_ratio, tau_ratio = universal_joint_transmission_ratio(
        phi_wrist_rad,
        theta_grip_rad,
    )
    torque_transmitted = input_torque * tau_ratio
    torque_alpha, torque_gamma = distribute_torque_by_grip_angle(
        torque_transmitted,
        theta_grip_rad,
    )
    epsilon = 1e-6
    accel_alpha = torque_alpha / i_alpha if i_alpha > epsilon else np.zeros_like(torque_alpha)
    accel_gamma = torque_gamma / i_gamma if i_gamma > epsilon else np.zeros_like(torque_gamma)

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

    omega_ratios_list = []
    tau_ratios_list = []
    accel_alpha_ratios_list = []
    accel_gamma_ratios_list = []

    for phi_rad in phi_sweep_rad:
        omega_r, tau_r = universal_joint_transmission_ratio(phi_rad, theta_grip_rad)
        omega_ratios_list.append(omega_r)
        tau_ratios_list.append(tau_r)

        torque_trans = 1.0 * tau_r
        t_alpha, t_gamma = distribute_torque_by_grip_angle(torque_trans, theta_grip_rad)
        epsilon = 1e-6
        # t_alpha and t_gamma can be ndarray or float, but here they are float because torque_trans is float
        t_alpha_val = float(t_alpha) if isinstance(t_alpha, float | int) else t_alpha.item()
        t_gamma_val = float(t_gamma) if isinstance(t_gamma, float | int) else t_gamma.item()

        accel_alpha_ratios_list.append(t_alpha_val / i_alpha if i_alpha > epsilon else 0.0)
        accel_gamma_ratios_list.append(t_gamma_val / i_gamma if i_gamma > epsilon else 0.0)

    omega_ratios = np.array(omega_ratios_list)
    tau_ratios = np.array(tau_ratios_list)
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
        f"Universal Joint Transmission vs Wrist Deviation Angle " f"(Grip={grip_angle_deg:.0f}°)",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("Wrist Deviation Angle (degrees)", fontsize=10)
    ax.set_ylabel("Transmission Ratio", fontsize=10)
    ax.grid(visible=True, alpha=0.3)
    ax.legend(loc="best", fontsize=9)

    plt.tight_layout()
    return fig


# Custom CSS
st.markdown(
    """
<style>
    .main {
        padding: 2rem 1rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #3282b8 0%, #0f4c75 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
    }
    h1 {
        background: linear-gradient(135deg, #0f4c75 0%, #3282b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Main app
st.title("🏌️ Enhanced Wrist Universal Joint Model")
st.markdown(
    """
<div style='background: #f0f4f8; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; \
border-left: 4px solid #3282b8;'>
    <p style='margin: 0; font-size: 1.1em;'>
    This interactive tool models the wrist as a universal joint (Hooke/Cardan)
    with proper kinematics,
    showing how grip angle and wrist deviation angle affect torque transmission
    and angular acceleration.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# Sidebar controls
with st.sidebar:
    st.header("Parameters")

    # Angle controls
    st.subheader("Grip Angle θ_grip")
    grip_angle = st.slider(
        "Grip Angle (degrees)",
        0,
        90,
        30,
        1,
        help="0° = parallel to fingers, 90° = perpendicular to fingers",
    )

    st.subheader("Wrist Deviation Angle φ")
    wrist_angle = st.slider(
        "Wrist Deviation (degrees)",
        -60,
        60,
        0,
        1,
        help="+ values = radial deviation, - values = ulnar deviation",
    )

    st.markdown("---")

    # Club Properties
    st.subheader("Club Properties")
    clubhead_weight = st.number_input(
        "Clubhead (g)",
        50.0,
        500.0,
        DEFAULT_CLUBHEAD_WEIGHT,
        1.0,
    )
    shaft_weight = st.number_input("Shaft (g)", 30.0, 200.0, DEFAULT_SHAFT_WEIGHT, 1.0)
    club_length = st.number_input("Length (m)", 0.5, 1.5, DEFAULT_CLUB_LENGTH, 0.01)
    cg_distance = st.number_input(
        "CG Dist (m)",
        0.3,
        1.2,
        DEFAULT_CLUBHEAD_CG_DISTANCE,
        0.01,
    )

    I_alpha, I_gamma = calculate_moments_of_inertia(
        clubhead_weight, shaft_weight, club_length, cg_distance
    )
    st.markdown(
        f"""
    **Moments of Inertia:**
    - I_α = {I_alpha:.4f} kg·m²
    - I_γ = {I_gamma:.4f} kg·m²
    """
    )

    st.markdown("---")

    # Signal Generator
    st.subheader("Input Signal Generator")
    noise_type = st.selectbox(
        "Signal Type",
        [
            "Golf-like Random",
            "Step",
            "Pulse",
            "Burst",
            "Sinusoidal",
            "Random",
            "Polynomial",
        ],
    )

    if noise_type == "Polynomial":
        polynomial_expr = st.text_input(
            "Polynomial Expression",
            value=st.session_state.polynomial_expression,
            help="Use 't' as variable. Example: t**2 - t",
        )
        st.session_state.polynomial_expression = polynomial_expr
        if st.session_state.polynomial_error:
            st.error(st.session_state.polynomial_error)

    if st.button("🎲 Regenerate Signal"):
        st.rerun()

    st.markdown("---")

    # Plot type selection
    st.subheader("Plot Type")
    plot_type = st.selectbox(
        "Select Plot",
        ["Torque", "Angular Acceleration", "Transmission Ratio vs Wrist Angle"],
    )

    st.markdown("---")

    # Signal visibility (depends on plot type)
    st.subheader("Show Signals")
    if plot_type == "Torque":
        show_input = st.checkbox("Input Torque", value=True)
        show_transmitted = st.checkbox("Transmitted Torque", value=True)
        show_alpha = st.checkbox("Torque α (higher MOI axis)", value=True)
        show_gamma = st.checkbox("Torque γ (lowest MOI axis)", value=True)
        show_velocity = False
        show_accel_alpha = False
        show_accel_gamma = False
    elif plot_type == "Angular Acceleration":
        show_input = False
        show_transmitted = False
        show_alpha = st.checkbox("Acceleration α", value=True)
        show_gamma = st.checkbox("Acceleration γ", value=True)
        show_velocity = False
        show_accel_alpha = False
        show_accel_gamma = False
    else:  # Transmission Ratio
        show_input = False
        show_transmitted = False
        show_alpha = False
        show_gamma = False
        show_transmission = st.checkbox("Transmission Ratio", value=True)
        show_velocity = st.checkbox("Velocity Ratio", value=False)
        show_accel_alpha = st.checkbox("Accel α Ratio", value=False)
        show_accel_gamma = st.checkbox("Accel γ Ratio", value=False)

# Generate signal
t = np.linspace(0, 1, 500)
input_torque = generate_sample_torque(
    noise_type,
    t,
    st.session_state.polynomial_expression,
)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Forearm-Hand-Club Diagram")
    diagram_fig = draw_diagram(grip_angle, wrist_angle)
    st.pyplot(diagram_fig)
    plt.close(diagram_fig)

with col2:
    st.subheader(f"{plot_type} Plot")

    if plot_type == "Torque":
        plot_fig = plot_torque(
            t,
            input_torque,
            grip_angle,
            wrist_angle,
            I_alpha,
            I_gamma,
            show_input,
            show_transmitted,
            show_alpha,
            show_gamma,
        )
    elif plot_type == "Angular Acceleration":
        plot_fig = plot_acceleration(
            t,
            input_torque,
            grip_angle,
            wrist_angle,
            I_alpha,
            I_gamma,
            show_alpha,
            show_gamma,
        )
    else:  # Transmission Ratio
        plot_fig = plot_transmission_sweep(
            grip_angle,
            wrist_angle,
            I_alpha,
            I_gamma,
            show_transmission,
            show_velocity,
            show_accel_alpha,
            show_accel_gamma,
        )

    st.pyplot(plot_fig)
    plt.close(plot_fig)

# Info panel
st.markdown("---")
with st.expander("📐 Model Information"):
    theta_grip_rad = np.radians(grip_angle)
    phi_wrist_rad = np.radians(wrist_angle)
    omega_ratio, tau_ratio = universal_joint_transmission_ratio(
        phi_wrist_rad,
        theta_grip_rad,
    )
    torque_transmitted = np.mean(input_torque) * tau_ratio
    torque_alpha, torque_gamma = distribute_torque_by_grip_angle(
        torque_transmitted,
        theta_grip_rad,
    )

    pct_alpha = np.abs(np.sin(theta_grip_rad)) * 100
    pct_gamma = np.abs(np.cos(theta_grip_rad)) * 100

    st.markdown(
        f"""
    ### Current Parameters
    - **Grip Angle (θ_grip):** {grip_angle}°
    - **Wrist Deviation Angle (φ):** {wrist_angle}°
    ({'radial' if wrist_angle > 0 else 'ulnar' if wrist_angle < 0 else 'neutral'} deviation)

    ### Transmission Ratios
    - **Angular Velocity Ratio (ω_out/ω_in):** {omega_ratio:.4f}
    - **Torque Transmission Ratio (τ_out/τ_in):** {tau_ratio:.4f}

    ### Torque Distribution (at mean input torque)
    - **Torque to α-axis (higher MOI):** {torque_alpha:.4f} N·m ({pct_alpha:.1f}% of transmitted)
    - **Torque to γ-axis (lowest MOI):** {torque_gamma:.4f} N·m ({pct_gamma:.1f}% of transmitted)

    ### Angular Acceleration (at mean torque)
    - **α-axis acceleration:** {torque_alpha/I_alpha:.4f} rad/s²
    - **γ-axis acceleration:** {torque_gamma/I_gamma:.4f} rad/s²

    ### Model Assumptions
    - Universal joint (Hooke/Cardan) kinematics
    - Rigid body model
    - Power conservation (P = τω)
    - Constant grip angle during motion
    - Wrist angle represents radial/ulnar deviation
    """
    )
