"""Offscreen tests for the wrist universal joint Qt window/builder contract.

These exercise the issue #3292 refactor: the builder returns a fully populated
``UiWidgets`` (no ``setattr`` injection), the window consumes it via ``self.ui``,
and slider/textbox/plot-type wiring works end to end.

Qt runs under ``QT_QPA_PLATFORM=offscreen`` and matplotlib under the Agg backend.
The ``diagram`` module imports streamlit at module load, so we install a minimal
streamlit mock before importing the Qt modules. A single ``QApplication`` is
shared across the module to respect the fleet-known Qt multi-widget segfault
constraint.
"""

from __future__ import annotations

import dataclasses
import os
import sys
import types
from typing import Any

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    import PyQt6.QtWidgets as QtWidgets

    _ = QtWidgets.QApplication
except (ImportError, Exception):
    pytest.skip("PyQt6 not loadable in this environment", allow_module_level=True)

pytest.importorskip("matplotlib", reason="matplotlib not installed")


def _install_streamlit_mock() -> None:
    """Install a minimal streamlit stub so diagram.py imports headlessly."""
    if "streamlit" in sys.modules:
        return
    st = types.ModuleType("streamlit")
    st.cache_resource = lambda **kw: lambda f: f  # type: ignore[attr-defined]
    st.cache_data = lambda **kw: lambda f: f  # type: ignore[attr-defined]
    sys.modules["streamlit"] = st


_install_streamlit_mock()

import matplotlib  # noqa: E402  # reason: module level imports after setup hook

matplotlib.use("Agg")

from PyQt6.QtWidgets import (  # noqa: E402  # reason: module level imports after setup hook
    QApplication,
)

from src.tools.wrist_universal_joint.qt_ui_sections import (  # noqa: E402  # reason: module level imports after setup hook
    UiCallbacks,
    UiWidgets,
    build_main_widget,
)
from src.tools.wrist_universal_joint.qt_window import (  # noqa: E402  # reason: module level imports after setup hook
    MainWindow,
)


@pytest.fixture(scope="module")
def qapp() -> Any:
    """Provide a single shared QApplication for the whole module."""
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def window(qapp: Any) -> MainWindow:
    """Construct a MainWindow (which builds its UI in __init__)."""
    return MainWindow()


def test_build_main_widget_populates_all_widget_fields(window: MainWindow) -> None:
    """Every UiWidgets field must be a constructed (non-None) widget."""
    ui = window.ui
    assert isinstance(ui, UiWidgets)
    none_fields = [
        field.name for field in dataclasses.fields(ui) if getattr(ui, field.name) is None
    ]
    assert none_fields == []


def test_window_implements_ui_callbacks_protocol(window: MainWindow) -> None:
    """The window must satisfy the UiCallbacks protocol the builders rely on."""
    assert isinstance(window, UiCallbacks)


def test_slider_syncs_into_textbox(window: MainWindow) -> None:
    """Moving the grip slider mirrors its value into the paired textbox."""
    window.ui.grip_slider.setValue(45)
    assert window.ui.grip_textbox.text() == "45"


def test_textbox_clamps_and_syncs_slider(window: MainWindow) -> None:
    """An out-of-range grip textbox value clamps and updates the slider."""
    window.ui.grip_textbox.setText("130")
    window.update_grip_from_textbox()
    assert window.ui.grip_slider.value() == 90
    assert window.ui.grip_textbox.text() == "90"


def test_polynomial_controls_toggle_with_noise_type(window: MainWindow) -> None:
    """Selecting the Polynomial noise type reveals the polynomial controls.

    ``isVisibleTo`` reports the widget's own visibility independent of whether
    an ancestor is shown, which keeps the assertion valid in offscreen tests.
    """
    window.update_noise_type("Polynomial")
    assert window.ui.polynomial_input.isVisibleTo(window.ui.polynomial_input.parentWidget())
    assert window.ui.polynomial_label.isVisibleTo(window.ui.polynomial_label.parentWidget())
    window.update_noise_type("Step")
    assert not window.ui.polynomial_input.isVisibleTo(window.ui.polynomial_input.parentWidget())


def test_plot_type_enables_relevant_checkboxes(window: MainWindow) -> None:
    """Torque plot type enables torque checkboxes and disables acceleration ones."""
    window.update_plot_type("Torque")
    assert window.ui.show_input_check.isEnabled()
    assert not window.ui.show_alpha_accel_check.isEnabled()
    window.update_plot_type("Angular Acceleration")
    assert window.ui.show_alpha_accel_check.isEnabled()
    assert not window.ui.show_input_check.isEnabled()


def test_build_main_widget_returns_widget_and_widgets(qapp: Any) -> None:
    """build_main_widget returns a (QWidget, UiWidgets) tuple given callbacks."""
    window = MainWindow()
    main_widget, widgets = build_main_widget(window)
    assert main_widget is not None
    assert isinstance(widgets, UiWidgets)
