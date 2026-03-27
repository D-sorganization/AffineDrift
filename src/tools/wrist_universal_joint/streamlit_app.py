"""Enhanced Wrist Universal Joint Model - Streamlit Web App.

# mypy: disable-error-code="no-any-unimported"

This is the Streamlit entry point for the wrist universal joint model.
It provides the interactive web UI with sidebar controls and visualization panels.

Run with: streamlit run streamlit_app.py
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import streamlit as st
from matplotlib.figure import Figure

from src.core.contracts import require

from .constants import (
    DEFAULT_CLUB_LENGTH,
    DEFAULT_CLUBHEAD_CG_DISTANCE,
    DEFAULT_CLUBHEAD_WEIGHT,
    DEFAULT_SHAFT_WEIGHT,
    DEFAULT_SIGNAL_LENGTH,
)
from .torque_calculator import (
    calculate_moments_of_inertia,
    distribute_torque_by_grip_angle,
    generate_sample_torque,
    universal_joint_transmission_ratio,
)
from .visualization import (
    draw_diagram,
    plot_acceleration,
    plot_torque,
    plot_transmission_sweep,
)

logger = logging.getLogger(__name__)


def _init_page() -> None:
    """Configure Streamlit page settings and initialize session state.

    Must be called once at application startup inside the main() entry point.
    Separating this from module level prevents side effects on import.
    """
    st.set_page_config(
        page_title="Enhanced Wrist Universal Joint Model",
        page_icon="🏌️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize session state
    if "polynomial_expression" not in st.session_state:
        st.session_state.polynomial_expression = "t**2 - t"
    if "polynomial_error" not in st.session_state:
        st.session_state.polynomial_error = None


def _inject_custom_css() -> None:
    """Inject custom CSS styles into the Streamlit page."""
    template_dir = Path(__file__).parent / "templates"
    css_path = template_dir / "style.css"
    if css_path.exists():
        css = css_path.read_text()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def _render_header() -> None:
    """Render the main app header and description."""
    st.title("🏌️ Enhanced Wrist Universal Joint Model")
    template_dir = Path(__file__).parent / "templates"
    header_path = template_dir / "header.html"
    if header_path.exists():
        header_html = header_path.read_text()
        st.markdown(header_html, unsafe_allow_html=True)


def _render_angle_controls() -> dict[str, float]:
    """Render grip and wrist angle sliders.

    Returns:
        Dictionary with 'grip_angle' and 'wrist_angle' values.
    """
    st.subheader("Grip Angle \u03b8_grip")
    grip_angle = st.slider(
        "Grip Angle (degrees)",
        0,
        90,
        30,
        1,
        help="0\u00b0 = parallel to fingers, 90\u00b0 = perpendicular to fingers",
    )

    st.subheader("Wrist Deviation Angle \u03c6")
    wrist_angle = st.slider(
        "Wrist Deviation (degrees)",
        -60,
        60,
        0,
        1,
        help="+ values = radial deviation, - values = ulnar deviation",
    )

    return {"grip_angle": grip_angle, "wrist_angle": wrist_angle}


def _render_club_properties() -> dict[str, float]:
    """Render club property inputs and compute moments of inertia.

    Returns:
        Dictionary with club parameters and computed moments of inertia.
    """
    st.subheader("Club Properties")
    clubhead_weight = st.number_input("Clubhead (g)", 50.0, 500.0, DEFAULT_CLUBHEAD_WEIGHT, 1.0)
    shaft_weight = st.number_input("Shaft (g)", 30.0, 200.0, DEFAULT_SHAFT_WEIGHT, 1.0)
    club_length = st.number_input("Length (m)", 0.5, 1.5, DEFAULT_CLUB_LENGTH, 0.01)
    cg_distance = st.number_input("CG Dist (m)", 0.3, 1.2, DEFAULT_CLUBHEAD_CG_DISTANCE, 0.01)

    i_alpha, i_gamma = calculate_moments_of_inertia(
        clubhead_weight, shaft_weight, club_length, cg_distance
    )

    st.markdown(
        f"""
    **Moments of Inertia:**
    - I_\u03b1 = {i_alpha:.4f} kg\u00b7m\u00b2
    - I_\u03b3 = {i_gamma:.4f} kg\u00b7m\u00b2
    """,
    )

    return {
        "clubhead_weight": clubhead_weight,
        "shaft_weight": shaft_weight,
        "club_length": club_length,
        "cg_distance": cg_distance,
        "I_alpha": i_alpha,
        "I_gamma": i_gamma,
    }


def _render_signal_generator() -> dict[str, Any]:
    """Render signal type selection and polynomial input.

    Returns:
        Dictionary with 'noise_type' key.
    """
    st.subheader("Input Signal Generator")
    noise_type = st.selectbox(
        "Signal Type",
        [
            "Golf-like Random",
            "Step",
            "Pulse",
            "Burst",
            "Sinusoidal",
            "Random",
            "Polynomial",
        ],
    )

    if noise_type == "Polynomial":
        polynomial_expr = st.text_input(
            "Polynomial Expression",
            value=st.session_state.polynomial_expression,
            help="Use 't' as variable. Example: t**2 - t",
        )
        st.session_state.polynomial_expression = polynomial_expr
        if st.session_state.polynomial_error:
            st.error(st.session_state.polynomial_error)

    if st.button("\U0001f3b2 Regenerate Signal"):
        st.rerun()

    return {"noise_type": noise_type}


def _render_sidebar() -> dict[str, Any]:
    """Render sidebar controls and return the selected parameters.

    Returns:
        Dictionary containing all user-selected parameters.
    """
    params: dict[str, Any] = {}

    with st.sidebar:
        st.header("Parameters")

        params.update(_render_angle_controls())
        st.markdown("---")

        params.update(_render_club_properties())
        st.markdown("---")

        params.update(_render_signal_generator())
        st.markdown("---")

        st.subheader("Plot Type")
        params["plot_type"] = st.selectbox(
            "Select Plot",
            ["Torque", "Angular Acceleration", "Transmission Ratio vs Wrist Angle"],
        )

        st.markdown("---")

        st.subheader("Show Signals")
        params.update(_render_signal_checkboxes(params["plot_type"]))

    return params


def _render_signal_checkboxes(plot_type: str) -> dict[str, bool]:
    """Render signal visibility checkboxes based on plot type.

    Args:
        plot_type: Currently selected plot type.

    Returns:
        Dictionary of checkbox states.
    """
    if plot_type == "Torque":
        return {
            "show_input": st.checkbox("Input Torque", value=True),
            "show_transmitted": st.checkbox("Transmitted Torque", value=True),
            "show_alpha": st.checkbox("Torque α (higher MOI axis)", value=True),
            "show_gamma": st.checkbox("Torque γ (lowest MOI axis)", value=True),
            "show_velocity": False,
            "show_accel_alpha": False,
            "show_accel_gamma": False,
            "show_transmission": False,
        }
    if plot_type == "Angular Acceleration":
        return {
            "show_input": False,
            "show_transmitted": False,
            "show_alpha": st.checkbox("Acceleration α", value=True),
            "show_gamma": st.checkbox("Acceleration γ", value=True),
            "show_velocity": False,
            "show_accel_alpha": False,
            "show_accel_gamma": False,
            "show_transmission": False,
        }
    # Transmission Ratio
    return {
        "show_input": False,
        "show_transmitted": False,
        "show_alpha": False,
        "show_gamma": False,
        "show_transmission": st.checkbox("Transmission Ratio", value=True),
        "show_velocity": st.checkbox("Velocity Ratio", value=False),
        "show_accel_alpha": st.checkbox("Accel α Ratio", value=False),
        "show_accel_gamma": st.checkbox("Accel γ Ratio", value=False),
    }


def _plot_torque_figure(
    params: dict[str, Any],
    t: npt.NDArray[Any],
    input_torque: npt.NDArray[Any],
) -> Figure:
    """Create a torque vs time figure."""
    return plot_torque(
        t,
        input_torque,
        params["grip_angle"],
        params["wrist_angle"],
        params["I_alpha"],
        params["I_gamma"],
        params["show_input"],
        params["show_transmitted"],
        params["show_alpha"],
        params["show_gamma"],
    )


def _plot_acceleration_figure(
    params: dict[str, Any],
    t: npt.NDArray[Any],
    input_torque: npt.NDArray[Any],
) -> Figure:
    """Create an angular acceleration vs time figure."""
    return plot_acceleration(
        t,
        input_torque,
        params["grip_angle"],
        params["wrist_angle"],
        params["I_alpha"],
        params["I_gamma"],
        params["show_alpha"],
        params["show_gamma"],
    )


def _plot_transmission_figure(params: dict[str, Any]) -> Figure:
    """Create a transmission ratio sweep figure."""
    return plot_transmission_sweep(
        params["grip_angle"],
        params["wrist_angle"],
        params["I_alpha"],
        params["I_gamma"],
        params["show_transmission"],
        params["show_velocity"],
        params["show_accel_alpha"],
        params["show_accel_gamma"],
    )


def _create_plot_figure(
    params: dict[str, Any],
    t: npt.NDArray[Any],
    input_torque: npt.NDArray[Any],
) -> Figure:
    """Create a torque vs time figure."""
    return plot_torque(  # type: ignore[no-any-return]
        t,
        input_torque,
        params["grip_angle"],
        params["wrist_angle"],
        params["I_alpha"],
        params["I_gamma"],
        params["show_input"],
        params["show_transmitted"],
        params["show_alpha"],
        params["show_gamma"],
    )


def _plot_acceleration_figure(
    params: dict[str, Any],
    t: np.ndarray,  # type: ignore[type-arg]
    input_torque: np.ndarray,  # type: ignore[type-arg]
) -> Figure:
    """Create an angular acceleration vs time figure."""
    return plot_acceleration(  # type: ignore[no-any-return]
        t,
        input_torque,
        params["grip_angle"],
        params["wrist_angle"],
        params["I_alpha"],
        params["I_gamma"],
        params["show_alpha"],
        params["show_gamma"],
    )


def _plot_transmission_figure(params: dict[str, Any]) -> Figure:
    """Create a transmission ratio sweep figure."""
    return plot_transmission_sweep(  # type: ignore[no-any-return]
        params["grip_angle"],
        params["wrist_angle"],
        params["I_alpha"],
        params["I_gamma"],
        params["show_transmission"],
        params["show_velocity"],
        params["show_accel_alpha"],
        params["show_accel_gamma"],
    )


def _create_plot_figure(
    params: dict[str, Any],
    t: npt.NDArray[Any],
    input_torque: npt.NDArray[Any],
) -> Figure:
    """Create the appropriate plot figure based on selected plot type.

    Args:
        params: User-selected parameters including plot_type and visibility flags.
        t: Time array for time-series plots.
        input_torque: Generated input torque signal.

    Returns:
        Matplotlib Figure for the selected plot type.
    """
    plot_type = params["plot_type"]
    if plot_type == "Torque":
        return _plot_torque_figure(params, t, input_torque)
    if plot_type == "Angular Acceleration":
        return _plot_acceleration_figure(params, t, input_torque)
    return _plot_transmission_figure(params)


def _render_main_content(params: dict[str, Any]) -> None:
    """Render the main content area with diagram and plots.

    Args:
        params: Dictionary of user-selected parameters from sidebar.
    """
    require(params is not None, "params dict must not be None")
    t = np.linspace(0, 1, DEFAULT_SIGNAL_LENGTH)
    input_torque, error = generate_sample_torque(
        params["noise_type"],
        t,
        st.session_state.polynomial_expression,
    )
    if error is not None:
        st.session_state.polynomial_error = error
    elif params["noise_type"] == "Polynomial":
        st.session_state.polynomial_error = None

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Forearm-Hand-Club Diagram")
        diagram_fig = draw_diagram(params["grip_angle"], params["wrist_angle"])
        st.pyplot(diagram_fig)
        plt.close(diagram_fig)

    with col2:
        st.subheader(f"{params['plot_type']} Plot")
        plot_fig = _create_plot_figure(params, t, input_torque)
        st.pyplot(plot_fig)
        plt.close(plot_fig)

    _render_info_panel(params, input_torque)


def _compute_info_metrics(params: dict[str, Any], input_torque: Any) -> dict[str, Any]:
    """Compute transmission and torque metrics for the info panel.

    Returns:
        Dictionary with keys: omega_ratio, tau_ratio, torque_alpha, torque_gamma,
        pct_alpha, pct_gamma, deviation.
    """
    grip_angle = params["grip_angle"]
    wrist_angle = params["wrist_angle"]
    theta_grip_rad = np.radians(grip_angle)
    phi_wrist_rad = np.radians(wrist_angle)
    omega_ratio, tau_ratio = universal_joint_transmission_ratio(phi_wrist_rad, theta_grip_rad)
    torque_transmitted = np.mean(input_torque) * tau_ratio
    torque_alpha, torque_gamma = distribute_torque_by_grip_angle(torque_transmitted, theta_grip_rad)
    return {
        "omega_ratio": omega_ratio,
        "tau_ratio": tau_ratio,
        "torque_alpha": torque_alpha,
        "torque_gamma": torque_gamma,
        "pct_alpha": np.abs(np.sin(theta_grip_rad)) * 100,
        "pct_gamma": np.abs(np.cos(theta_grip_rad)) * 100,
        "deviation": "radial" if wrist_angle > 0 else "ulnar" if wrist_angle < 0 else "neutral",
    }


def _render_info_markdown(params: dict[str, Any], info: dict[str, Any]) -> None:
    """Render the model information markdown block inside the expander."""
    grip_angle = params["grip_angle"]
    wrist_angle = params["wrist_angle"]
    i_alpha = params["I_alpha"]
    i_gamma = params["I_gamma"]
    st.markdown(
        f"""
    ### Current Parameters
    - **Grip Angle (θ_grip):** {grip_angle}°
    - **Wrist Deviation Angle (φ):** {wrist_angle}° ({info["deviation"]} deviation)

    ### Transmission Ratios
    - **Angular Velocity Ratio (ω_out/ω_in):** {info["omega_ratio"]:.4f}
    - **Torque Transmission Ratio (τ_out/τ_in):** {info["tau_ratio"]:.4f}

    ### Torque Distribution (at mean input torque)
    - **Torque to α-axis (higher MOI):** {info["torque_alpha"]:.4f} N·m
    ({info["pct_alpha"]:.1f}% of transmitted)
    - **Torque to γ-axis (lowest MOI):** {info["torque_gamma"]:.4f} N·m
    ({info["pct_gamma"]:.1f}% of transmitted)

    ### Angular Acceleration (at mean torque)
    - **α-axis acceleration:** {info["torque_alpha"] / i_alpha:.4f} rad/s²
    - **γ-axis acceleration:** {info["torque_gamma"] / i_gamma:.4f} rad/s²

    ### Model Assumptions
    - Universal joint (Hooke/Cardan) kinematics
    - Rigid body model
    - Power conservation (P = τω)
    - Constant grip angle during motion
    - Wrist angle represents radial/ulnar deviation
    """,
    )


def _render_info_panel(params: dict[str, Any], input_torque: Any) -> None:
    """Render the expandable model information panel.

    Args:
        params: Dictionary of user-selected parameters.
        input_torque: Generated input torque signal.
    """
    st.markdown("---")
    with st.expander("📐 Model Information"):
        info = _compute_info_metrics(params, input_torque)
        _render_info_markdown(params, info)


def main() -> None:
    """Run the Streamlit application.

    All Streamlit UI calls are contained here so that importing this module
    does not execute any side effects.  Run via:
        streamlit run streamlit_app.py
    """
    _init_page()
    _inject_custom_css()
    _render_header()
    params = _render_sidebar()
    _render_main_content(params)


if __name__ == "__main__":
    main()
elif hasattr(st, "runtime") and st.runtime.exists():
    main()
