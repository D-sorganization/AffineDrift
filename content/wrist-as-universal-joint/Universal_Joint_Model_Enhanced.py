"""
Enhanced Wrist Universal Joint Model - PyQt6 GUI
---

This program models the wrist as a universal joint with proper kinematics,
distinguishing between:
1. Grip angle (θ_grip): How the club is oriented in the hand (static)
2. Wrist angle (φ): The dynamic radial/ulnar deviation angle of the wrist joint

Key improvements over previous model:
- Implements actual universal joint (Hooke/Cardan) transmission characteristics
- Torque transmission ratio varies with wrist angle: τ_out/τ_in = f(φ, δ)
- Separates static grip configuration from dynamic wrist motion
- Shows transmission fraction vs. wrist angle for selected grip angles
- More physically accurate modeling of constraint torques

Author: Enhanced model based on universal joint mechanics
Date: 2025-11-25
"""

import sys

import matplotlib
import numpy as np

from src.core.contracts import check_positive

matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Ellipse, Polygon
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class WheelIgnoringSlider(QSlider):  # type: ignore[misc]
    """Slider that ignores mouse wheel events - wheel only scrolls page"""

    def wheelEvent(self, event: QEvent) -> None:
        """Ignore wheel events - let parent handle scrolling"""
        event.ignore()  # Let the event propagate to parent for scrolling


class WheelIgnoringLineEdit(QLineEdit):  # type: ignore[misc]
    """LineEdit that ignores mouse wheel events - wheel only scrolls page"""

    def wheelEvent(self, event: QEvent) -> None:
        """Ignore wheel events - let parent handle scrolling"""
        event.ignore()  # Let the event propagate to parent for scrolling


# Default golf club properties
DEFAULT_CLUBHEAD_WEIGHT = 200.0  # grams
DEFAULT_SHAFT_WEIGHT = 100.0  # grams
DEFAULT_CLUB_LENGTH = 1.0  # meters
DEFAULT_CLUBHEAD_CG_DISTANCE = 0.85  # meters


def calculate_moments_of_inertia(
    clubhead_weight_g: float,
    shaft_weight_g: float,
    club_length_m: float,
    cg_distance_m: float,
) -> tuple[float, float]:
    """
    Calculate moments of inertia for golf club about two axes.

    Args:
        clubhead_weight_g (float): Clubhead weight in grams.
        shaft_weight_g (float): Shaft weight in grams.
        club_length_m (float): Total club length in meters.
        cg_distance_m (float): Distance from grip to clubhead center of mass in meters.

    Returns:
        tuple[float, float]: A tuple containing:
            - I_alpha (float): Moment of inertia about shaft axis (kg·m²) - higher MOI.
            - I_gamma (float): Moment of inertia about local gamma axis (kg·m²) - lowest MOI.
    """
    check_positive(clubhead_weight_g, "clubhead_weight_g")
    check_positive(shaft_weight_g, "shaft_weight_g")
    check_positive(club_length_m, "club_length_m")
    check_positive(cg_distance_m, "cg_distance_m")

    m_head = clubhead_weight_g / 1000.0  # kg
    m_shaft = shaft_weight_g / 1000.0  # kg

    # Shaft inertia (thin rod about end): I = (1/3) * m * L²
    I_shaft_alpha = (1 / 3) * m_shaft * club_length_m**2

    # Clubhead inertia about shaft axis (point mass)
    I_head_alpha = m_head * cg_distance_m**2

    # Total I_alpha (about shaft axis) - higher MOI axis
    I_alpha = I_shaft_alpha + I_head_alpha

    # I_gamma (lowest MOI axis) - typically 0.5x for golf clubs
    I_gamma = 0.5 * I_alpha

    return I_alpha, I_gamma


