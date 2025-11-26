"""
Enhanced Wrist Universal Joint Model - PyQt6 GUI
================================================

This program models the wrist as a universal joint with proper kinematics,
distinguishing between:
1. Grip angle (θ_grip): How the club is oriented in the hand (static)
2. Wrist angle (φ): The dynamic flexion/extension angle of the wrist joint

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

matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Ellipse, Rectangle
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSlider,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Default golf club properties
DEFAULT_CLUBHEAD_WEIGHT = 200.0  # grams
DEFAULT_SHAFT_WEIGHT = 100.0  # grams
DEFAULT_CLUB_LENGTH = 1.0  # meters
DEFAULT_CLUBHEAD_CG_DISTANCE = 0.85  # meters

def calculate_moments_of_inertia(clubhead_weight_g, shaft_weight_g, club_length_m, cg_distance_m):
    """
    Calculate moments of inertia for golf club about two axes.

    Returns:
        I_alpha: Moment of inertia about shaft axis (kg·m²)
        I_gamma: Moment of inertia about high inertia axis (kg·m²)
    """
    m_head = clubhead_weight_g / 1000.0  # kg
    m_shaft = shaft_weight_g / 1000.0  # kg

    # Shaft inertia (thin rod about end): I = (1/3) * m * L²
    I_shaft_alpha = (1/3) * m_shaft * club_length_m**2

    # Clubhead inertia about shaft axis (point mass)
    I_head_alpha = m_head * cg_distance_m**2

    # Total I_alpha (about shaft axis)
    I_alpha = I_shaft_alpha + I_head_alpha

    # I_gamma (high inertia axis) - typically 2x for golf clubs
    I_gamma = 2.0 * I_alpha

    return I_alpha, I_gamma


def universal_joint_transmission_ratio(phi_rad, delta_rad):
    """
    Calculate transmission ratios for a universal (Hooke/Cardan) joint.

    For a universal joint with bend angle δ (angle between input and output shafts),
    the transmission ratio varies with the rotation angle φ.

    Angular velocity ratio:
        ω_out/ω_in = cos(δ) / sqrt(1 - sin²(δ) × sin²(φ))

    Torque ratio (from power conservation, P = τω):
        τ_out/τ_in = ω_in/ω_out = sqrt(1 - sin²(δ) × sin²(φ)) / cos(δ)

    Parameters:
        phi_rad: Rotation angle of input shaft (radians)
        delta_rad: Bend angle between shafts (radians)

    Returns:
        omega_ratio: ω_out / ω_in (angular velocity ratio)
        tau_ratio: τ_out / τ_in (torque transmission ratio)
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


def distribute_torque_by_grip_angle(torque_transmitted, theta_grip_rad):
    """
    Distribute transmitted torque to club axes based on grip angle.

    Grip angle determines how the club sits in the hand:
    - θ = 0°: Club aligned with fingers → torque goes to high-inertia axis (γ)
    - θ = 90°: Club aligned with palm → torque goes to shaft axis (α)

    Parameters:
        torque_transmitted: Torque transmitted through universal joint
        theta_grip_rad: Grip angle in radians

    Returns:
        torque_alpha: Torque to shaft axis
        torque_gamma: Torque to high-inertia axis
    """
    torque_alpha = torque_transmitted * np.sin(theta_grip_rad)
    torque_gamma = torque_transmitted * np.cos(theta_grip_rad)

    return torque_alpha, torque_gamma


