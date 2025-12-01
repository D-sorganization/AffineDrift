"""Regression tests for the legacy navigation update utility."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.update_navigation import main as update_nav_main
from tools.update_navigation import update_navigation


def _write_sample_html(tmp_path: Path, body: str) -> Path:
    """Write a sample HTML file for testing."""
    page = tmp_path / "sample.html"
    page.write_text(
        f"""<!DOCTYPE html>
<html>
  <body>
{body}
  </body>
</html>
""",
        encoding="utf-8",
    )
    return page


def test_update_navigation_replaces_nav_and_logo(tmp_path: Path) -> None:
    """Test that update_navigation replaces legacy nav and logo with new ones."""
    legacy_nav = """    <nav>
      <ul class="nav-links">
        <li><a href="old.html">Legacy</a></li>
      </ul>
    </nav>
    <img src="logo/AffineDriftLogo.png" alt="logo">
"""
    page = _write_sample_html(tmp_path, legacy_nav)

    changed = update_navigation(page)
    updated = page.read_text(encoding="utf-8")

    assert changed is True
    assert '<nav class="top-nav">' in updated
    assert 'logo/Logo Transparent/1.png' in updated
    assert '<li><a href="articles.html">Articles</a></li>' in updated


def test_update_navigation_raises_for_missing_nav(tmp_path: Path) -> None:
    """Test that update_navigation raises ValueError when nav is missing."""
    body = "    <nav class='top-nav'></nav>"
    page = _write_sample_html(tmp_path, body)

    with pytest.raises(ValueError):
        update_navigation(page)


def test_main_reports_missing_files(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test that main reports missing files correctly."""
    missing = tmp_path / "does-not-exist.html"
    caplog.set_level("INFO")

    exit_code = update_nav_main([str(missing)])

    assert exit_code == 1
    assert "Not found" in caplog.text

