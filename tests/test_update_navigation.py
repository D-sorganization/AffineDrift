"""Regression tests for the legacy navigation update utility."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from src.tools.update_navigation import NEW_NAV
from src.tools.update_navigation import main as update_nav_main
from src.tools.update_navigation import update_navigation

if TYPE_CHECKING:
    from pathlib import Path


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
    assert "logo/Logo Transparent/1.png" in updated
    assert '<li><a href="articles.html">Articles</a></li>' in updated


def test_update_navigation_raises_for_missing_nav(tmp_path: Path) -> None:
    """Test that update_navigation raises ValueError when nav is missing."""
    body = "    <nav class='top-nav'></nav>"
    page = _write_sample_html(tmp_path, body)

    with pytest.raises(ValueError):
        update_navigation(page)


def test_main_reports_missing_files(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that main reports missing files correctly."""
    missing = tmp_path / "does-not-exist.html"
    caplog.set_level("INFO")

    exit_code = update_nav_main([str(missing)])

    assert exit_code == 1
    assert "Not found" in caplog.text


def test_update_navigation_returns_false_when_already_up_to_date(tmp_path: Path) -> None:
    """update_navigation should return False when no changes are required."""
    # Write a file already containing the current nav markup
    nav_content = f"""    <nav>
      <ul class="nav-links">
{chr(10).join("        " + line for line in NEW_NAV.splitlines())}
      </ul>
    </nav>
"""
    page = _write_sample_html(tmp_path, nav_content)

    # First call: applies update
    update_navigation(page)
    # Second call: already up to date — should return False
    changed = update_navigation(page)
    assert changed is False


def test_main_returns_zero_on_success(tmp_path: Path) -> None:
    """main should return 0 when all files are updated or already current."""
    legacy_nav = """    <nav>
      <ul class="nav-links">
        <li><a href="old.html">Legacy</a></li>
      </ul>
    </nav>
"""
    page = _write_sample_html(tmp_path, legacy_nav)

    exit_code = update_nav_main([str(page)])

    assert exit_code == 0


def test_main_returns_one_when_value_error(tmp_path: Path) -> None:
    """main should return 1 when update_navigation raises ValueError."""
    # File that triggers ValueError: has no nav-links ul
    body = "<p>No nav here</p>"
    page = _write_sample_html(tmp_path, body)

    exit_code = update_nav_main([str(page)])

    assert exit_code == 1