class DiagramCanvas(FigureCanvas):
    """Canvas showing forearm, hand, and club with both angles"""
    def __init__(self, grip_angle_deg, wrist_angle_deg):
        self.figure = Figure(figsize=(12, 4))
        super().__init__(self.figure)
        self.setMinimumSize(800, 300)

        self.ax = self.figure.add_subplot(111)
        self.grip_angle_deg = grip_angle_deg
        self.wrist_angle_deg = wrist_angle_deg

        self.update_diagram()

    def update_diagram(self):
        """Update the diagram with current angles"""
        self.ax.clear()

        theta_grip_rad = np.radians(self.grip_angle_deg)
        phi_wrist_rad = np.radians(self.wrist_angle_deg)

        # Coordinate system: club is always horizontal, clubhead on left pointing up
        # Wrist joint position
        wrist_x = 0.4
        wrist_y = 0.5

        # Club shaft: always horizontal, extends left from hand midpoint (wrist)
        shaft_length = 0.35
        # Club attaches to hand midpoint (wrist)
        shaft_attach_x = wrist_x
        shaft_attach_y = wrist_y
        shaft_end_x = shaft_attach_x - shaft_length  # Left side
        shaft_end_y = shaft_attach_y  # Horizontal

        # Draw club shaft (horizontal)
        self.ax.plot([shaft_end_x, shaft_attach_x], [shaft_end_y, shaft_attach_y],
                     'k-', linewidth=8, solid_capstyle='round', label='Club Shaft', zorder=3)

        # Clubhead: on left end, pointing up, 2/3 width, 2x height, starts at bottom and overlays shaft
        clubhead_width = 0.08  # 2/3 of original 0.12
        clubhead_height = 0.24  # 2x original 0.12
        clubhead_x = shaft_end_x - clubhead_width / 2  # Center on shaft end
        clubhead_y = shaft_end_y  # Start at top of shaft, pointing up

        clubhead = Rectangle((clubhead_x, clubhead_y), clubhead_width, clubhead_height,
                            facecolor='silver', alpha=0.9, edgecolor='gray', linewidth=2, zorder=4)
        self.ax.add_patch(clubhead)

        # Hand: attached at midpoint to wrist, rotated by grip angle relative to club
        # Hand's long axis makes angle theta_grip with horizontal club shaft
        hand_length = 0.2
        hand_width = 0.12
        # Hand center is at wrist (midpoint attachment)
        hand_center_x = wrist_x
        hand_center_y = wrist_y

        # Hand ellipse (same color as forearm - tan)
        hand = Ellipse((hand_center_x, hand_center_y), hand_length, hand_width,
                      angle=np.degrees(theta_grip_rad), facecolor='tan', alpha=0.8,
                      edgecolor='saddlebrown', linewidth=2, zorder=6)
        self.ax.add_patch(hand)

        # Draw 4 fingers on hand
        finger_length = 0.12
        finger_width = 0.015
        hand_dir_x = np.cos(theta_grip_rad)
        hand_dir_y = np.sin(theta_grip_rad)
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
            finger = Ellipse((finger_mid_x, finger_mid_y), finger_length, finger_width,
                           angle=finger_angle, facecolor='tan', alpha=0.9,
                           edgecolor='saddlebrown', linewidth=1, zorder=7)
            self.ax.add_patch(finger)

        # Forearm: attached to hand midpoint (on side opposite to club)
        # When wrist angle = 0, forearm aligns with hand's long axis
        # Hand's long axis angle = theta_grip_rad (relative to horizontal)
        # Forearm angle = hand angle + wrist angle (when wrist flexes, forearm rotates relative to hand)
        # Flip 180 degrees: forearm extends opposite to hand direction
        forearm_angle_rad = theta_grip_rad + phi_wrist_rad + np.pi  # Add 180 degrees
        forearm_length = 0.35
        forearm_width = 0.1

        # Forearm center is at hand midpoint (wrist), extends away from club
        forearm_center_x = wrist_x
        forearm_center_y = wrist_y

        # Forearm as ellipse (same color as hand - tan)
        forearm = Ellipse((forearm_center_x, forearm_center_y), forearm_length, forearm_width,
                         angle=np.degrees(forearm_angle_rad), facecolor='tan', alpha=0.8,
                         edgecolor='saddlebrown', linewidth=2, zorder=5)
        self.ax.add_patch(forearm)

        # Draw wrist joint (circle)
        self.ax.plot(wrist_x, wrist_y, 'ko', markersize=12, zorder=10)
        self.ax.text(wrist_x, wrist_y - 0.1, 'Wrist Joint', ha='center', fontsize=10, fontweight='bold', zorder=11)

        # Draw grip angle arc (θ_grip): from club axis (horizontal) to hand axis
        arc_center_x = wrist_x - 0.05
        arc_center_y = wrist_y
        arc_radius = 0.12
        arc_theta = np.linspace(0, theta_grip_rad, 30)
        arc_x = arc_center_x + arc_radius * np.cos(arc_theta)
        arc_y = arc_center_y + arc_radius * np.sin(arc_theta)
        self.ax.plot(arc_x, arc_y, 'g-', linewidth=2.5, zorder=8)

        # Grip angle lines
        self.ax.arrow(arc_center_x, arc_center_y, arc_radius, 0,
                     head_width=0.012, head_length=0.018, fc='k', ec='k', linewidth=2, zorder=8)
        self.ax.arrow(arc_center_x, arc_center_y, arc_radius*np.cos(theta_grip_rad),
                     arc_radius*np.sin(theta_grip_rad), head_width=0.012, head_length=0.018,
                     fc='r', ec='r', linewidth=2, zorder=8)

        # Label grip angle
        label_x = arc_center_x + arc_radius * np.cos(theta_grip_rad/2) * 0.7
        label_y = arc_center_y + arc_radius * np.sin(theta_grip_rad/2) * 0.7
        self.ax.text(label_x, label_y + 0.02, r"$\theta_{grip}$", color='g',
                    fontsize=13, ha='center', fontweight='bold', zorder=9)
        self.ax.text(arc_center_x + arc_radius + 0.02, arc_center_y - 0.03, 'Club Axis',
                    color='k', fontsize=9, ha='left', fontweight='bold')
        self.ax.text(arc_center_x + arc_radius*np.cos(theta_grip_rad) + 0.02,
                    arc_center_y + arc_radius*np.sin(theta_grip_rad) + 0.02, 'Hand Axis',
                    color='r', fontsize=9, ha='left', fontweight='bold')

        # Draw wrist angle arc (φ): from hand axis to forearm axis
        wrist_arc_center_x = wrist_x
        wrist_arc_center_y = wrist_y
        wrist_arc_radius = 0.15

        # Wrist angle: angle between hand and forearm
        if abs(self.wrist_angle_deg) > 0.1:
            wrist_arc_start = theta_grip_rad  # Hand angle
            wrist_arc_end = forearm_angle_rad  # Forearm angle
            wrist_arc_theta = np.linspace(wrist_arc_start, wrist_arc_end, 30)
            wrist_arc_x = wrist_arc_center_x + wrist_arc_radius * np.cos(wrist_arc_theta)
            wrist_arc_y = wrist_arc_center_y + wrist_arc_radius * np.sin(wrist_arc_theta)
            self.ax.plot(wrist_arc_x, wrist_arc_y, 'b-', linewidth=2.5, alpha=0.8, zorder=8)

            # Label wrist angle
            phi_mid = (wrist_arc_start + wrist_arc_end) / 2
            phi_label_x = wrist_arc_center_x + wrist_arc_radius * np.cos(phi_mid) * 0.9
            phi_label_y = wrist_arc_center_y + wrist_arc_radius * np.sin(phi_mid) * 0.9
            self.ax.text(phi_label_x, phi_label_y, r"$\phi$", color='b',
                        fontsize=13, ha='center', fontweight='bold', zorder=9)

        # Set axis properties
        self.ax.set_xlim(-0.05, 0.9)
        self.ax.set_ylim(0.15, 0.85)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_title('Forearm-Hand-Club Diagram', fontsize=12, fontweight='bold', pad=20)

        self.figure.tight_layout()
        self.draw()

    def update_angles(self, grip_angle_deg, wrist_angle_deg):
        """Update angles and redraw"""
        self.grip_angle_deg = grip_angle_deg
        self.wrist_angle_deg = wrist_angle_deg
        self.update_diagram()


