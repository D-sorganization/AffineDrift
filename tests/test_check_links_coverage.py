
"""Additional tests for check_links to improve coverage."""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.tools.check_links import check_links, _is_broken_link


def test_check_links_finds_broken_links(tmp_path: Path) -> None:
    """End-to-end check_links should report broken links."""
    root = tmp_path

    # Create a source file with one valid and one broken link
    page = root / "index.qmd"
    page.write_text("[Valid](valid.md)\n[Broken](missing.md)", encoding="utf-8")

    # Create the valid target
    (root / "valid.md").touch()

    # Run check_links
    broken = check_links(str(root))

    # Verify broken link is found
    assert len(broken) == 1
    rel_path, line, link = broken[0]
    assert rel_path == "index.qmd"
    assert line == 2
    assert link == "missing.md"


def test_check_links_ignores_skipped_files(tmp_path: Path) -> None:
    """Files in skip list or excluded dirs should not be scanned."""
    root = tmp_path

    # Create a file that should be skipped (e.g. CONTRIBUTING.md is in SKIP_FILES)
    skip_file = root / "CONTRIBUTING.md"
    skip_file.write_text("[Broken](missing.md)", encoding="utf-8")

    # Create a file in excluded dir
    exclude_dir = root / "node_modules"
    exclude_dir.mkdir()
    exclude_file = exclude_dir / "bad.md"
    exclude_file.write_text("[Broken](missing.md)", encoding="utf-8")

    # Run check_links
    broken = check_links(str(root))

    # Should be empty because files are skipped
    assert broken == []


def test_check_links_handles_read_errors(tmp_path: Path) -> None:
    """Files that cannot be read should be logged and skipped."""
    root = tmp_path

    # Create a file
    page = root / "unreadable.qmd"
    page.touch()

    # Mock find_links to raise OSError
    with patch("src.tools.check_links.find_links", side_effect=OSError("Read error")):
        with patch("src.tools.check_links.logger") as mock_logger:
            broken = check_links(str(root))

            assert broken == []
            mock_logger.exception.assert_called()

def test_is_broken_link_returns_false_for_none_url(tmp_path: Path) -> None:
    """_is_broken_link should return False if _normalize_internal_url returns None."""
    # This covers line 104: if url is None: return False
    # _normalize_internal_url returns None for external links like http://...

    root = tmp_path
    file_path = root / "test.md"

    # External link
    assert _is_broken_link(root_path=root, file_path=file_path, link="http://google.com") is False
