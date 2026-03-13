"""
PyQt6 GUI for Wrist Grip Sensitivity Simulation
------------------------------------------------
This GUI allows users to explore how grip position affects torque and inertia at the wrist joint.
It features interactive sliders, live-updating plots, and a schematic diagram to visualize the mechanics.
"""

import sys

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSlider,
    QVBoxLayout,
    QWidget,
)

# Simulation parameters
WRIST_LENGTH = 0.18  # meters
FORCE_MAGNITUDE = 50  # Newtons
FORCE_ANGLE_DEG = 90  # degrees
MASS_HAND = 0.5  # kg
MASS_FOREARM = 1.2  # kg


# Calculation functions
def calculate_torque(grip_pos, force_magnitude, force_angle_deg):
    force_angle_rad = np.deg2rad(force_angle_deg)
    torque = grip_pos * force_magnitude * np.sin(force_angle_rad)
    return torque


def calculate_inertia_effect(grip_pos, mass_hand, mass_forearm):
    I_hand = mass_hand * grip_pos**2
    I_forearm = mass_forearm * (grip_pos / 2) ** 2
    return I_hand + I_forearm


class SchematicCanvas(FigureCanvas):
    """Draws a simple schematic of the wrist and grip position."""

    def __init__(self, grip_pos):
        fig = Figure(figsize=(3, 2))
        super().__init__(fig)
        self.ax = fig.add_subplot(111)
        self.grip_pos = grip_pos
        self.draw_schematic()

    def draw_schematic(self):
        self.ax.clear()
        # Draw forearm
        self.ax.plot([0, WRIST_LENGTH], [0, 0], "k-", lw=4, label="Forearm")
        # Draw wrist joint
        self.ax.plot([0], [0], "ro", markersize=10, label="Wrist Joint")
        # Draw grip position
        self.ax.plot([self.grip_pos], [0], "bo", markersize=10, label="Grip Position")
        self.ax.annotate("Grip", (self.grip_pos, 0.02), color="blue", ha="center")
        self.ax.annotate("Wrist", (0, -0.03), color="red", ha="center")
        self.ax.set_xlim(-0.02, WRIST_LENGTH + 0.02)
        self.ax.set_ylim(-0.05, 0.05)
        self.ax.axis("off")
        self.ax.legend(loc="upper right", fontsize=8)
        self.draw()

    def update_grip(self, grip_pos):
        self.grip_pos = grip_pos
        self.draw_schematic()


class PlotCanvas(FigureCanvas):
    """Matplotlib canvas for torque and inertia plots."""

    def __init__(self, grip_pos):
        fig = Figure(figsize=(5, 3))
        super().__init__(fig)
        self.ax = fig.add_subplot(111)
        self.grip_pos = grip_pos
        self.plot_data()

    def plot_data(self):
        self.ax.clear()
        grip_positions = np.linspace(0.02, WRIST_LENGTH - 0.02, 50)
        torques = [calculate_torque(x, FORCE_MAGNITUDE, FORCE_ANGLE_DEG) for x in grip_positions]
        inertia = [calculate_inertia_effect(x, MASS_HAND, MASS_FOREARM) for x in grip_positions]
        self.ax.plot(grip_positions, torques, label="Torque (Nm)")
        self.ax.plot(grip_positions, inertia, label="Inertia (kg*m^2)")
        # Highlight current grip position
        t = calculate_torque(self.grip_pos, FORCE_MAGNITUDE, FORCE_ANGLE_DEG)
        i = calculate_inertia_effect(self.grip_pos, MASS_HAND, MASS_FOREARM)
        self.ax.plot([self.grip_pos], [t], "ro", label="Current Torque")
        self.ax.plot([self.grip_pos], [i], "go", label="Current Inertia")
        self.ax.set_xlabel("Grip Position from Wrist (m)")
        self.ax.set_ylabel("Value")
        self.ax.set_title("Torque & Inertia vs. Grip Position")
        self.ax.grid(True)
        self.ax.legend(fontsize=8)
        self.draw()

    def update_grip(self, grip_pos):
        self.grip_pos = grip_pos
        self.plot_data()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wrist Grip Sensitivity Simulator")
        self.setGeometry(100, 100, 900, 500)
        self.grip_pos = 0.09  # Initial grip position (midpoint)
        self.initUI()

    def initUI(self):
        from PyQt6.QtWidgets import QSizePolicy, QSplitter

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Left panel: Controls (smaller size)
        control_group = QGroupBox("Controls")
        control_layout = QVBoxLayout()
        grip_label = QLabel("Grip Position (cm):")
        self.grip_slider = QSlider(Qt.Orientation.Horizontal)
        self.grip_slider.setMinimum(2)
        self.grip_slider.setMaximum(int((WRIST_LENGTH - 0.02) * 100))
        self.grip_slider.setValue(int(self.grip_pos * 100))
        self.grip_slider.setTickInterval(1)
        self.grip_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.grip_slider.valueChanged.connect(self.update_grip)
        self.grip_value_label = QLabel(f"{self.grip_pos*100:.1f} cm")
        control_layout.addWidget(grip_label)
        control_layout.addWidget(self.grip_slider)
        control_layout.addWidget(self.grip_value_label)
        control_group.setLayout(control_layout)
        control_group.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        # Info panel: Explanatory text
        info_group = QGroupBox("Explanation & Stats")
        info_layout = QVBoxLayout()
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.update_info()
        info_layout.addWidget(self.info_label)
        info_group.setLayout(info_layout)
        info_group.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(control_group)
        left_layout.addWidget(info_group)
        left_panel.setMaximumWidth(250)

        # Center panel: Plots
        self.plot_canvas = PlotCanvas(self.grip_pos)
        self.plot_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Right panel: Schematic (larger size)
        schematic_group = QGroupBox("Wrist Schematic")
        schematic_layout = QVBoxLayout()
        self.schematic_canvas = SchematicCanvas(self.grip_pos)
        self.schematic_canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        schematic_layout.addWidget(self.schematic_canvas)
        schematic_group.setLayout(schematic_layout)
        schematic_group.setMinimumWidth(300)
        schematic_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Use QSplitter for resizable sections
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(self.plot_canvas)
        splitter.addWidget(schematic_group)
        splitter.setSizes([200, 400, 300])

        main_layout.addWidget(splitter)
        self.setCentralWidget(main_widget)

    def update_grip(self, value):
        self.grip_pos = value / 100.0
        self.grip_value_label.setText(f"{self.grip_pos*100:.1f} cm")
        self.plot_canvas.update_grip(self.grip_pos)
        self.schematic_canvas.update_grip(self.grip_pos)
        self.update_info()

    def update_info(self):
        t = calculate_torque(self.grip_pos, FORCE_MAGNITUDE, FORCE_ANGLE_DEG)
        i = calculate_inertia_effect(self.grip_pos, MASS_HAND, MASS_FOREARM)
        explanation = (
            f"<b>Grip Position:</b> {self.grip_pos*100:.1f} cm from wrist joint<br>"
            f"<b>Torque at Wrist:</b> {t:.2f} Nm<br>"
            f"<b>Inertia Effect:</b> {i:.4f} kg·m²<br>"
            "<hr>"
            "<b>Explanation:</b> Changing the grip position alters the torque and inertia at the wrist. "
            "A grip farther from the wrist increases both torque and inertia, affecting force transmission. "
            "This reflects the mechanical principles described in the article: grip geometry modulates how constraint torques are routed through the wrist, influencing clubface variability and speed."
        )
        self.info_label.setText(explanation)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
