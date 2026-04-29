"""Qt UI section builders for the enhanced wrist universal joint app."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from .constants import (
    DEFAULT_CLUB_LENGTH,
    DEFAULT_CLUBHEAD_CG_DISTANCE,
    DEFAULT_CLUBHEAD_WEIGHT,
    DEFAULT_SHAFT_WEIGHT,
)
from .qt_canvases import DiagramCanvas, PlotCanvas
from .qt_widgets import WheelIgnoringLineEdit, WheelIgnoringSlider

_SLIDER_WIDTH = 300
_TEXTBOX_WIDTH = 80
_LABEL_AREA_WIDTH = 100


def _build_tick_container(values: list[int], width: int = _SLIDER_WIDTH) -> QWidget:
    """Create the evenly spaced tick-label row used below angle sliders."""
    container = QWidget()
    container.setFixedWidth(width)
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    for index, value in enumerate(values):
        label = QLabel(f"{value}°")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 10pt; font-weight: bold;")
        layout.addWidget(label)
        if index < len(values) - 1:
            layout.addStretch()
    return container


def _build_angle_section(
    window: Any,
    *,
    title: str,
    info_text: str,
    minimum: int,
    maximum: int,
    initial_value: int,
    tick_values: list[int],
    placeholder: str,
    slider_attr: str,
    textbox_attr: str,
    slider_handler: Callable[[int], None],
    textbox_handler: Callable[[], None],
) -> QVBoxLayout:
    """Build one slider/textbox angle section and return its layout."""
    section_layout = QVBoxLayout()
    section_layout.setSpacing(5)
    section_layout.setContentsMargins(0, 0, 0, 0)

    label = QLabel(title)
    label.setStyleSheet("font-size: 14pt; font-weight: bold;")
    section_layout.addWidget(label)

    slider_container = QWidget()
    slider_container_layout = QVBoxLayout(slider_container)
    slider_container_layout.setContentsMargins(0, 0, 0, 0)
    slider_container_layout.setSpacing(0)

    control_layout = QHBoxLayout()
    control_layout.setContentsMargins(0, 0, 0, 0)
    control_layout.setSpacing(5)

    slider = WheelIgnoringSlider(Qt.Orientation.Horizontal)
    slider.setMinimum(minimum)
    slider.setMaximum(maximum)
    slider.setValue(initial_value)
    slider.setTickInterval(15)
    slider.setTickPosition(QSlider.TickPosition.TicksBelow)
    slider.setFixedWidth(_SLIDER_WIDTH)
    slider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    slider.valueChanged.connect(slider_handler)
    setattr(window, slider_attr, slider)
    control_layout.addWidget(slider)

    textbox = WheelIgnoringLineEdit()
    textbox.setText(str(initial_value))
    textbox.setFixedWidth(_TEXTBOX_WIDTH)
    textbox.setAlignment(Qt.AlignmentFlag.AlignRight)
    textbox.setPlaceholderText(placeholder)
    textbox.editingFinished.connect(textbox_handler)
    setattr(window, textbox_attr, textbox)
    control_layout.addWidget(textbox)

    degree_label = QLabel("°")
    degree_label.setFixedWidth(15)
    control_layout.addWidget(degree_label)
    control_layout.addStretch()
    slider_container_layout.addLayout(control_layout)
    slider_container_layout.addWidget(_build_tick_container(tick_values))
    section_layout.addWidget(slider_container)

    info_label = QLabel(info_text)
    info_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
    section_layout.addWidget(info_label)
    return section_layout


def _add_labeled_numeric_input(
    window: Any,
    parent_layout: QVBoxLayout,
    *,
    attr_name: str,
    label_text: str,
    initial_text: str,
    placeholder: str,
    unit: str,
    handler: Callable[[], None],
) -> None:
    """Add a labeled numeric line edit row to the given layout."""
    row = QHBoxLayout()
    label = QLabel(label_text)
    label.setStyleSheet("font-size: 11pt; font-weight: bold;")
    label.setFixedWidth(_LABEL_AREA_WIDTH)
    label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    row.addWidget(label)

    textbox = WheelIgnoringLineEdit()
    textbox.setText(initial_text)
    textbox.setFixedWidth(_TEXTBOX_WIDTH)
    textbox.setAlignment(Qt.AlignmentFlag.AlignRight)
    textbox.setPlaceholderText(placeholder)
    textbox.editingFinished.connect(handler)
    setattr(window, attr_name, textbox)
    row.addWidget(textbox)
    row.addWidget(QLabel(unit))
    parent_layout.addLayout(row)


def _add_signal_checkbox(
    window: Any,
    layout: QHBoxLayout,
    *,
    attr_name: str,
    label_text: str,
    signal_name: str,
    checked: bool,
) -> None:
    """Create one signal-visibility checkbox and wire it to the window callback."""
    checkbox = QCheckBox(label_text)
    checkbox.setChecked(checked)
    checkbox.stateChanged.connect(
        lambda _state=0, name=signal_name, cb=checkbox: window.update_signal_visibility(
            name,
            cb.isChecked(),
        )
    )
    setattr(window, attr_name, checkbox)
    layout.addWidget(checkbox)


def _build_parameter_group(window: Any, main_layout: QVBoxLayout) -> None:
    """Add the combined angle and club-property parameter group."""
    control_group = QGroupBox("Parameters")
    control_layout = QHBoxLayout()

    left_column = QVBoxLayout()
    left_column.setSpacing(0)
    left_column.setContentsMargins(0, 0, 0, 0)
    left_column.addLayout(
        _build_angle_section(
            window,
            title="Grip Angle θ<sub>grip</sub>:",
            info_text="0° = parallel to fingers, 90° = perpendicular to fingers",
            minimum=0,
            maximum=90,
            initial_value=30,
            tick_values=[0, 15, 30, 45, 60, 75, 90],
            placeholder="0-90",
            slider_attr="grip_slider",
            textbox_attr="grip_textbox",
            slider_handler=window.update_grip_label,
            textbox_handler=window.update_grip_from_textbox,
        )
    )
    left_column.addLayout(
        _build_angle_section(
            window,
            title="Wrist Deviation Angle φ:",
            info_text="+ values = radial deviation, - values = ulnar deviation",
            minimum=-60,
            maximum=60,
            initial_value=0,
            tick_values=[-60, -45, -30, -15, 0, 15, 30, 45, 60],
            placeholder="-60 to 60",
            slider_attr="wrist_slider",
            textbox_attr="wrist_textbox",
            slider_handler=window.update_wrist_label,
            textbox_handler=window.update_wrist_from_textbox,
        )
    )
    left_column.addStretch()
    control_layout.addLayout(left_column)

    club_layout = QVBoxLayout()
    club_props_label = QLabel("Club Properties:")
    club_props_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
    club_layout.addWidget(club_props_label)

    _add_labeled_numeric_input(
        window,
        club_layout,
        attr_name="clubhead_weight",
        label_text="Clubhead:",
        initial_text=str(int(DEFAULT_CLUBHEAD_WEIGHT)),
        placeholder="50-500",
        unit=" g",
        handler=window.update_clubhead_from_textbox,
    )
    _add_labeled_numeric_input(
        window,
        club_layout,
        attr_name="shaft_weight",
        label_text="Shaft:",
        initial_text=str(int(DEFAULT_SHAFT_WEIGHT)),
        placeholder="30-200",
        unit=" g",
        handler=window.update_shaft_from_textbox,
    )
    _add_labeled_numeric_input(
        window,
        club_layout,
        attr_name="club_length",
        label_text="Length:",
        initial_text=f"{DEFAULT_CLUB_LENGTH:.2f}",
        placeholder="0.5-1.5",
        unit=" m",
        handler=window.update_length_from_textbox,
    )
    _add_labeled_numeric_input(
        window,
        club_layout,
        attr_name="cg_distance",
        label_text="CG Dist:",
        initial_text=f"{DEFAULT_CLUBHEAD_CG_DISTANCE:.2f}",
        placeholder="0.3-1.2",
        unit=" m",
        handler=window.update_cg_from_textbox,
    )

    window.inertia_label = QLabel()
    window.inertia_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
    club_layout.addWidget(window.inertia_label)
    club_layout.addStretch()
    control_layout.addLayout(club_layout)

    control_group.setLayout(control_layout)
    main_layout.addWidget(control_group)


def _build_signal_group(window: Any, main_layout: QVBoxLayout) -> None:
    """Add the input-signal generator group."""
    signal_group = QGroupBox("Input Signal Generator")
    signal_layout = QVBoxLayout()

    noise_layout = QHBoxLayout()
    signal_type_label = QLabel("Signal Type:")
    signal_type_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
    noise_layout.addWidget(signal_type_label)
    window.noise_type_combo = QComboBox()
    window.noise_type_combo.addItems(
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
    window.noise_type_combo.currentTextChanged.connect(window.update_noise_type)
    noise_layout.addWidget(window.noise_type_combo)
    noise_layout.addStretch()
    signal_layout.addLayout(noise_layout)

    poly_layout = QHBoxLayout()
    window.polynomial_label = QLabel('Polynomial (e.g., "t**2 + 2*t - 1" or "t**3 - 0.5*t"):')
    window.polynomial_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
    poly_layout.addWidget(window.polynomial_label)
    window.polynomial_input = QLineEdit()
    window.polynomial_input.setPlaceholderText("Enter polynomial expression using t as variable")
    window.polynomial_input.setText("t**2 - t")
    window.polynomial_input.setVisible(False)
    window.polynomial_input.textChanged.connect(window.update_polynomial_signal)
    poly_layout.addWidget(window.polynomial_input)
    window.polynomial_label.setVisible(False)
    signal_layout.addLayout(poly_layout)

    regen_layout = QHBoxLayout()
    regen_layout.addStretch()
    regen_btn = QPushButton("🎲 Regenerate Signal")
    regen_btn.clicked.connect(window.regenerate_noise)
    regen_layout.addWidget(regen_btn)
    regen_layout.addStretch()
    signal_layout.addLayout(regen_layout)

    signal_group.setLayout(signal_layout)
    main_layout.addWidget(signal_group)


def _build_plot_controls_group(window: Any, main_layout: QVBoxLayout) -> None:
    """Add the plot-type selector and signal-visibility controls."""
    plot_control_group = QGroupBox("Plot Controls")
    plot_control_layout = QHBoxLayout()
    plot_control_layout.setSpacing(15)

    plot_type_label = QLabel("Plot Type:")
    plot_type_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
    plot_control_layout.addWidget(plot_type_label)
    window.plot_type_combo = QComboBox()
    window.plot_type_combo.addItems(
        ["Torque", "Angular Acceleration", "Transmission Ratio vs Wrist Angle"]
    )
    window.plot_type_combo.currentTextChanged.connect(window.update_plot_type)
    plot_control_layout.addWidget(window.plot_type_combo)

    plot_control_layout.addSpacing(20)
    plot_control_layout.addStretch()

    show_label = QLabel("Show:")
    show_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
    plot_control_layout.addWidget(show_label)
    plot_control_layout.addSpacing(10)

    _add_signal_checkbox(
        window,
        plot_control_layout,
        attr_name="show_input_check",
        label_text="Input Torque",
        signal_name="input_torque",
        checked=True,
    )
    plot_control_layout.addSpacing(10)
    _add_signal_checkbox(
        window,
        plot_control_layout,
        attr_name="show_transmitted_check",
        label_text="Transmitted Torque",
        signal_name="transmitted_torque",
        checked=True,
    )
    plot_control_layout.addSpacing(10)
    _add_signal_checkbox(
        window,
        plot_control_layout,
        attr_name="show_alpha_torque_check",
        label_text="τ_α",
        signal_name="torque_alpha",
        checked=True,
    )
    plot_control_layout.addSpacing(10)
    _add_signal_checkbox(
        window,
        plot_control_layout,
        attr_name="show_gamma_torque_check",
        label_text="τ_γ",
        signal_name="torque_gamma",
        checked=True,
    )
    plot_control_layout.addSpacing(10)
    _add_signal_checkbox(
        window,
        plot_control_layout,
        attr_name="show_alpha_accel_check",
        label_text="α_α",
        signal_name="accel_alpha",
        checked=True,
    )
    plot_control_layout.addSpacing(10)
    _add_signal_checkbox(
        window,
        plot_control_layout,
        attr_name="show_gamma_accel_check",
        label_text="α_γ",
        signal_name="accel_gamma",
        checked=True,
    )
    plot_control_layout.addSpacing(10)
    _add_signal_checkbox(
        window,
        plot_control_layout,
        attr_name="show_transmission_check",
        label_text="Transmission Ratio",
        signal_name="transmission_ratio",
        checked=True,
    )
    plot_control_layout.addSpacing(10)
    _add_signal_checkbox(
        window,
        plot_control_layout,
        attr_name="show_velocity_check",
        label_text="Velocity Ratio",
        signal_name="velocity_ratio",
        checked=False,
    )
    plot_control_layout.addSpacing(10)
    _add_signal_checkbox(
        window,
        plot_control_layout,
        attr_name="show_accel_alpha_ratio_check",
        label_text="Accel_α Ratio",
        signal_name="accel_alpha_ratio",
        checked=False,
    )
    plot_control_layout.addSpacing(10)
    _add_signal_checkbox(
        window,
        plot_control_layout,
        attr_name="show_accel_gamma_ratio_check",
        label_text="Accel_γ Ratio",
        signal_name="accel_gamma_ratio",
        checked=False,
    )

    plot_control_group.setLayout(plot_control_layout)
    main_layout.addWidget(plot_control_group)


def _build_plot_group(window: Any, main_layout: QVBoxLayout) -> None:
    """Add the main plot canvas group."""
    plot_group = QGroupBox("Plot")
    plot_layout = QVBoxLayout()
    i_alpha, i_gamma = window.get_inertia_values()
    window.plot_canvas = PlotCanvas(
        grip_angle_deg=30,
        wrist_angle_deg=0,
        i_alpha=i_alpha,
        i_gamma=i_gamma,
    )
    plot_layout.addWidget(window.plot_canvas)
    plot_group.setLayout(plot_layout)
    main_layout.addWidget(plot_group)


def build_main_widget(window: Any) -> QWidget:
    """Build and return the main scrollable widget tree."""
    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)
    main_layout.setSpacing(15)

    top_bar = QHBoxLayout()
    top_bar.addStretch()
    doc_btn = QPushButton("📘 Model Documentation & Mathematics")
    doc_btn.setToolTip("View detailed mathematical documentation and physics")
    doc_btn.clicked.connect(window.show_documentation)
    doc_btn.setStyleSheet("font-weight: bold; padding: 8px;")
    top_bar.addWidget(doc_btn)
    top_bar.addStretch()
    main_layout.addLayout(top_bar)

    diagram_group = QGroupBox("Forearm-Hand-Club Diagram")
    diagram_layout = QVBoxLayout()
    window.diagram_canvas = DiagramCanvas(grip_angle_deg=30, wrist_angle_deg=0)
    diagram_layout.addWidget(window.diagram_canvas)
    diagram_group.setLayout(diagram_layout)
    main_layout.addWidget(diagram_group)

    _build_parameter_group(window, main_layout)
    _build_signal_group(window, main_layout)
    _build_plot_controls_group(window, main_layout)
    _build_plot_group(window, main_layout)

    info_group = QGroupBox("Model Information")
    info_layout = QVBoxLayout()
    window.info_label = QLabel()
    window.info_label.setWordWrap(True)
    window.info_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
    window.update_info()
    info_layout.addWidget(window.info_label)
    info_group.setLayout(info_layout)
    main_layout.addWidget(info_group)

    return main_widget
