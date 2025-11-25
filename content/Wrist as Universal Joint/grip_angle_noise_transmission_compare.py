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
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QGroupBox, QSplitter, QCheckBox, QComboBox, QPushButton
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

NOISE_TYPES = ['Golf-like Random', 'Burst', 'Step', 'Sinusoidal']

class NoiseTransmissionCanvas(FigureCanvas):
    def __init__(self, grip_angle_deg, noise_type, show_input, show_alpha, show_gamma, noise=None):
        fig = Figure(figsize=(6, 4))
        super().__init__(fig)
        self.ax = fig.add_subplot(111)
        self.grip_angle_deg = grip_angle_deg
        self.noise_type = noise_type
        self.show_input = show_input
        self.show_alpha = show_alpha
        self.show_gamma = show_gamma
        self.noise = noise if noise is not None else self.generate_noise()
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
        def update_plot(self):
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
            # Schematic: hand gripping club and theta angle
            try:
                inset_ax = self.ax.inset_axes([0.65, 0.65, 0.32, 0.32])
                # Draw club as horizontal shaft
                inset_ax.plot([0, 1], [0, 0], 'k-', lw=6)
                # Draw hand as ellipse
                hand_center = (0.5, 0.1)
                hand_width = 0.25
                hand_height = 0.12
                from matplotlib.patches import Ellipse
                hand = Ellipse(hand_center, hand_width, hand_height, angle=self.grip_angle_deg, color='tan', alpha=0.7)
                inset_ax.add_patch(hand)
                # Draw theta angle arc
                arc_radius = 0.18
                arc_theta = np.linspace(0, theta_rad, 30)
                arc_x = hand_center[0] + arc_radius * np.cos(arc_theta)
                arc_y = hand_center[1] + arc_radius * np.sin(arc_theta)
                inset_ax.plot(arc_x, arc_y, 'g-', lw=2)
                # Draw angle lines
                # Club axis (horizontal)
                inset_ax.arrow(hand_center[0], hand_center[1], 0.18, 0, head_width=0.02, head_length=0.03, fc='k', ec='k')
                # Hand axis (rotated)
                inset_ax.arrow(hand_center[0], hand_center[1], 0.18*np.cos(theta_rad), 0.18*np.sin(theta_rad), head_width=0.02, head_length=0.03, fc='r', ec='r')
                # Label theta
                label_x = hand_center[0] + arc_radius * np.cos(theta_rad/2)
                label_y = hand_center[1] + arc_radius * np.sin(theta_rad/2)
                inset_ax.text(label_x, label_y+0.03, r"$\theta$", color='g', fontsize=14, ha='center')
                inset_ax.text(hand_center[0]+0.19, hand_center[1]-0.04, 'Club Axis', color='k', fontsize=8, ha='center')
                inset_ax.text(hand_center[0]+0.19*np.cos(theta_rad), hand_center[1]+0.19*np.sin(theta_rad)+0.04, 'Hand Axis', color='r', fontsize=8, ha='center')
                inset_ax.set_xlim(0, 1)
                inset_ax.set_ylim(-0.15, 0.35)
                inset_ax.axis('off')
                inset_ax.set_title(r"Schematic: $\theta$", fontsize=10)
            except Exception as e:
                pass
            self.draw()
        inset_ax.set_xlim(0, 1)
        inset_ax.set_ylim(-0.15, 0.35)
        inset_ax.axis('off')
        inset_ax.set_title(r"Schematic: $\theta$")
        self.draw()

    def update_signals(self, grip_angle_deg, noise_type, show_input, show_alpha, show_gamma):
        self.grip_angle_deg = grip_angle_deg
        self.noise_type = noise_type
        self.show_input = show_input
        self.show_alpha = show_alpha
        self.show_gamma = show_gamma
        self.noise = self.generate_noise()
        self.update_plot()

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
        main_layout = QHBoxLayout(main_widget)

        # Top header: sliders and options for both plots
        header_layout = QHBoxLayout()
        # Initialize angle panels before use
        self.angle_panel1 = AnglePanel('Grip Angle 1', 0)
        self.angle_panel2 = AnglePanel('Grip Angle 2', 90)
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
        plot_layout.addWidget(self.canvas1)
        plot_layout.addWidget(self.canvas2)

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

        # Connect controls
        self.update_btn1.clicked.connect(self.update_plot1)
        self.update_btn2.clicked.connect(self.update_plot2)

    def update_plot1(self):
        self.canvas1.update_signals(
            self.angle_panel1.angle,
            self.noise_type_box1.currentText(),
            self.show_input1.isChecked(),
            self.show_alpha1.isChecked(),
            self.show_gamma1.isChecked()
        )
        self.update_info()

    def update_plot2(self):
        self.canvas2.update_signals(
            self.angle_panel2.angle,
            self.noise_type_box2.currentText(),
            self.show_input2.isChecked(),
            self.show_alpha2.isChecked(),
            self.show_gamma2.isChecked()
        )
        self.update_info()

    def update_info(self):
        theta1 = self.angle_panel1.angle
        theta2 = self.angle_panel2.angle
        info = (
            f"<b>Transmission Functions:</b><br>"
            f"Local Alpha (shaft axis): sin(θ)<br>"
            f"Local Gamma (high inertia axis): cos(θ)<br>"
            f"<hr>"
            f"<b>Grip Angle 1:</b> {theta1}°<br>"
            f"Local Alpha: {np.sin(np.deg2rad(theta1))*100:.1f}%<br>"
            f"Local Gamma: {np.cos(np.deg2rad(theta1))*100:.1f}%<br>"
            f"<b>Grip Angle 2:</b> {theta2}°<br>"
            f"Local Alpha: {np.sin(np.deg2rad(theta2))*100:.1f}%<br>"
            f"Local Gamma: {np.cos(np.deg2rad(theta2))*100:.1f}%<br>"
            "<hr>"
            "Use checkboxes to show/hide signals."
        )
        self.info_label.setText(info)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
