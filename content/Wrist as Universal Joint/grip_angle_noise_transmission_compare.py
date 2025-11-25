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
import numpy as np
import matplotlib
matplotlib.use('QtAgg')  # Set backend explicitly for PyQt6
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QGroupBox, QSplitter, QCheckBox, QComboBox, QPushButton
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

NOISE_TYPES = ['Golf-like Random', 'Burst', 'Step', 'Sinusoidal']

class NoiseTransmissionCanvas(FigureCanvas):
    def __init__(self, grip_angle_deg, noise_type, show_input, show_alpha, show_gamma, noise=None):
        self.figure = Figure(figsize=(6, 4))
        super().__init__(self.figure)
        self.setMinimumSize(400, 300)  # Set minimum size for canvas
        self.ax = self.figure.add_subplot(111)
        self.grip_angle_deg = grip_angle_deg
        self.noise_type = noise_type
        self.show_input = show_input
        self.show_alpha = show_alpha
        self.show_gamma = show_gamma
        self.noise = noise if noise is not None else self.generate_noise()
        # Store y-axis limits based on initial noise (will be set after first plot)
        self.y_min = None
        self.y_max = None
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
        alpha = self.noise * np.sin(theta_rad)
        gamma = self.noise * np.cos(theta_rad)
        self.ax.clear()
        # Main noise transmission plot
        if self.show_input:
            self.ax.plot(t, self.noise, label='Total Input', color='gray', alpha=0.7)
        if self.show_alpha:
            self.ax.plot(t, alpha, label='Local Alpha (sin θ)', color='red')
        if self.show_gamma:
            self.ax.plot(t, gamma, label='Local Gamma (cos θ)', color='blue')
        self.ax.set_title(f'Noise Transmission (Grip Angle {self.grip_angle_deg:.0f}°)', fontsize=12)
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Amplitude')
        self.ax.grid(True)
        self.ax.legend(loc='upper left', fontsize=9)
        
        # Set y-axis limits only when noise is regenerated, not when angle changes
        if update_limits or self.y_min is None or self.y_max is None:
            # Calculate limits based on all possible signals (input, alpha, gamma)
            all_data = [self.noise]
            if self.show_alpha:
                all_data.append(alpha)
            if self.show_gamma:
                all_data.append(gamma)
            if all_data:
                combined = np.concatenate(all_data)
                data_range = np.max(combined) - np.min(combined)
                margin = data_range * 0.1  # 10% margin
                self.y_min = np.min(combined) - margin
                self.y_max = np.max(combined) + margin
        # Always use the stored limits
        self.ax.set_ylim(self.y_min, self.y_max)
        # Schematic: hand gripping club and theta angle
        try:
            inset_ax = self.ax.inset_axes([0.65, 0.65, 0.32, 0.32])
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
                                color='silver', alpha=0.8, edgecolor='gray', linewidth=1.5)
            inset_ax.add_patch(clubhead)
            
            # Draw hand as ellipse on the right side
            hand_center = (0.75, shaft_y)
            hand_width = 0.25
            hand_height = 0.12
            from matplotlib.patches import Ellipse
            hand = Ellipse(hand_center, hand_width, hand_height, angle=self.grip_angle_deg, color='tan', alpha=0.7, edgecolor='saddlebrown', linewidth=1.5)
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
            
            for i, pos in enumerate(finger_positions):
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
                                angle=finger_angle, color='tan', alpha=0.8, edgecolor='saddlebrown', linewidth=0.5)
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
        self.figure.tight_layout()
        self.draw()

    def update_signals(self, grip_angle_deg, noise_type, show_input, show_alpha, show_gamma, regenerate_noise=False):
        self.grip_angle_deg = grip_angle_deg
        self.show_input = show_input
        self.show_alpha = show_alpha
        self.show_gamma = show_gamma
        # Only regenerate noise if noise type changed or explicitly requested
        if regenerate_noise or noise_type != self.noise_type:
            self.noise_type = noise_type
            self.noise = self.generate_noise()
            self.update_plot(update_limits=True)  # Update limits when noise changes
        else:
            self.update_plot(update_limits=False)  # Keep same limits when only angle changes

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
        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.value_label)
        self.slider.valueChanged.connect(self.update_value)
    def update_value(self, value):
        self.angle = value
        self.value_label.setText(f'{self.angle}°')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Grip Angle Noise Transmission Comparison')
        self.setGeometry(100, 100, 1200, 700)
        self.initUI()

    def initUI(self):
        main_widget = QWidget()

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
        self.canvas1 = NoiseTransmissionCanvas(
            self.angle_panel1.angle,
            self.noise_type_box1.currentText(),
            self.show_input1.isChecked(),
            self.show_alpha1.isChecked(),
            self.show_gamma1.isChecked()
        )
        self.canvas2 = NoiseTransmissionCanvas(
            self.angle_panel2.angle,
            self.noise_type_box2.currentText(),
            self.show_input2.isChecked(),
            self.show_alpha2.isChecked(),
            self.show_gamma2.isChecked()
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
        main_vlayout.addLayout(header_layout)
        main_vlayout.addLayout(plot_layout)
        main_vlayout.addWidget(info_group)
        self.setCentralWidget(main_widget)

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

    def update_plot1(self):
        # Check if noise type changed (requires regeneration)
        current_noise_type = self.noise_type_box1.currentText()
        regenerate = (current_noise_type != self.canvas1.noise_type)
        self.canvas1.update_signals(
            self.angle_panel1.angle,
            current_noise_type,
            self.show_input1.isChecked(),
            self.show_alpha1.isChecked(),
            self.show_gamma1.isChecked(),
            regenerate_noise=regenerate
        )
        self.update_info()

    def update_plot2(self):
        # Check if noise type changed (requires regeneration)
        current_noise_type = self.noise_type_box2.currentText()
        regenerate = (current_noise_type != self.canvas2.noise_type)
        self.canvas2.update_signals(
            self.angle_panel2.angle,
            current_noise_type,
            self.show_input2.isChecked(),
            self.show_alpha2.isChecked(),
            self.show_gamma2.isChecked(),
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # Force initial update so plots are visible
    window.update_plot1()
    window.update_plot2()
    sys.exit(app.exec())
