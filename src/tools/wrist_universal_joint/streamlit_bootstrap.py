"""Bootstrap helpers for the wrist Streamlit application."""

from __future__ import annotations

from pathlib import Path

import streamlit as st


def configure_page() -> None:
    """Configure the Streamlit page metadata."""
    st.set_page_config(
        page_title="Enhanced Wrist Universal Joint Model",
        page_icon="🏌️",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def initialize_session_state() -> None:
    """Initialize the app session state lazily."""
    if "polynomial_expression" not in st.session_state:
        st.session_state.polynomial_expression = "t**2 - t"
    if "polynomial_error" not in st.session_state:
        st.session_state.polynomial_error = None


def inject_custom_css(template_dir: Path) -> None:
    """Inject custom CSS styles into the Streamlit page."""
    css_path = template_dir / "style.css"
    if css_path.exists():
        css = css_path.read_text()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