class PlotCanvas(FigureCanvas):
    """Single plot canvas with selectable Y-axis and checkboxes"""
    def __init__(self, grip_angle_deg, wrist_angle_deg, I_alpha, I_gamma):
        self.figure = Figure(figsize=(10, 6))
        super().__init__(self.figure)
        self.setMinimumSize(700, 500)

        self.ax = self.figure.add_subplot(111)
        self.grip_angle_deg = grip_angle_deg
        self.wrist_angle_deg = wrist_angle_deg
        self.I_alpha = I_alpha
        self.I_gamma = I_gamma

        # Generate sample input torque signal
        self.t = np.linspace(0, 1, 500)
        self.noise_type = 'Golf-like Random'
        self.input_torque = self.generate_sample_torque()

        # Available plot types
        self.current_plot_type = 'Torque'

        # Signal visibility for each plot type
        self.visible_signals = {
            'input_torque': True,
            'transmitted_torque': True,
            'torque_alpha': True,
            'torque_gamma': True,
            'accel_alpha': True,
            'accel_gamma': True,
            'transmission_ratio': True,
            'velocity_ratio': False,
            'accel_alpha_ratio': False,
            'accel_gamma_ratio': False
        }

        self.update_plot()

    def generate_sample_torque(self):
        """Generate a torque signal based on noise type"""
        t = self.t

        if self.noise_type == 'Golf-like Random':
            torque = np.random.normal(0, 1, len(t))
            torque += np.exp(-50*(t-0.5)**2) * 8 * np.random.randn(len(t))
            torque = np.convolve(torque, np.ones(10)/10, mode='same')
        elif self.noise_type == 'Step':
            torque = np.zeros_like(t)
            torque[250:] = 3.0  # Step at midpoint
        elif self.noise_type == 'Pulse':
            torque = np.zeros_like(t)
            pulse_start = 200
            pulse_end = 300
            torque[pulse_start:pulse_end] = 5.0 * np.random.randn(pulse_end - pulse_start)
        elif self.noise_type == 'Burst':
            torque = np.zeros_like(t)
            burst_center = 250
            burst_width = 50
            burst_indices = np.arange(max(0, burst_center - burst_width),
                                     min(len(t), burst_center + burst_width))
            torque[burst_indices] = np.random.normal(0, 3, len(burst_indices))
        elif self.noise_type == 'Sinusoidal':
            torque = 2.0 * np.sin(8 * np.pi * t)
        elif self.noise_type == 'Random':
            torque = np.random.normal(0, 1.5, len(t))
            torque = np.convolve(torque, np.ones(10)/10, mode='same')
        else:
            # Default to golf-like
            torque = np.random.normal(0, 1, len(t))
            torque += np.exp(-50*(t-0.5)**2) * 8 * np.random.randn(len(t))
            torque = np.convolve(torque, np.ones(10)/10, mode='same')

        return torque

    def set_noise_type(self, noise_type):
        """Set noise type and regenerate"""
        self.noise_type = noise_type
        self.input_torque = self.generate_sample_torque()
        if self.current_plot_type in ['Torque', 'Angular Acceleration']:
            self.update_plot()

    def update_plot(self):
        """Update plot based on current settings"""
        self.ax.clear()

        theta_grip_rad = np.radians(self.grip_angle_deg)
        phi_wrist_rad = np.radians(self.wrist_angle_deg)

        if self.current_plot_type == 'Torque':
            self._plot_torque(theta_grip_rad, phi_wrist_rad)
        elif self.current_plot_type == 'Angular Acceleration':
            self._plot_acceleration(theta_grip_rad, phi_wrist_rad)
        elif self.current_plot_type == 'Transmission Ratio vs Wrist Angle':
            self._plot_transmission_sweep(theta_grip_rad)

        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc='best', fontsize=9)
        self.figure.tight_layout()
        self.draw()

    def _plot_torque(self, theta_grip_rad, phi_wrist_rad):
        """Plot torque vs time"""
        omega_ratio, tau_ratio = universal_joint_transmission_ratio(phi_wrist_rad, theta_grip_rad)
        torque_transmitted = self.input_torque * tau_ratio
        torque_alpha, torque_gamma = distribute_torque_by_grip_angle(torque_transmitted, theta_grip_rad)

        if self.visible_signals['input_torque']:
            self.ax.plot(self.t, self.input_torque, label='Input Torque (forearm)',
                       color='gray', alpha=0.7, linewidth=1.5)
        if self.visible_signals['transmitted_torque']:
            self.ax.plot(self.t, torque_transmitted,
                       label=f'Transmitted (ratio={tau_ratio:.3f})',
                       color='purple', linewidth=2)
        if self.visible_signals['torque_alpha']:
            self.ax.plot(self.t, torque_alpha, label='τ_α (shaft axis)',
                       color='red', linewidth=2)
        if self.visible_signals['torque_gamma']:
            self.ax.plot(self.t, torque_gamma, label='τ_γ (high-I axis)',
                       color='blue', linewidth=2)

        self.ax.set_title(f'Torque vs Time (Grip: {self.grip_angle_deg:.0f}°, Wrist: {self.wrist_angle_deg:.0f}°)',
                         fontsize=12, fontweight='bold')
        self.ax.set_xlabel('Time (s)', fontsize=10)
        self.ax.set_ylabel('Torque (N·m)', fontsize=10)

    def _plot_acceleration(self, theta_grip_rad, phi_wrist_rad):
        """Plot angular acceleration vs time"""
        omega_ratio, tau_ratio = universal_joint_transmission_ratio(phi_wrist_rad, theta_grip_rad)
        torque_transmitted = self.input_torque * tau_ratio
        torque_alpha, torque_gamma = distribute_torque_by_grip_angle(torque_transmitted, theta_grip_rad)
        accel_alpha = torque_alpha / self.I_alpha if self.I_alpha > 1e-6 else np.zeros_like(torque_alpha)
        accel_gamma = torque_gamma / self.I_gamma if self.I_gamma > 1e-6 else np.zeros_like(torque_gamma)

        if self.visible_signals['accel_alpha']:
            self.ax.plot(self.t, accel_alpha, label=f'α_α (I_α={self.I_alpha:.4f})',
                          color='red', linewidth=2, linestyle='--')
        if self.visible_signals['accel_gamma']:
            self.ax.plot(self.t, accel_gamma, label=f'α_γ (I_γ={self.I_gamma:.4f})',
                          color='blue', linewidth=2, linestyle='--')

        self.ax.set_title(f'Angular Acceleration vs Time (Grip: {self.grip_angle_deg:.0f}°, Wrist: {self.wrist_angle_deg:.0f}°)',
                         fontsize=12, fontweight='bold')
        self.ax.set_xlabel('Time (s)', fontsize=10)
        self.ax.set_ylabel('Angular Acceleration (rad/s²)', fontsize=10)

    def _plot_transmission_sweep(self, theta_grip_rad):
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

        if self.visible_signals['transmission_ratio']:
            self.ax.plot(phi_sweep, tau_ratios, label='Torque Transmission Ratio (τ_out/τ_in)',
                                 color='purple', linewidth=2.5)
        if self.visible_signals['velocity_ratio']:
            self.ax.plot(phi_sweep, omega_ratios, label='Velocity Ratio (ω_out/ω_in)',
                                 color='orange', linewidth=2, linestyle='--')
        if self.visible_signals['accel_alpha_ratio']:
            self.ax.plot(phi_sweep, accel_alpha_ratios,
                                 label='Accel_α ratio (rad/s²)/(N·m)',
                                 color='red', linewidth=1.5, alpha=0.7)
        if self.visible_signals['accel_gamma_ratio']:
            self.ax.plot(phi_sweep, accel_gamma_ratios,
                                 label='Accel_γ ratio (rad/s²)/(N·m)',
                                 color='blue', linewidth=1.5, alpha=0.7)

        # Mark current wrist angle
        current_idx = np.argmin(np.abs(phi_sweep - self.wrist_angle_deg))
        self.ax.axvline(self.wrist_angle_deg, color='green', linestyle=':', linewidth=2,
                                    label=f'Current wrist angle ({self.wrist_angle_deg:.0f}°)')
        if self.visible_signals['transmission_ratio']:
            self.ax.plot(self.wrist_angle_deg, tau_ratios[current_idx], 'go', markersize=10,
                        markerfacecolor='lime')

        self.ax.axhline(1.0, color='gray', linestyle='--', alpha=0.5, linewidth=1)

        self.ax.set_title(f'Universal Joint Transmission vs Wrist Flexion Angle (Grip={self.grip_angle_deg:.0f}°)',
                         fontsize=12, fontweight='bold')
        self.ax.set_xlabel('Wrist Flexion Angle (degrees)', fontsize=10)
        self.ax.set_ylabel('Transmission Ratio', fontsize=10)

    def update_parameters(self, grip_angle_deg, wrist_angle_deg, I_alpha, I_gamma):
        """Update all parameters and redraw"""
        self.grip_angle_deg = grip_angle_deg
        self.wrist_angle_deg = wrist_angle_deg
        self.I_alpha = I_alpha
        self.I_gamma = I_gamma
        self.update_plot()

    def set_plot_type(self, plot_type):
        """Set the plot type"""
        self.current_plot_type = plot_type
        self.update_plot()

    def set_signal_visible(self, signal_name, visible):
        """Set visibility of a signal"""
        if signal_name in self.visible_signals:
            self.visible_signals[signal_name] = visible
        self.update_plot()

    def regenerate_noise(self):
        """Regenerate noise signal with current noise type"""
        self.input_torque = self.generate_sample_torque()
        if self.current_plot_type in ['Torque', 'Angular Acceleration']:
            self.update_plot()


