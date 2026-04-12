"""Qt canvas widgets for the enhanced wrist universal joint app."""

from __future__ import annotations

import matplotlib
import numpy as np
from PyQt6.QtCore import QEvent
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QWidget

from .constants import DEFAULT_SIGNAL_LENGTH
from .enhanced_model_geometry import draw_enhanced_model_diagram
from .enhanced_model_kinematics import (
    TransmissionSweep,
    build_info_html,
    compute_acceleration_signals,
    compute_torque_signals,
    compute_transmission_sweep,
)
from .torque_calculator import calculate_moments_of_inertia, generate_sample_torque

# Do not force "QtAgg" if already configured to a non-interactive backend (like "headless" during tests)
if matplotlib.get_backend().lower() not in ("agg", "headless", "template"):
    matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


def find_main_window_parent(widget: QWidget | None) -> QMainWindow | None:
    """Walk parent pointers until the owning main window is found."""
    parent = widget
    while parent and not isinstance(parent, QMainWindow):
        parent = parent.parentWidget()
    return parent if isinstance(parent, QMainWindow) else None


class DiagramCanvas(FigureCanvas):  # type: ignore[misc]
    """Canvas showing the forearm-hand-club diagram."""

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
        """Ignore wheel events so the parent scroll area handles them."""
        event.ignore()

    def update_diagram(self) -> None:
        """Redraw the diagram for the current angles."""
        self.ax.clear()
        draw_enhanced_model_diagram(self.ax, self.grip_angle_deg, self.wrist_angle_deg)
        self.figure.tight_layout()
        self.draw()

    def update_angles(self, grip_angle_deg: float, wrist_angle_deg: float) -> None:
        """Update angles and redraw the diagram."""
        self.grip_angle_deg = grip_angle_deg
        self.wrist_angle_deg = wrist_angle_deg
        self.update_diagram()


