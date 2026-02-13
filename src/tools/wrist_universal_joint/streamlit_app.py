"""Enhanced Wrist Universal Joint Model - Streamlit Web App.

# mypy: disable-error-code="no-any-unimported"

This is the Streamlit entry point for the wrist universal joint model.
It provides the interactive web UI with sidebar controls and visualization panels.

Run with: streamlit run streamlit_app.py
"""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from src.core.contracts import require

from .constants import (
    DEFAULT_CLUB_LENGTH,
    DEFAULT_CLUBHEAD_CG_DISTANCE,
    DEFAULT_CLUBHEAD_WEIGHT,
    DEFAULT_SHAFT_WEIGHT,
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

# Page config
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
    st.markdown(
        """
    <style>
        .main {
            padding: 2rem 1rem;
        }
        .stButton>button {
            background: linear-gradient(135deg, #3282b8 0%, #0f4c75 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 2rem;
            font-weight: 600;
        }
        h1 {
            background: linear-gradient(135deg, #0f4c75 0%, #3282b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def _render_header() -> None:
    """Render the main app header and description."""
    st.title("🏌️ Enhanced Wrist Universal Joint Model")
    st.markdown(
        """
    <div style='background: #f0f4f8; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; \
    border-left: 4px solid #3282b8;'>
        <p style='margin: 0; font-size: 1.1em;'>
        This interactive tool models the wrist as a universal joint (Hooke/Cardan)
        with proper kinematics,
        showing how grip angle and wrist deviation angle affect torque transmission
        and angular acceleration.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def _render_sidebar() -> dict[str, Any]:
    """Render sidebar controls and return the selected parameters.

    Returns:
        Dictionary containing all user-selected parameters.
    """
    params: dict[str, Any] = {}

    with st.sidebar:
        st.header("Parameters")

        # Angle controls
        st.subheader("Grip Angle θ_grip")
        params["grip_angle"] = st.slider(
            "Grip Angle (degrees)",
            0,
            90,
            30,
            1,
            help="0° = parallel to fingers, 90° = perpendicular to fingers",
        )

        st.subheader("Wrist Deviation Angle φ")
        params["wrist_angle"] = st.slider(
            "Wrist Deviation (degrees)",
            -60,
            60,
            0,
            1,
            help="+ values = radial deviation, - values = ulnar deviation",
        )

        st.markdown("---")

        # Club Properties
        st.subheader("Club Properties")
        params["clubhead_weight"] = st.number_input(
            "Clubhead (g)",
            50.0,
            500.0,
            DEFAULT_CLUBHEAD_WEIGHT,
            1.0,
        )
        params["shaft_weight"] = st.number_input(
            "Shaft (g)",
            30.0,
            200.0,
            DEFAULT_SHAFT_WEIGHT,
            1.0,
        )
        params["club_length"] = st.number_input(
            "Length (m)",
            0.5,
            1.5,
            DEFAULT_CLUB_LENGTH,
            0.01,
        )
        params["cg_distance"] = st.number_input(
            "CG Dist (m)",
            0.3,
            1.2,
            DEFAULT_CLUBHEAD_CG_DISTANCE,
            0.01,
        )

        i_alpha, i_gamma = calculate_moments_of_inertia(
            params["clubhead_weight"],
            params["shaft_weight"],
            params["club_length"],
            params["cg_distance"],
        )
        params["I_alpha"] = i_alpha
        params["I_gamma"] = i_gamma

        st.markdown(
            f"""
        **Moments of Inertia:**
        - I_α = {i_alpha:.4f} kg·m²
        - I_γ = {i_gamma:.4f} kg·m²
        """,
        )

        st.markdown("---")

        # Signal Generator
        st.subheader("Input Signal Generator")
        params["noise_type"] = st.selectbox(
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

        if params["noise_type"] == "Polynomial":
            polynomial_expr = st.text_input(
                "Polynomial Expression",
                value=st.session_state.polynomial_expression,
                help="Use 't' as variable. Example: t**2 - t",
            )
            st.session_state.polynomial_expression = polynomial_expr
            if st.session_state.polynomial_error:
                st.error(st.session_state.polynomial_error)

        if st.button("🎲 Regenerate Signal"):
            st.rerun()

        st.markdown("---")

        # Plot type selection
        st.subheader("Plot Type")
        params["plot_type"] = st.selectbox(
            "Select Plot",
            ["Torque", "Angular Acceleration", "Transmission Ratio vs Wrist Angle"],
        )

        st.markdown("---")

        # Signal visibility (depends on plot type)
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


def _render_main_content(params: dict[str, Any]) -> None:
    """Render the main content area with diagram and plots.

    Args:
        params: Dictionary of user-selected parameters from sidebar.
    """
    require(params is not None, "params dict must not be None")
    # Generate signal
    t = np.linspace(0, 1, 500)
    input_torque, error = generate_sample_torque(
        params["noise_type"],
        t,
        st.session_state.polynomial_expression,
    )
    if error is not None:
        st.session_state.polynomial_error = error
    elif params["noise_type"] == "Polynomial":
        st.session_state.polynomial_error = None

    # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Forearm-Hand-Club Diagram")
        diagram_fig = draw_diagram(params["grip_angle"], params["wrist_angle"])
        st.pyplot(diagram_fig)
        plt.close(diagram_fig)

    with col2:
        plot_type = params["plot_type"]
        st.subheader(f"{plot_type} Plot")

        if plot_type == "Torque":
            plot_fig = plot_torque(
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
        elif plot_type == "Angular Acceleration":
            plot_fig = plot_acceleration(
                t,
                input_torque,
                params["grip_angle"],
                params["wrist_angle"],
                params["I_alpha"],
                params["I_gamma"],
                params["show_alpha"],
                params["show_gamma"],
            )
        else:  # Transmission Ratio
            plot_fig = plot_transmission_sweep(
                params["grip_angle"],
                params["wrist_angle"],
                params["I_alpha"],
                params["I_gamma"],
                params["show_transmission"],
                params["show_velocity"],
                params["show_accel_alpha"],
                params["show_accel_gamma"],
            )

        st.pyplot(plot_fig)
        plt.close(plot_fig)

    # Info panel
    _render_info_panel(params, input_torque)


def _render_info_panel(params: dict[str, Any], input_torque: Any) -> None:
    """Render the expandable model information panel.

    Args:
        params: Dictionary of user-selected parameters.
        input_torque: Generated input torque signal.
    """
    st.markdown("---")
    with st.expander("📐 Model Information"):
        grip_angle = params["grip_angle"]
        wrist_angle = params["wrist_angle"]
        i_alpha = params["I_alpha"]
        i_gamma = params["I_gamma"]

        theta_grip_rad = np.radians(grip_angle)
        phi_wrist_rad = np.radians(wrist_angle)
        omega_ratio, tau_ratio = universal_joint_transmission_ratio(
            phi_wrist_rad,
            theta_grip_rad,
        )
        torque_transmitted = np.mean(input_torque) * tau_ratio
        torque_alpha, torque_gamma = distribute_torque_by_grip_angle(
            torque_transmitted,
            theta_grip_rad,
        )

        pct_alpha = np.abs(np.sin(theta_grip_rad)) * 100
        pct_gamma = np.abs(np.cos(theta_grip_rad)) * 100

        deviation = "radial" if wrist_angle > 0 else "ulnar" if wrist_angle < 0 else "neutral"

        st.markdown(
            f"""
        ### Current Parameters
        - **Grip Angle (θ_grip):** {grip_angle}°
        - **Wrist Deviation Angle (φ):** {wrist_angle}°
        ({deviation} deviation)

        ### Transmission Ratios
        - **Angular Velocity Ratio (ω_out/ω_in):** {omega_ratio:.4f}
        - **Torque Transmission Ratio (τ_out/τ_in):** {tau_ratio:.4f}

        ### Torque Distribution (at mean input torque)
        - **Torque to α-axis (higher MOI):** {torque_alpha:.4f} N·m
        ({pct_alpha:.1f}% of transmitted)
        - **Torque to γ-axis (lowest MOI):** {torque_gamma:.4f} N·m
        ({pct_gamma:.1f}% of transmitted)

        ### Angular Acceleration (at mean torque)
        - **α-axis acceleration:** {torque_alpha / i_alpha:.4f} rad/s²
        - **γ-axis acceleration:** {torque_gamma / i_gamma:.4f} rad/s²

        ### Model Assumptions
        - Universal joint (Hooke/Cardan) kinematics
        - Rigid body model
        - Power conservation (P = τω)
        - Constant grip angle during motion
        - Wrist angle represents radial/ulnar deviation
        """,
        )


# ===== Main App Entry Point =====
_inject_custom_css()
_render_header()
_params = _render_sidebar()
_render_main_content(_params)
