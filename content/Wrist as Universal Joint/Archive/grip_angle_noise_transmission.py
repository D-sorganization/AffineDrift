"""
PyQt6 GUI: Grip Angle Noise Transmission Visualization
-----------------------------------------------------
This program demonstrates how grip angle modulates the transmission of forearm axis noise to the club's shaft axis.
At 0° grip angle, all noise is transmitted to the shaft axis (100%).
At 90°, none is transmitted (0%). Transmission is cos(angle).
"""

import sys

import numpy as np
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QLabel,
                             QMainWindow, QSlider, QSplitter, QVBoxLayout,
                             QWidget)


class NoiseTransmissionCanvas(FigureCanvas):
    """Shows original and transmitted noise plots."""

    def __init__(self, grip_angle_deg, noise=None):
        fig = Figure(figsize=(6, 4))
        super().__init__(fig)
        self.ax1 = fig.add_subplot(211)
        self.ax2 = fig.add_subplot(212)
        self.grip_angle_deg = grip_angle_deg
        self.noise = noise if noise is not None else self.generate_noise()
        self.plot_data()

    def generate_noise(self):
        # Example: sinusoidal + random noise
        t = np.linspace(0, 1, 500)
        noise = np.sin(8 * np.pi * t) + 0.3 * np.random.randn(len(t))
        return noise

    def plot_data(self):
        t = np.linspace(0, 1, len(self.noise))
        transmission = np.cos(np.deg2rad(self.grip_angle_deg))
        transmitted_noise = self.noise * transmission
        self.ax1.clear()
        self.ax2.clear()
        self.ax1.plot(t, self.noise, label="Original Noise", color="gray")
        self.ax1.set_title("Forearm Axis Noise Input")
        self.ax1.set_ylabel("Amplitude")
        self.ax1.grid(True)
        self.ax1.legend()
        self.ax2.plot(t, transmitted_noise, label="Transmitted to Shaft Axis", color="blue")
        self.ax2.set_title(f"Transmitted Noise (Grip Angle {self.grip_angle_deg:.0f}°)")
        self.ax2.set_xlabel("Time (s)")
        self.ax2.set_ylabel("Amplitude")
        self.ax2.grid(True)
        self.ax2.legend()
        self.draw()

    def update_grip_angle(self, grip_angle_deg):
        self.grip_angle_deg = grip_angle_deg
        self.plot_data()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grip Angle Noise Transmission Simulator")
        self.setGeometry(100, 100, 900, 600)
        self.grip_angle_deg = 0  # Initial grip angle
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Left panel: Controls
        control_group = QGroupBox("Controls")
        control_layout = QVBoxLayout()
        grip_label = QLabel("Grip Angle (degrees):")
        self.grip_slider = QSlider(Qt.Orientation.Horizontal)
        self.grip_slider.setMinimum(0)
        self.grip_slider.setMaximum(90)
        self.grip_slider.setValue(self.grip_angle_deg)
        self.grip_slider.setTickInterval(5)
        self.grip_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.grip_slider.valueChanged.connect(self.update_grip_angle)
        self.grip_value_label = QLabel(f"{self.grip_angle_deg}°")
        control_layout.addWidget(grip_label)
        control_layout.addWidget(self.grip_slider)
        control_layout.addWidget(self.grip_value_label)
        control_group.setLayout(control_layout)
        control_group.setMaximumWidth(250)

        # Info panel: Transmission percentage
        info_group = QGroupBox("Transmission Info")
        info_layout = QVBoxLayout()
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.update_info()
        info_layout.addWidget(self.info_label)
        info_group.setLayout(info_layout)
        info_group.setMaximumWidth(250)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(control_group)
        left_layout.addWidget(info_group)

        # Center panel: Noise transmission plot
        self.noise_canvas = NoiseTransmissionCanvas(self.grip_angle_deg)

        # Use QSplitter for resizable sections
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(self.noise_canvas)
        splitter.setSizes([250, 650])

        main_layout.addWidget(splitter)
        self.setCentralWidget(main_widget)

    def update_grip_angle(self, value):
        self.grip_angle_deg = value
        self.grip_value_label.setText(f"{self.grip_angle_deg}°")
        self.noise_canvas.update_grip_angle(self.grip_angle_deg)
        self.update_info()

    def update_info(self):
        transmission = np.cos(np.deg2rad(self.grip_angle_deg))
        percent = transmission * 100
        explanation = (
            f"<b>Grip Angle:</b> {self.grip_angle_deg}°<br>"
            f"<b>Transmission to Shaft Axis:</b> {percent:.1f}%<br>"
            "<hr>"
            "At 0°, all forearm axis noise is transmitted to the shaft axis (100%).<br>"
            "At 90°, none is transmitted (0%).<br>"
            "Transmission is proportional to cos(angle)."
        )
        self.info_label.setText(explanation)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
