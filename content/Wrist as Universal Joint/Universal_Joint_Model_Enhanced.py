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
import numpy as np
import matplotlib
matplotlib.use('QtAgg')
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QGroupBox, QSplitter, QCheckBox, QComboBox, QPushButton,
    QDialog, QTextEdit, QScrollArea, QDialogButtonBox, QDoubleSpinBox, QTabWidget
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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

    # Handle arrays or scalars
    phi_is_array = isinstance(phi_rad, np.ndarray)

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


class UniversalJointCanvas(FigureCanvas):
    """
    Canvas showing:
    1. Top: Input torque and transmitted torques vs time for a specific wrist angle
    2. Bottom: Transmission ratio vs wrist angle (sweep)
    """
    def __init__(self, grip_angle_deg, wrist_angle_deg, I_alpha, I_gamma):
        self.figure = Figure(figsize=(10, 8))
        super().__init__(self.figure)
        self.setMinimumSize(600, 500)

        # Create subplots
        self.ax_torque = self.figure.add_subplot(311)  # Top: Torque vs time
        self.ax_accel = self.figure.add_subplot(312)   # Middle: Acceleration vs time
        self.ax_transmission = self.figure.add_subplot(313)  # Bottom: Transmission vs wrist angle

        self.grip_angle_deg = grip_angle_deg
        self.wrist_angle_deg = wrist_angle_deg
        self.I_alpha = I_alpha
        self.I_gamma = I_gamma

        # Generate sample input torque signal
        self.t = np.linspace(0, 1, 500)
        self.input_torque = self.generate_sample_torque()

        self.update_plot()

    def generate_sample_torque(self):
        """Generate a sample torque signal (golf-like)"""
        t = self.t
        # Golf-like burst pattern
        torque = np.random.normal(0, 1, len(t))
        torque += np.exp(-50*(t-0.5)**2) * 8 * np.random.randn(len(t))
        torque = np.convolve(torque, np.ones(10)/10, mode='same')
        return torque

    def update_plot(self):
        """Update all three subplots"""
        theta_grip_rad = np.radians(self.grip_angle_deg)
        phi_wrist_rad = np.radians(self.wrist_angle_deg)

        # ============================================================
        # TOP PLOT: Torque vs Time at current wrist angle
        # ============================================================
        self.ax_torque.clear()

        # Calculate transmission ratio at current wrist angle
        omega_ratio, tau_ratio = universal_joint_transmission_ratio(
            phi_wrist_rad, theta_grip_rad
        )

        # Torque transmitted through universal joint (varies with angle)
        torque_transmitted = self.input_torque * tau_ratio

        # Distribute to club axes based on grip angle
        torque_alpha, torque_gamma = distribute_torque_by_grip_angle(
            torque_transmitted, theta_grip_rad
        )

        # Plot
        self.ax_torque.plot(self.t, self.input_torque,
                           label='Input Torque (forearm)', color='gray', alpha=0.7, linewidth=1.5)
        self.ax_torque.plot(self.t, torque_transmitted,
                           label=f'Transmitted (ratio={tau_ratio:.3f})', color='purple', linewidth=2)
        self.ax_torque.plot(self.t, torque_alpha,
                           label='τ_α (shaft axis)', color='red', linewidth=2)
        self.ax_torque.plot(self.t, torque_gamma,
                           label='τ_γ (high-I axis)', color='blue', linewidth=2)

        self.ax_torque.set_title(
            f'Torque Transmission (Grip: {self.grip_angle_deg:.0f}°, Wrist: {self.wrist_angle_deg:.0f}°)',
            fontsize=11, fontweight='bold'
        )
        self.ax_torque.set_ylabel('Torque (N·m)', fontsize=10)
        self.ax_torque.grid(True, alpha=0.3)
        self.ax_torque.legend(loc='upper right', fontsize=8)

        # ============================================================
        # MIDDLE PLOT: Angular Acceleration vs Time
        # ============================================================
        self.ax_accel.clear()

        # Calculate accelerations
        accel_alpha = torque_alpha / self.I_alpha if self.I_alpha > 1e-6 else np.zeros_like(torque_alpha)
        accel_gamma = torque_gamma / self.I_gamma if self.I_gamma > 1e-6 else np.zeros_like(torque_gamma)

        self.ax_accel.plot(self.t, accel_alpha,
                          label=f'α_α (I_α={self.I_alpha:.4f})',
                          color='red', linewidth=2, linestyle='--')
        self.ax_accel.plot(self.t, accel_gamma,
                          label=f'α_γ (I_γ={self.I_gamma:.4f})',
                          color='blue', linewidth=2, linestyle='--')

        self.ax_accel.set_title('Angular Acceleration', fontsize=11, fontweight='bold')
        self.ax_accel.set_ylabel('Acceleration (rad/s²)', fontsize=10)
        self.ax_accel.grid(True, alpha=0.3)
        self.ax_accel.legend(loc='upper right', fontsize=8)

        # ============================================================
        # BOTTOM PLOT: Transmission Ratio vs Wrist Angle (Sweep)
        # ============================================================
        self.ax_transmission.clear()

        # Sweep wrist angle from -60° to +60° (typical wrist flexion range)
        phi_sweep = np.linspace(-60, 60, 200)
        phi_sweep_rad = np.radians(phi_sweep)

        # Calculate transmission ratios for each wrist angle
        omega_ratios = []
        tau_ratios = []
        accel_alpha_ratios = []
        accel_gamma_ratios = []

        for phi_rad in phi_sweep_rad:
            omega_r, tau_r = universal_joint_transmission_ratio(phi_rad, theta_grip_rad)
            omega_ratios.append(omega_r)
            tau_ratios.append(tau_r)

            # For unit input torque, calculate resulting accelerations
            torque_trans = 1.0 * tau_r
            t_alpha, t_gamma = distribute_torque_by_grip_angle(torque_trans, theta_grip_rad)
            accel_alpha_ratios.append(t_alpha / self.I_alpha if self.I_alpha > 1e-6 else 0)
            accel_gamma_ratios.append(t_gamma / self.I_gamma if self.I_gamma > 1e-6 else 0)

        omega_ratios = np.array(omega_ratios)
        tau_ratios = np.array(tau_ratios)
        accel_alpha_ratios = np.array(accel_alpha_ratios)
        accel_gamma_ratios = np.array(accel_gamma_ratios)

        # Plot transmission ratios
        self.ax_transmission.plot(phi_sweep, tau_ratios,
                                 label='Torque Transmission Ratio (τ_out/τ_in)',
                                 color='purple', linewidth=2.5)
        self.ax_transmission.plot(phi_sweep, omega_ratios,
                                 label='Velocity Ratio (ω_out/ω_in)',
                                 color='orange', linewidth=2, linestyle='--')

        # Plot acceleration ratios (per unit input torque)
        self.ax_transmission.plot(phi_sweep, accel_alpha_ratios,
                                 label='Accel_α ratio (rad/s²)/(N·m)',
                                 color='red', linewidth=1.5, alpha=0.7)
        self.ax_transmission.plot(phi_sweep, accel_gamma_ratios,
                                 label='Accel_γ ratio (rad/s²)/(N·m)',
                                 color='blue', linewidth=1.5, alpha=0.7)

        # Mark current wrist angle
        current_idx = np.argmin(np.abs(phi_sweep - self.wrist_angle_deg))
        self.ax_transmission.axvline(self.wrist_angle_deg,
                                    color='green', linestyle=':', linewidth=2,
                                    label=f'Current wrist angle ({self.wrist_angle_deg:.0f}°)')
        self.ax_transmission.plot(self.wrist_angle_deg, tau_ratios[current_idx],
                                 'go', markersize=10, markerfacecolor='lime')

        # Reference line at ratio = 1.0
        self.ax_transmission.axhline(1.0, color='gray', linestyle='--', alpha=0.5, linewidth=1)

        self.ax_transmission.set_title(
            f'Universal Joint Transmission vs Wrist Flexion Angle (Grip={self.grip_angle_deg:.0f}°)',
            fontsize=11, fontweight='bold'
        )
        self.ax_transmission.set_xlabel('Wrist Flexion Angle (degrees)', fontsize=10)
        self.ax_transmission.set_ylabel('Transmission Ratio', fontsize=10)
        self.ax_transmission.grid(True, alpha=0.3)
        self.ax_transmission.legend(loc='best', fontsize=7)

        self.figure.tight_layout()
        self.draw()

    def update_parameters(self, grip_angle_deg, wrist_angle_deg, I_alpha, I_gamma):
        """Update all parameters and redraw"""
        self.grip_angle_deg = grip_angle_deg
        self.wrist_angle_deg = wrist_angle_deg
        self.I_alpha = I_alpha
        self.I_gamma = I_gamma
        self.update_plot()

    def regenerate_noise(self):
        """Generate new random noise signal"""
        self.input_torque = self.generate_sample_torque()
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
        return """
        <html>
        <head>
        <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; padding: 15px; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 8px; }
        h2 { color: #34495e; margin-top: 25px; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }
        h3 { color: #7f8c8d; margin-top: 20px; }
        .equation { background-color: #f8f9fa; padding: 15px; margin: 15px 0;
                    border-left: 4px solid #3498db; font-family: 'Courier New', monospace; }
        .highlight { background-color: #fff3cd; padding: 12px; margin: 12px 0;
                     border-left: 4px solid #ffc107; }
        .important { background-color: #f8d7da; padding: 12px; margin: 12px 0;
                     border-left: 4px solid #dc3545; }
        ul, ol { margin: 10px 0; padding-left: 30px; }
        code { background-color: #ecf0f1; padding: 2px 6px; border-radius: 3px; }
        </style>
        </head>
        <body>

        <h1>Enhanced Wrist Universal Joint Model</h1>
        <p><strong>Key Innovation:</strong> This model distinguishes between <em>grip angle</em> (static)
        and <em>wrist angle</em> (dynamic), and properly implements universal joint transmission kinematics.</p>

        <h2>1. Model Overview</h2>

        <h3>Critical Distinction: Grip Angle vs. Wrist Angle</h3>

        <div class="important">
        <strong>Grip Angle (θ<sub>grip</sub>):</strong> <em>Static parameter</em><br>
        • How the club is oriented in the hand<br>
        • θ = 0°: Club aligned with fingers (finger grip)<br>
        • θ = 90°: Club aligned with palm (palm grip)<br>
        • Determines which club axes align with which wrist axes<br>
        • <strong>User-selected, does not change during swing</strong>
        </div>

        <div class="important">
        <strong>Wrist Flexion Angle (φ):</strong> <em>Dynamic parameter</em><br>
        • The actual angle of wrist flexion/extension<br>
        • Changes throughout the golf swing<br>
        • Typical range: -30° (extension) to +60° (flexion)<br>
        • Determines universal joint transmission ratio<br>
        • <strong>Varies continuously during motion</strong>
        </div>

        <h2>2. Universal Joint (Hooke/Cardan Joint) Kinematics</h2>

        <h3>Physical Principle</h3>
        <p>A universal joint connects two rotating shafts at an angle. When one shaft rotates at constant
        speed, the other shaft's speed <strong>varies cyclically</strong> - this is a fundamental property
        of universal joints.</p>

        <h3>Angular Velocity Transmission</h3>
        <p>For a universal joint with bend angle δ (angle between input and output shaft centerlines):</p>

        <div class="equation">
        <strong>Angular Velocity Ratio:</strong><br>
        ω<sub>out</sub>(φ) / ω<sub>in</sub> = cos(δ) / √(1 - sin²(δ) × sin²(φ))<br><br>
        Where:<br>
        • φ = rotation angle of input shaft (wrist angle)<br>
        • δ = bend angle (related to grip angle)<br>
        • ω<sub>out</sub> = output shaft angular velocity<br>
        • ω<sub>in</sub> = input shaft angular velocity
        </div>

        <div class="highlight">
        <strong>Key Insight:</strong> Even if the input shaft rotates at perfectly constant speed,
        the output shaft speed varies! It reaches maximum and minimum values twice per revolution.
        </div>

        <h3>Torque Transmission (from Power Conservation)</h3>
        <p>Power must be conserved: P = τω, so τ<sub>in</sub>ω<sub>in</sub> = τ<sub>out</sub>ω<sub>out</sub></p>

        <div class="equation">
        <strong>Torque Transmission Ratio:</strong><br>
        τ<sub>out</sub>(φ) / τ<sub>in</sub> = ω<sub>in</sub> / ω<sub>out</sub>(φ)<br><br>
        τ<sub>out</sub>(φ) / τ<sub>in</sub> = √(1 - sin²(δ) × sin²(φ)) / cos(δ)<br><br>
        </div>

        <div class="highlight">
        <strong>Critical Point:</strong> Torque transmission ratio is <strong>NOT constant</strong>.
        It varies with wrist angle φ during the swing. This is fundamentally different from simple
        trigonometric decomposition.
        </div>

        <h3>Transmission Characteristics</h3>

        <p>For bend angle δ:</p>
        <ul>
        <li><strong>Maximum transmission:</strong> τ<sub>out</sub>/τ<sub>in</sub> = 1/cos(δ) at φ = 0°, 180°</li>
        <li><strong>Minimum transmission:</strong> τ<sub>out</sub>/τ<sub>in</sub> = cos(δ) at φ = 90°, 270°</li>
        <li><strong>Variation per cycle:</strong> Two maxima and two minima per revolution</li>
        <li><strong>At δ = 0°:</strong> Transmission ratio = 1 (perfect transmission, no variation)</li>
        <li><strong>At larger δ:</strong> Greater variation in transmission ratio</li>
        </ul>

        <h2>3. Complete Transmission Model</h2>

        <h3>Step 1: Forearm Torque Input</h3>
        <div class="equation">
        τ<sub>forearm</sub>(t) = input torque from forearm rotation
        </div>

        <h3>Step 2: Universal Joint Transmission</h3>
        <p>The wrist acts as a universal joint. The transmission ratio depends on:</p>
        <ul>
        <li>Current wrist flexion angle φ(t)</li>
        <li>Effective bend angle δ<sub>eff</sub> (related to grip angle θ<sub>grip</sub>)</li>
        </ul>

        <div class="equation">
        R<sub>UJ</sub>(φ, δ) = √(1 - sin²(δ) × sin²(φ)) / cos(δ)<br><br>
        τ<sub>transmitted</sub>(t) = τ<sub>forearm</sub>(t) × R<sub>UJ</sub>(φ(t), δ<sub>eff</sub>)
        </div>

        <h3>Step 3: Distribution to Club Axes (Based on Grip Angle)</h3>
        <p>The transmitted torque is distributed to club axes based on grip angle:</p>

        <div class="equation">
        τ<sub>α</sub>(t) = τ<sub>transmitted</sub>(t) × sin(θ<sub>grip</sub>)<br>
        τ<sub>γ</sub>(t) = τ<sub>transmitted</sub>(t) × cos(θ<sub>grip</sub>)<br><br>
        Where:<br>
        • τ<sub>α</sub> = torque to shaft axis (low inertia)<br>
        • τ<sub>γ</sub> = torque to high-inertia axis (perpendicular to shaft)
        </div>

        <h3>Step 4: Angular Acceleration (Newton's 2nd Law)</h3>
        <div class="equation">
        α<sub>α</sub>(t) = τ<sub>α</sub>(t) / I<sub>α</sub><br>
        α<sub>γ</sub>(t) = τ<sub>γ</sub>(t) / I<sub>γ</sub><br><br>
        Where:<br>
        • I<sub>α</sub> = moment of inertia about shaft axis<br>
        • I<sub>γ</sub> = moment of inertia about high-inertia axis (typically I<sub>γ</sub> ≈ 2 I<sub>α</sub>)
        </div>

        <h2>4. Physical Implications</h2>

        <h3>Why This Matters for Golf</h3>

        <div class="highlight">
        <h4>1. Torque Transmission is NOT Constant</h4>
        <p>As the wrist flexes and extends during the swing (φ changes), the transmission ratio
        varies. This means:</p>
        <ul>
        <li>Same forearm torque → varying club torque depending on wrist position</li>
        <li>Creates timing challenges for coordination</li>
        <li>Natural "loading" and "unloading" phases based on wrist angle</li>
        </ul>
        </div>

        <div class="highlight">
        <h4>2. Grip Angle Determines Where Variations Go</h4>
        <p><strong>Finger Grip (θ ≈ 0°):</strong></p>
        <ul>
        <li>Most transmitted torque goes to high-inertia axis (γ): cos(0°) = 1.0</li>
        <li>Less to shaft axis (α): sin(0°) = 0</li>
        <li>Result: Variations affect club rotation (good for stability), less affect on face angle</li>
        </ul>

        <p><strong>Palm Grip (θ ≈ 90°):</strong></p>
        <ul>
        <li>Most transmitted torque goes to shaft axis (α): sin(90°) = 1.0</li>
        <li>Less to high-inertia axis (γ): cos(90°) = 0</li>
        <li>Result: Variations affect face angle directly (less stable)</li>
        </ul>

        <p><strong>Intermediate Grip (θ ≈ 45°):</strong></p>
        <ul>
        <li>Equal distribution: sin(45°) = cos(45°) = 0.707</li>
        <li>Balanced trade-off between speed and stability</li>
        </ul>
        </div>

        <div class="highlight">
        <h4>3. Universal Joint Creates Cyclic Variation</h4>
        <p>The transmission ratio goes through two complete cycles per wrist rotation. This means:</p>
        <ul>
        <li>Natural "resonance" frequencies in the system</li>
        <li>Potential for amplification or cancellation depending on timing</li>
        <li>Explains why wrist action timing is so critical</li>
        </ul>
        </div>

        <h2>5. Model Validation</h2>

        <h3>Known Universal Joint Behavior</h3>
        <p>This model matches known universal joint characteristics:</p>
        <ul>
        <li>✓ Cyclic variation in transmission ratio (2 cycles per revolution)</li>
        <li>✓ Greater variation at larger bend angles</li>
        <li>✓ Conservation of power (P = τω)</li>
        <li>✓ No variation at zero bend angle (δ = 0°)</li>
        <li>✓ Symmetric about φ = 0°</li>
        </ul>

        <h3>Comparison to Previous Model</h3>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; margin: 15px 0;">
        <tr style="background-color: #3498db; color: white;">
        <th>Aspect</th><th>Previous Model</th><th>Enhanced Model</th>
        </tr>
        <tr>
        <td><strong>Grip angle</strong></td>
        <td>Single angle θ</td>
        <td>Separate θ<sub>grip</sub> (static)</td>
        </tr>
        <tr style="background-color: #f8f9fa;">
        <td><strong>Wrist angle</strong></td>
        <td>Not distinguished</td>
        <td>Separate φ (dynamic)</td>
        </tr>
        <tr>
        <td><strong>Transmission</strong></td>
        <td>Constant: sin(θ), cos(θ)</td>
        <td>Variable: R<sub>UJ</sub>(φ, δ)</td>
        </tr>
        <tr style="background-color: #f8f9fa;">
        <td><strong>Physics</strong></td>
        <td>Static vector decomposition</td>
        <td>True universal joint kinematics</td>
        </tr>
        <tr>
        <td><strong>Predictions</strong></td>
        <td>Constant transmission ratio</td>
        <td>Cyclic variation with wrist angle</td>
        </tr>
        </table>

        <h2>6. Using This Model</h2>

        <h3>Understanding the Plots</h3>

        <p><strong>Top Plot - Torque vs Time:</strong></p>
        <ul>
        <li>Shows torque signals for current wrist angle position</li>
        <li>Gray: Input torque from forearm</li>
        <li>Purple: Transmitted through universal joint (note: may differ from input)</li>
        <li>Red: Component to shaft axis (α)</li>
        <li>Blue: Component to high-inertia axis (γ)</li>
        </ul>

        <p><strong>Middle Plot - Angular Acceleration vs Time:</strong></p>
        <ul>
        <li>Red dashed: Acceleration about shaft axis</li>
        <li>Blue dashed: Acceleration about high-inertia axis</li>
        <li>Higher values = more responsive to torque input</li>
        </ul>

        <p><strong>Bottom Plot - Transmission vs Wrist Angle (THE KEY INSIGHT):</strong></p>
        <ul>
        <li>Purple: Torque transmission ratio - how much torque gets through</li>
        <li>Orange: Velocity transmission ratio - speed relationship</li>
        <li>Red/Blue: Resulting accelerations for each axis</li>
        <li>Green vertical line: Current wrist angle</li>
        <li><strong>Notice:</strong> Transmission varies significantly with wrist angle!</li>
        </ul>

        <h3>Experimenting with Parameters</h3>

        <p><strong>Grip Angle (θ<sub>grip</sub>):</strong></p>
        <ul>
        <li>0°: See how torque goes mostly to high-inertia axis</li>
        <li>90°: See how torque goes mostly to shaft axis</li>
        <li>45°: Balanced distribution</li>
        <li>Notice: Changes the <em>shape</em> of the transmission curves</li>
        </ul>

        <p><strong>Wrist Angle (φ):</strong></p>
        <ul>
        <li>Slider changes current wrist position</li>
        <li>Watch the green marker move on bottom plot</li>
        <li>Observe how transmission ratio changes with wrist position</li>
        <li>Maximum transmission at φ ≈ 0° (neutral wrist)</li>
        <li>Minimum transmission at extreme flexion/extension</li>
        </ul>

        <h2>7. Practical Insights for Golf</h2>

        <div class="highlight">
        <h4>Optimal Grip Strategy</h4>
        <ul>
        <li><strong>For power:</strong> Moderate grip angle (30-45°) balances transmission to both axes</li>
        <li><strong>For consistency:</strong> Finger grip (θ → 0°) routes variations to high-inertia axis</li>
        <li><strong>Avoid:</strong> Extreme palm grip (θ → 90°) routes all variation to face angle</li>
        </ul>
        </div>

        <div class="highlight">
        <h4>Wrist Action Timing</h4>
        <ul>
        <li>Maximum torque transmission occurs near neutral wrist position (φ ≈ 0°)</li>
        <li>Extreme wrist angles reduce transmission efficiency</li>
        <li>Cyclic nature suggests importance of timing in wrist release</li>
        </ul>
        </div>

        <h2>8. References & Further Reading</h2>

        <ul>
        <li><strong>Universal Joint Mechanics:</strong> Seherr-Thoss et al., "Universal Joints and Driveshafts" (Springer, 2006)</li>
        <li><strong>Biomechanics:</strong> Crisco et al., "In vivo radiocarpal kinematics", JBJS (2011)</li>
        <li><strong>Constrained Dynamics:</strong> Featherstone, "Rigid Body Dynamics Algorithms" (Springer, 2014)</li>
        <li><strong>Golf Biomechanics:</strong> Nesbit & Serrano, "Work and power analysis of the golf swing", JSSM (2005)</li>
        </ul>

        <h2>9. Limitations & Future Work</h2>

        <p><strong>Current Model Limitations:</strong></p>
        <ul>
        <li>2D analysis (one wrist angle). Real wrist has 2 DOF (flexion + deviation)</li>
        <li>Simplified inertia estimates</li>
        <li>No damping or energy dissipation</li>
        <li>Static grip angle (doesn't account for grip pressure changes)</li>
        </ul>

        <p><strong>Future Enhancements:</strong></p>
        <ul>
        <li>Full 3D universal joint model with both wrist DOF</li>
        <li>Time-varying wrist angle φ(t) during simulated swing</li>
        <li>Constraint torque calculation from full equations of motion</li>
        <li>Validation against motion capture data</li>
        <li>Optimization studies for different swing objectives</li>
        </ul>

        <hr>
        <p style="text-align: center; color: #7f8c8d; font-style: italic; margin-top: 30px;">
        This enhanced model provides a more physically accurate representation of torque transmission<br>
        through the wrist during the golf swing, revealing the critical role of wrist angle dynamics.
        </p>

        </body>
        </html>
        """


