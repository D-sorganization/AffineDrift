"""Tests for wrist_universal_joint visualization modules (plots, diagram, visualization).

These modules use streamlit which is not installed in CI. We mock the streamlit
package at the sys.modules level before importing so all tests can run headlessly.
We also use matplotlib's Agg backend to prevent display calls.

streamlit_app.py wraps all Streamlit UI calls inside main() and _init_page() so
that importing the module has no side effects.  Individual helper functions and the
top-level entry points are tested in TestStreamlitAppFunctions below.
"""

from __future__ import annotations

import contextlib
import sys
import types
from typing import Any
from unittest.mock import MagicMock, patch


def _build_streamlit_mock() -> types.ModuleType:
    """Build a minimal streamlit mock module adequate for testing."""
    st = types.ModuleType("streamlit")

    # Decorator that passes through the function unmodified
    st.cache_resource = lambda **kw: (lambda f: f)  # type: ignore[attr-defined]
    st.cache_data = lambda **kw: (lambda f: f)  # type: ignore[attr-defined]

    # Session state
    class FakeSessionState(dict):  # type: ignore[type-arg]
        def __getattr__(self, k: str) -> Any:
            return self.get(k)

        def __setattr__(self, k: str, v: Any) -> None:
            self[k] = v

        def __contains__(self, k: object) -> bool:
            return super().__contains__(k)

    st.session_state = FakeSessionState()  # type: ignore[attr-defined]

    # Context managers (sidebar, expander, etc.)
    class _FakeContext:
        def __enter__(self) -> _FakeContext:
            return self

        def __exit__(self, *a: Any) -> None:
            pass

    fake_ctx = _FakeContext()
    st.sidebar = fake_ctx  # type: ignore[attr-defined]

    # Streamlit UI stubs
    st.set_page_config = MagicMock()  # type: ignore[attr-defined]
    st.title = MagicMock()  # type: ignore[attr-defined]
    st.header = MagicMock()  # type: ignore[attr-defined]
    st.subheader = MagicMock()  # type: ignore[attr-defined]
    st.markdown = MagicMock()  # type: ignore[attr-defined]
    st.info = MagicMock()  # type: ignore[attr-defined]
    st.error = MagicMock()  # type: ignore[attr-defined]
    st.button = MagicMock(return_value=False)  # type: ignore[attr-defined]
    st.rerun = MagicMock()  # type: ignore[attr-defined]
    st.pyplot = MagicMock()  # type: ignore[attr-defined]
    st.write = MagicMock()  # type: ignore[attr-defined]
    st.slider = MagicMock(return_value=30.0)  # type: ignore[attr-defined]
    st.number_input = MagicMock(return_value=200.0)  # type: ignore[attr-defined]
    st.selectbox = MagicMock(return_value="Torque")  # type: ignore[attr-defined]
    st.checkbox = MagicMock(return_value=True)  # type: ignore[attr-defined]
    st.text_input = MagicMock(return_value="t**2")  # type: ignore[attr-defined]
    st.expander = MagicMock(return_value=fake_ctx)  # type: ignore[attr-defined]

    def fake_columns(n: Any) -> list[MagicMock]:
        count = n if isinstance(n, int) else len(n)
        cols = []
        for _ in range(count):
            col = MagicMock()
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock(return_value=None)
            cols.append(col)
        return cols

    st.columns = fake_columns  # type: ignore[attr-defined]

    def fake_tabs(labels: list[str]) -> list[MagicMock]:
        tabs = []
        for _ in labels:
            tab = MagicMock()
            tab.__enter__ = MagicMock(return_value=tab)
            tab.__exit__ = MagicMock(return_value=None)
            tabs.append(tab)
        return tabs

    st.tabs = fake_tabs  # type: ignore[attr-defined]

    return st


