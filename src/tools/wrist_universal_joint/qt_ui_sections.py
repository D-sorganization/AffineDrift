"""Qt UI section builders for the enhanced wrist universal joint app.

The builders own widget construction and return them to the window through an
explicit :class:`UiWidgets` dataclass, while the surface the window exposes to
the builders is declared by the :class:`UiCallbacks` protocol. This replaces
the previous ``setattr(window, ...)`` injection and ``window: Any`` parameter,
so cross-module member access is type-checked instead of opaque.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

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
from .qt_canvases import (
    DiagramCanvas,
    PlotCanvas,
    current_inertia_values,
    current_info_html,
)
from .qt_widgets import WheelIgnoringLineEdit, WheelIgnoringSlider, suppress_wheel_on_widgets

_SLIDER_WIDTH = 300
_TEXTBOX_WIDTH = 80
_LABEL_AREA_WIDTH = 100

# Default angles used to seed the initial plot/info before the window refreshes.
_DEFAULT_GRIP_ANGLE_DEG = 30
_DEFAULT_WRIST_ANGLE_DEG = 0


@runtime_checkable
class UiCallbacks(Protocol):
    """Handlers the builders may invoke, wired by the owning window.

    Declaring the surface explicitly (instead of ``window: Any``) lets mypy
    verify that every handler referenced during construction actually exists
    on the window.
    """

    def update_grip_label(self, value: int) -> None: ...

    def update_grip_from_textbox(self) -> None: ...

    def update_wrist_label(self, value: int) -> None: ...

    def update_wrist_from_textbox(self) -> None: ...

    def update_clubhead_from_textbox(self) -> None: ...

    def update_shaft_from_textbox(self) -> None: ...

    def update_length_from_textbox(self) -> None: ...

    def update_cg_from_textbox(self) -> None: ...

    def update_noise_type(self, noise_type: str) -> None: ...

    def update_polynomial_signal(self, expression: str) -> None: ...

    def update_plot_type(self, plot_type: str) -> None: ...

    def update_signal_visibility(self, signal_name: str, visible: bool) -> None: ...

    def regenerate_noise(self) -> None: ...

    def show_documentation(self) -> None: ...


@dataclass(frozen=True)
class UiWidgets:
    """Widgets produced by :func:`build_main_widget`, consumed by the window.

    The window assigns this atomically after construction (``self.ui = ...``),
    so there is no window-construction-order shared state and no need for the
    defensive ``hasattr`` guards the old setattr-injection design required.
    """

    grip_slider: QSlider
    grip_textbox: QLineEdit
    wrist_slider: QSlider
    wrist_textbox: QLineEdit
    clubhead_weight: QLineEdit
    shaft_weight: QLineEdit
    club_length: QLineEdit
    cg_distance: QLineEdit
    inertia_label: QLabel
    noise_type_combo: QComboBox
    polynomial_label: QLabel
    polynomial_input: QLineEdit
    plot_type_combo: QComboBox
    show_input_check: QCheckBox
    show_transmitted_check: QCheckBox
    show_alpha_torque_check: QCheckBox
    show_gamma_torque_check: QCheckBox
    show_alpha_accel_check: QCheckBox
    show_gamma_accel_check: QCheckBox
    show_transmission_check: QCheckBox
    show_velocity_check: QCheckBox
    show_accel_alpha_ratio_check: QCheckBox
    show_accel_gamma_ratio_check: QCheckBox
    plot_canvas: PlotCanvas
    diagram_canvas: DiagramCanvas
    info_label: QLabel


@dataclass
class _UiWidgetsBuilder:
    """Mutable accumulator for the widgets created while building the tree."""

    grip_slider: QSlider | None = None
    grip_textbox: QLineEdit | None = None
    wrist_slider: QSlider | None = None
    wrist_textbox: QLineEdit | None = None
    clubhead_weight: QLineEdit | None = None
    shaft_weight: QLineEdit | None = None
    club_length: QLineEdit | None = None
    cg_distance: QLineEdit | None = None
    inertia_label: QLabel | None = None
    noise_type_combo: QComboBox | None = None
    polynomial_label: QLabel | None = None
    polynomial_input: QLineEdit | None = None
    plot_type_combo: QComboBox | None = None
    show_input_check: QCheckBox | None = None
    show_transmitted_check: QCheckBox | None = None
    show_alpha_torque_check: QCheckBox | None = None
    show_gamma_torque_check: QCheckBox | None = None
    show_alpha_accel_check: QCheckBox | None = None
    show_gamma_accel_check: QCheckBox | None = None
    show_transmission_check: QCheckBox | None = None
    show_velocity_check: QCheckBox | None = None
    show_accel_alpha_ratio_check: QCheckBox | None = None
    show_accel_gamma_ratio_check: QCheckBox | None = None
    plot_canvas: PlotCanvas | None = None
    diagram_canvas: DiagramCanvas | None = None
    info_label: QLabel | None = None

    def finalize(self) -> UiWidgets:
        """Build the immutable :class:`UiWidgets`, asserting all fields are set."""
        values = vars(self)
        missing = [name for name, value in values.items() if value is None]
        if missing:
            raise RuntimeError(f"UI build incomplete; missing widgets: {sorted(missing)}")
        return UiWidgets(**values)


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
    *,
    title: str,
    info_text: str,
    minimum: int,
    maximum: int,
    initial_value: int,
    tick_values: list[int],
    placeholder: str,
    slider_handler: Callable[[int], None],
    textbox_handler: Callable[[], None],
) -> tuple[QVBoxLayout, WheelIgnoringSlider, WheelIgnoringLineEdit]:
    """Build one slider/textbox angle section and return its layout and widgets."""
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
    control_layout.addWidget(slider)

    textbox = WheelIgnoringLineEdit()
    textbox.setText(str(initial_value))
    textbox.setFixedWidth(_TEXTBOX_WIDTH)
    textbox.setAlignment(Qt.AlignmentFlag.AlignRight)
    textbox.setPlaceholderText(placeholder)
    textbox.editingFinished.connect(textbox_handler)
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
    return section_layout, slider, textbox


def _build_labeled_numeric_input(
    parent_layout: QVBoxLayout,
    *,
    label_text: str,
    initial_text: str,
    placeholder: str,
    unit: str,
    handler: Callable[[], None],
) -> WheelIgnoringLineEdit:
    """Add a labeled numeric line edit row and return the created text box."""
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
    row.addWidget(textbox)
    row.addWidget(QLabel(unit))
    parent_layout.addLayout(row)
    return textbox


def _build_signal_checkbox(
    layout: QHBoxLayout,
    callbacks: UiCallbacks,
    *,
    label_text: str,
    signal_name: str,
    checked: bool,
) -> QCheckBox:
    """Create one signal-visibility checkbox wired to the visibility callback."""
    checkbox = QCheckBox(label_text)
    checkbox.setChecked(checked)
    checkbox.stateChanged.connect(
        lambda _state=0, name=signal_name, cb=checkbox: callbacks.update_signal_visibility(
            name,
            cb.isChecked(),
        )
    )
    layout.addWidget(checkbox)
    return checkbox


def _build_parameter_group(
    callbacks: UiCallbacks,
    widgets: _UiWidgetsBuilder,
    main_layout: QVBoxLayout,
) -> None:
    """Add the combined angle and club-property parameter group."""
    control_group = QGroupBox("Parameters")
    control_layout = QHBoxLayout()

    left_column = QVBoxLayout()
    left_column.setSpacing(0)
    left_column.setContentsMargins(0, 0, 0, 0)

    grip_layout, widgets.grip_slider, widgets.grip_textbox = _build_angle_section(
        title="Grip Angle θ<sub>grip</sub>:",
        info_text="0° = parallel to fingers, 90° = perpendicular to fingers",
        minimum=0,
        maximum=90,
        initial_value=_DEFAULT_GRIP_ANGLE_DEG,
        tick_values=[0, 15, 30, 45, 60, 75, 90],
        placeholder="0-90",
        slider_handler=callbacks.update_grip_label,
        textbox_handler=callbacks.update_grip_from_textbox,
    )
    left_column.addLayout(grip_layout)

    wrist_layout, widgets.wrist_slider, widgets.wrist_textbox = _build_angle_section(
        title="Wrist Deviation Angle φ:",
        info_text="+ values = radial deviation, - values = ulnar deviation",
        minimum=-60,
        maximum=60,
        initial_value=_DEFAULT_WRIST_ANGLE_DEG,
        tick_values=[-60, -45, -30, -15, 0, 15, 30, 45, 60],
        placeholder="-60 to 60",
        slider_handler=callbacks.update_wrist_label,
        textbox_handler=callbacks.update_wrist_from_textbox,
    )
    left_column.addLayout(wrist_layout)
    left_column.addStretch()
    control_layout.addLayout(left_column)

    club_layout = QVBoxLayout()
    club_props_label = QLabel("Club Properties:")
    club_props_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
    club_layout.addWidget(club_props_label)

    widgets.clubhead_weight = _build_labeled_numeric_input(
        club_layout,
        label_text="Clubhead:",
        initial_text=str(int(DEFAULT_CLUBHEAD_WEIGHT)),
        placeholder="50-500",
        unit=" g",
        handler=callbacks.update_clubhead_from_textbox,
    )
    widgets.shaft_weight = _build_labeled_numeric_input(
        club_layout,
        label_text="Shaft:",
        initial_text=str(int(DEFAULT_SHAFT_WEIGHT)),
        placeholder="30-200",
        unit=" g",
        handler=callbacks.update_shaft_from_textbox,
    )
    widgets.club_length = _build_labeled_numeric_input(
        club_layout,
        label_text="Length:",
        initial_text=f"{DEFAULT_CLUB_LENGTH:.2f}",
        placeholder="0.5-1.5",
        unit=" m",
        handler=callbacks.update_length_from_textbox,
    )
    widgets.cg_distance = _build_labeled_numeric_input(
        club_layout,
        label_text="CG Dist:",
        initial_text=f"{DEFAULT_CLUBHEAD_CG_DISTANCE:.2f}",
        placeholder="0.3-1.2",
        unit=" m",
        handler=callbacks.update_cg_from_textbox,
    )

    inertia_label = QLabel()
    inertia_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
    widgets.inertia_label = inertia_label
    club_layout.addWidget(inertia_label)
    club_layout.addStretch()
    control_layout.addLayout(club_layout)

    control_group.setLayout(control_layout)
    main_layout.addWidget(control_group)


def _build_signal_group(
    callbacks: UiCallbacks,
    widgets: _UiWidgetsBuilder,
    main_layout: QVBoxLayout,
) -> None:
    """Add the input-signal generator group."""
    signal_group = QGroupBox("Input Signal Generator")
    signal_layout = QVBoxLayout()

    noise_layout = QHBoxLayout()
    signal_type_label = QLabel("Signal Type:")
    signal_type_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
    noise_layout.addWidget(signal_type_label)
    noise_type_combo = QComboBox()
    suppress_wheel_on_widgets(noise_type_combo)
    noise_type_combo.addItems(
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
    noise_type_combo.currentTextChanged.connect(callbacks.update_noise_type)
    widgets.noise_type_combo = noise_type_combo
    noise_layout.addWidget(noise_type_combo)
    noise_layout.addStretch()
    signal_layout.addLayout(noise_layout)

    poly_layout = QHBoxLayout()
    polynomial_label = QLabel('Polynomial (e.g., "t**2 + 2*t - 1" or "t**3 - 0.5*t"):')
    polynomial_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
    poly_layout.addWidget(polynomial_label)
    polynomial_input = QLineEdit()
    polynomial_input.setPlaceholderText("Enter polynomial expression using t as variable")
    polynomial_input.setText("t**2 - t")
    polynomial_input.setVisible(False)
    polynomial_input.textChanged.connect(callbacks.update_polynomial_signal)
    poly_layout.addWidget(polynomial_input)
    polynomial_label.setVisible(False)
    widgets.polynomial_label = polynomial_label
    widgets.polynomial_input = polynomial_input
    signal_layout.addLayout(poly_layout)

    regen_layout = QHBoxLayout()
    regen_layout.addStretch()
    regen_btn = QPushButton("🎲 Regenerate Signal")
    regen_btn.clicked.connect(callbacks.regenerate_noise)
    regen_layout.addWidget(regen_btn)
    regen_layout.addStretch()
    signal_layout.addLayout(regen_layout)

    signal_group.setLayout(signal_layout)
    main_layout.addWidget(signal_group)


def _build_plot_controls_group(
    callbacks: UiCallbacks,
    widgets: _UiWidgetsBuilder,
    main_layout: QVBoxLayout,
) -> None:
    """Add the plot-type selector and signal-visibility controls."""
    plot_control_group = QGroupBox("Plot Controls")
    plot_control_layout = QHBoxLayout()
    plot_control_layout.setSpacing(15)

    plot_type_label = QLabel("Plot Type:")
    plot_type_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
    plot_control_layout.addWidget(plot_type_label)
    plot_type_combo = QComboBox()
    suppress_wheel_on_widgets(plot_type_combo)
    plot_type_combo.addItems(
        ["Torque", "Angular Acceleration", "Transmission Ratio vs Wrist Angle"]
    )
    plot_type_combo.currentTextChanged.connect(callbacks.update_plot_type)
    widgets.plot_type_combo = plot_type_combo
    plot_control_layout.addWidget(plot_type_combo)

    plot_control_layout.addSpacing(20)
    plot_control_layout.addStretch()

    show_label = QLabel("Show:")
    show_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
    plot_control_layout.addWidget(show_label)
    plot_control_layout.addSpacing(10)

    widgets.show_input_check = _build_signal_checkbox(
        plot_control_layout,
        callbacks,
        label_text="Input Torque",
        signal_name="input_torque",
        checked=True,
    )
    plot_control_layout.addSpacing(10)
    widgets.show_transmitted_check = _build_signal_checkbox(
        plot_control_layout,
        callbacks,
        label_text="Transmitted Torque",
        signal_name="transmitted_torque",
        checked=True,
    )
    plot_control_layout.addSpacing(10)
    widgets.show_alpha_torque_check = _build_signal_checkbox(
        plot_control_layout,
        callbacks,
        label_text="τ_α",
        signal_name="torque_alpha",
        checked=True,
    )
    plot_control_layout.addSpacing(10)
    widgets.show_gamma_torque_check = _build_signal_checkbox(
        plot_control_layout,
        callbacks,
        label_text="τ_γ",
        signal_name="torque_gamma",
        checked=True,
    )
    plot_control_layout.addSpacing(10)
    widgets.show_alpha_accel_check = _build_signal_checkbox(
        plot_control_layout,
        callbacks,
        label_text="α_α",
        signal_name="accel_alpha",
        checked=True,
    )
    plot_control_layout.addSpacing(10)
    widgets.show_gamma_accel_check = _build_signal_checkbox(
        plot_control_layout,
        callbacks,
        label_text="α_γ",
        signal_name="accel_gamma",
        checked=True,
    )
    plot_control_layout.addSpacing(10)
    widgets.show_transmission_check = _build_signal_checkbox(
        plot_control_layout,
        callbacks,
        label_text="Transmission Ratio",
        signal_name="transmission_ratio",
        checked=True,
    )
    plot_control_layout.addSpacing(10)
    widgets.show_velocity_check = _build_signal_checkbox(
        plot_control_layout,
        callbacks,
        label_text="Velocity Ratio",
        signal_name="velocity_ratio",
        checked=False,
    )
    plot_control_layout.addSpacing(10)
    widgets.show_accel_alpha_ratio_check = _build_signal_checkbox(
        plot_control_layout,
        callbacks,
        label_text="Accel_α Ratio",
        signal_name="accel_alpha_ratio",
        checked=False,
    )
    plot_control_layout.addSpacing(10)
    widgets.show_accel_gamma_ratio_check = _build_signal_checkbox(
        plot_control_layout,
        callbacks,
        label_text="Accel_γ Ratio",
        signal_name="accel_gamma_ratio",
        checked=False,
    )

    plot_control_group.setLayout(plot_control_layout)
    main_layout.addWidget(plot_control_group)


def _build_plot_group(widgets: _UiWidgetsBuilder, main_layout: QVBoxLayout) -> None:
    """Add the main plot canvas group, seeded from the default club properties."""
    plot_group = QGroupBox("Plot")
    plot_layout = QVBoxLayout()
    i_alpha, i_gamma = current_inertia_values(
        DEFAULT_CLUBHEAD_WEIGHT,
        DEFAULT_SHAFT_WEIGHT,
        DEFAULT_CLUB_LENGTH,
        DEFAULT_CLUBHEAD_CG_DISTANCE,
    )
    plot_canvas = PlotCanvas(
        grip_angle_deg=_DEFAULT_GRIP_ANGLE_DEG,
        wrist_angle_deg=_DEFAULT_WRIST_ANGLE_DEG,
        i_alpha=i_alpha,
        i_gamma=i_gamma,
    )
    widgets.plot_canvas = plot_canvas
    plot_layout.addWidget(plot_canvas)
    plot_group.setLayout(plot_layout)
    main_layout.addWidget(plot_group)


def build_main_widget(callbacks: UiCallbacks) -> tuple[QWidget, UiWidgets]:
    """Build the main scrollable widget tree and the widgets the window owns.

    The builders never dereference the window: they only invoke the explicit
    :class:`UiCallbacks` handlers (for signal wiring) and return every widget
    the window needs via :class:`UiWidgets`. The initial plot and info content
    are seeded from the default constants; the window refreshes them once after
    assigning ``self.ui``.

    Args:
        callbacks: The owning window, satisfying the :class:`UiCallbacks` protocol.

    Returns:
        A ``(main_widget, widgets)`` tuple.
    """
    widgets = _UiWidgetsBuilder()
    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)
    main_layout.setSpacing(15)

    top_bar = QHBoxLayout()
    top_bar.addStretch()
    doc_btn = QPushButton("📘 Model Documentation & Mathematics")
    doc_btn.setToolTip("View detailed mathematical documentation and physics")
    doc_btn.clicked.connect(callbacks.show_documentation)
    doc_btn.setStyleSheet("font-weight: bold; padding: 8px;")
    top_bar.addWidget(doc_btn)
    top_bar.addStretch()
    main_layout.addLayout(top_bar)

    diagram_group = QGroupBox("Forearm-Hand-Club Diagram")
    diagram_layout = QVBoxLayout()
    diagram_canvas = DiagramCanvas(
        grip_angle_deg=_DEFAULT_GRIP_ANGLE_DEG,
        wrist_angle_deg=_DEFAULT_WRIST_ANGLE_DEG,
    )
    widgets.diagram_canvas = diagram_canvas
    diagram_layout.addWidget(diagram_canvas)
    diagram_group.setLayout(diagram_layout)
    main_layout.addWidget(diagram_group)

    _build_parameter_group(callbacks, widgets, main_layout)
    _build_signal_group(callbacks, widgets, main_layout)
    _build_plot_controls_group(callbacks, widgets, main_layout)
    _build_plot_group(widgets, main_layout)

    info_group = QGroupBox("Model Information")
    info_layout = QVBoxLayout()
    info_label = QLabel()
    info_label.setWordWrap(True)
    info_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
    info_label.setText(current_info_html(_DEFAULT_GRIP_ANGLE_DEG, _DEFAULT_WRIST_ANGLE_DEG))
    widgets.info_label = info_label
    info_layout.addWidget(info_label)
    info_group.setLayout(info_layout)
    main_layout.addWidget(info_group)

    return main_widget, widgets.finalize()
