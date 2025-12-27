"""
PyQt6 GUI: Grip Angle Noise Transmission Comparison
--------------------------------------------------
This program visualizes how grip angle modulates transmission of forearm axis noise to the club's shaft axis (local alpha) and high inertia axis (local gamma).
Features:
- Two independently adjustable grip angles for side-by-side comparison
- Multiple noise input options (random, burst, step, user-defined)
- Plot total input, local alpha (sin(theta)), local gamma (cos(theta)) on same plot
- Checkboxes to toggle signal visibility
- Clear labels and explanations
"""
import sys

import matplotlib
import numpy as np

matplotlib.use('QtAgg')  # Set backend explicitly for PyQt6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
                             QDialogButtonBox, QDoubleSpinBox, QGroupBox,
                             QHBoxLayout, QLabel, QMainWindow, QPushButton,
                             QScrollArea, QSlider, QTextEdit, QVBoxLayout,
                             QWidget)

NOISE_TYPES = ['Golf-like Random', 'Burst', 'Step', 'Sinusoidal']

# Default golf club properties (representative values)
DEFAULT_CLUBHEAD_WEIGHT = 200.0  # grams
DEFAULT_SHAFT_WEIGHT = 100.0  # grams
DEFAULT_CLUB_LENGTH = 1.0  # meters (typical driver length)
DEFAULT_CLUBHEAD_CG_DISTANCE = 0.85  # meters from grip (distance to center of mass)

def calculate_moments_of_inertia(clubhead_weight_g, shaft_weight_g, club_length_m, cg_distance_m):
    """
    Calculate moments of inertia for golf club about two axes.

    Parameters:
    - clubhead_weight_g: Clubhead weight in grams
    - shaft_weight_g: Shaft weight in grams
    - club_length_m: Total club length in meters
    - cg_distance_m: Distance from grip to clubhead center of mass in meters

    Returns:
    - I_alpha: Moment of inertia about shaft axis (kg·m²)
    - I_gamma: Moment of inertia about high inertia axis (kg·m²)
    """
    # Convert to kg
    m_head = clubhead_weight_g / 1000.0  # kg
    m_shaft = shaft_weight_g / 1000.0  # kg

    # Shaft inertia (thin rod about its end): I = (1/3) * m * L²
    # For shaft, assume uniform distribution
    I_shaft_alpha = (1/3) * m_shaft * club_length_m**2

    # Clubhead inertia about shaft axis (point mass at distance r)
    I_head_alpha = m_head * cg_distance_m**2

    # Total I_alpha (about shaft axis)
    I_alpha = I_shaft_alpha + I_head_alpha

    # I_gamma (about high inertia axis, perpendicular to shaft)
    # For clubhead: treat as point mass, but with additional term for rotation
    # Typical golf club: I_gamma is larger due to clubhead geometry
    # Approximate: I_gamma ≈ 2-3 × I_alpha for typical clubs
    # More accurate: I_gamma includes clubhead's own moment of inertia
    # For a typical iron: I_gamma ≈ 1.5-2.5 × I_alpha
    # Using a conservative estimate: I_gamma = 2.0 × I_alpha
    I_gamma = 2.0 * I_alpha

    return I_alpha, I_gamma

def calculate_acceleration(torque, moment_of_inertia):
    """
    Calculate angular acceleration from torque.

    α = τ / I

    Parameters:
    - torque: Torque array (N·m)
    - moment_of_inertia: Moment of inertia (kg·m²)

    Returns:
    - acceleration: Angular acceleration array (rad/s²)
    """
    # Avoid division by zero
    if moment_of_inertia < 1e-6:
        return np.zeros_like(torque)
    return torque / moment_of_inertia