def universal_joint_transmission_ratio(phi_rad: float, delta_rad: float) -> tuple[float, float]:
    """
    Calculate transmission ratios for a universal (Hooke/Cardan) joint.

    For a universal joint with bend angle δ (angle between input and output shafts),
    the transmission ratio varies with the rotation angle φ.

    Angular velocity ratio:
        ω_out/ω_in = cos(δ) / sqrt(1 - sin²(δ) × sin²(φ))

    Torque ratio (from power conservation, P = τω):
        τ_out/τ_in = ω_in/ω_out = sqrt(1 - sin²(δ) × sin²(φ)) / cos(δ)

    Args:
        phi_rad (float): Rotation angle of input shaft (radians).
        delta_rad (float): Bend angle between shafts (radians).

    Returns:
        tuple[float, float]: A tuple containing:
            - omega_ratio (float): ω_out / ω_in (angular velocity ratio).
            - tau_ratio (float): τ_out / τ_in (torque transmission ratio).
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
    torque_transmitted: float, theta_grip_rad: float
) -> tuple[float, float]:
    """
    Distribute transmitted torque to club axes based on grip angle.

    Grip angle determines how the club sits in the hand:
    - θ = 0°: Club aligned with fingers → torque goes to lowest MOI axis (γ)
    - θ = 90°: Club aligned with palm → torque goes to shaft axis (α)

    Args:
        torque_transmitted (float): Torque transmitted through universal joint (N·m).
        theta_grip_rad (float): Grip angle in radians.

    Returns:
        tuple[float, float]: A tuple containing:
            - torque_alpha (float): Torque to shaft axis (N·m).
            - torque_gamma (float): Torque to lowest MOI axis (N·m).
    """
    torque_alpha = torque_transmitted * np.sin(theta_grip_rad)
    torque_gamma = torque_transmitted * np.cos(theta_grip_rad)

    return torque_alpha, torque_gamma


class DiagramCanvas(FigureCanvas):  # type: ignore[misc]
    """Canvas showing forearm, hand, and club with both angles"""

    def __init__(self, grip_angle_deg: float, wrist_angle_deg: float) -> None:
        """Initialize diagram canvas with grip and wrist angles."""
        self.figure = Figure(figsize=(12, 4))
        super().__init__(self.figure)
        self.setMinimumSize(800, 300)

        self.ax = self.figure.add_subplot(111)
        self.grip_angle_deg = grip_angle_deg
        self.wrist_angle_deg = wrist_angle_deg

        self.update_diagram()

    def wheelEvent(self, event: QEvent) -> None:
        """Ignore wheel events - let parent scroll area handle scrolling"""
        event.ignore()  # Let the event propagate to parent for scrolling

    def update_diagram(self) -> None:
        """Update the diagram with current angles"""
        self.ax.clear()

        theta_grip_rad = np.radians(self.grip_angle_deg)
        phi_wrist_rad = np.radians(self.wrist_angle_deg)

        # Coordinate system: club is always horizontal, clubhead on left pointing up
        # Wrist joint position
        wrist_x = 0.4
        wrist_y = 0.5

        # Club shaft: always horizontal, extends left from hand midpoint (wrist)
        shaft_length = 1.05  # 3x longer (was 0.35)
        hand_length = 0.2
        hand_dir_x = np.cos(theta_grip_rad)
        hand_dir_y = np.sin(theta_grip_rad)
        # Club attaches to hand at hand's midpoint (wrist)
        shaft_attach_x = wrist_x
        shaft_attach_y = wrist_y
        shaft_end_x = shaft_attach_x - shaft_length  # Left side
        shaft_end_y = shaft_attach_y  # Horizontal

        # Draw club shaft (horizontal)
        self.ax.plot(
            [shaft_end_x, shaft_attach_x],
            [shaft_end_y, shaft_attach_y],
            "k-",
            linewidth=8,
            solid_capstyle="round",
            label="Club Shaft",
            zorder=3,
        )

        # Clubhead: on left end, pointing up, trapezoid shape, tilted 30 degrees (top to left)
        clubhead_width_base = 0.08  # Base width (2/3 of original 0.12)
        clubhead_width_bottom = clubhead_width_base / 3  # Bottom is 1/3 as wide
        clubhead_width_top = clubhead_width_base * 4 / 3  # Top is 4/3 as wide
        clubhead_height = 0.24  # 2x original 0.12
        clubhead_angle_deg = 30  # Tilt top to left by 30 degrees (counterclockwise)
        clubhead_angle_rad = np.radians(clubhead_angle_deg)

        # Clubhead base at shaft end, pointing up initially
        clubhead_base_x = shaft_end_x
        clubhead_base_y = shaft_end_y

        # Define trapezoid corners (before rotation) - bottom narrower, top wider
        corners = np.array(
            [
                [-clubhead_width_bottom / 2, 0],  # Bottom left
                [clubhead_width_bottom / 2, 0],  # Bottom right
                [clubhead_width_top / 2, clubhead_height],  # Top right
                [-clubhead_width_top / 2, clubhead_height],  # Top left
            ]
        )

        # Rotate corners around origin
        cos_a = np.cos(clubhead_angle_rad)
        sin_a = np.sin(clubhead_angle_rad)
        rotation_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        rotated_corners = corners @ rotation_matrix.T

        # Translate to clubhead position
        rotated_corners[:, 0] += clubhead_base_x
        rotated_corners[:, 1] += clubhead_base_y

        # Create polygon for rotated clubhead
        clubhead = Polygon(
            rotated_corners,
            facecolor="silver",
            alpha=0.9,
            edgecolor="gray",
            linewidth=2,
            zorder=4,
        )
        self.ax.add_patch(clubhead)

        # Hand: attached at midpoint to wrist, rotated by grip angle relative to club
        # Hand's long axis makes angle theta_grip with horizontal club shaft
        hand_width = 0.12
        # Hand center is at wrist (midpoint attachment)
        hand_center_x = wrist_x
        hand_center_y = wrist_y

        # Hand ellipse (same color as forearm - tan)
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
        self.ax.add_patch(hand)

        # Draw 4 fingers on hand
        finger_length = 0.12
        finger_width = 0.015
        finger_dir_x = -hand_dir_x  # Fingers point opposite to hand long axis
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
            self.ax.add_patch(finger)

        # Forearm: attached to hand at long axis endpoints
        # When wrist angle = 0, forearm aligns with hand's long axis
        # Hand's long axis angle = theta_grip_rad (relative to horizontal)
        # Forearm angle = hand angle + wrist angle (when wrist deviates, forearm rotates relative to hand)  # noqa: E501
        # Flip 180 degrees so forearm extends opposite to hand direction
        forearm_angle_rad = theta_grip_rad + phi_wrist_rad + np.pi  # Add 180 degrees
        forearm_length = 0.35
        forearm_width = 0.1

        # Hand's endpoint away from club (forearm attachment point)
        hand_endpoint_forearm_x = wrist_x + (hand_length / 2) * hand_dir_x
        hand_endpoint_forearm_y = wrist_y + (hand_length / 2) * hand_dir_y

        # Forearm attaches at its long axis endpoint to hand's endpoint
        # Forearm center is offset from attachment point
        forearm_dir_x = np.cos(forearm_angle_rad)
        forearm_dir_y = np.sin(forearm_angle_rad)
        forearm_center_x = hand_endpoint_forearm_x - (forearm_length / 2) * forearm_dir_x
        forearm_center_y = hand_endpoint_forearm_y - (forearm_length / 2) * forearm_dir_y

        # Forearm as ellipse (same color as hand - tan)
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
        self.ax.add_patch(forearm)

        # Draw wrist joint (circle)
        self.ax.plot(wrist_x, wrist_y, "ko", markersize=12, zorder=10)
        self.ax.text(
            wrist_x,
            wrist_y - 0.1,
            "Wrist Joint",
            ha="center",
            fontsize=10,
            fontweight="bold",
            zorder=11,
        )

        # Draw grip angle arc (θ_grip): from club axis (horizontal) to hand axis
        arc_center_x = wrist_x - 0.05
        arc_center_y = wrist_y
        arc_radius = 0.12
        arc_theta = np.linspace(0, theta_grip_rad, 30)
        arc_x = arc_center_x + arc_radius * np.cos(arc_theta)
        arc_y = arc_center_y + arc_radius * np.sin(arc_theta)
        self.ax.plot(arc_x, arc_y, "g-", linewidth=2.5, zorder=8)

        # Grip angle lines
        self.ax.arrow(
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
        self.ax.arrow(
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

        # Label grip angle
        label_x = arc_center_x + arc_radius * np.cos(theta_grip_rad / 2) * 0.7
        label_y = arc_center_y + arc_radius * np.sin(theta_grip_rad / 2) * 0.7
        self.ax.text(
            label_x,
            label_y + 0.02,
            r"$\theta_{grip}$",
            color="g",
            fontsize=13,
            ha="center",
            fontweight="bold",
            zorder=9,
        )
        self.ax.text(
            arc_center_x + arc_radius + 0.02,
            arc_center_y - 0.03,
            "Club Axis",
            color="k",
            fontsize=9,
            ha="left",
            fontweight="bold",
        )
        self.ax.text(
            arc_center_x + arc_radius * np.cos(theta_grip_rad) + 0.02,
            arc_center_y + arc_radius * np.sin(theta_grip_rad) + 0.02,
            "Hand Axis",
            color="r",
            fontsize=9,
            ha="left",
            fontweight="bold",
        )

        # Draw wrist angle arc (φ): from hand axis to forearm axis (similar to grip angle)
        # The wrist angle φ is the actual angle between hand and forearm
        # When φ = 0, forearm aligns with hand. When φ changes, forearm rotates relative to hand.
        wrist_arc_center_x = hand_endpoint_forearm_x - 0.05
        wrist_arc_center_y = hand_endpoint_forearm_y
        wrist_arc_radius = 0.12

        # Draw arc showing the actual wrist angle φ
        # The arc should show just phi_wrist_rad, not including the π offset
        # Hand axis direction (away from club)
        hand_axis_angle_for_arc = theta_grip_rad
        # Forearm axis direction relative to hand (without π offset for arc visualization)
        forearm_axis_angle_for_arc = theta_grip_rad + phi_wrist_rad
        wrist_arc_start = hand_axis_angle_for_arc
        wrist_arc_end = forearm_axis_angle_for_arc
        wrist_arc_theta = np.linspace(wrist_arc_start, wrist_arc_end, 30)
        wrist_arc_x = wrist_arc_center_x + wrist_arc_radius * np.cos(wrist_arc_theta)
        wrist_arc_y = wrist_arc_center_y + wrist_arc_radius * np.sin(wrist_arc_theta)
        self.ax.plot(wrist_arc_x, wrist_arc_y, "b-", linewidth=2.5, alpha=0.8, zorder=8)

        # Wrist angle lines - show hand axis and forearm axis (for arc visualization)
        self.ax.arrow(
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
        self.ax.arrow(
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

        # Label wrist angle
        phi_mid = (wrist_arc_start + wrist_arc_end) / 2
        phi_label_x = wrist_arc_center_x + wrist_arc_radius * np.cos(phi_mid) * 0.7
        phi_label_y = wrist_arc_center_y + wrist_arc_radius * np.sin(phi_mid) * 0.7
        self.ax.text(
            phi_label_x,
            phi_label_y + 0.02,
            r"$\phi$",
            color="b",
            fontsize=13,
            ha="center",
            fontweight="bold",
            zorder=9,
        )
        self.ax.text(
            wrist_arc_center_x + wrist_arc_radius * np.cos(hand_axis_angle_for_arc) + 0.02,
            wrist_arc_center_y + wrist_arc_radius * np.sin(hand_axis_angle_for_arc) + 0.02,
            "Hand Axis",
            color="r",
            fontsize=9,
            ha="left",
            fontweight="bold",
        )
        self.ax.text(
            wrist_arc_center_x + wrist_arc_radius * np.cos(forearm_axis_angle_for_arc) + 0.02,
            wrist_arc_center_y + wrist_arc_radius * np.sin(forearm_axis_angle_for_arc) + 0.02,
            "Forearm Axis",
            color="b",
            fontsize=9,
            ha="left",
            fontweight="bold",
        )

        # Set axis properties (adjusted for longer shaft and to show full forearm)
        # Expand window significantly to accommodate forearm extension in all directions
        # Forearm can extend up to 0.35 length, and with angles it can go far left
        self.ax.set_xlim(-1.5, 0.8)
        self.ax.set_ylim(-0.2, 1.2)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.ax.set_title("Forearm-Hand-Club Diagram", fontsize=12, fontweight="bold", pad=20)

        self.figure.tight_layout()
        self.draw()

    def update_angles(self, grip_angle_deg: float, wrist_angle_deg: float) -> None:
        """Update angles and redraw"""
        self.grip_angle_deg = grip_angle_deg
        self.wrist_angle_deg = wrist_angle_deg
        self.update_diagram()


class PlotCanvas(FigureCanvas):  # type: ignore[misc]
    """Single plot canvas with selectable Y-axis and checkboxes"""

    def __init__(
        self,
        grip_angle_deg: float,
        wrist_angle_deg: float,
        I_alpha: float,
        I_gamma: float,
    ) -> None:
        """Initialize plot canvas with angles and inertia values."""
        self.figure = Figure(figsize=(10, 6))
        super().__init__(self.figure)
        self.setMinimumSize(700, 500)

        self.ax = self.figure.add_subplot(111)
        self.grip_angle_deg = grip_angle_deg
        self.wrist_angle_deg = wrist_angle_deg
        self.I_alpha = I_alpha
        self.I_gamma = I_gamma
        self.polynomial_error: str | None = None  # Store polynomial evaluation errors
        self.DEFAULT_POLYNOMIAL = "t**2 - t"  # Fallback polynomial expression

        # Generate sample input torque signal
        self.t = np.linspace(0, 1, 500)
        self.noise_type = "Golf-like Random"
        self.polynomial_expression = self.DEFAULT_POLYNOMIAL
        self.input_torque = self.generate_sample_torque()

        # Available plot types
        self.current_plot_type = "Torque"

        # Signal visibility for each plot type
        self.visible_signals = {
            "input_torque": True,
            "transmitted_torque": True,
            "torque_alpha": True,
            "torque_gamma": True,
            "accel_alpha": True,
            "accel_gamma": True,
            "transmission_ratio": True,
            "velocity_ratio": False,
            "accel_alpha_ratio": False,
            "accel_gamma_ratio": False,
        }

        self.update_plot()

    def _gen_golf_random(self) -> np.ndarray:
        """Generate a golf-like random torque trace with a smoothed impact burst."""
        torque = np.random.normal(0, 1, len(self.t))
        torque += np.exp(-50 * (self.t - 0.5) ** 2) * 8 * np.random.randn(len(self.t))
        return np.convolve(torque, np.ones(10) / 10, mode="same")

    def _gen_step(self) -> np.ndarray:
        """Generate a step-input torque profile."""
        torque = np.zeros_like(self.t)
        torque[len(self.t) // 2 :] = 3.0
        return torque

    def _gen_pulse(self) -> np.ndarray:
        """Generate a short random pulse torque profile."""
        torque = np.zeros_like(self.t)
        pulse_start = int(len(self.t) * 0.4)
        pulse_end = int(len(self.t) * 0.6)
        torque[pulse_start:pulse_end] = 5.0 * np.random.randn(pulse_end - pulse_start)
        return torque

    def _gen_burst(self) -> np.ndarray:
        """Generate a localized burst of random torque around mid-swing."""
        torque = np.zeros_like(self.t)
        burst_center = len(self.t) // 2
        burst_width = len(self.t) // 10
        burst_indices = np.arange(
            max(0, burst_center - burst_width),
            min(len(self.t), burst_center + burst_width),
        )
        torque[burst_indices] = np.random.normal(0, 3, len(burst_indices))
        return torque

    def _gen_sinusoidal(self) -> np.ndarray:
        """Generate a smooth sinusoidal torque profile."""
        return 2.0 * np.sin(8 * np.pi * self.t)

    def _gen_random_noise(self) -> np.ndarray:
        """Generate filtered random noise as a baseline torque profile."""
        torque = np.random.normal(0, 1.5, len(self.t))
        return np.convolve(torque, np.ones(10) / 10, mode="same")

    def _gen_polynomial(self) -> np.ndarray:
        """Evaluate the configured polynomial torque expression safely."""
        try:
            from simpleeval import simple_eval

            safe_dict = {
                "t": self.t,
                "sin": np.sin,
                "cos": np.cos,
                "exp": np.exp,
                "sqrt": np.sqrt,
                "log": np.log,
                "pi": np.pi,
                "e": np.e,
            }
            result = simple_eval(self.polynomial_expression, names=safe_dict)
            if isinstance(result, np.ndarray):
                torque = result
            else:
                torque = np.full_like(self.t, float(result))
            self.polynomial_error = None
        except SyntaxError:
            self.polynomial_error = "Invalid polynomial syntax. Please check your expression."
            torque = self.t**2 - self.t
        except NameError:
            self.polynomial_error = (
                "Invalid variable or function. Only 't', 'sin', 'cos', "
                "'exp', 'sqrt', 'log', 'pi', & 'e' allowed."
            )
            torque = self.t**2 - self.t
        except (TypeError, ValueError) as e:
            self.polynomial_error = (
                f"Error in polynomial expression: {type(e).__name__}. " "Please check your formula."
            )
            torque = self.t**2 - self.t
        except (Exception, ArithmeticError):
            self.polynomial_error = (
                "Unexpected error evaluating polynomial. " "Please check your formula."
            )
            torque = self.t**2 - self.t
        return torque

    def generate_sample_torque(self) -> np.ndarray:
        """Generate a torque signal based on noise type"""
        generators = {
            "Golf-like Random": self._gen_golf_random,
            "Step": self._gen_step,
            "Pulse": self._gen_pulse,
            "Burst": self._gen_burst,
            "Sinusoidal": self._gen_sinusoidal,
            "Random": self._gen_random_noise,
            "Polynomial": self._gen_polynomial,
        }
        gen_func = generators.get(self.noise_type, self._gen_golf_random)
        return gen_func()

    def set_noise_type(self, noise_type: str) -> None:
        """Set noise type and regenerate"""
        self.noise_type = noise_type
        self.input_torque = self.generate_sample_torque()
        if self.current_plot_type in ["Torque", "Angular Acceleration"]:
            self.update_plot()

    def set_polynomial_expression(self, expression: str) -> None:
        """Set polynomial expression and regenerate if polynomial type is selected"""
        self.polynomial_expression = expression
        if self.noise_type == "Polynomial":
            self.input_torque = self.generate_sample_torque()
            # Show error message if evaluation failed
            if self.polynomial_error:
                # Get parent widget to show message box
                parent = self.parent()
                while parent and not isinstance(parent, QMainWindow):
                    parent = parent.parent()
                if parent:
                    QMessageBox.warning(
                        parent, "Polynomial Evaluation Error", self.polynomial_error
                    )
            if self.current_plot_type in ["Torque", "Angular Acceleration"]:
                self.update_plot()

    def update_plot(self) -> None:
        """Update plot based on current settings"""
        self.ax.clear()

        theta_grip_rad = np.radians(self.grip_angle_deg)
        phi_wrist_rad = np.radians(self.wrist_angle_deg)

        if self.current_plot_type == "Torque":
            self._plot_torque(theta_grip_rad, phi_wrist_rad)
        elif self.current_plot_type == "Angular Acceleration":
            self._plot_acceleration(theta_grip_rad, phi_wrist_rad)
        elif self.current_plot_type == "Transmission Ratio vs Wrist Angle":
            self._plot_transmission_sweep(theta_grip_rad)

        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc="best", fontsize=9)
        self.figure.tight_layout()
        self.draw()

    def _plot_torque(self, theta_grip_rad: float, phi_wrist_rad: float) -> None:
        """Plot torque vs time"""
        omega_ratio, tau_ratio = universal_joint_transmission_ratio(phi_wrist_rad, theta_grip_rad)
        torque_transmitted = self.input_torque * tau_ratio
        torque_alpha, torque_gamma = distribute_torque_by_grip_angle(
            torque_transmitted, theta_grip_rad
        )

        if self.visible_signals["input_torque"]:
            self.ax.plot(
                self.t,
                self.input_torque,
                label="Input Torque (forearm)",
                color="gray",
                alpha=0.7,
                linewidth=1.5,
            )
        if self.visible_signals["transmitted_torque"]:
            self.ax.plot(
                self.t,
                torque_transmitted,
                label=f"Transmitted (ratio={tau_ratio:.3f})",
                color="purple",
                linewidth=2,
            )
        if self.visible_signals["torque_alpha"]:
            self.ax.plot(
                self.t,
                torque_alpha,
                label="τ_α (higher MOI axis)",
                color="red",
                linewidth=2,
            )
        if self.visible_signals["torque_gamma"]:
            self.ax.plot(
                self.t,
                torque_gamma,
                label="τ_γ (lowest MOI axis)",
                color="blue",
                linewidth=2,
            )

        self.ax.set_title(
            f"Torque vs Time (Grip: {self.grip_angle_deg:.0f}°, Wrist: {self.wrist_angle_deg:.0f}°)",  # noqa: E501
            fontsize=12,
            fontweight="bold",
        )
        self.ax.set_xlabel("Time (s)", fontsize=10)
        self.ax.set_ylabel("Torque (N·m)", fontsize=10)

    def _plot_acceleration(self, theta_grip_rad: float, phi_wrist_rad: float) -> None:
        """Plot angular acceleration vs time"""
        omega_ratio, tau_ratio = universal_joint_transmission_ratio(phi_wrist_rad, theta_grip_rad)
        torque_transmitted = self.input_torque * tau_ratio
        torque_alpha, torque_gamma = distribute_torque_by_grip_angle(
            torque_transmitted, theta_grip_rad
        )
        accel_alpha = (
            torque_alpha / self.I_alpha if self.I_alpha > 1e-6 else np.zeros_like(torque_alpha)
        )
        accel_gamma = (
            torque_gamma / self.I_gamma if self.I_gamma > 1e-6 else np.zeros_like(torque_gamma)
        )

        if self.visible_signals["accel_alpha"]:
            self.ax.plot(
                self.t,
                accel_alpha,
                label=f"α_α (I_α---{self.I_alpha:.4f})",
                color="red",
                linewidth=2,
                linestyle="--",
            )
        if self.visible_signals["accel_gamma"]:
            self.ax.plot(
                self.t,
                accel_gamma,
                label=f"α_γ (I_γ---{self.I_gamma:.4f})",
                color="blue",
                linewidth=2,
                linestyle="--",
            )

        self.ax.set_title(
            f"Angular Acceleration vs Time (Grip: {self.grip_angle_deg:.0f}°, Wrist: {self.wrist_angle_deg:.0f}°)",  # noqa: E501
            fontsize=12,
            fontweight="bold",
        )
        self.ax.set_xlabel("Time (s)", fontsize=10)
        self.ax.set_ylabel("Angular Acceleration (rad/s²)", fontsize=10)

    def _plot_transmission_sweep(self, theta_grip_rad: float) -> None:
        """Plot transmission ratio vs wrist angle sweep"""
        phi_sweep = np.linspace(-60, 60, 200)
        phi_sweep_rad = np.radians(phi_sweep)

        omega_ratios = []
        tau_ratios = []
        accel_alpha_ratios = []
        accel_gamma_ratios = []

        for phi_rad in phi_sweep_rad:
            omega_r, tau_r = universal_joint_transmission_ratio(phi_rad, theta_grip_rad)
            omega_ratios.append(omega_r)
            tau_ratios.append(tau_r)

            torque_trans = 1.0 * tau_r
            t_alpha, t_gamma = distribute_torque_by_grip_angle(torque_trans, theta_grip_rad)
            accel_alpha_ratios.append(t_alpha / self.I_alpha if self.I_alpha > 1e-6 else 0)
            accel_gamma_ratios.append(t_gamma / self.I_gamma if self.I_gamma > 1e-6 else 0)

        omega_ratios = np.array(omega_ratios)
        tau_ratios = np.array(tau_ratios)
        accel_alpha_ratios = np.array(accel_alpha_ratios)
        accel_gamma_ratios = np.array(accel_gamma_ratios)

        if self.visible_signals["transmission_ratio"]:
            self.ax.plot(
                phi_sweep,
                tau_ratios,
                label="Torque Transmission Ratio (τ_out/τ_in)",
                color="purple",
                linewidth=2.5,
            )
        if self.visible_signals["velocity_ratio"]:
            self.ax.plot(
                phi_sweep,
                omega_ratios,
                label="Velocity Ratio (ω_out/ω_in)",
                color="orange",
                linewidth=2,
                linestyle="--",
            )
        if self.visible_signals["accel_alpha_ratio"]:
            self.ax.plot(
                phi_sweep,
                accel_alpha_ratios,
                label="Accel_α ratio (rad/s²)/(N·m)",
                color="red",
                linewidth=1.5,
                alpha=0.7,
            )
        if self.visible_signals["accel_gamma_ratio"]:
            self.ax.plot(
                phi_sweep,
                accel_gamma_ratios,
                label="Accel_γ ratio (rad/s²)/(N·m)",
                color="blue",
                linewidth=1.5,
                alpha=0.7,
            )

        # Mark current wrist angle
        current_idx = np.argmin(np.abs(phi_sweep - self.wrist_angle_deg))
        self.ax.axvline(
            self.wrist_angle_deg,
            color="green",
            linestyle=":",
            linewidth=2,
            label=f"Current wrist angle ({self.wrist_angle_deg:.0f}°)",
        )
        if self.visible_signals["transmission_ratio"]:
            self.ax.plot(
                self.wrist_angle_deg,
                tau_ratios[current_idx],
                "go",
                markersize=10,
                markerfacecolor="lime",
            )

        self.ax.axhline(1.0, color="gray", linestyle="--", alpha=0.5, linewidth=1)

        self.ax.set_title(
            f"Universal Joint Transmission vs Wrist Deviation Angle (Grip={self.grip_angle_deg:.0f}°)",  # noqa: E501
            fontsize=12,
            fontweight="bold",
        )
        self.ax.set_xlabel("Wrist Deviation Angle (degrees)", fontsize=10)
        self.ax.set_ylabel("Transmission Ratio", fontsize=10)

    def update_parameters(
        self,
        grip_angle_deg: float,
        wrist_angle_deg: float,
        I_alpha: float,
        I_gamma: float,
    ) -> None:
        """Update all parameters and redraw"""
        self.grip_angle_deg = grip_angle_deg
        self.wrist_angle_deg = wrist_angle_deg
        self.I_alpha = I_alpha
        self.I_gamma = I_gamma
        self.update_plot()

    def set_plot_type(self, plot_type: str) -> None:
        """Set the plot type"""
        self.current_plot_type = plot_type
        self.update_plot()

    def set_signal_visible(self, signal_name: str, visible: bool) -> None:
        """Set visibility of a signal"""
        if signal_name in self.visible_signals:
            self.visible_signals[signal_name] = visible
        self.update_plot()

    def regenerate_noise(self) -> None:
        """Regenerate noise signal with current noise type"""
        self.input_torque = self.generate_sample_torque()
        if self.current_plot_type in ["Torque", "Angular Acceleration"]:
            self.update_plot()


class DocumentationDialog(QDialog):  # type: ignore[misc]
    """Dialog showing mathematical documentation"""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize documentation dialog."""
        super().__init__(parent)
        self.setWindowTitle("Universal Joint Model - Mathematics & Physics")
        self.setGeometry(150, 150, 900, 800)
        self.initUI()

    def initUI(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        text_widget = QTextEdit()
        text_widget.setReadOnly(True)
        text_widget.setHtml(self.get_documentation_html())
        scroll.setWidget(text_widget)
        layout.addWidget(scroll)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)

    def get_documentation_html(self) -> str:
        """Return HTML documentation content."""
        # Return the same documentation as before - keeping it short for now
        return """
        <html>
        <head>
        <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; padding: 15px; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 8px; }
        h2 { color: #34495e; margin-top: 25px; border-bottom: 1px solid #bdc3c7;
             padding-bottom: 5px; }
        </style>
        </head>
        <body>
        <h1>Enhanced Wrist Universal Joint Model</h1>
        <p>See the full documentation in the README_ENHANCED_MODEL.md file.</p>
        </body>
        </html>
        """