class DocumentationDialog(QDialog):
    """Dialog showing mathematical documentation"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Universal Joint Model - Mathematics & Physics')
        self.setGeometry(150, 150, 900, 800)
        self.initUI()

    def initUI(self):
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

    def get_documentation_html(self):
        # Return the same documentation as before - keeping it short for now
        return """
        <html>
        <head>
        <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; padding: 15px; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 8px; }
        h2 { color: #34495e; margin-top: 25px; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }
        </style>
        </head>
        <body>
        <h1>Enhanced Wrist Universal Joint Model</h1>
        <p>See the full documentation in the README_ENHANCED_MODEL.md file.</p>
        </body>
        </html>
        """


class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Enhanced Universal Joint Model - Wrist Biomechanics')
        self.setGeometry(100, 100, 1600, 1000)
        self.initUI()

    def initUI(self):
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

        # ============================================================
        # Top: Documentation button
        # ============================================================
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        doc_btn = QPushButton('📘 Model Documentation & Mathematics')
        doc_btn.setToolTip('View detailed mathematical documentation and physics')
        doc_btn.clicked.connect(self.show_documentation)
        doc_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        top_bar.addWidget(doc_btn)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        # ============================================================
        # Diagram Canvas (above plots)
        # ============================================================
        diagram_group = QGroupBox('Forearm-Hand-Club Diagram')
        diagram_layout = QVBoxLayout()
        self.diagram_canvas = DiagramCanvas(grip_angle_deg=30, wrist_angle_deg=0)
        diagram_layout.addWidget(self.diagram_canvas)
        diagram_group.setLayout(diagram_layout)
        main_layout.addWidget(diagram_group)

        # ============================================================
        # Club Properties
        # ============================================================
        club_group = QGroupBox('Club Properties')
        club_layout = QHBoxLayout()

        club_layout.addWidget(QLabel('Clubhead (g):'))
        self.clubhead_weight = QDoubleSpinBox()
        self.clubhead_weight.setRange(50, 500)
        self.clubhead_weight.setValue(DEFAULT_CLUBHEAD_WEIGHT)
        self.clubhead_weight.setSuffix(' g')
        club_layout.addWidget(self.clubhead_weight)

        club_layout.addWidget(QLabel('Shaft (g):'))
        self.shaft_weight = QDoubleSpinBox()
        self.shaft_weight.setRange(30, 200)
        self.shaft_weight.setValue(DEFAULT_SHAFT_WEIGHT)
        self.shaft_weight.setSuffix(' g')
        club_layout.addWidget(self.shaft_weight)

        club_layout.addWidget(QLabel('Length (m):'))
        self.club_length = QDoubleSpinBox()
        self.club_length.setRange(0.5, 1.5)
        self.club_length.setValue(DEFAULT_CLUB_LENGTH)
        self.club_length.setDecimals(2)
        self.club_length.setSuffix(' m')
        club_layout.addWidget(self.club_length)

        club_layout.addWidget(QLabel('CG Dist (m):'))
        self.cg_distance = QDoubleSpinBox()
        self.cg_distance.setRange(0.3, 1.2)
        self.cg_distance.setValue(DEFAULT_CLUBHEAD_CG_DISTANCE)
        self.cg_distance.setDecimals(2)
        self.cg_distance.setSuffix(' m')
        club_layout.addWidget(self.cg_distance)

        self.inertia_label = QLabel()
        club_layout.addWidget(self.inertia_label)
        club_layout.addStretch()

        club_group.setLayout(club_layout)
        main_layout.addWidget(club_group)

        # Connect club property changes
        self.clubhead_weight.valueChanged.connect(self.update_inertia)
        self.shaft_weight.valueChanged.connect(self.update_inertia)
        self.club_length.valueChanged.connect(self.update_inertia)
        self.cg_distance.valueChanged.connect(self.update_inertia)

        # ============================================================
        # Control Panel
        # ============================================================
        control_group = QGroupBox('Universal Joint Parameters')
        control_layout = QVBoxLayout()

        # Grip angle (static)
        grip_layout = QHBoxLayout()
        grip_layout.addWidget(QLabel('Grip Angle θ<sub>grip</sub> (static):'))
        self.grip_slider = QSlider(Qt.Orientation.Horizontal)
        self.grip_slider.setMinimum(0)
        self.grip_slider.setMaximum(90)
        self.grip_slider.setValue(30)
        self.grip_slider.setTickInterval(15)
        self.grip_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        grip_layout.addWidget(self.grip_slider)
        self.grip_label = QLabel('30°')
        self.grip_label.setMinimumWidth(50)
        grip_layout.addWidget(self.grip_label)
        grip_layout.addWidget(QLabel('   [0°=fingers, 90°=palm]'))
        self.grip_slider.valueChanged.connect(self.update_grip_label)
        control_layout.addLayout(grip_layout)

        # Wrist angle (dynamic)
        wrist_layout = QHBoxLayout()
        wrist_layout.addWidget(QLabel('Wrist Flexion Angle φ (dynamic):'))
        self.wrist_slider = QSlider(Qt.Orientation.Horizontal)
        self.wrist_slider.setMinimum(-60)
        self.wrist_slider.setMaximum(60)
        self.wrist_slider.setValue(0)
        self.wrist_slider.setTickInterval(15)
        self.wrist_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        wrist_layout.addWidget(self.wrist_slider)
        self.wrist_label = QLabel('0°')
        self.wrist_label.setMinimumWidth(50)
        wrist_layout.addWidget(self.wrist_label)
        wrist_layout.addWidget(QLabel('   [-60°=ext, +60°=flex]'))
        self.wrist_slider.valueChanged.connect(self.update_wrist_label)
        control_layout.addLayout(wrist_layout)

        # Noise type selection
        noise_layout = QHBoxLayout()
        noise_layout.addWidget(QLabel('Noise Type:'))
        self.noise_type_combo = QComboBox()
        self.noise_type_combo.addItems(['Golf-like Random', 'Step', 'Pulse', 'Burst', 'Sinusoidal', 'Random'])
        self.noise_type_combo.currentTextChanged.connect(self.update_noise_type)
        noise_layout.addWidget(self.noise_type_combo)
        noise_layout.addStretch()
        control_layout.addLayout(noise_layout)

        # Regenerate noise button
        regen_layout = QHBoxLayout()
        regen_layout.addStretch()
        regen_btn = QPushButton('🎲 Regenerate Noise Signal')
        regen_btn.clicked.connect(self.regenerate_noise)
        regen_layout.addWidget(regen_btn)
        regen_layout.addStretch()
        control_layout.addLayout(regen_layout)

        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)

        # ============================================================
        # Plot Controls
        # ============================================================
        plot_control_group = QGroupBox('Plot Controls')
        plot_control_layout = QHBoxLayout()

        # Plot type dropdown
        plot_control_layout.addWidget(QLabel('Plot Type:'))
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems(['Torque', 'Angular Acceleration', 'Transmission Ratio vs Wrist Angle'])
        self.plot_type_combo.currentTextChanged.connect(self.update_plot_type)
        plot_control_layout.addWidget(self.plot_type_combo)

        plot_control_layout.addStretch()

        # Signal visibility checkboxes
        plot_control_layout.addWidget(QLabel('Show:'))
        self.show_input_check = QCheckBox('Input Torque')
        self.show_input_check.setChecked(True)
        self.show_input_check.stateChanged.connect(lambda: self.update_signal_visibility('input_torque', self.show_input_check.isChecked()))
        plot_control_layout.addWidget(self.show_input_check)

        self.show_transmitted_check = QCheckBox('Transmitted Torque')
        self.show_transmitted_check.setChecked(True)
        self.show_transmitted_check.stateChanged.connect(lambda: self.update_signal_visibility('transmitted_torque', self.show_transmitted_check.isChecked()))
        plot_control_layout.addWidget(self.show_transmitted_check)

        self.show_alpha_torque_check = QCheckBox('τ_α')
        self.show_alpha_torque_check.setChecked(True)
        self.show_alpha_torque_check.stateChanged.connect(lambda: self.update_signal_visibility('torque_alpha', self.show_alpha_torque_check.isChecked()))
        plot_control_layout.addWidget(self.show_alpha_torque_check)

        self.show_gamma_torque_check = QCheckBox('τ_γ')
        self.show_gamma_torque_check.setChecked(True)
        self.show_gamma_torque_check.stateChanged.connect(lambda: self.update_signal_visibility('torque_gamma', self.show_gamma_torque_check.isChecked()))
        plot_control_layout.addWidget(self.show_gamma_torque_check)

        self.show_alpha_accel_check = QCheckBox('α_α')
        self.show_alpha_accel_check.setChecked(True)
        self.show_alpha_accel_check.stateChanged.connect(lambda: self.update_signal_visibility('accel_alpha', self.show_alpha_accel_check.isChecked()))
        plot_control_layout.addWidget(self.show_alpha_accel_check)

        self.show_gamma_accel_check = QCheckBox('α_γ')
        self.show_gamma_accel_check.setChecked(True)
        self.show_gamma_accel_check.stateChanged.connect(lambda: self.update_signal_visibility('accel_gamma', self.show_gamma_accel_check.isChecked()))
        plot_control_layout.addWidget(self.show_gamma_accel_check)

        self.show_transmission_check = QCheckBox('Transmission Ratio')
        self.show_transmission_check.setChecked(True)
        self.show_transmission_check.stateChanged.connect(lambda: self.update_signal_visibility('transmission_ratio', self.show_transmission_check.isChecked()))
        plot_control_layout.addWidget(self.show_transmission_check)

        self.show_velocity_check = QCheckBox('Velocity Ratio')
        self.show_velocity_check.setChecked(False)
        self.show_velocity_check.stateChanged.connect(lambda: self.update_signal_visibility('velocity_ratio', self.show_velocity_check.isChecked()))
        plot_control_layout.addWidget(self.show_velocity_check)

        self.show_accel_alpha_ratio_check = QCheckBox('Accel_α Ratio')
        self.show_accel_alpha_ratio_check.setChecked(False)
        self.show_accel_alpha_ratio_check.stateChanged.connect(lambda: self.update_signal_visibility('accel_alpha_ratio', self.show_accel_alpha_ratio_check.isChecked()))
        plot_control_layout.addWidget(self.show_accel_alpha_ratio_check)

        self.show_accel_gamma_ratio_check = QCheckBox('Accel_γ Ratio')
        self.show_accel_gamma_ratio_check.setChecked(False)
        self.show_accel_gamma_ratio_check.stateChanged.connect(lambda: self.update_signal_visibility('accel_gamma_ratio', self.show_accel_gamma_ratio_check.isChecked()))
        plot_control_layout.addWidget(self.show_accel_gamma_ratio_check)

        plot_control_group.setLayout(plot_control_layout)
        main_layout.addWidget(plot_control_group)

        # ============================================================
        # Plot Canvas
        # ============================================================
        plot_group = QGroupBox('Plot')
        plot_layout = QVBoxLayout()
        I_alpha, I_gamma = self.get_inertia_values()
        self.plot_canvas = PlotCanvas(
            grip_angle_deg=30,
            wrist_angle_deg=0,
            I_alpha=I_alpha,
            I_gamma=I_gamma
        )
        plot_layout.addWidget(self.plot_canvas)
        plot_group.setLayout(plot_layout)
        main_layout.addWidget(plot_group)

        # ============================================================
        # Info panel
        # ============================================================
        info_group = QGroupBox('Model Information')
        info_layout = QVBoxLayout()
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.update_info()
        info_layout.addWidget(self.info_label)
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)

        # Set main widget to scroll area
        self.scroll.setWidget(main_widget)
        self.setCentralWidget(self.scroll)

        # Connect sliders to update
        self.grip_slider.valueChanged.connect(self.update_all)
        self.wrist_slider.valueChanged.connect(self.update_all)

        # Initial update
        self.update_inertia()

    def get_inertia_values(self):
        """Get current inertia values from club properties"""
        return calculate_moments_of_inertia(
            self.clubhead_weight.value(),
            self.shaft_weight.value(),
            self.club_length.value(),
            self.cg_distance.value()
        )

    def update_inertia(self):
        """Update inertia display and plots"""
        I_alpha, I_gamma = self.get_inertia_values()
        self.inertia_label.setText(f'I_α={I_alpha:.4f} kg·m², I_γ={I_gamma:.4f} kg·m²')
        if hasattr(self, 'plot_canvas'):
            self.update_all()

    def update_grip_label(self, value):
        """Update grip angle label"""
        self.grip_label.setText(f'{value}°')
        if hasattr(self, 'plot_canvas'):
            self.update_all()

    def update_wrist_label(self, value):
        """Update wrist angle label"""
        self.wrist_label.setText(f'{value}°')
        if hasattr(self, 'plot_canvas'):
            self.update_all()

    def update_all(self):
        """Update diagram and plot"""
        grip_angle = self.grip_slider.value()
        wrist_angle = self.wrist_slider.value()
        I_alpha, I_gamma = self.get_inertia_values()

        self.diagram_canvas.update_angles(grip_angle, wrist_angle)
        self.plot_canvas.update_parameters(grip_angle, wrist_angle, I_alpha, I_gamma)
        self.update_info()

    def update_plot_type(self, plot_type):
        """Update plot type and enable/disable appropriate checkboxes"""
        self.plot_canvas.set_plot_type(plot_type)

        # Enable/disable checkboxes based on plot type
        is_torque = (plot_type == 'Torque')
        is_accel = (plot_type == 'Angular Acceleration')
        is_transmission = (plot_type == 'Transmission Ratio vs Wrist Angle')

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

    def update_signal_visibility(self, signal_name, visible):
        """Update signal visibility"""
        self.plot_canvas.set_signal_visible(signal_name, visible)

    def update_info(self):
        """Update information panel"""
        grip = self.grip_slider.value()
        wrist = self.wrist_slider.value()

        omega, tau = universal_joint_transmission_ratio(
            np.radians(wrist), np.radians(grip)
        )

        info_text = f"""
        <b>Current Configuration:</b><br>
        Grip={grip}°, Wrist={wrist}° → Transmission Ratio = {tau:.3f}<br>
        <br>
        <b>Key Insights:</b><br>
        • Transmission ratio <b>varies with wrist angle</b> (see transmission plot)<br>
        • At neutral wrist (φ≈0°): Maximum transmission efficiency<br>
        • At extreme flexion/extension: Reduced transmission<br>
        • Grip angle determines <b>which axes</b> receive transmitted torque<br>
        • Lower grip angle (fingers) → more torque to high-inertia axis (stability)<br>
        • Higher grip angle (palm) → more torque to shaft axis (face angle control)
        """
        self.info_label.setText(info_text)

    def regenerate_noise(self):
        """Regenerate noise on plot canvas"""
        self.plot_canvas.regenerate_noise()

    def update_noise_type(self, noise_type):
        """Update noise type"""
        self.plot_canvas.set_noise_type(noise_type)

    def eventFilter(self, obj, event):
        """Filter events to handle mouse wheel scrolling globally"""
        if event.type() == QEvent.Type.Wheel:
            scroll = self.centralWidget()
            if isinstance(scroll, QScrollArea):
                scroll_bar = scroll.verticalScrollBar()
                if scroll_bar and scroll_bar.isVisible():
                    delta = event.angleDelta().y()
                    scroll_bar.setValue(scroll_bar.value() - delta // 8)
                    return True
        return super().eventFilter(obj, event)

    def show_documentation(self):
        """Show documentation dialog"""
        dialog = DocumentationDialog(self)
        dialog.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