class NoiseTransmissionCanvas(FigureCanvas):
    def __init__(self, grip_angle_deg, noise_type, show_input, show_alpha, show_gamma,
                 I_alpha, I_gamma, show_torque, show_acceleration, noise=None):
        self.figure = Figure(figsize=(8, 6))
        super().__init__(self.figure)
        self.setMinimumSize(500, 400)  # Set minimum size for canvas
        # Create two subplots: torque and acceleration
        self.ax_torque = self.figure.add_subplot(211)
        self.ax_accel = self.figure.add_subplot(212)
        self.grip_angle_deg = grip_angle_deg
        self.noise_type = noise_type
        self.show_input = show_input
        self.show_alpha = show_alpha
        self.show_gamma = show_gamma
        self.I_alpha = I_alpha
        self.I_gamma = I_gamma
        self.show_torque = show_torque
        self.show_acceleration = show_acceleration
        self.noise = noise if noise is not None else self.generate_noise()
        # Store y-axis limits
        self.torque_y_min = None
        self.torque_y_max = None
        self.accel_y_min = None
        self.accel_y_max = None
        self.update_plot()

    def generate_noise(self):
        t = np.linspace(0, 1, 500)
        if self.noise_type == 'Golf-like Random':
            # Simulate golf-like bursts and randomness
            noise = np.random.normal(0, 1, len(t))
            noise += np.exp(-50*(t-0.5)**2)*8*np.random.randn(len(t))  # burst near middle
            noise = np.convolve(noise, np.ones(10)/10, mode='same')  # smooth
        elif self.noise_type == 'Burst':
            noise = np.zeros_like(t)
            noise[200:300] = np.random.normal(0, 2, 100)
        elif self.noise_type == 'Step':
            noise = np.zeros_like(t)
            noise[250:] = 3
        elif self.noise_type == 'Sinusoidal':
            noise = np.sin(8 * np.pi * t)
        else:
            noise = np.random.normal(0, 1, len(t))
        return noise

    def update_plot(self, update_limits=False):
        t = np.linspace(0, 1, len(self.noise))
        theta_rad = np.deg2rad(self.grip_angle_deg)
        # Calculate transmitted torques (N·m) - treating noise as torque input
        torque_alpha = self.noise * np.sin(theta_rad)
        torque_gamma = self.noise * np.cos(theta_rad)

        # Calculate angular accelerations (rad/s²): α = τ / I
        accel_alpha = calculate_acceleration(torque_alpha, self.I_alpha)
        accel_gamma = calculate_acceleration(torque_gamma, self.I_gamma)

        # TORQUE PLOT (top subplot)
        self.ax_torque.clear()
        if self.show_torque:
            if self.show_input:
                self.ax_torque.plot(t, self.noise, label='Input Torque', color='gray', alpha=0.7, linewidth=1.5)
            if self.show_alpha:
                self.ax_torque.plot(t, torque_alpha, label='Torque α (sin θ)', color='red', linewidth=2)
            if self.show_gamma:
                self.ax_torque.plot(t, torque_gamma, label='Torque γ (cos θ)', color='blue', linewidth=2)

        self.ax_torque.set_title(f'Transmitted Torque (Grip Angle {self.grip_angle_deg:.0f}°)', fontsize=11, fontweight='bold')
        self.ax_torque.set_ylabel('Torque (N·m)', fontsize=10)
        self.ax_torque.grid(True, alpha=0.3)
        self.ax_torque.legend(loc='upper left', fontsize=8)

        # Set torque y-axis limits
        if update_limits or self.torque_y_min is None or self.torque_y_max is None:
            all_torque_data = [self.noise]
            if self.show_alpha:
                all_torque_data.append(torque_alpha)
            if self.show_gamma:
                all_torque_data.append(torque_gamma)
            if all_torque_data:
                combined = np.concatenate(all_torque_data)
                data_range = np.max(combined) - np.min(combined)
                margin = data_range * 0.1 if data_range > 0 else 0.1
                self.torque_y_min = np.min(combined) - margin
                self.torque_y_max = np.max(combined) + margin
        self.ax_torque.set_ylim(self.torque_y_min, self.torque_y_max)

        # Add schematic to torque plot
        try:
            inset_ax = self.ax_torque.inset_axes([0.65, 0.65, 0.32, 0.32])
            # Draw club as horizontal shaft
            shaft_y = 0.15
            inset_ax.plot([0, 1], [shaft_y, shaft_y], 'k-', lw=6)

            # Draw golf clubhead as rectangle pointing upwards above the shaft at far left end
            from matplotlib.patches import Rectangle
            clubhead_x = 0.0  # Far left end of shaft
            clubhead_y = shaft_y + 0.05  # Above the shaft
            clubhead_width = 0.1
            clubhead_height = 0.12
            clubhead = Rectangle((clubhead_x, clubhead_y), clubhead_width, clubhead_height,
                                facecolor='silver', alpha=0.8, edgecolor='gray', linewidth=1.5)
            inset_ax.add_patch(clubhead)

            # Draw hand as ellipse on the right side
            hand_center = (0.75, shaft_y)
            hand_width = 0.25
            hand_height = 0.12
            from matplotlib.patches import Ellipse
            hand = Ellipse(hand_center, hand_width, hand_height, angle=self.grip_angle_deg, facecolor='tan', alpha=0.7, edgecolor='saddlebrown', linewidth=1.5)
            inset_ax.add_patch(hand)

            # Draw 4 fingers that rotate from pointing left (at 0°) to pointing down (at 90°)
            finger_length = 0.15
            finger_width = 0.02
            # Hand's long axis direction
            hand_dir_x = np.cos(theta_rad)
            hand_dir_y = np.sin(theta_rad)
            # Finger direction: rotates from left (-1,0) at 0° to down (0,-1) at 90°
            finger_dir_x = -np.cos(theta_rad)  # Points left at 0°, down at 90°
            finger_dir_y = -np.sin(theta_rad)

            # Finger base positions along the hand (perpendicular to hand's long axis)
            # Spacing along the hand's short axis
            perp_to_hand_x = -hand_dir_y  # Perpendicular to hand axis
            perp_to_hand_y = hand_dir_x
            finger_spacing = 0.04
            finger_positions = [-1.5, -0.5, 0.5, 1.5]  # Relative positions for 4 fingers

            for _i, pos in enumerate(finger_positions):
                # Calculate finger base position (along hand's short axis)
                base_x = hand_center[0] + pos * finger_spacing * perp_to_hand_x
                base_y = hand_center[1] + pos * finger_spacing * perp_to_hand_y
                # Finger extends in finger direction
                tip_x = base_x + finger_length * finger_dir_x
                tip_y = base_y + finger_length * finger_dir_y
                # Draw finger as ellipse
                finger_mid_x = (base_x + tip_x) / 2
                finger_mid_y = (base_y + tip_y) / 2
                finger_angle = np.rad2deg(np.arctan2(finger_dir_y, finger_dir_x))
                finger = Ellipse((finger_mid_x, finger_mid_y), finger_length, finger_width,
                                angle=finger_angle, facecolor='tan', alpha=0.8, edgecolor='saddlebrown', linewidth=0.5)
                inset_ax.add_patch(finger)

            # Draw theta angle arc (from club axis to hand axis)
            arc_radius = 0.18
            arc_theta = np.linspace(0, theta_rad, 30)
            arc_center_x = hand_center[0] - 0.1  # Slightly left of hand center
            arc_center_y = shaft_y
            arc_x = arc_center_x + arc_radius * np.cos(arc_theta)
            arc_y = arc_center_y + arc_radius * np.sin(arc_theta)
            inset_ax.plot(arc_x, arc_y, 'g-', lw=2)

            # Draw angle lines
            # Club axis (horizontal)
            inset_ax.arrow(arc_center_x, arc_center_y, 0.18, 0, head_width=0.02, head_length=0.03, fc='k', ec='k')
            # Hand axis (rotated)
            inset_ax.arrow(arc_center_x, arc_center_y, 0.18*np.cos(theta_rad), 0.18*np.sin(theta_rad),
                          head_width=0.02, head_length=0.03, fc='r', ec='r')
            # Label theta
            label_x = arc_center_x + arc_radius * np.cos(theta_rad/2)
            label_y = arc_center_y + arc_radius * np.sin(theta_rad/2)
            inset_ax.text(label_x, label_y+0.03, r"$\theta$", color='g', fontsize=14, ha='center')
            inset_ax.text(arc_center_x+0.19, arc_center_y-0.04, 'Club Axis', color='k', fontsize=8, ha='center')
            inset_ax.text(arc_center_x+0.19*np.cos(theta_rad), arc_center_y+0.19*np.sin(theta_rad)+0.04, 'Hand Axis', color='r', fontsize=8, ha='center')
            inset_ax.set_xlim(0, 1)
            inset_ax.set_ylim(-0.1, 0.4)
            inset_ax.axis('off')
            inset_ax.set_title(r"Schematic: $\theta$", fontsize=10)
        except Exception as e:
            print(f"Warning: Could not create inset axes: {e}")

        # ACCELERATION PLOT (bottom subplot)
        self.ax_accel.clear()
        if self.show_acceleration:
            if self.show_alpha:
                self.ax_accel.plot(t, accel_alpha, label='Accel α (rad/s²)', color='red', linewidth=2, linestyle='--')
            if self.show_gamma:
                self.ax_accel.plot(t, accel_gamma, label='Accel γ (rad/s²)', color='blue', linewidth=2, linestyle='--')

        self.ax_accel.set_title(f'Angular Acceleration (Iα={self.I_alpha:.4f} kg·m², Iγ={self.I_gamma:.4f} kg·m²)',
                               fontsize=11, fontweight='bold')
        self.ax_accel.set_xlabel('Time (s)', fontsize=10)
        self.ax_accel.set_ylabel('Acceleration (rad/s²)', fontsize=10)
        self.ax_accel.grid(True, alpha=0.3)
        self.ax_accel.legend(loc='upper left', fontsize=8)

        # Set acceleration y-axis limits
        if update_limits or self.accel_y_min is None or self.accel_y_max is None:
            all_accel_data = []
            if self.show_alpha:
                all_accel_data.append(accel_alpha)
            if self.show_gamma:
                all_accel_data.append(accel_gamma)
            if all_accel_data:
                combined = np.concatenate(all_accel_data)
                data_range = np.max(combined) - np.min(combined)
                margin = data_range * 0.1 if data_range > 0 else 0.1
                self.accel_y_min = np.min(combined) - margin
                self.accel_y_max = np.max(combined) + margin
        self.ax_accel.set_ylim(self.accel_y_min, self.accel_y_max)

        self.figure.tight_layout()
        self.draw()

    def update_signals(self, grip_angle_deg, noise_type, show_input, show_alpha, show_gamma,
                      I_alpha, I_gamma, show_torque, show_acceleration, regenerate_noise=False):
        self.grip_angle_deg = grip_angle_deg
        self.show_input = show_input
        self.show_alpha = show_alpha
        self.show_gamma = show_gamma
        self.I_alpha = I_alpha
        self.I_gamma = I_gamma
        self.show_torque = show_torque
        self.show_acceleration = show_acceleration
        # Only regenerate noise if noise type changed or explicitly requested
        if regenerate_noise or noise_type != self.noise_type:
            self.noise_type = noise_type
            self.noise = self.generate_noise()
            self.update_plot(update_limits=True)  # Update limits when noise changes
        else:
            self.update_plot(update_limits=False)  # Keep same limits when only angle changes

class CalculationsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Calculations & Assumptions')
        self.setGeometry(200, 200, 800, 700)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Scrollable text area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        text_widget = QTextEdit()
        text_widget.setReadOnly(True)
        text_widget.setHtml(self.get_calculations_text())
        scroll.setWidget(text_widget)
        layout.addWidget(scroll)

        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)

    def get_calculations_text(self):
        return """
        <html>
        <head>
        <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
        h2 { color: #34495e; margin-top: 20px; }
        h3 { color: #7f8c8d; margin-top: 15px; }
        p { margin: 10px 0; }
        ul, ol { margin: 10px 0; padding-left: 30px; }
        code { background-color: #ecf0f1; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }
        .equation { background-color: #f8f9fa; padding: 10px; margin: 10px 0; border-left: 4px solid #3498db; }
        .assumption { background-color: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; }
        </style>
        </head>
        <body>

        <h1>Grip Angle Noise Transmission: Calculations & Assumptions</h1>

        <h2>1. Physical Model</h2>
        <p>This simulation models how torque noise in the forearm axis is transmitted to the golf club through the wrist joint, which acts as a universal joint. The transmission depends on the grip angle θ, defined as the angle between the club's shaft axis and the hand's long axis.</p>

        <h3>Coordinate System</h3>
        <ul>
        <li><strong>Forearm Axis:</strong> The axis along which torque noise originates (input signal)</li>
        <li><strong>Local Alpha (Shaft Axis):</strong> The component along the club's shaft axis</li>
        <li><strong>Local Gamma (High Inertia Axis):</strong> The component along the club's high moment of inertia axis (perpendicular to shaft)</li>
        </ul>

        <h2>2. Mathematical Relationships</h2>

        <h3>Vector Decomposition</h3>
        <p>When a torque <code>T</code> is applied along the forearm axis, it decomposes into two orthogonal components:</p>

        <div class="equation">
        <strong>Component Magnitudes:</strong><br>
        T<sub>α</sub> = T × sin(θ)  &nbsp;&nbsp;&nbsp; (Shaft axis component)<br>
        T<sub>γ</sub> = T × cos(θ)  &nbsp;&nbsp;&nbsp; (High inertia axis component)
        </div>

        <p>Where θ is the grip angle in degrees (0° to 90°).</p>

        <h3>Signal Transmission</h3>
        <p>For a noise signal <code>n(t)</code> in the forearm axis, the transmitted signals are:</p>

        <div class="equation">
        α(t) = n(t) × sin(θ)<br>
        γ(t) = n(t) × cos(θ)
        </div>

        <h3>Power/Energy Distribution</h3>
        <p>The power (or energy) distribution between components follows:</p>

        <div class="equation">
        P<sub>α</sub> = sin²(θ) × 100%<br>
        P<sub>γ</sub> = cos²(θ) × 100%<br>
        P<sub>α</sub> + P<sub>γ</sub> = sin²(θ) + cos²(θ) = 100%
        </div>

        <p><strong>Note:</strong> Component magnitudes (sin θ, cos θ) do not add to 100% because they are orthogonal vector components. The vector magnitude is preserved through the Pythagorean relationship: |T|² = |T<sub>α</sub>|² + |T<sub>γ</sub>|²</p>

        <h2>3. Key Assumptions</h2>

        <div class="assumption">
        <h3>3.1 Rigid Body Assumption</h3>
        <p>The hand, wrist, and club are treated as rigid bodies connected at the wrist joint. Deformations and compliance are neglected.</p>
        </div>

        <div class="assumption">
        <h3>3.2 Universal Joint Model</h3>
        <p>The wrist is modeled as an ideal universal joint, allowing rotation about two perpendicular axes. This assumes perfect mechanical coupling with no slip or play.</p>
        </div>

        <div class="assumption">
        <h3>3.3 Orthogonal Axes</h3>
        <p>The shaft axis (alpha) and high inertia axis (gamma) are assumed to be perfectly orthogonal. In reality, there may be slight deviations.</p>
        </div>

        <div class="assumption">
        <h3>3.4 Linear Transmission</h3>
        <p>The transmission is assumed to be linear - the output is directly proportional to the input, scaled by the trigonometric functions. Nonlinear effects (friction, damping, etc.) are not included.</p>
        </div>

        <div class="assumption">
        <h3>3.5 Constant Grip Angle</h3>
        <p>The grip angle θ is assumed to remain constant throughout the motion. Dynamic changes in grip angle during the swing are not modeled.</p>
        </div>

        <div class="assumption">
        <h3>3.6 No Energy Loss</h3>
        <p>The model assumes no energy dissipation. All input torque is transmitted to the output components (conservation of energy through vector decomposition).</p>
        </div>

        <div class="assumption">
        <h3>3.7 Two-Dimensional Analysis</h3>
        <p>The analysis is limited to a two-dimensional plane. Out-of-plane components and three-dimensional effects are not considered.</p>
        </div>

        <h2>4. Boundary Conditions</h2>

        <h3>At θ = 0°:</h3>
        <ul>
        <li>sin(0°) = 0 → No transmission to shaft axis (alpha = 0)</li>
        <li>cos(0°) = 1 → Full transmission to high inertia axis (gamma = 100%)</li>
        <li>All torque goes to the high inertia axis</li>
        </ul>

        <h3>At θ = 90°:</h3>
        <ul>
        <li>sin(90°) = 1 → Full transmission to shaft axis (alpha = 100%)</li>
        <li>cos(90°) = 0 → No transmission to high inertia axis (gamma = 0)</li>
        <li>All torque goes to the shaft axis</li>
        </ul>

        <h3>At θ = 45°:</h3>
        <ul>
        <li>sin(45°) = cos(45°) = 0.707 → Equal component magnitudes (70.7%)</li>
        <li>Power distribution: 50% to each axis</li>
        </ul>

        <h2>5. Noise Signal Types</h2>

        <h3>Golf-like Random</h3>
        <p>Simulates realistic golf swing noise with random variations and a burst near the middle of the swing (t = 0.5s), smoothed with a moving average filter.</p>

        <h3>Burst</h3>
        <p>A localized noise burst between t = 0.4s and t = 0.6s, useful for studying transient responses.</p>

        <h3>Step</h3>
        <p>A step function that jumps from 0 to a constant value at t = 0.5s, useful for studying steady-state transmission.</p>

        <h3>Sinusoidal</h3>
        <p>A sinusoidal signal with frequency 4 Hz (8π rad/s), useful for studying frequency-dependent transmission characteristics.</p>

        <h2>6. Moment of Inertia Calculations</h2>

        <h3>Club Inertia Model</h3>
        <p>The golf club is modeled as a composite system with two main components:</p>
        <ul>
        <li><strong>Shaft:</strong> Uniform rod rotating about one end</li>
        <li><strong>Clubhead:</strong> Point mass at distance r from grip</li>
        </ul>

        <h3>I_alpha (Shaft Axis Inertia)</h3>
        <div class="equation">
        I<sub>α</sub> = I<sub>shaft</sub> + I<sub>head</sub><br>
        I<sub>shaft</sub> = (1/3) × m<sub>shaft</sub> × L²<br>
        I<sub>head</sub> = m<sub>head</sub> × r²<br>
        Where:<br>
        - m<sub>shaft</sub> = shaft mass (kg)<br>
        - m<sub>head</sub> = clubhead mass (kg)<br>
        - L = club length (m)<br>
        - r = distance from grip to clubhead CG (m)
        </div>

        <h3>I_gamma (High Inertia Axis)</h3>
        <p>For typical golf clubs, the moment of inertia about the high inertia axis (perpendicular to shaft) is approximately 2× the shaft axis inertia due to clubhead geometry and mass distribution.</p>
        <div class="equation">
        I<sub>γ</sub> ≈ 2.0 × I<sub>α</sub>
        </div>

        <h2>7. Angular Acceleration Calculations</h2>

        <h3>Newton's Second Law for Rotation</h3>
        <p>Angular acceleration is calculated from transmitted torque using:</p>
        <div class="equation">
        α = τ / I<br>
        Where:<br>
        - α = angular acceleration (rad/s²)<br>
        - τ = torque (N·m)<br>
        - I = moment of inertia (kg·m²)
        </div>

        <h3>Acceleration Components</h3>
        <p>For each axis:</p>
        <div class="equation">
        α<sub>α</sub> = τ<sub>α</sub> / I<sub>α</sub><br>
        α<sub>γ</sub> = τ<sub>γ</sub> / I<sub>γ</sub>
        </div>

        <p><strong>Key Insight:</strong> Higher inertia means lower acceleration for the same torque. This is why clubhead weight and distribution significantly affect how noise impacts club motion.</p>

        <h2>8. Interpretation of Results</h2>

        <h3>What the Plots Show</h3>
        <p><strong>Torque Plots:</strong></p>
        <ul>
        <li><strong>Input Torque (gray):</strong> The original torque noise signal in the forearm axis</li>
        <li><strong>Torque α (red):</strong> The component transmitted to the shaft axis - affects clubhead orientation</li>
        <li><strong>Torque γ (blue):</strong> The component transmitted to the high inertia axis - affects club rotation about the shaft</li>
        </ul>
        <p><strong>Acceleration Plots:</strong></p>
        <ul>
        <li><strong>Accel α (red, dashed):</strong> Angular acceleration about shaft axis - shows how noise affects clubhead motion</li>
        <li><strong>Accel γ (blue, dashed):</strong> Angular acceleration about high inertia axis - shows how noise affects club rotation</li>
        </ul>
        <p><strong>Key Relationship:</strong> Acceleration = Torque / Inertia. Higher inertia reduces acceleration for the same torque input.</p>

        <h3>Understanding the Transmission</h3>
        <p>As the grip angle increases from 0° to 90°:</p>
        <ul>
        <li>More noise is transmitted to the shaft axis (alpha increases)</li>
        <li>Less noise is transmitted to the high inertia axis (gamma decreases)</li>
        <li>The total vector magnitude is preserved: |T| = √(T<sub>α</sub>² + T<sub>γ</sub>²)</li>
        </ul>

        <h2>9. Limitations & Future Work</h2>
        <ul>
        <li>This is a simplified model - real wrist mechanics involve more complex kinematics</li>
        <li>No damping or energy dissipation is included</li>
        <li>Dynamic grip angle changes during the swing are not modeled</li>
        <li>Three-dimensional effects and out-of-plane motion are not considered</li>
        <li>Muscle activation and active control are not included</li>
        </ul>

        <h2>10. References</h2>
        <p>This model is based on:</p>
        <ul>
        <li>Universal joint mechanics and vector decomposition principles</li>
        <li>Biomechanical models of wrist joint kinematics</li>
        <li>Golf swing biomechanics literature on grip effects</li>
        </ul>

        </body>
        </html>
        """

