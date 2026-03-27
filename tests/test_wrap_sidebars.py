"""Tests for sidebar wrapping utility."""

from __future__ import annotations

from pathlib import Path

from src.tools.wrap_sidebars import wrap_file


def test_wrap_file_adds_sticky_wrapper_to_supported_asides(tmp_path: Path) -> None:
    """Sidebar wrapper should be inserted for each supported aside type."""
    file_path = tmp_path / "page.qmd"
    file_path.write_text(
        """
<aside class="left-sidebar">
  Left
</aside>
<aside class="right-sidebar">
  Right
</aside>
<aside class="resources-sidebar">
  Resources
</aside>
""".strip(),
        encoding="utf-8",
    )

    wrap_file(file_path)
    updated = file_path.read_text(encoding="utf-8")

    assert updated.count('div class="sidebar-sticky-content"') == 3


def test_wrap_file_skips_already_wrapped_right_sidebar(tmp_path: Path) -> None:
    """Existing sticky wrappers should not be duplicated."""
    file_path = tmp_path / "page.qmd"
    original = """
<aside class="right-sidebar">
  <div class="sidebar-sticky-content">
    Existing
  </div>
</aside>
""".strip()
    file_path.write_text(original, encoding="utf-8")

    wrap_file(file_path)

    assert file_path.read_text(encoding="utf-8") == original
