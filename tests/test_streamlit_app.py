"""Tests for the wrist Streamlit app entrypoint behavior."""

from __future__ import annotations

from unittest.mock import patch

from src.tools.wrist_universal_joint import streamlit_app


def test_import_does_not_initialize_session_state() -> None:
    """Importing the module should not mutate Streamlit state eagerly."""
    assert hasattr(streamlit_app, "main")


def test_main_runs_entry_sequence() -> None:
    """The top-level app flow should execute only through main()."""
    with (
        patch.object(streamlit_app, "configure_page") as configure_page,
        patch.object(streamlit_app, "initialize_session_state") as initialize_session_state,
        patch.object(streamlit_app, "inject_custom_css") as inject_custom_css,
        patch.object(streamlit_app, "_render_header") as render_header,
        patch.object(
            streamlit_app, "_render_sidebar", return_value={"plot_type": "Torque"}
        ) as render_sidebar,
        patch.object(streamlit_app, "_render_main_content") as render_main_content,
    ):
        streamlit_app.main()

    configure_page.assert_called_once_with()
    initialize_session_state.assert_called_once_with()
    inject_custom_css.assert_called_once()
    render_header.assert_called_once_with()
    render_sidebar.assert_called_once_with()
    render_main_content.assert_called_once_with({"plot_type": "Torque"})
