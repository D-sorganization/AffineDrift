"""Tests for src.tools.fix_html_validation — individual fixers and apply_all_fixes."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from src.tools.fix_html_validation import (
    add_button_type,
    add_iframe_title,
    add_landmark_aria_labels,
    add_navbar_brand_aria_label,
    apply_all_fixes,
    fix_crossorigin_attribute,
    fix_dots_in_ids,
    remove_aria_labelledby_dropdown,
    remove_redundant_role_link,
)


class TestFixCrossoriginAttribute:
    """Tests for fix_crossorigin_attribute()."""

    def test_replaces_crossorigin_empty(self) -> None:
        """Should replace crossorigin="" with crossorigin."""
        result = fix_crossorigin_attribute('crossorigin=""')
        assert result == "crossorigin"

    def test_no_change_without_attribute(self) -> None:
        """Should not change content without crossorigin=""."""
        result = fix_crossorigin_attribute("<script src='x.js'></script>")
        assert 'crossorigin=""' not in result

    def test_multiple_occurrences(self) -> None:
        """Should replace all occurrences."""
        html = 'crossorigin="" crossorigin=""'
        result = fix_crossorigin_attribute(html)
        assert 'crossorigin=""' not in result
        assert result.count("crossorigin") == 2


class TestRemoveRedundantRoleLink:
    """Tests for remove_redundant_role_link()."""

    def test_removes_role_link(self) -> None:
        """Should remove role='link' from anchor elements."""
        result = remove_redundant_role_link('<a href="x" role="link">text</a>')
        assert 'role="link"' not in result
        assert "text" in result

    def test_no_change_without_role_link(self) -> None:
        """Should not change content without role='link'."""
        html = '<a href="x">text</a>'
        result = remove_redundant_role_link(html)
        assert result == html


class TestRemoveAriaLabelledbyDropdown:
    """Tests for remove_aria_labelledby_dropdown()."""

    def test_removes_aria_labelledby(self) -> None:
        """Should remove aria-labelledby from dropdown-menu."""
        html = '<ul class="dropdown-menu" aria-labelledby="dropdownBtn">'
        result = remove_aria_labelledby_dropdown(html)
        assert "aria-labelledby" not in result
        assert 'class="dropdown-menu"' in result

    def test_no_change_without_dropdown(self) -> None:
        """Should not change content without dropdown-menu."""
        html = '<ul class="nav-menu" aria-labelledby="nav">'
        result = remove_aria_labelledby_dropdown(html)
        assert result == html


class TestAddNavbarBrandAriaLabel:
    """Tests for add_navbar_brand_aria_label()."""

    def test_adds_aria_label_to_navbar_brand(self) -> None:
        """Should add aria-label='Home' to navbar-brand-logo links."""
        html = '<a href="/" class="navbar-brand navbar-brand-logo">'
        result = add_navbar_brand_aria_label(html)
        assert 'aria-label="Home"' in result

    def test_no_change_without_navbar_brand(self) -> None:
        """Should not change content without navbar-brand-logo class."""
        html = '<a href="/" class="other-class">'
        result = add_navbar_brand_aria_label(html)
        assert result == html

    def test_no_duplicate_aria_label(self) -> None:
        """Should not add duplicate aria-label when already present."""
        html = '<a href="/" class="navbar-brand navbar-brand-logo" aria-label="Home">'
        result = add_navbar_brand_aria_label(html)
        assert result.count('aria-label="Home"') == 1


class TestFixDotsInIds:
    """Tests for fix_dots_in_ids()."""

    def test_replaces_dots_in_id(self) -> None:
        """Should replace dots with dashes in id attributes."""
        html = 'id="section.1.2"'
        result = fix_dots_in_ids(html)
        assert "section-1-2" in result

    def test_replaces_dots_in_href(self) -> None:
        """Should replace dots with dashes in href anchor links."""
        html = 'href="#section.1.2"'
        result = fix_dots_in_ids(html)
        assert "section-1-2" in result

    def test_no_change_without_dots(self) -> None:
        """Should not change IDs without dots."""
        html = 'id="section-intro"'
        result = fix_dots_in_ids(html)
        assert result == html


class TestAddButtonType:
    """Tests for add_button_type()."""

    def test_adds_type_to_button(self) -> None:
        """Should add type='button' to button without type."""
        html = "<button>Click me</button>"
        result = add_button_type(html)
        assert 'type="button"' in result

    def test_no_change_when_type_present(self) -> None:
        """Should not modify button that already has type attribute."""
        html = '<button type="submit">Submit</button>'
        result = add_button_type(html)
        assert result == html

    def test_no_change_without_buttons(self) -> None:
        """Should not change content without button elements."""
        html = "<div>No buttons here.</div>"
        result = add_button_type(html)
        assert result == html


class TestAddIframeTitle:
    """Tests for add_iframe_title()."""

    def test_adds_title_to_iframe(self) -> None:
        """Should add title='Embedded Content' to iframe without title."""
        html = "<iframe src='x.html'>"
        result = add_iframe_title(html)
        assert 'title="Embedded Content"' in result

    def test_no_change_when_title_present(self) -> None:
        """Should not modify iframe that already has title attribute."""
        html = '<iframe src="x.html" title="My Frame">'
        result = add_iframe_title(html)
        assert result == html


class TestAddLandmarkAriaLabels:
    """Tests for add_landmark_aria_labels()."""

    def test_adds_toc_label(self) -> None:
        """Should add aria-label to TOC navigation."""
        html = '<nav id="TOC">'
        result = add_landmark_aria_labels(html)
        assert 'aria-label="Table of Contents"' in result

    def test_adds_left_sidebar_label(self) -> None:
        """Should add aria-label to left sidebar."""
        html = '<aside class="left-sidebar">'
        result = add_landmark_aria_labels(html)
        assert 'aria-label="Primary Sidebar"' in result

    def test_adds_right_sidebar_label(self) -> None:
        """Should add aria-label to right sidebar."""
        html = '<aside class="right-sidebar">'
        result = add_landmark_aria_labels(html)
        assert 'aria-label="Secondary Sidebar"' in result

    def test_no_duplicate_labels(self) -> None:
        """Should not add duplicate aria-labels when already present."""
        html = '<nav id="TOC" aria-label="Table of Contents">'
        result = add_landmark_aria_labels(html)
        assert result.count('aria-label="Table of Contents"') == 1


class TestApplyAllFixes:
    """Tests for apply_all_fixes()."""

    def test_applies_multiple_fixes(self) -> None:
        """Should apply all fixes to HTML content."""
        html = (
            '<button>Click</button><iframe src="x.html"></iframe><a href="x" role="link">link</a>'
        )
        result = apply_all_fixes(html)
        assert 'type="button"' in result
        assert 'title="Embedded Content"' in result
        assert 'role="link"' not in result

    def test_raises_on_empty_content(self) -> None:
        """Should raise ContractViolationError on empty content (DbC)."""
        with pytest.raises(AssertionError):
            apply_all_fixes("")

    def test_plain_html_unchanged_structure(self) -> None:
        """Should preserve structure of clean HTML."""
        html = "<html><head></head><body><p>Clean.</p></body></html>"
        result = apply_all_fixes(html)
        assert "<p>Clean.</p>" in result


class TestFixHtmlValidationMain:
    """Tests for main() function."""

    def test_main_returns_2_on_missing_docs_dir(self, tmp_path: Path) -> None:
        """main() should return 2 when docs-dir does not exist."""
        from src.tools.fix_html_validation import main

        with patch.object(
            sys, "argv", ["fix_html_validation", "--docs-dir", str(tmp_path / "missing")]
        ):
            result = main()
        assert result == 2

    def test_main_returns_0_on_empty_docs_dir(self, tmp_path: Path) -> None:
        """main() should return 0 when docs-dir exists but has no HTML files."""
        from src.tools.fix_html_validation import main

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        with patch.object(sys, "argv", ["fix_html_validation", "--docs-dir", str(docs_dir)]):
            result = main()
        assert result == 0

    def test_main_dry_run_on_html_file(self, tmp_path: Path) -> None:
        """main() --dry-run should not modify files."""
        from src.tools.fix_html_validation import main

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        html_file = docs_dir / "page.html"
        original = "<button>Click</button>"
        html_file.write_text(original, encoding="utf-8")

        with patch.object(
            sys,
            "argv",
            ["fix_html_validation", "--docs-dir", str(docs_dir), "--dry-run"],
        ):
            result = main()

        assert result == 0
        # In dry-run mode, file should not be modified
        assert html_file.read_text() == original

    def test_main_fixes_html_file(self, tmp_path: Path) -> None:
        """main() should fix HTML files in docs-dir."""
        from src.tools.fix_html_validation import main

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        html_file = docs_dir / "page.html"
        html_file.write_text("<button>Click</button>", encoding="utf-8")

        with patch.object(sys, "argv", ["fix_html_validation", "--docs-dir", str(docs_dir)]):
            result = main()

        assert result == 0
        content = html_file.read_text()
        assert 'type="button"' in content