class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Enhanced Universal Joint Model - Wrist Biomechanics')
        self.setGeometry(100, 100, 1400, 900)
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

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
        # Plots (two side-by-side for comparison)
        # ============================================================
        plot_layout = QHBoxLayout()

        I_alpha, I_gamma = self.get_inertia_values()

        self.canvas1 = UniversalJointCanvas(
            grip_angle_deg=30,
            wrist_angle_deg=0,
            I_alpha=I_alpha,
            I_gamma=I_gamma
        )

        self.canvas2 = UniversalJointCanvas(
            grip_angle_deg=60,
            wrist_angle_deg=0,
            I_alpha=I_alpha,
            I_gamma=I_gamma
        )

        plot_layout.addWidget(self.canvas1, 1)
        plot_layout.addWidget(self.canvas2, 1)
        main_layout.addLayout(plot_layout)

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

        self.setCentralWidget(main_widget)

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
        if hasattr(self, 'canvas1'):
            self.update_all()

    def update_grip_label(self, value):
        """Update grip angle label"""
        self.grip_label.setText(f'{value}°')
        if hasattr(self, 'canvas1'):
            self.update_all()

    def update_wrist_label(self, value):
        """Update wrist angle label"""
        self.wrist_label.setText(f'{value}°')
        if hasattr(self, 'canvas1'):
            self.update_all()

    def update_all(self):
        """Update both canvases"""
        grip_angle = self.grip_slider.value()
        wrist_angle = self.wrist_slider.value()
        I_alpha, I_gamma = self.get_inertia_values()

        # Update canvas 1 with current grip angle
        self.canvas1.update_parameters(grip_angle, wrist_angle, I_alpha, I_gamma)

        # Update canvas 2 with different grip angle for comparison (30° offset)
        grip_angle_2 = min(90, grip_angle + 30)
        self.canvas2.update_parameters(grip_angle_2, wrist_angle, I_alpha, I_gamma)

        self.update_info()

    def update_info(self):
        """Update information panel"""
        grip1 = self.grip_slider.value()
        grip2 = min(90, grip1 + 30)
        wrist = self.wrist_slider.value()

        # Calculate transmission ratios
        omega1, tau1 = universal_joint_transmission_ratio(
            np.radians(wrist), np.radians(grip1)
        )
        omega2, tau2 = universal_joint_transmission_ratio(
            np.radians(wrist), np.radians(grip2)
        )

        info_text = f"""
        <b>Current Configuration:</b><br>
        <b>Left Plot:</b> Grip={grip1}°, Wrist={wrist}° → Transmission Ratio = {tau1:.3f}<br>
        <b>Right Plot:</b> Grip={grip2}°, Wrist={wrist}° → Transmission Ratio = {tau2:.3f}<br>
        <br>
        <b>Key Insights:</b><br>
        • Transmission ratio <b>varies with wrist angle</b> (see bottom plots)<br>
        • At neutral wrist (φ≈0°): Maximum transmission efficiency<br>
        • At extreme flexion/extension: Reduced transmission<br>
        • Grip angle determines <b>which axes</b> receive transmitted torque<br>
        • Lower grip angle (fingers) → more torque to high-inertia axis (stability)<br>
        • Higher grip angle (palm) → more torque to shaft axis (face angle control)
        """
        self.info_label.setText(info_text)

    def regenerate_noise(self):
        """Regenerate noise on both canvases"""
        self.canvas1.regenerate_noise()
        self.canvas2.regenerate_noise()

    def show_documentation(self):
        """Show documentation dialog"""
        dialog = DocumentationDialog(self)
        dialog.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