@contextlib.contextmanager
def _streamlit_context():  # type: ignore[return]
    """Context manager that installs a fake streamlit into sys.modules."""
    st_mock = _build_streamlit_mock()
    old_st = sys.modules.get("streamlit")

    # Ensure matplotlib uses Agg (non-interactive) backend
    import matplotlib

    matplotlib.use("Agg")

    sys.modules["streamlit"] = st_mock

    # Remove cached imports of the modules we want to re-import fresh
    for key in list(sys.modules.keys()):
        if "wrist_universal_joint" in key:
            del sys.modules[key]

    try:
        yield st_mock
    finally:
        if old_st is None:
            sys.modules.pop("streamlit", None)
        else:
            sys.modules["streamlit"] = old_st
        # Clean up wrist modules so other tests start fresh
        for key in list(sys.modules.keys()):
            if "wrist_universal_joint" in key:
                del sys.modules[key]


class TestPlotsModule:
    """Tests for src.tools.wrist_universal_joint.plots functions."""

    def test_compute_torque_signals_delegates_to_enhanced_kinematics(self) -> None:
        """_compute_torque_signals should proxy the shared kinematics helper."""
        import numpy as np

        with _streamlit_context():
            import src.tools.wrist_universal_joint.plots as plots
            from src.tools.wrist_universal_joint.enhanced_model_kinematics import TorqueSignals

            signals = TorqueSignals(
                omega_ratio=0.91,
                tau_ratio=1.09,
                torque_transmitted=np.array([1.0, 2.0]),
                torque_alpha=np.array([0.4, 0.8]),
                torque_gamma=np.array([0.6, 1.2]),
            )
            with patch.object(plots, "_compute_torque_signals_core", return_value=signals) as core:
                result = plots._compute_torque_signals(np.array([3.0, 4.0]), 30.0, 10.0)

            core.assert_called_once()
            called_input, called_grip, called_wrist = core.call_args.args
            np.testing.assert_array_equal(called_input, np.array([3.0, 4.0]))
            assert called_grip == 30.0
            assert called_wrist == 10.0
            np.testing.assert_array_equal(result[0], signals.torque_transmitted)
            np.testing.assert_array_equal(result[1], signals.torque_alpha)
            np.testing.assert_array_equal(result[2], signals.torque_gamma)
            assert result[3] == signals.tau_ratio

    def test_compute_acceleration_signals_delegates_to_enhanced_kinematics(self) -> None:
        """_compute_acceleration_signals should proxy the shared kinematics helper."""
        import numpy as np

        with _streamlit_context():
            import src.tools.wrist_universal_joint.plots as plots
            from src.tools.wrist_universal_joint.enhanced_model_kinematics import (
                AccelerationSignals,
            )

            signals = AccelerationSignals(
                accel_alpha=np.array([1.5, 2.5]),
                accel_gamma=np.array([3.5, 4.5]),
            )
            with patch.object(
                plots,
                "_compute_acceleration_signals_core",
                return_value=signals,
            ) as core:
                result = plots._compute_acceleration_signals(np.array([5.0, 6.0]), 25.0, -5.0, 0.1, 0.2)

            core.assert_called_once()
            called_input, called_grip, called_wrist, called_i_alpha, called_i_gamma = core.call_args.args
            np.testing.assert_array_equal(called_input, np.array([5.0, 6.0]))
            assert called_grip == 25.0
            assert called_wrist == -5.0
            assert called_i_alpha == 0.1
            assert called_i_gamma == 0.2
            np.testing.assert_array_equal(result[0], signals.accel_alpha)
            np.testing.assert_array_equal(result[1], signals.accel_gamma)

    def test_compute_transmission_sweep_delegates_to_enhanced_kinematics(self) -> None:
        """_compute_transmission_sweep should proxy the shared kinematics helper."""
        import numpy as np

        with _streamlit_context():
            import src.tools.wrist_universal_joint.plots as plots
            from src.tools.wrist_universal_joint.enhanced_model_kinematics import TransmissionSweep

            sweep = TransmissionSweep(
                wrist_angle_deg=np.array([-60.0, 0.0, 60.0]),
                omega_ratios=np.array([0.8, 1.0, 0.8]),
                tau_ratios=np.array([1.25, 1.0, 1.25]),
                accel_alpha_ratios=np.array([2.0, 2.5, 2.0]),
                accel_gamma_ratios=np.array([1.0, 1.2, 1.0]),
            )
            with patch.object(
                plots,
                "_compute_transmission_sweep_core",
                return_value=sweep,
            ) as core:
                result = plots._compute_transmission_sweep(np.array([-30.0, 0.0, 30.0]), 0.5, 0.1, 0.2)

            core.assert_called_once()
            called_grip_deg, called_wrist_deg, called_i_alpha, called_i_gamma = core.call_args.args
            assert called_grip_deg == np.degrees(0.5)
            assert called_wrist_deg == 0.0
            assert called_i_alpha == 0.1
            assert called_i_gamma == 0.2
            np.testing.assert_array_equal(result[0], sweep.tau_ratios)
            np.testing.assert_array_equal(result[1], sweep.omega_ratios)
            np.testing.assert_array_equal(result[2], sweep.accel_alpha_ratios)
            np.testing.assert_array_equal(result[3], sweep.accel_gamma_ratios)

    def test_plot_torque_returns_figure(self) -> None:
        """plot_torque should return a matplotlib Figure."""
        import numpy as np

        with _streamlit_context():
            import matplotlib.figure as mfig

            import src.tools.wrist_universal_joint.plots as plots

            t = np.linspace(0, 1, 50)
            torque = np.sin(t) * 10.0
            fig = plots.plot_torque(
                t,
                torque,
                30.0,
                10.0,
                0.005,
                0.001,
                show_input=True,
                show_transmitted=True,
                show_alpha=True,
                show_gamma=True,
            )
            assert isinstance(fig, mfig.Figure)

    def test_plot_torque_all_flags_false(self) -> None:
        """plot_torque with all flags False should still return a Figure."""
        import numpy as np

        with _streamlit_context():
            import matplotlib.figure as mfig

            import src.tools.wrist_universal_joint.plots as plots

            t = np.linspace(0, 1, 50)
            torque = np.ones(50) * 5.0
            fig = plots.plot_torque(
                t,
                torque,
                0.0,
                0.0,
                0.005,
                0.001,
                show_input=False,
                show_transmitted=False,
                show_alpha=False,
                show_gamma=False,
            )
            assert isinstance(fig, mfig.Figure)

    def test_plot_acceleration_returns_figure(self) -> None:
        """plot_acceleration should return a matplotlib Figure."""
        import numpy as np

        with _streamlit_context():
            import matplotlib.figure as mfig

            import src.tools.wrist_universal_joint.plots as plots

            t = np.linspace(0, 1, 50)
            torque = np.cos(t) * 8.0
            fig = plots.plot_acceleration(
                t,
                torque,
                45.0,
                20.0,
                0.005,
                0.001,
                show_alpha=True,
                show_gamma=True,
            )
            assert isinstance(fig, mfig.Figure)

    def test_plot_acceleration_all_flags_false(self) -> None:
        """plot_acceleration with all flags False should still return a Figure."""
        import numpy as np

        with _streamlit_context():
            import matplotlib.figure as mfig

            import src.tools.wrist_universal_joint.plots as plots

            t = np.linspace(0, 1, 50)
            torque = np.ones(50) * 3.0
            fig = plots.plot_acceleration(
                t,
                torque,
                30.0,
                0.0,
                0.005,
                0.001,
                show_alpha=False,
                show_gamma=False,
            )
            assert isinstance(fig, mfig.Figure)

    def test_plot_transmission_sweep_returns_figure(self) -> None:
        """plot_transmission_sweep should return a matplotlib Figure."""
        with _streamlit_context():
            import matplotlib.figure as mfig

            import src.tools.wrist_universal_joint.plots as plots

            fig = plots.plot_transmission_sweep(
                30.0,
                10.0,
                0.005,
                0.001,
                show_transmission=True,
                show_velocity=True,
                show_accel_alpha=True,
                show_accel_gamma=True,
            )
            assert isinstance(fig, mfig.Figure)

    def test_plot_transmission_sweep_all_flags_false(self) -> None:
        """plot_transmission_sweep with all flags False should still return a Figure."""
        with _streamlit_context():
            import matplotlib.figure as mfig

            import src.tools.wrist_universal_joint.plots as plots

            fig = plots.plot_transmission_sweep(
                0.0,
                0.0,
                0.005,
                0.001,
                show_transmission=False,
                show_velocity=False,
                show_accel_alpha=False,
                show_accel_gamma=False,
            )
            assert isinstance(fig, mfig.Figure)

    def test_compute_transmission_sweep_returns_arrays(self) -> None:
        """_compute_transmission_sweep should return 4 numpy arrays."""
        import numpy as np

        with _streamlit_context():
            import src.tools.wrist_universal_joint.plots as plots

            phi_sweep = np.linspace(-30, 30, 20)
            tau, omega, a_alpha, a_gamma = plots._compute_transmission_sweep(
                phi_sweep, 0.5, 0.005, 0.001
            )
            assert len(tau) == 200
            assert len(omega) == 200
            assert len(a_alpha) == 200
            assert len(a_gamma) == 200