class PlotCanvas(FigureCanvas):  # type: ignore[misc]
    """Canvas showing torque, acceleration, or transmission plots."""

    DEFAULT_POLYNOMIAL = "t**2 - t"

    def __init__(
        self,
        grip_angle_deg: float,
        wrist_angle_deg: float,
        i_alpha: float,
        i_gamma: float,
    ) -> None:
        """Initialize plot canvas with angles and inertia values."""
        self.figure = Figure(figsize=(10, 6))
        super().__init__(self.figure)
        self.setMinimumSize(700, 500)
        self.ax = self.figure.add_subplot(111)
        self.grip_angle_deg = grip_angle_deg
        self.wrist_angle_deg = wrist_angle_deg
        self.i_alpha = i_alpha
        self.i_gamma = i_gamma
        self.polynomial_error: str | None = None
        self.t = np.linspace(0, 1, DEFAULT_SIGNAL_LENGTH)
        self.noise_type = "Golf-like Random"
        self.polynomial_expression = self.DEFAULT_POLYNOMIAL
        self.current_plot_type = "Torque"
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
        self._refresh_input_torque()
        self.update_plot()

    def _refresh_input_torque(self) -> None:
        """Regenerate the configured input torque signal."""
        self.input_torque, self.polynomial_error = generate_sample_torque(
            self.noise_type,
            self.t,
            self.polynomial_expression,
        )

    def _warn_polynomial_error(self) -> None:
        """Display the current polynomial-evaluation warning, if present."""
        if not self.polynomial_error:
            return
        parent = find_main_window_parent(self.parentWidget())
        if parent is not None:
            QMessageBox.warning(parent, "Polynomial Evaluation Error", self.polynomial_error)

    def set_noise_type(self, noise_type: str) -> None:
        """Set noise type and regenerate the input signal."""
        self.noise_type = noise_type
        self._refresh_input_torque()
        if self.current_plot_type in {"Torque", "Angular Acceleration"}:
            self.update_plot()

    def set_polynomial_expression(self, expression: str) -> None:
        """Set the polynomial expression and refresh the signal if needed."""
        self.polynomial_expression = expression
        if self.noise_type == "Polynomial":
            self._refresh_input_torque()
            self._warn_polynomial_error()
            if self.current_plot_type in {"Torque", "Angular Acceleration"}:
                self.update_plot()

    def update_plot(self) -> None:
        """Update the plot based on current settings."""
        self.ax.clear()
        if self.current_plot_type == "Torque":
            self._plot_torque()
        elif self.current_plot_type == "Angular Acceleration":
            self._plot_acceleration()
        else:
            self._plot_transmission_sweep()
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc="best", fontsize=9)
        self.figure.tight_layout()
        self.draw()

    def _plot_torque(self) -> None:
        """Plot torque traces for the current configuration."""
        signals = compute_torque_signals(
            self.input_torque,
            self.grip_angle_deg,
            self.wrist_angle_deg,
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
                signals.torque_transmitted,
                label=f"Transmitted (ratio={signals.tau_ratio:.3f})",
                color="purple",
                linewidth=2,
            )
        if self.visible_signals["torque_alpha"]:
            self.ax.plot(
                self.t,
                signals.torque_alpha,
                label="τ_α (higher MOI axis)",
                color="red",
                linewidth=2,
            )
        if self.visible_signals["torque_gamma"]:
            self.ax.plot(
                self.t,
                signals.torque_gamma,
                label="τ_γ (lowest MOI axis)",
                color="blue",
                linewidth=2,
            )
        self.ax.set_title(
            (
                "Torque vs Time "
                f"(Grip: {self.grip_angle_deg:.0f}°, Wrist: {self.wrist_angle_deg:.0f}°)"
            ),
            fontsize=12,
            fontweight="bold",
        )
        self.ax.set_xlabel("Time (s)", fontsize=10)
        self.ax.set_ylabel("Torque (N·m)", fontsize=10)

    def _plot_acceleration(self) -> None:
        """Plot angular acceleration traces for the current configuration."""
        signals = compute_acceleration_signals(
            self.input_torque,
            self.grip_angle_deg,
            self.wrist_angle_deg,
            self.i_alpha,
            self.i_gamma,
        )
        if self.visible_signals["accel_alpha"]:
            self.ax.plot(
                self.t,
                signals.accel_alpha,
                label=f"α_α (I_α={self.i_alpha:.4f})",
                color="red",
                linewidth=2,
                linestyle="--",
            )
        if self.visible_signals["accel_gamma"]:
            self.ax.plot(
                self.t,
                signals.accel_gamma,
                label=f"α_γ (I_γ={self.i_gamma:.4f})",
                color="blue",
                linewidth=2,
                linestyle="--",
            )
        self.ax.set_title(
            (
                "Angular Acceleration vs Time "
                f"(Grip: {self.grip_angle_deg:.0f}°, Wrist: {self.wrist_angle_deg:.0f}°)"
            ),
            fontsize=12,
            fontweight="bold",
        )
        self.ax.set_xlabel("Time (s)", fontsize=10)
        self.ax.set_ylabel("Angular Acceleration (rad/s²)", fontsize=10)

    def _plot_transmission_sweep(self) -> None:
        """Plot transmission ratios across the wrist-angle sweep."""
        sweep = compute_transmission_sweep(
            self.grip_angle_deg,
            self.wrist_angle_deg,
            self.i_alpha,
            self.i_gamma,
        )
        self._plot_transmission_sweep_lines(sweep)
        self._plot_current_wrist_marker(sweep)
        self._set_transmission_sweep_axes()

    def _plot_transmission_sweep_lines(self, sweep: TransmissionSweep) -> None:
        """Plot the visible transmission sweep data series."""
        if self.visible_signals["transmission_ratio"]:
            self.ax.plot(
                sweep.wrist_angle_deg,
                sweep.tau_ratios,
                label="Torque Transmission Ratio (τ_out/τ_in)",
                color="purple",
                linewidth=2.5,
            )
        if self.visible_signals["velocity_ratio"]:
            self.ax.plot(
                sweep.wrist_angle_deg,
                sweep.omega_ratios,
                label="Velocity Ratio (ω_out/ω_in)",
                color="orange",
                linewidth=2,
                linestyle="--",
            )
        if self.visible_signals["accel_alpha_ratio"]:
            self.ax.plot(
                sweep.wrist_angle_deg,
                sweep.accel_alpha_ratios,
                label="Accel_α ratio (rad/s²)/(N·m)",
                color="red",
                linewidth=1.5,
                alpha=0.7,
            )
        if self.visible_signals["accel_gamma_ratio"]:
            self.ax.plot(
                sweep.wrist_angle_deg,
                sweep.accel_gamma_ratios,
                label="Accel_γ ratio (rad/s²)/(N·m)",
                color="blue",
                linewidth=1.5,
                alpha=0.7,
            )

    def _plot_current_wrist_marker(self, sweep: TransmissionSweep) -> None:
        """Plot the current wrist-angle marker on the sweep graph."""
        current_idx = int(np.argmin(np.abs(sweep.wrist_angle_deg - self.wrist_angle_deg)))
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
                sweep.tau_ratios[current_idx],
                "go",
                markersize=10,
                markerfacecolor="lime",
            )
        self.ax.axhline(1.0, color="gray", linestyle="--", alpha=0.5, linewidth=1)

    def _set_transmission_sweep_axes(self) -> None:
        """Set labels and title for the transmission sweep graph."""
        self.ax.set_title(
            (
                "Universal Joint Transmission vs Wrist Deviation Angle "
                f"(Grip={self.grip_angle_deg:.0f}°)"
            ),
            fontsize=12,
            fontweight="bold",
        )
        self.ax.set_xlabel("Wrist Deviation Angle (degrees)", fontsize=10)
        self.ax.set_ylabel("Transmission Ratio", fontsize=10)

    def update_parameters(
        self,
        grip_angle_deg: float,
        wrist_angle_deg: float,
        i_alpha: float,
        i_gamma: float,
    ) -> None:
        """Update all parameters and redraw the plot."""
        self.grip_angle_deg = grip_angle_deg
        self.wrist_angle_deg = wrist_angle_deg
        self.i_alpha = i_alpha
        self.i_gamma = i_gamma
        self.update_plot()

    def set_plot_type(self, plot_type: str) -> None:
        """Set the plot type and redraw."""
        self.current_plot_type = plot_type
        self.update_plot()

    def set_signal_visible(self, signal_name: str, visible: bool) -> None:
        """Toggle visibility for a named signal and redraw."""
        if signal_name in self.visible_signals:
            self.visible_signals[signal_name] = visible
        self.update_plot()

    def regenerate_noise(self) -> None:
        """Regenerate the input signal with the current settings."""
        self._refresh_input_torque()
        if self.current_plot_type in {"Torque", "Angular Acceleration"}:
            self.update_plot()


def current_info_html(grip_angle_deg: int, wrist_angle_deg: int) -> str:
    """Return the shared info-panel HTML for the current configuration."""
    return build_info_html(grip_angle_deg, wrist_angle_deg)


def current_inertia_values(
    clubhead_weight: float,
    shaft_weight: float,
    club_length: float,
    cg_distance: float,
) -> tuple[float, float]:
    """Return current inertia values for the configured club properties."""
    return calculate_moments_of_inertia(
        clubhead_weight,
        shaft_weight,
        club_length,
        cg_distance,
    )
