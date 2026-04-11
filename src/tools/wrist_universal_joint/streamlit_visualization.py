"""Streamlit-cached visualization wrappers for the wrist universal joint app."""

from __future__ import annotations

import streamlit as st

from .diagram import draw_diagram as _draw_diagram
from .plots import (
    plot_acceleration as _plot_acceleration,
)
from .plots import (
    plot_torque as _plot_torque,
)
from .plots import (
    plot_transmission_sweep as _plot_transmission_sweep,
)


@st.cache_resource(max_entries=20)
def draw_diagram(grip_angle_deg: float, wrist_angle_deg: float):
    """Cache the common diagram renderer for the Streamlit app."""
    return _draw_diagram(grip_angle_deg, wrist_angle_deg)


@st.cache_resource(max_entries=20)
def plot_torque(
    t,
    input_torque,
    grip_angle_deg: float,
    wrist_angle_deg: float,
    i_alpha: float,
    i_gamma: float,
    show_input: bool,
    show_transmitted: bool,
    show_alpha: bool,
    show_gamma: bool,
):
    """Cache the torque plot for the Streamlit app."""
    return _plot_torque(
        t,
        input_torque,
        grip_angle_deg,
        wrist_angle_deg,
        i_alpha,
        i_gamma,
        show_input,
        show_transmitted,
        show_alpha,
        show_gamma,
    )


@st.cache_resource(max_entries=20)
def plot_acceleration(
    t,
    input_torque,
    grip_angle_deg: float,
    wrist_angle_deg: float,
    i_alpha: float,
    i_gamma: float,
    show_alpha: bool,
    show_gamma: bool,
):
    """Cache the acceleration plot for the Streamlit app."""
    return _plot_acceleration(
        t,
        input_torque,
        grip_angle_deg,
        wrist_angle_deg,
        i_alpha,
        i_gamma,
        show_alpha,
        show_gamma,
    )


@st.cache_resource(max_entries=20)
def plot_transmission_sweep(
    grip_angle_deg: float,
    wrist_angle_deg: float,
    i_alpha: float,
    i_gamma: float,
    show_transmission: bool,
    show_velocity: bool,
    show_accel_alpha: bool,
    show_accel_gamma: bool,
):
    """Cache the transmission sweep plot for the Streamlit app."""
    return _plot_transmission_sweep(
        grip_angle_deg,
        wrist_angle_deg,
        i_alpha,
        i_gamma,
        show_transmission,
        show_velocity,
        show_accel_alpha,
        show_accel_gamma,
    )
