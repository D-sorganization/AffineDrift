"""Qt main window for the enhanced wrist universal joint app."""

from __future__ import annotations

import sys

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QScrollArea, QWidget

from .constants import (
    DEFAULT_CLUB_LENGTH,
    DEFAULT_CLUBHEAD_CG_DISTANCE,
    DEFAULT_CLUBHEAD_WEIGHT,
    DEFAULT_SHAFT_WEIGHT,
)
from .qt_canvases import current_inertia_values, current_info_html
from .qt_dialogs import DocumentationDialog
from .qt_ui_sections import build_main_widget


class MainWindow(QMainWindow):  # type: ignore[misc]
    """Main application window for the enhanced universal-joint model."""

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        self.setWindowTitle("Enhanced Universal Joint Model - Wrist Biomechanics")
        self.setGeometry(100, 100, 1600, 1000)
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize UI components."""
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.installEventFilter(self)
        self.installEventFilter(self)

        self.scroll.setWidget(build_main_widget(self))
        self.setCentralWidget(self.scroll)
        self.update_inertia()

    def get_inertia_values(self) -> tuple[float, float]:
        """Get current inertia values from club-property inputs."""
        return current_inertia_values(
            self._read_float(self.clubhead_weight.text(), DEFAULT_CLUBHEAD_WEIGHT),
            self._read_float(self.shaft_weight.text(), DEFAULT_SHAFT_WEIGHT),
            self._read_float(self.club_length.text(), DEFAULT_CLUB_LENGTH),
            self._read_float(self.cg_distance.text(), DEFAULT_CLUBHEAD_CG_DISTANCE),
        )

    @staticmethod
    def _read_float(text: str, default: float) -> float:
        """Parse a float from text, falling back to the provided default."""
        try:
            return float(text)
        except ValueError:
            return default

    @staticmethod
    def _clamp_value(value: float, minimum: float, maximum: float) -> float:
        """Clamp a numeric value into the allowed inclusive range."""
        return max(minimum, min(maximum, value))

    def _apply_numeric_textbox_update(
        self,
        widget: QWidget,
        *,
        minimum: float,
        maximum: float,
        default: float,
        formatter: str,
    ) -> None:
        """Normalize one numeric textbox and refresh inertia-dependent outputs."""
        text_widget = widget
        try:
            value = self._read_float(text_widget.text(), default)  # type: ignore[attr-defined]
            value = self._clamp_value(value, minimum, maximum)
        except AttributeError:
            return
        text_widget.blockSignals(True)  # type: ignore[attr-defined]
        text_widget.setText(formatter.format(value))  # type: ignore[attr-defined]
        text_widget.blockSignals(False)  # type: ignore[attr-defined]
        self.update_inertia()

    def update_clubhead_from_textbox(self) -> None:
        """Update clubhead weight from its text box."""
        self._apply_numeric_textbox_update(
            self.clubhead_weight,
            minimum=50,
            maximum=500,
            default=DEFAULT_CLUBHEAD_WEIGHT,
            formatter="{:.0f}",
        )

    def update_shaft_from_textbox(self) -> None:
        """Update shaft weight from its text box."""
        self._apply_numeric_textbox_update(
            self.shaft_weight,
            minimum=30,
            maximum=200,
            default=DEFAULT_SHAFT_WEIGHT,
            formatter="{:.0f}",
        )

    def update_length_from_textbox(self) -> None:
        """Update club length from its text box."""
        self._apply_numeric_textbox_update(
            self.club_length,
            minimum=0.5,
            maximum=1.5,
            default=DEFAULT_CLUB_LENGTH,
            formatter="{:.2f}",
        )

    def update_cg_from_textbox(self) -> None:
        """Update CG distance from its text box."""
        self._apply_numeric_textbox_update(
            self.cg_distance,
            minimum=0.3,
            maximum=1.2,
            default=DEFAULT_CLUBHEAD_CG_DISTANCE,
            formatter="{:.2f}",
        )

    def update_inertia(self) -> None:
        """Update inertia display and dependent views."""
        i_alpha, i_gamma = self.get_inertia_values()
        self.inertia_label.setText(f"I_α={i_alpha:.4f} kg·m², I_γ={i_gamma:.4f} kg·m²")
        if hasattr(self, "plot_canvas"):
            self.update_all()

    def _sync_slider_textbox(self, textbox: QWidget, value: int) -> None:
        """Mirror the given slider value into its paired textbox."""
        textbox.blockSignals(True)  # type: ignore[attr-defined]
        textbox.setText(str(value))  # type: ignore[attr-defined]
        textbox.blockSignals(False)  # type: ignore[attr-defined]

    def update_grip_label(self, value: int) -> None:
        """Update grip-angle textbox from the slider."""
        if hasattr(self, "grip_textbox"):
            self._sync_slider_textbox(self.grip_textbox, value)
        if hasattr(self, "plot_canvas"):
            self.update_all()

    def update_wrist_label(self, value: int) -> None:
        """Update wrist-angle textbox from the slider."""
        if hasattr(self, "wrist_textbox"):
            self._sync_slider_textbox(self.wrist_textbox, value)
        if hasattr(self, "plot_canvas"):
            self.update_all()

    def _update_angle_from_textbox(
        self,
        *,
        textbox: QWidget,
        slider: QWidget,
        minimum: int,
        maximum: int,
    ) -> None:
        """Clamp one angle textbox, sync its slider, and refresh the views."""
        value = self._clamp_value(
            self._read_float(textbox.text(), slider.value()),  # type: ignore[attr-defined]
            minimum,
            maximum,
        )
        slider.blockSignals(True)  # type: ignore[attr-defined]
        slider.setValue(int(value))  # type: ignore[attr-defined]
        slider.blockSignals(False)  # type: ignore[attr-defined]
        self._sync_slider_textbox(textbox, int(value))
        if hasattr(self, "plot_canvas"):
            self.update_all()

    def update_grip_from_textbox(self) -> None:
        """Update grip angle from its text box."""
        self._update_angle_from_textbox(
            textbox=self.grip_textbox,
            slider=self.grip_slider,
            minimum=0,
            maximum=90,
        )

    def update_wrist_from_textbox(self) -> None:
        """Update wrist angle from its text box."""
        self._update_angle_from_textbox(
            textbox=self.wrist_textbox,
            slider=self.wrist_slider,
            minimum=-60,
            maximum=60,
        )

    def update_all(self) -> None:
        """Refresh the diagram, plot, and info panel."""
        grip_angle = self.grip_slider.value()
        wrist_angle = self.wrist_slider.value()
        i_alpha, i_gamma = self.get_inertia_values()
        self.diagram_canvas.update_angles(grip_angle, wrist_angle)
        self.plot_canvas.update_parameters(grip_angle, wrist_angle, i_alpha, i_gamma)
        self.update_info()

    def update_plot_type(self, plot_type: str) -> None:
        """Update plot type and enable or disable the relevant checkboxes."""
        self.plot_canvas.set_plot_type(plot_type)
        is_torque = plot_type == "Torque"
        is_accel = plot_type == "Angular Acceleration"
        is_transmission = plot_type == "Transmission Ratio vs Wrist Angle"

        self.show_input_check.setEnabled(is_torque)
        self.show_transmitted_check.setEnabled(is_torque)
        self.show_alpha_torque_check.setEnabled(is_torque)
        self.show_gamma_torque_check.setEnabled(is_torque)
        self.show_alpha_accel_check.setEnabled(is_accel)
        self.show_gamma_accel_check.setEnabled(is_accel)
        self.show_transmission_check.setEnabled(is_transmission)
        self.show_velocity_check.setEnabled(is_transmission)
        self.show_accel_alpha_ratio_check.setEnabled(is_transmission)
        self.show_accel_gamma_ratio_check.setEnabled(is_transmission)

    def update_signal_visibility(self, signal_name: str, visible: bool) -> None:
        """Update signal visibility on the plot canvas."""
        self.plot_canvas.set_signal_visible(signal_name, visible)

    def update_info(self) -> None:
        """Refresh the informational summary panel."""
        self.info_label.setText(
            current_info_html(self.grip_slider.value(), self.wrist_slider.value())
        )

    def regenerate_noise(self) -> None:
        """Regenerate the noise signal on the plot canvas."""
        self.plot_canvas.regenerate_noise()

    def update_noise_type(self, noise_type: str) -> None:
        """Update noise type and show or hide the polynomial controls."""
        self.plot_canvas.set_noise_type(noise_type)
        is_polynomial = noise_type == "Polynomial"
        self.polynomial_input.setVisible(is_polynomial)
        self.polynomial_label.setVisible(is_polynomial)

    def update_polynomial_signal(self, expression: str) -> None:
        """Update the polynomial expression used by the signal generator."""
        if hasattr(self, "plot_canvas"):
            self.plot_canvas.set_polynomial_expression(expression)

    def eventFilter(self, obj: QWidget, event: QEvent) -> bool:
        """Redirect wheel events to the scroll area instead of nested controls."""
        if event.type() == QEvent.Type.Wheel:
            scroll = self.centralWidget()
            if isinstance(scroll, QScrollArea):
                scroll_bar = scroll.verticalScrollBar()
                if scroll_bar and scroll_bar.isVisible():
                    delta = event.angleDelta().y()
                    scroll_bar.setValue(scroll_bar.value() - delta // 8)
                    return True
        result = super().eventFilter(obj, event)
        return bool(result)

    def show_documentation(self) -> None:
        """Show the documentation dialog."""
        DocumentationDialog(self).exec()


def run() -> int:
    """Launch the Qt application and return its exit code."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
