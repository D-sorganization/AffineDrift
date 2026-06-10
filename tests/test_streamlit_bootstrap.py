"""Behavioral tests for ``streamlit_bootstrap`` pure logic (issue #3230).

Streamlit is optional, so guarded by ``importorskip``. The Streamlit surface is
mocked; we assert the real branching logic: page config is forwarded, session
defaults are set only when absent, and CSS injection is conditional on the file
existing.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("streamlit")

from src.tools.wrist_universal_joint import streamlit_bootstrap


class _FakeSessionState(dict):
    """Mimics st.session_state: dict membership + attribute assignment."""

    def __setattr__(self, key: str, value: object) -> None:
        self[key] = value

    def __getattr__(self, key: str) -> object:
        try:
            return self[key]
        except KeyError as exc:  # pragma: no cover - defensive
            raise AttributeError(key) from exc


def test_configure_page_forwards_metadata() -> None:
    with patch.object(streamlit_bootstrap, "st") as st:
        streamlit_bootstrap.configure_page()
    st.set_page_config.assert_called_once()
    kwargs = st.set_page_config.call_args.kwargs
    assert kwargs["layout"] == "wide"
    assert "Wrist" in kwargs["page_title"]


def test_initialize_session_state_sets_defaults_when_empty() -> None:
    fake_state = _FakeSessionState()
    with patch.object(streamlit_bootstrap, "st") as st:
        st.session_state = fake_state
        streamlit_bootstrap.initialize_session_state()
    assert fake_state["polynomial_expression"] == "t**2 - t"
    assert fake_state["polynomial_error"] is None


def test_initialize_session_state_preserves_existing_values() -> None:
    fake_state = _FakeSessionState()
    fake_state["polynomial_expression"] = "custom-expr"
    fake_state["polynomial_error"] = "prior error"
    with patch.object(streamlit_bootstrap, "st") as st:
        st.session_state = fake_state
        streamlit_bootstrap.initialize_session_state()
    # Existing values must not be overwritten.
    assert fake_state["polynomial_expression"] == "custom-expr"
    assert fake_state["polynomial_error"] == "prior error"


def test_inject_custom_css_reads_and_renders_when_present(tmp_path) -> None:
    css = tmp_path / "style.css"
    css.write_text("body { color: red; }", encoding="utf-8")
    with patch.object(streamlit_bootstrap, "st") as st:
        st.markdown = MagicMock()
        streamlit_bootstrap.inject_custom_css(tmp_path)
    st.markdown.assert_called_once()
    rendered = st.markdown.call_args.args[0]
    assert "body { color: red; }" in rendered
    assert st.markdown.call_args.kwargs["unsafe_allow_html"] is True


def test_inject_custom_css_noop_when_missing(tmp_path) -> None:
    with patch.object(streamlit_bootstrap, "st") as st:
        st.markdown = MagicMock()
        streamlit_bootstrap.inject_custom_css(tmp_path)  # no style.css present
    st.markdown.assert_not_called()