class TestDiagramModule:
    """Tests for src.tools.wrist_universal_joint.diagram functions."""

    def test_draw_diagram_delegates_to_shared_geometry(self) -> None:
        """draw_diagram should call the shared enhanced-model renderer."""
        with _streamlit_context():
            import matplotlib.figure as mfig

            import src.tools.wrist_universal_joint.diagram as diagram

            with patch("src.tools.wrist_universal_joint.enhanced_model_geometry.draw_enhanced_model_diagram") as draw:
                fig = diagram.draw_diagram(grip_angle_deg=30.0, wrist_angle_deg=10.0)

            draw.assert_called_once()
            assert isinstance(fig, mfig.Figure)

    def test_draw_diagram_returns_figure(self) -> None:
        """draw_diagram should return a matplotlib Figure."""
        with _streamlit_context():
            import matplotlib.figure as mfig

            import src.tools.wrist_universal_joint.diagram as diagram

            fig = diagram.draw_diagram(grip_angle_deg=30.0, wrist_angle_deg=10.0)
            assert isinstance(fig, mfig.Figure)

    def test_draw_diagram_zero_angles(self) -> None:
        """draw_diagram should work with zero angles."""
        with _streamlit_context():
            import matplotlib.figure as mfig

            import src.tools.wrist_universal_joint.diagram as diagram

            fig = diagram.draw_diagram(grip_angle_deg=0.0, wrist_angle_deg=0.0)
            assert isinstance(fig, mfig.Figure)

    def test_draw_diagram_max_grip_angle(self) -> None:
        """draw_diagram should work with maximum grip angle."""
        with _streamlit_context():
            import matplotlib.figure as mfig

            import src.tools.wrist_universal_joint.diagram as diagram

            fig = diagram.draw_diagram(grip_angle_deg=90.0, wrist_angle_deg=0.0)
            assert isinstance(fig, mfig.Figure)

    def test_draw_diagram_negative_wrist_angle(self) -> None:
        """draw_diagram should work with negative wrist angle."""
        with _streamlit_context():
            import matplotlib.figure as mfig

            import src.tools.wrist_universal_joint.diagram as diagram

            fig = diagram.draw_diagram(grip_angle_deg=30.0, wrist_angle_deg=-30.0)
            assert isinstance(fig, mfig.Figure)