class AnglePanel(QWidget):
    def __init__(self, label, initial_angle=0):
        super().__init__()
        self.angle = initial_angle
        self.label = QLabel(label)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(90)
        self.slider.setValue(self.angle)
        self.slider.setTickInterval(5)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.value_label = QLabel(f'{self.angle}°')

        # Create layout with slider and labels
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(2)

        # Top row: label, slider, value
        top_row = QHBoxLayout()
        top_row.addWidget(self.label)
        top_row.addWidget(self.slider)
        top_row.addWidget(self.value_label)
        main_layout.addLayout(top_row)

        # Bottom row: degree labels below slider
        label_row = QHBoxLayout()
        label_row.addWidget(QLabel('0°'))  # Left label
        label_row.addStretch()  # Space for middle labels
        label_row.addWidget(QLabel('45°'))  # Middle label
        label_row.addStretch()  # Space for right
        label_row.addWidget(QLabel('90°'))  # Right label
        main_layout.addLayout(label_row)

        self.slider.valueChanged.connect(self.update_value)

    def update_value(self, value):
        self.angle = value
        self.value_label.setText(f'{self.angle}°')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Grip Angle Torque Transmission & Acceleration Analysis')
        self.setGeometry(100, 100, 1400, 900)
        self.initUI()

    def initUI(self):
        main_widget = QWidget()

        # Top bar with calculations button
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        calc_btn = QPushButton('📐 Calculations & Assumptions')
        calc_btn.setToolTip('View detailed calculations, assumptions, and model information')
        calc_btn.clicked.connect(self.show_calculations)
        top_bar.addWidget(calc_btn)
        top_bar.addStretch()

        # Club properties section
        club_props_group = QGroupBox('Club Properties (affects inertia and acceleration)')
        club_props_layout = QHBoxLayout()

        # Clubhead weight
        club_props_layout.addWidget(QLabel('Clubhead Weight (g):'))
        self.clubhead_weight = QDoubleSpinBox()
        self.clubhead_weight.setRange(50, 500)
        self.clubhead_weight.setValue(DEFAULT_CLUBHEAD_WEIGHT)
        self.clubhead_weight.setSuffix(' g')
        self.clubhead_weight.setDecimals(1)
        club_props_layout.addWidget(self.clubhead_weight)

        # Shaft weight
        club_props_layout.addWidget(QLabel('Shaft Weight (g):'))
        self.shaft_weight = QDoubleSpinBox()
        self.shaft_weight.setRange(30, 200)
        self.shaft_weight.setValue(DEFAULT_SHAFT_WEIGHT)
        self.shaft_weight.setSuffix(' g')
        self.shaft_weight.setDecimals(1)
        club_props_layout.addWidget(self.shaft_weight)

        # Club length
        club_props_layout.addWidget(QLabel('Club Length (m):'))
        self.club_length = QDoubleSpinBox()
        self.club_length.setRange(0.5, 1.5)
        self.club_length.setValue(DEFAULT_CLUB_LENGTH)
        self.club_length.setSuffix(' m')
        self.club_length.setDecimals(2)
        club_props_layout.addWidget(self.club_length)

        # CG distance
        club_props_layout.addWidget(QLabel('CG Distance (m):'))
        self.cg_distance = QDoubleSpinBox()
        self.cg_distance.setRange(0.3, 1.2)
        self.cg_distance.setValue(DEFAULT_CLUBHEAD_CG_DISTANCE)
        self.cg_distance.setSuffix(' m')
        self.cg_distance.setDecimals(2)
        club_props_layout.addWidget(self.cg_distance)

        # Inertia display
        self.inertia_label = QLabel()
        club_props_layout.addWidget(self.inertia_label)
        club_props_layout.addStretch()

        club_props_group.setLayout(club_props_layout)

        # Display/plot options
        display_group = QGroupBox('Display Options')
        display_layout = QHBoxLayout()
        self.show_torque = QCheckBox('Show Torque Plots')
        self.show_torque.setChecked(True)
        self.show_acceleration = QCheckBox('Show Acceleration Plots')
        self.show_acceleration.setChecked(True)
        display_layout.addWidget(self.show_torque)
        display_layout.addWidget(self.show_acceleration)
        display_layout.addStretch()
        display_group.setLayout(display_layout)

        # Connect club property changes
        self.clubhead_weight.valueChanged.connect(self.update_inertia)
        self.shaft_weight.valueChanged.connect(self.update_inertia)
        self.club_length.valueChanged.connect(self.update_inertia)
        self.cg_distance.valueChanged.connect(self.update_inertia)
        self.show_torque.stateChanged.connect(self.update_all_plots)
        self.show_acceleration.stateChanged.connect(self.update_all_plots)

        # Top header: sliders and options for both plots
        header_layout = QHBoxLayout()
        # Initialize all widgets before use
        self.angle_panel1 = AnglePanel('Grip Angle 1', 0)
        self.noise_type_box1 = QComboBox()
        self.noise_type_box1.addItems(NOISE_TYPES)
        self.show_input1 = QCheckBox('Show Total Input')
        self.show_input1.setChecked(True)
        self.show_alpha1 = QCheckBox('Show Local Alpha (sin θ)')
        self.show_alpha1.setChecked(True)
        self.show_gamma1 = QCheckBox('Show Local Gamma (cos θ)')
        self.show_gamma1.setChecked(True)
        self.update_btn1 = QPushButton('Update Plot 1')

        self.angle_panel2 = AnglePanel('Grip Angle 2', 90)
        self.noise_type_box2 = QComboBox()
        self.noise_type_box2.addItems(NOISE_TYPES)
        self.show_input2 = QCheckBox('Show Total Input')
        self.show_input2.setChecked(True)
        self.show_alpha2 = QCheckBox('Show Local Alpha (sin θ)')
        self.show_alpha2.setChecked(True)
        self.show_gamma2 = QCheckBox('Show Local Gamma (cos θ)')
        self.show_gamma2.setChecked(True)
        self.update_btn2 = QPushButton('Update Plot 2')

        # Plot 1 controls
        plot1_controls = QVBoxLayout()
        plot1_controls.addWidget(self.angle_panel1)
        plot1_controls.addWidget(QLabel('Noise Type'))
        plot1_controls.addWidget(self.noise_type_box1)
        plot1_controls.addWidget(self.show_input1)
        plot1_controls.addWidget(self.show_alpha1)
        plot1_controls.addWidget(self.show_gamma1)
        plot1_controls.addWidget(self.update_btn1)
        plot1_controls_widget = QWidget()
        plot1_controls_widget.setLayout(plot1_controls)
        # Plot 2 controls
        plot2_controls = QVBoxLayout()
        plot2_controls.addWidget(self.angle_panel2)
        plot2_controls.addWidget(QLabel('Noise Type'))
        plot2_controls.addWidget(self.noise_type_box2)
        plot2_controls.addWidget(self.show_input2)
        plot2_controls.addWidget(self.show_alpha2)
        plot2_controls.addWidget(self.show_gamma2)
        plot2_controls.addWidget(self.update_btn2)
        plot2_controls_widget = QWidget()
        plot2_controls_widget.setLayout(plot2_controls)
        header_layout.addWidget(plot1_controls_widget)
        header_layout.addWidget(plot2_controls_widget)

        # Center: Two plots
        I_alpha, I_gamma = self.get_inertia_values()
        self.canvas1 = NoiseTransmissionCanvas(
            self.angle_panel1.angle,
            self.noise_type_box1.currentText(),
            self.show_input1.isChecked(),
            self.show_alpha1.isChecked(),
            self.show_gamma1.isChecked(),
            I_alpha, I_gamma,
            self.show_torque.isChecked(),
            self.show_acceleration.isChecked()
        )
        self.canvas2 = NoiseTransmissionCanvas(
            self.angle_panel2.angle,
            self.noise_type_box2.currentText(),
            self.show_input2.isChecked(),
            self.show_alpha2.isChecked(),
            self.show_gamma2.isChecked(),
            I_alpha, I_gamma,
            self.show_torque.isChecked(),
            self.show_acceleration.isChecked()
        )
        plot_layout = QHBoxLayout()
        plot_layout.addWidget(self.canvas1, 1)  # Add stretch factor
        plot_layout.addWidget(self.canvas2, 1)  # Add stretch factor

        # Bottom: Transmission functions info
        info_group = QGroupBox('Transmission Functions')
        info_layout = QHBoxLayout()
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.update_info()
        info_layout.addWidget(self.info_label)
        info_group.setLayout(info_layout)

        # Main vertical layout
        main_vlayout = QVBoxLayout(main_widget)
        main_vlayout.addLayout(top_bar)
        main_vlayout.addWidget(club_props_group)
        main_vlayout.addWidget(display_group)
        main_vlayout.addLayout(header_layout)
        main_vlayout.addLayout(plot_layout)
        main_vlayout.addWidget(info_group)
        self.setCentralWidget(main_widget)

        # Initialize inertia display and update plots (after all widgets are created)
        self.update_inertia()

        # Connect controls for immediate interactivity
        self.update_btn1.clicked.connect(self.update_plot1)
        self.update_btn2.clicked.connect(self.update_plot2)
        self.angle_panel1.slider.valueChanged.connect(self.update_plot1)
        self.noise_type_box1.currentIndexChanged.connect(self.update_plot1)
        self.show_input1.stateChanged.connect(self.update_plot1)
        self.show_alpha1.stateChanged.connect(self.update_plot1)
        self.show_gamma1.stateChanged.connect(self.update_plot1)
        self.angle_panel2.slider.valueChanged.connect(self.update_plot2)
        self.noise_type_box2.currentIndexChanged.connect(self.update_plot2)
        self.show_input2.stateChanged.connect(self.update_plot2)
        self.show_alpha2.stateChanged.connect(self.update_plot2)
        self.show_gamma2.stateChanged.connect(self.update_plot2)

    def get_inertia_values(self):
        """Calculate and return I_alpha and I_gamma based on current club properties"""
        return calculate_moments_of_inertia(
            self.clubhead_weight.value(),
            self.shaft_weight.value(),
            self.club_length.value(),
            self.cg_distance.value()
        )

    def update_inertia(self):
        """Update inertia values and display, then update all plots"""
        I_alpha, I_gamma = self.get_inertia_values()
        self.inertia_label.setText(f'Iα = {I_alpha:.4f} kg·m², Iγ = {I_gamma:.4f} kg·m²')
        # Only update plots if canvases exist (after initialization)
        if hasattr(self, 'canvas1') and hasattr(self, 'canvas2'):
            self.update_all_plots()

    def update_all_plots(self):
        """Update both plots with current settings"""
        self.update_plot1()
        self.update_plot2()

    def update_plot1(self):
        # Check if noise type changed (requires regeneration)
        current_noise_type = self.noise_type_box1.currentText()
        regenerate = (current_noise_type != self.canvas1.noise_type)
        I_alpha, I_gamma = self.get_inertia_values()
        self.canvas1.update_signals(
            self.angle_panel1.angle,
            current_noise_type,
            self.show_input1.isChecked(),
            self.show_alpha1.isChecked(),
            self.show_gamma1.isChecked(),
            I_alpha, I_gamma,
            self.show_torque.isChecked(),
            self.show_acceleration.isChecked(),
            regenerate_noise=regenerate
        )
        self.update_info()

    def update_plot2(self):
        # Check if noise type changed (requires regeneration)
        current_noise_type = self.noise_type_box2.currentText()
        regenerate = (current_noise_type != self.canvas2.noise_type)
        I_alpha, I_gamma = self.get_inertia_values()
        self.canvas2.update_signals(
            self.angle_panel2.angle,
            current_noise_type,
            self.show_input2.isChecked(),
            self.show_alpha2.isChecked(),
            self.show_gamma2.isChecked(),
            I_alpha, I_gamma,
            self.show_torque.isChecked(),
            self.show_acceleration.isChecked(),
            regenerate_noise=regenerate
        )
        self.update_info()

    def update_info(self):
        theta1 = self.angle_panel1.angle
        theta2 = self.angle_panel2.angle
        theta1_rad = np.deg2rad(theta1)
        theta2_rad = np.deg2rad(theta2)

        # Component magnitudes (what's actually transmitted)
        alpha1_mag = np.abs(np.sin(theta1_rad))
        gamma1_mag = np.abs(np.cos(theta1_rad))
        alpha2_mag = np.abs(np.sin(theta2_rad))
        gamma2_mag = np.abs(np.cos(theta2_rad))

        # Power/energy percentages (these add to 100%)
        alpha1_power = np.sin(theta1_rad)**2
        gamma1_power = np.cos(theta1_rad)**2
        alpha2_power = np.sin(theta2_rad)**2
        gamma2_power = np.cos(theta2_rad)**2

        info = (
            f"<b>Transmission Functions:</b><br>"
            f"Local Alpha (shaft axis): sin(θ)<br>"
            f"Local Gamma (high inertia axis): cos(θ)<br>"
            f"<hr>"
            f"<b>Grip Angle 1:</b> {theta1}°<br>"
            f"Component Magnitudes: Alpha = {alpha1_mag*100:.1f}%, Gamma = {gamma1_mag*100:.1f}%<br>"
            f"Power Distribution: Alpha = {alpha1_power*100:.1f}%, Gamma = {gamma1_power*100:.1f}% (sum = {(alpha1_power+gamma1_power)*100:.1f}%)<br>"
            f"<b>Grip Angle 2:</b> {theta2}°<br>"
            f"Component Magnitudes: Alpha = {alpha2_mag*100:.1f}%, Gamma = {gamma2_mag*100:.1f}%<br>"
            f"Power Distribution: Alpha = {alpha2_power*100:.1f}%, Gamma = {gamma2_power*100:.1f}% (sum = {(alpha2_power+gamma2_power)*100:.1f}%)<br>"
            "<hr>"
            "<i>Note: Component magnitudes don't add to 100% (orthogonal vectors).<br>"
            "Power distribution shows energy share (adds to 100%).</i>"
        )
        self.info_label.setText(info)

    def show_calculations(self):
        """Open the calculations and assumptions dialog"""
        dialog = CalculationsDialog(self)
        dialog.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # Force initial update so plots are visible
    window.update_plot1()
    window.update_plot2()
    sys.exit(app.exec())