class MainWindow(QMainWindow):  # type: ignore[misc]
    """Main application window"""

    def __init__(self) -> None:
        """Initialize main window."""
        super().__init__()
        self.setWindowTitle("Enhanced Universal Joint Model - Wrist Biomechanics")
        self.setGeometry(100, 100, 1600, 1000)
        self.initUI()

    def initUI(self) -> None:
        """Initialize UI components."""
        # Create scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Install event filter to handle mouse wheel globally
        self.scroll.installEventFilter(self)
        self.installEventFilter(self)

        # Main widget for scroll area
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)

        # ---
        # Top: Documentation button
        # ---
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        doc_btn = QPushButton("📘 Model Documentation & Mathematics")
        doc_btn.setToolTip("View detailed mathematical documentation and physics")
        doc_btn.clicked.connect(self.show_documentation)
        doc_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        top_bar.addWidget(doc_btn)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        # ---
        # Diagram Canvas (above plots)
        # ---
        diagram_group = QGroupBox("Forearm-Hand-Club Diagram")
        diagram_layout = QVBoxLayout()
        self.diagram_canvas = DiagramCanvas(grip_angle_deg=30, wrist_angle_deg=0)
        diagram_layout.addWidget(self.diagram_canvas)
        diagram_group.setLayout(diagram_layout)
        main_layout.addWidget(diagram_group)

        # ---
        # Control Panel
        # ---
        control_group = QGroupBox("Parameters")
        control_layout = QHBoxLayout()  # Horizontal layout for two columns

        # Grip angle
        grip_layout = QVBoxLayout()
        grip_layout.setSpacing(5)  # Consistent spacing
        grip_layout.setContentsMargins(0, 0, 0, 0)  # No margins for consistent alignment
        grip_label = QLabel("Grip Angle θ<sub>grip</sub>:")
        grip_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        grip_layout.addWidget(grip_label)

        # Container for slider row and tick labels - ensures alignment
        slider_container = QWidget()
        slider_container_layout = QVBoxLayout(slider_container)
        slider_container_layout.setContentsMargins(0, 0, 0, 0)
        slider_container_layout.setSpacing(0)

        # Slider and text box row
        grip_control_layout = QHBoxLayout()
        grip_control_layout.setContentsMargins(0, 0, 0, 0)
        grip_control_layout.setSpacing(5)  # Small gap between slider and text box
        self.grip_slider = WheelIgnoringSlider(Qt.Orientation.Horizontal)
        self.grip_slider.setMinimum(0)
        self.grip_slider.setMaximum(90)
        self.grip_slider.setValue(30)
        self.grip_slider.setTickInterval(15)
        self.grip_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.grip_slider.setFixedWidth(300)  # Fixed width to match tick labels
        self.grip_slider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        grip_control_layout.addWidget(self.grip_slider)
        self.grip_textbox = WheelIgnoringLineEdit()
        self.grip_textbox.setText("30")
        self.grip_textbox.setFixedWidth(80)
        self.grip_textbox.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.grip_textbox.setPlaceholderText("0-90")
        self.grip_textbox.editingFinished.connect(self.update_grip_from_textbox)
        grip_control_layout.addWidget(self.grip_textbox)
        degree_label1 = QLabel("°")
        degree_label1.setFixedWidth(15)
        grip_control_layout.addWidget(degree_label1)
        grip_control_layout.addStretch()  # Push everything to the left
        slider_container_layout.addLayout(grip_control_layout)

        # Add tick mark labels below slider - aligned with slider
        tick_container = QWidget()
        tick_container.setFixedWidth(300)  # Match slider width exactly
        tick_label_layout = QHBoxLayout(tick_container)
        tick_label_layout.setContentsMargins(0, 0, 0, 0)
        tick_label_layout.setSpacing(0)
        # 7 ticks at 0, 15, 30, 45, 60, 75, 90 - evenly spaced
        tick_values = [0, 15, 30, 45, 60, 75, 90]
        for i, val in enumerate(tick_values):
            label = QLabel(f"{val}°")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 10pt; font-weight: bold;")
            tick_label_layout.addWidget(label)
            if i < len(tick_values) - 1:
                tick_label_layout.addStretch()
        slider_container_layout.addWidget(tick_container)
        grip_layout.addWidget(slider_container)

        grip_info = QLabel("0° = parallel to fingers, 90° = perpendicular to fingers")
        grip_info.setStyleSheet("font-size: 12pt; font-weight: bold;")
        grip_layout.addWidget(grip_info)
        self.grip_slider.valueChanged.connect(self.update_grip_label)

        # Wrist deviation angle - radial/ulnar deviation
        wrist_layout = QVBoxLayout()
        wrist_layout.setSpacing(5)  # Match grip_layout exactly
        wrist_layout.setContentsMargins(0, 0, 0, 0)  # Match grip_layout exactly
        wrist_label = QLabel("Wrist Deviation Angle φ:")
        wrist_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        wrist_layout.addWidget(wrist_label)

        # Container for slider row and tick labels - ensures alignment (match grip structure exactly)  # noqa: E501
        wrist_slider_container = QWidget()
        wrist_slider_container_layout = QVBoxLayout(wrist_slider_container)
        wrist_slider_container_layout.setContentsMargins(0, 0, 0, 0)  # Match grip
        wrist_slider_container_layout.setSpacing(0)  # Match grip

        # Slider and text box row
        wrist_control_layout = QHBoxLayout()
        wrist_control_layout.setContentsMargins(0, 0, 0, 0)
        wrist_control_layout.setSpacing(5)  # Small gap between slider and text box
        self.wrist_slider = WheelIgnoringSlider(Qt.Orientation.Horizontal)
        self.wrist_slider.setMinimum(-60)
        self.wrist_slider.setMaximum(60)
        self.wrist_slider.setValue(0)
        self.wrist_slider.setTickInterval(15)
        self.wrist_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.wrist_slider.setFixedWidth(300)  # Match grip
        self.wrist_slider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        wrist_control_layout.addWidget(self.wrist_slider)
        self.wrist_textbox = WheelIgnoringLineEdit()
        self.wrist_textbox.setText("0")
        self.wrist_textbox.setFixedWidth(80)  # Match grip text box width
        self.wrist_textbox.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.wrist_textbox.setPlaceholderText("-60 to 60")
        self.wrist_textbox.editingFinished.connect(self.update_wrist_from_textbox)
        wrist_control_layout.addWidget(self.wrist_textbox)
        degree_label2 = QLabel("°")
        degree_label2.setFixedWidth(15)  # Match grip degree label width
        wrist_control_layout.addWidget(degree_label2)
        wrist_control_layout.addStretch()  # Push everything to the left
        wrist_slider_container_layout.addLayout(wrist_control_layout)

        # Add tick mark labels below slider - aligned with slider (match grip structure exactly)
        wrist_tick_container = QWidget()
        wrist_tick_container.setFixedWidth(300)  # Match grip
        wrist_tick_label_layout = QHBoxLayout(wrist_tick_container)
        wrist_tick_label_layout.setContentsMargins(0, 0, 0, 0)  # Match grip
        wrist_tick_label_layout.setSpacing(0)  # Match grip
        # 9 ticks at -60, -45, -30, -15, 0, 15, 30, 45, 60 - evenly spaced
        wrist_tick_values = [-60, -45, -30, -15, 0, 15, 30, 45, 60]
        for i, val in enumerate(wrist_tick_values):
            label = QLabel(f"{val}°")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 10pt; font-weight: bold;")  # Match grip
            wrist_tick_label_layout.addWidget(label)
            if i < len(wrist_tick_values) - 1:
                wrist_tick_label_layout.addStretch()
        wrist_slider_container_layout.addWidget(wrist_tick_container)
        wrist_layout.addWidget(wrist_slider_container)

        wrist_info = QLabel("+ values = radial deviation, - values = ulnar deviation")
        wrist_info.setStyleSheet("font-size: 12pt; font-weight: bold;")  # Match grip
        wrist_layout.addWidget(wrist_info)
        self.wrist_slider.valueChanged.connect(self.update_wrist_label)

        # Left column: Angle controls
        left_column = QVBoxLayout()
        left_column.setSpacing(0)  # No extra spacing between sections
        left_column.setContentsMargins(0, 0, 0, 0)  # No margins
        left_column.addLayout(grip_layout)
        left_column.addLayout(wrist_layout)
        left_column.addStretch()
        control_layout.addLayout(left_column)

        # Right column: Club Properties
        club_layout = QVBoxLayout()

        club_props_label = QLabel("Club Properties:")
        club_props_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        club_layout.addWidget(club_props_label)

        # Club properties in vertical layout - text boxes just right of labels, right edges aligned
        # Use fixed minimum width for label area so all text boxes align on the right
        label_area_width = 100  # Fixed width for label + spacer area

        clubhead_layout = QHBoxLayout()
        clubhead_label = QLabel("Clubhead:")
        clubhead_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        clubhead_label.setFixedWidth(label_area_width)  # Fixed width for alignment
        clubhead_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        clubhead_layout.addWidget(clubhead_label)
        self.clubhead_weight = WheelIgnoringLineEdit()
        self.clubhead_weight.setText(str(int(DEFAULT_CLUBHEAD_WEIGHT)))
        self.clubhead_weight.setFixedWidth(80)
        self.clubhead_weight.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.clubhead_weight.setPlaceholderText("50-500")
        self.clubhead_weight.editingFinished.connect(self.update_clubhead_from_textbox)
        clubhead_layout.addWidget(self.clubhead_weight)
        clubhead_layout.addWidget(QLabel(" g"))
        club_layout.addLayout(clubhead_layout)

        shaft_layout = QHBoxLayout()
        shaft_label = QLabel("Shaft:")
        shaft_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        shaft_label.setFixedWidth(label_area_width)  # Same fixed width
        shaft_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        shaft_layout.addWidget(shaft_label)
        self.shaft_weight = WheelIgnoringLineEdit()
        self.shaft_weight.setText(str(int(DEFAULT_SHAFT_WEIGHT)))
        self.shaft_weight.setFixedWidth(80)  # Match clubhead width
        self.shaft_weight.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.shaft_weight.setPlaceholderText("30-200")
        self.shaft_weight.editingFinished.connect(self.update_shaft_from_textbox)
        shaft_layout.addWidget(self.shaft_weight)
        shaft_layout.addWidget(QLabel(" g"))
        club_layout.addLayout(shaft_layout)

        length_layout = QHBoxLayout()
        length_label = QLabel("Length:")
        length_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        length_label.setFixedWidth(label_area_width)  # Same fixed width
        length_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        length_layout.addWidget(length_label)
        self.club_length = WheelIgnoringLineEdit()
        self.club_length.setText(f"{DEFAULT_CLUB_LENGTH:.2f}")
        self.club_length.setFixedWidth(80)  # Match other text boxes
        self.club_length.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.club_length.setPlaceholderText("0.5-1.5")
        self.club_length.editingFinished.connect(self.update_length_from_textbox)
        length_layout.addWidget(self.club_length)
        length_layout.addWidget(QLabel(" m"))
        club_layout.addLayout(length_layout)

        cg_layout = QHBoxLayout()
        cg_label = QLabel("CG Dist:")
        cg_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        cg_label.setFixedWidth(label_area_width)  # Same fixed width
        cg_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        cg_layout.addWidget(cg_label)
        self.cg_distance = WheelIgnoringLineEdit()
        self.cg_distance.setText(f"{DEFAULT_CLUBHEAD_CG_DISTANCE:.2f}")
        self.cg_distance.setFixedWidth(80)  # Match other text boxes
        self.cg_distance.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.cg_distance.setPlaceholderText("0.3-1.2")
        self.cg_distance.editingFinished.connect(self.update_cg_from_textbox)
        cg_layout.addWidget(self.cg_distance)
        cg_layout.addWidget(QLabel(" m"))
        club_layout.addLayout(cg_layout)

        self.inertia_label = QLabel()
        self.inertia_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        club_layout.addWidget(self.inertia_label)
        club_layout.addStretch()

        control_layout.addLayout(club_layout)

        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)

        # Connect club property changes (text boxes trigger on editingFinished)
        # No need to connect - editingFinished already calls update methods

        # Signal Generator Section
        signal_group = QGroupBox("Input Signal Generator")
        signal_layout = QVBoxLayout()

        # Noise type selection
        noise_layout = QHBoxLayout()
        signal_type_label = QLabel("Signal Type:")
        signal_type_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        noise_layout.addWidget(signal_type_label)
        self.noise_type_combo = QComboBox()
        self.noise_type_combo.addItems(
            [
                "Golf-like Random",
                "Step",
                "Pulse",
                "Burst",
                "Sinusoidal",
                "Random",
                "Polynomial",
            ]
        )
        self.noise_type_combo.currentTextChanged.connect(self.update_noise_type)
        noise_layout.addWidget(self.noise_type_combo)
        noise_layout.addStretch()
        signal_layout.addLayout(noise_layout)

        # Polynomial input section (shown when Polynomial is selected)
        poly_layout = QHBoxLayout()
        self.polynomial_label = QLabel('Polynomial (e.g., "t**2 + 2*t - 1" or "t**3 - 0.5*t"):')
        self.polynomial_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        poly_layout.addWidget(self.polynomial_label)
        self.polynomial_input = QLineEdit()
        self.polynomial_input.setPlaceholderText("Enter polynomial expression using t as variable")
        self.polynomial_input.setText("t**2 - t")
        self.polynomial_input.setVisible(False)  # Hidden by default
        self.polynomial_input.textChanged.connect(self.update_polynomial_signal)
        poly_layout.addWidget(self.polynomial_input)
        self.polynomial_label.setVisible(False)  # Hidden by default
        signal_layout.addLayout(poly_layout)

        # Regenerate noise button
        regen_layout = QHBoxLayout()
        regen_layout.addStretch()
        regen_btn = QPushButton("🎲 Regenerate Signal")
        regen_btn.clicked.connect(self.regenerate_noise)
        regen_layout.addWidget(regen_btn)
        regen_layout.addStretch()
        signal_layout.addLayout(regen_layout)

        signal_group.setLayout(signal_layout)
        main_layout.addWidget(signal_group)

        # ---
        # Plot Controls
        # ---
        plot_control_group = QGroupBox("Plot Controls")
        plot_control_layout = QHBoxLayout()
        plot_control_layout.setSpacing(15)  # Add spacing between widgets

        # Plot type dropdown
        plot_type_label = QLabel("Plot Type:")
        plot_type_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        plot_control_layout.addWidget(plot_type_label)
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems(
            ["Torque", "Angular Acceleration", "Transmission Ratio vs Wrist Angle"]
        )
        self.plot_type_combo.currentTextChanged.connect(self.update_plot_type)
        plot_control_layout.addWidget(self.plot_type_combo)

        plot_control_layout.addSpacing(20)  # Extra space after combo box
        plot_control_layout.addStretch()

        # Signal visibility checkboxes
        show_label = QLabel("Show:")
        show_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        plot_control_layout.addWidget(show_label)
        plot_control_layout.addSpacing(10)  # Space after label

        self.show_input_check = QCheckBox("Input Torque")
        self.show_input_check.setChecked(True)
        self.show_input_check.stateChanged.connect(
            lambda: self.update_signal_visibility("input_torque", self.show_input_check.isChecked())
        )
        plot_control_layout.addWidget(self.show_input_check)
        plot_control_layout.addSpacing(10)  # Space between checkboxes

        self.show_transmitted_check = QCheckBox("Transmitted Torque")
        self.show_transmitted_check.setChecked(True)
        self.show_transmitted_check.stateChanged.connect(
            lambda: self.update_signal_visibility(
                "transmitted_torque", self.show_transmitted_check.isChecked()
            )
        )
        plot_control_layout.addWidget(self.show_transmitted_check)
        plot_control_layout.addSpacing(10)  # Space between checkboxes

        self.show_alpha_torque_check = QCheckBox("τ_α")
        self.show_alpha_torque_check.setChecked(True)
        self.show_alpha_torque_check.stateChanged.connect(
            lambda: self.update_signal_visibility(
                "torque_alpha", self.show_alpha_torque_check.isChecked()
            )
        )
        plot_control_layout.addWidget(self.show_alpha_torque_check)
        plot_control_layout.addSpacing(10)  # Space between checkboxes

        self.show_gamma_torque_check = QCheckBox("τ_γ")
        self.show_gamma_torque_check.setChecked(True)
        self.show_gamma_torque_check.stateChanged.connect(
            lambda: self.update_signal_visibility(
                "torque_gamma", self.show_gamma_torque_check.isChecked()
            )
        )
        plot_control_layout.addWidget(self.show_gamma_torque_check)
        plot_control_layout.addSpacing(10)  # Space between checkboxes

        self.show_alpha_accel_check = QCheckBox("α_α")
        self.show_alpha_accel_check.setChecked(True)
        self.show_alpha_accel_check.stateChanged.connect(
            lambda: self.update_signal_visibility(
                "accel_alpha", self.show_alpha_accel_check.isChecked()
            )
        )
        plot_control_layout.addWidget(self.show_alpha_accel_check)
        plot_control_layout.addSpacing(10)  # Space between checkboxes

        self.show_gamma_accel_check = QCheckBox("α_γ")
        self.show_gamma_accel_check.setChecked(True)
        self.show_gamma_accel_check.stateChanged.connect(
            lambda: self.update_signal_visibility(
                "accel_gamma", self.show_gamma_accel_check.isChecked()
            )
        )
        plot_control_layout.addWidget(self.show_gamma_accel_check)
        plot_control_layout.addSpacing(10)  # Space between checkboxes

        self.show_transmission_check = QCheckBox("Transmission Ratio")
        self.show_transmission_check.setChecked(True)
        self.show_transmission_check.stateChanged.connect(
            lambda: self.update_signal_visibility(
                "transmission_ratio", self.show_transmission_check.isChecked()
            )
        )
        plot_control_layout.addWidget(self.show_transmission_check)
        plot_control_layout.addSpacing(10)  # Space between checkboxes

        self.show_velocity_check = QCheckBox("Velocity Ratio")
        self.show_velocity_check.setChecked(False)
        self.show_velocity_check.stateChanged.connect(
            lambda: self.update_signal_visibility(
                "velocity_ratio", self.show_velocity_check.isChecked()
            )
        )
        plot_control_layout.addWidget(self.show_velocity_check)
        plot_control_layout.addSpacing(10)  # Space between checkboxes

        self.show_accel_alpha_ratio_check = QCheckBox("Accel_α Ratio")
        self.show_accel_alpha_ratio_check.setChecked(False)
        self.show_accel_alpha_ratio_check.stateChanged.connect(
            lambda: self.update_signal_visibility(
                "accel_alpha_ratio", self.show_accel_alpha_ratio_check.isChecked()
            )
        )
        plot_control_layout.addWidget(self.show_accel_alpha_ratio_check)
        plot_control_layout.addSpacing(10)  # Space between checkboxes

        self.show_accel_gamma_ratio_check = QCheckBox("Accel_γ Ratio")
        self.show_accel_gamma_ratio_check.setChecked(False)
        self.show_accel_gamma_ratio_check.stateChanged.connect(
            lambda: self.update_signal_visibility(
                "accel_gamma_ratio", self.show_accel_gamma_ratio_check.isChecked()
            )
        )
        plot_control_layout.addWidget(self.show_accel_gamma_ratio_check)

        plot_control_group.setLayout(plot_control_layout)
        main_layout.addWidget(plot_control_group)

        # ---
        # Plot Canvas
        # ---
        plot_group = QGroupBox("Plot")
        plot_layout = QVBoxLayout()
        I_alpha, I_gamma = self.get_inertia_values()
        self.plot_canvas = PlotCanvas(
            grip_angle_deg=30, wrist_angle_deg=0, I_alpha=I_alpha, I_gamma=I_gamma
        )
        plot_layout.addWidget(self.plot_canvas)
        plot_group.setLayout(plot_layout)
        main_layout.addWidget(plot_group)

        # ---
        # Info panel
        # ---
        info_group = QGroupBox("Model Information")
        info_layout = QVBoxLayout()
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        self.update_info()
        info_layout.addWidget(self.info_label)
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)

        # Set main widget to scroll area
        self.scroll.setWidget(main_widget)
        self.setCentralWidget(self.scroll)

        # Connect sliders and spinboxes to update (with signal blocking to prevent loops)
        self.grip_slider.valueChanged.connect(self.update_grip_label)
        self.wrist_slider.valueChanged.connect(self.update_wrist_label)

        # Initial update
        self.update_inertia()

    def get_inertia_values(self) -> tuple[float, float]:
        """Get current inertia values from club properties"""
        try:
            clubhead = float(self.clubhead_weight.text())
            shaft = float(self.shaft_weight.text())
            length = float(self.club_length.text())
            cg = float(self.cg_distance.text())
        except ValueError:
            # If text boxes have invalid values, use defaults
            clubhead = DEFAULT_CLUBHEAD_WEIGHT
            shaft = DEFAULT_SHAFT_WEIGHT
            length = DEFAULT_CLUB_LENGTH
            cg = DEFAULT_CLUBHEAD_CG_DISTANCE
        return calculate_moments_of_inertia(clubhead, shaft, length, cg)

    def update_clubhead_from_textbox(self) -> None:
        """Update clubhead weight from text box"""
        try:
            value = float(self.clubhead_weight.text())
            value = max(50, min(500, value))  # Clamp to range
            self.clubhead_weight.blockSignals(True)
            self.clubhead_weight.setText(str(int(value)))
            self.clubhead_weight.blockSignals(False)
            self.update_inertia()
        except ValueError:
            # Invalid input, restore to default
            self.clubhead_weight.setText(str(int(DEFAULT_CLUBHEAD_WEIGHT)))
            self.update_inertia()

    def update_shaft_from_textbox(self) -> None:
        """Update shaft weight from text box"""
        try:
            value = float(self.shaft_weight.text())
            value = max(30, min(200, value))  # Clamp to range
            self.shaft_weight.blockSignals(True)
            self.shaft_weight.setText(str(int(value)))
            self.shaft_weight.blockSignals(False)
            self.update_inertia()
        except ValueError:
            self.shaft_weight.setText(str(int(DEFAULT_SHAFT_WEIGHT)))
            self.update_inertia()

    def update_length_from_textbox(self) -> None:
        """Update club length from text box"""
        try:
            value = float(self.club_length.text())
            value = max(0.5, min(1.5, value))  # Clamp to range
            self.club_length.blockSignals(True)
            self.club_length.setText(f"{value:.2f}")
            self.club_length.blockSignals(False)
            self.update_inertia()
        except ValueError:
            self.club_length.setText(f"{DEFAULT_CLUB_LENGTH:.2f}")
            self.update_inertia()

    def update_cg_from_textbox(self) -> None:
        """Update CG distance from text box"""
        try:
            value = float(self.cg_distance.text())
            value = max(0.3, min(1.2, value))  # Clamp to range
            self.cg_distance.blockSignals(True)
            self.cg_distance.setText(f"{value:.2f}")
            self.cg_distance.blockSignals(False)
            self.update_inertia()
        except ValueError:
            self.cg_distance.setText(f"{DEFAULT_CLUBHEAD_CG_DISTANCE:.2f}")
            self.update_inertia()

    def update_inertia(self) -> None:
        """Update inertia display and plots"""
        I_alpha, I_gamma = self.get_inertia_values()
        self.inertia_label.setText(f"I_α---{I_alpha:.4f} kg·m², I_γ---{I_gamma:.4f} kg·m²")
        if hasattr(self, "plot_canvas"):
            self.update_all()

    def update_grip_label(self, value: int) -> None:
        """Update grip angle from slider"""
        if hasattr(self, "grip_textbox"):
            self.grip_textbox.blockSignals(True)
            self.grip_textbox.setText(str(value))
            self.grip_textbox.blockSignals(False)
        if hasattr(self, "plot_canvas"):
            self.update_all()

    def update_wrist_label(self, value: int) -> None:
        """Update wrist angle from slider"""
        if hasattr(self, "wrist_textbox"):
            self.wrist_textbox.blockSignals(True)
            self.wrist_textbox.setText(str(value))
            self.wrist_textbox.blockSignals(False)
        if hasattr(self, "plot_canvas"):
            self.update_all()

    def update_grip_from_textbox(self) -> None:
        """Update grip angle from text box"""
        try:
            value = float(self.grip_textbox.text())
            # Clamp to valid range
            value = max(0, min(90, value))
            if hasattr(self, "grip_slider"):
                self.grip_slider.blockSignals(True)
                self.grip_slider.setValue(int(value))
                self.grip_slider.blockSignals(False)
            # Update text box with clamped value
            self.grip_textbox.blockSignals(True)
            self.grip_textbox.setText(str(int(value)))
            self.grip_textbox.blockSignals(False)
            if hasattr(self, "plot_canvas"):
                self.update_all()
        except ValueError:
            # Invalid input, restore to slider value
            if hasattr(self, "grip_slider"):
                self.grip_textbox.setText(str(self.grip_slider.value()))

    def update_wrist_from_textbox(self) -> None:
        """Update wrist angle from text box"""
        try:
            value = float(self.wrist_textbox.text())
            # Clamp to valid range
            value = max(-60, min(60, value))
            if hasattr(self, "wrist_slider"):
                self.wrist_slider.blockSignals(True)
                self.wrist_slider.setValue(int(value))
                self.wrist_slider.blockSignals(False)
            # Update text box with clamped value
            self.wrist_textbox.blockSignals(True)
            self.wrist_textbox.setText(str(int(value)))
            self.wrist_textbox.blockSignals(False)
            if hasattr(self, "plot_canvas"):
                self.update_all()
        except ValueError:
            # Invalid input, restore to slider value
            if hasattr(self, "wrist_slider"):
                self.wrist_textbox.setText(str(self.wrist_slider.value()))

    def update_all(self) -> None:
        """Update diagram and plot"""
        grip_angle = self.grip_slider.value()
        wrist_angle = self.wrist_slider.value()
        I_alpha, I_gamma = self.get_inertia_values()

        self.diagram_canvas.update_angles(grip_angle, wrist_angle)
        self.plot_canvas.update_parameters(grip_angle, wrist_angle, I_alpha, I_gamma)
        self.update_info()

    def update_plot_type(self, plot_type: str) -> None:
        """Update plot type and enable/disable appropriate checkboxes"""
        self.plot_canvas.set_plot_type(plot_type)

        # Enable/disable checkboxes based on plot type
        is_torque = plot_type == "Torque"
        is_accel = plot_type == "Angular Acceleration"
        is_transmission = plot_type == "Transmission Ratio vs Wrist Angle"

        # Torque plot checkboxes
        self.show_input_check.setEnabled(is_torque)
        self.show_transmitted_check.setEnabled(is_torque)
        self.show_alpha_torque_check.setEnabled(is_torque)
        self.show_gamma_torque_check.setEnabled(is_torque)

        # Acceleration plot checkboxes
        self.show_alpha_accel_check.setEnabled(is_accel)
        self.show_gamma_accel_check.setEnabled(is_accel)

        # Transmission plot checkboxes
        self.show_transmission_check.setEnabled(is_transmission)
        self.show_velocity_check.setEnabled(is_transmission)
        self.show_accel_alpha_ratio_check.setEnabled(is_transmission)
        self.show_accel_gamma_ratio_check.setEnabled(is_transmission)

    def update_signal_visibility(self, signal_name: str, visible: bool) -> None:
        """Update signal visibility"""
        self.plot_canvas.set_signal_visible(signal_name, visible)

    def update_info(self) -> None:
        """Update information panel"""
        grip = self.grip_slider.value()
        wrist = self.wrist_slider.value()

        omega, tau = universal_joint_transmission_ratio(np.radians(wrist), np.radians(grip))

        info_text = f"""
        <b>Current Configuration:</b><br>
        Grip={grip}°, Wrist={wrist}° → Transmission Ratio = {tau:.3f}<br>
        <br>
        <b>Key Insights:</b><br>
        • Transmission ratio <b>varies with wrist angle</b> (see transmission plot)<br>
        • At neutral wrist (φ≈0°): Maximum transmission efficiency<br>
        • At extreme radial/ulnar deviation: Reduced transmission<br>
        • Grip angle determines <b>which axes</b> receive transmitted torque<br>
        • Lower grip angle (fingers) → more torque to lowest MOI axis (γ) (stability)<br>
        • Higher grip angle (palm) → more torque to higher MOI axis (α) (face angle control)
        """
        self.info_label.setText(info_text)

    def regenerate_noise(self) -> None:
        """Regenerate noise on plot canvas"""
        self.plot_canvas.regenerate_noise()

    def update_noise_type(self, noise_type: str) -> None:
        """Update noise type and show/hide polynomial input"""
        self.plot_canvas.set_noise_type(noise_type)
        # Show/hide polynomial input and label based on selection
        is_polynomial = noise_type == "Polynomial"
        if hasattr(self, "polynomial_input"):
            self.polynomial_input.setVisible(is_polynomial)
        if hasattr(self, "polynomial_label"):
            self.polynomial_label.setVisible(is_polynomial)

    def update_polynomial_signal(self, expression: str) -> None:
        """Update polynomial expression"""
        if hasattr(self, "plot_canvas"):
            self.plot_canvas.set_polynomial_expression(expression)

    def eventFilter(self, obj: QWidget, event: QEvent) -> bool:
        """Filter events to handle mouse wheel scrolling globally - prevent sliders from responding"""  # noqa: E501
        if event.type() == QEvent.Type.Wheel:
            # Always redirect wheel events to scroll area, never let sliders/spinboxes handle them
            scroll = self.centralWidget()
            if isinstance(scroll, QScrollArea):
                scroll_bar = scroll.verticalScrollBar()
                if scroll_bar and scroll_bar.isVisible():
                    delta = event.angleDelta().y()
                    scroll_bar.setValue(scroll_bar.value() - delta // 8)
                    return True  # Consume the event so sliders don't get it
        result = super().eventFilter(obj, event)
        return bool(result)

    def show_documentation(self) -> None:
        """Show documentation dialog"""
        dialog = DocumentationDialog(self)
        dialog.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