class TestVisualizationModule:
    """Tests for src.tools.wrist_universal_joint.visualization re-exports."""

    def test_visualization_exports_draw_diagram(self) -> None:
        """visualization module should export draw_diagram."""
        with _streamlit_context():
            import src.tools.wrist_universal_joint.visualization as vis

            assert hasattr(vis, "draw_diagram")
            assert callable(vis.draw_diagram)

    def test_visualization_exports_plot_functions(self) -> None:
        """visualization module should export plot_torque, plot_acceleration, plot_transmission_sweep."""
        with _streamlit_context():
            import src.tools.wrist_universal_joint.visualization as vis

            assert hasattr(vis, "plot_torque")
            assert hasattr(vis, "plot_acceleration")
            assert hasattr(vis, "plot_transmission_sweep")

    def test_visualization_all_in_all(self) -> None:
        """visualization.__all__ should contain all four exports."""
        with _streamlit_context():
            import src.tools.wrist_universal_joint.visualization as vis

            for name in [
                "draw_diagram",
                "plot_acceleration",
                "plot_torque",
                "plot_transmission_sweep",
            ]:
                assert name in vis.__all__


class TestStreamlitAppFunctions:
    """Tests for streamlit_app.py individual utility functions.

    The module-level code in streamlit_app.py executes the full app at import time.
    We test individual helper functions by re-importing after the mock is in place.
    """

    def test_inject_custom_css_no_template_dir(self) -> None:
        """_inject_custom_css should not raise when template dir doesn't exist."""
        with _streamlit_context():
            import src.tools.wrist_universal_joint.streamlit_app as app

            # Should not raise — css_path.exists() returns False
            app._inject_custom_css()

    def test_render_header_no_template(self) -> None:
        """_render_header should not raise when template header doesn't exist."""
        with _streamlit_context():
            import src.tools.wrist_universal_joint.streamlit_app as app

            app._render_header()

    def test_render_signal_checkboxes_torque(self) -> None:
        """_render_signal_checkboxes should return Torque flags when plot_type=Torque."""
        with _streamlit_context():
            import src.tools.wrist_universal_joint.streamlit_app as app

            result = app._render_signal_checkboxes("Torque")
            assert "show_input" in result
            assert "show_transmitted" in result
            assert "show_alpha" in result
            assert "show_gamma" in result

    def test_render_signal_checkboxes_acceleration(self) -> None:
        """_render_signal_checkboxes should return Accel flags when type=Angular Acceleration."""
        with _streamlit_context():
            import src.tools.wrist_universal_joint.streamlit_app as app

            result = app._render_signal_checkboxes("Angular Acceleration")
            assert result["show_input"] is False
            assert result["show_transmitted"] is False

    def test_render_signal_checkboxes_transmission(self) -> None:
        """_render_signal_checkboxes should return Transmission flags for other types."""
        with _streamlit_context():
            import src.tools.wrist_universal_joint.streamlit_app as app

            result = app._render_signal_checkboxes("Transmission Ratio vs Wrist Angle")
            assert "show_transmission" in result
            assert "show_velocity" in result

    def test_create_plot_figure_torque(self) -> None:
        """_create_plot_figure should dispatch to plot_torque for Torque type."""
        import numpy as np

        with _streamlit_context():
            import matplotlib.figure as mfig

            import src.tools.wrist_universal_joint.streamlit_app as app

            t = np.linspace(0, 1, 50)
            torque = np.sin(t) * 10.0
            params = {
                "plot_type": "Torque",
                "grip_angle": 30.0,
                "wrist_angle": 10.0,
                "I_alpha": 0.005,
                "I_gamma": 0.001,
                "show_input": True,
                "show_transmitted": True,
                "show_alpha": True,
                "show_gamma": True,
            }
            fig = app._create_plot_figure(params, t, torque)
            assert isinstance(fig, mfig.Figure)

    def test_create_plot_figure_acceleration(self) -> None:
        """_create_plot_figure should dispatch to plot_acceleration."""
        import numpy as np

        with _streamlit_context():
            import matplotlib.figure as mfig

            import src.tools.wrist_universal_joint.streamlit_app as app

            t = np.linspace(0, 1, 50)
            torque = np.ones(50) * 5.0
            params = {
                "plot_type": "Angular Acceleration",
                "grip_angle": 30.0,
                "wrist_angle": 0.0,
                "I_alpha": 0.005,
                "I_gamma": 0.001,
                "show_alpha": True,
                "show_gamma": False,
            }
            fig = app._create_plot_figure(params, t, torque)
            assert isinstance(fig, mfig.Figure)

    def test_create_plot_figure_transmission(self) -> None:
        """_create_plot_figure should dispatch to plot_transmission_sweep."""
        import numpy as np

        with _streamlit_context():
            import matplotlib.figure as mfig

            import src.tools.wrist_universal_joint.streamlit_app as app

            t = np.linspace(0, 1, 50)
            torque = np.ones(50) * 5.0
            params = {
                "plot_type": "Transmission Ratio vs Wrist Angle",
                "grip_angle": 30.0,
                "wrist_angle": 0.0,
                "I_alpha": 0.005,
                "I_gamma": 0.001,
                "show_transmission": True,
                "show_velocity": False,
                "show_accel_alpha": False,
                "show_accel_gamma": False,
            }
            fig = app._create_plot_figure(params, t, torque)
            assert isinstance(fig, mfig.Figure)

    def test_render_main_content(self) -> None:
        """_render_main_content should execute without raising."""
        with _streamlit_context():
            import src.tools.wrist_universal_joint.streamlit_app as app

            params = {
                "grip_angle": 30.0,
                "wrist_angle": 10.0,
                "I_alpha": 0.005,
                "I_gamma": 0.001,
                "plot_type": "Torque",
                "noise_type": "Golf-like Random",
                "show_input": True,
                "show_transmitted": True,
                "show_alpha": True,
                "show_gamma": True,
                "show_velocity": False,
                "show_accel_alpha": False,
                "show_accel_gamma": False,
                "show_transmission": False,
            }
            # Should not raise
            app._render_main_content(params)

    def test_render_club_properties_returns_dict(self) -> None:
        """_render_club_properties should return a dictionary with club parameters."""
        with _streamlit_context():
            import src.tools.wrist_universal_joint.streamlit_app as app

            result = app._render_club_properties()
            assert isinstance(result, dict)
            assert "I_alpha" in result
            assert "I_gamma" in result

    def test_render_angle_controls_returns_dict(self) -> None:
        """_render_angle_controls should return a dictionary with angle values."""
        with _streamlit_context():
            import src.tools.wrist_universal_joint.streamlit_app as app

            result = app._render_angle_controls()
            assert isinstance(result, dict)
            assert "grip_angle" in result
            assert "wrist_angle" in result

    def test_init_page_calls_set_page_config(self) -> None:
        """_init_page should call st.set_page_config and seed session state."""
        with _streamlit_context() as st_mock:
            import src.tools.wrist_universal_joint.streamlit_app as app

            app._init_page()
            st_mock.set_page_config.assert_called_once()
            assert "polynomial_expression" in st_mock.session_state
            assert "polynomial_error" in st_mock.session_state

    def test_init_page_idempotent_session_state(self) -> None:
        """_init_page should not overwrite existing session_state values."""
        with _streamlit_context() as st_mock:
            import src.tools.wrist_universal_joint.streamlit_app as app

            st_mock.session_state["polynomial_expression"] = "custom_expr"
            app._init_page()
            # Value set before _init_page must be preserved
            assert st_mock.session_state["polynomial_expression"] == "custom_expr"

    def test_import_has_no_side_effects(self) -> None:
        """Importing streamlit_app must not call set_page_config or UI functions."""
        with _streamlit_context() as st_mock:
            import src.tools.wrist_universal_joint.streamlit_app  # noqa: F401

            st_mock.set_page_config.assert_not_called()
            st_mock.title.assert_not_called()

    def test_main_runs_full_app(self) -> None:
        """main() should call init, header, sidebar, and content without raising."""
        with _streamlit_context() as st_mock:
            import src.tools.wrist_universal_joint.streamlit_app as app

            app.main()
            st_mock.set_page_config.assert_called_once()
            st_mock.title.assert_called_once()
