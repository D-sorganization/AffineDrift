"""Behavioral tests for Streamlit visualization wrapper delegation."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

pytest.importorskip("streamlit")

from src.tools.wrist_universal_joint import streamlit_visualization


def test_draw_diagram_delegates_angles() -> None:
    sentinel = object()
    with patch.object(
        streamlit_visualization, "_draw_diagram", MagicMock(return_value=sentinel)
    ) as draw:
        assert streamlit_visualization.draw_diagram(12.5, -3.0) is sentinel

    draw.assert_called_once_with(12.5, -3.0)


def test_plot_torque_delegates_full_argument_set() -> None:
    t = np.array([0.0, 1.0])
    torque = np.array([2.0, 3.0])
    sentinel = object()

    with patch.object(
        streamlit_visualization, "_plot_torque", MagicMock(return_value=sentinel)
    ) as plot:
        assert (
            streamlit_visualization.plot_torque(
                t,
                torque,
                10.0,
                20.0,
                1.5,
                2.5,
                True,
                False,
                True,
                False,
            )
            is sentinel
        )

    plot.assert_called_once_with(t, torque, 10.0, 20.0, 1.5, 2.5, True, False, True, False)


def test_plot_acceleration_delegates_full_argument_set() -> None:
    t = np.array([0.0, 1.0])
    torque = np.array([2.0, 3.0])
    sentinel = object()

    with patch.object(
        streamlit_visualization, "_plot_acceleration", MagicMock(return_value=sentinel)
    ) as plot:
        assert (
            streamlit_visualization.plot_acceleration(
                t,
                torque,
                10.0,
                20.0,
                1.5,
                2.5,
                True,
                False,
            )
            is sentinel
        )

    plot.assert_called_once_with(t, torque, 10.0, 20.0, 1.5, 2.5, True, False)


def test_plot_transmission_sweep_delegates_full_argument_set() -> None:
    sentinel = object()

    with patch.object(
        streamlit_visualization, "_plot_transmission_sweep", MagicMock(return_value=sentinel)
    ) as plot:
        assert (
            streamlit_visualization.plot_transmission_sweep(
                10.0,
                20.0,
                1.5,
                2.5,
                True,
                False,
                True,
                False,
            )
            is sentinel
        )

    plot.assert_called_once_with(10.0, 20.0, 1.5, 2.5, True, False, True, False)
