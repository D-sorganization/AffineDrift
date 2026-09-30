"""Print stylesheet consolidation contract (WEB-07.9 #4550).

`css/print.css` and `styles.css` previously defined two competing
`@media print` blocks, and the page size was hard-coded to A4. This enforces
a single print stylesheet that lets the printer/OS paper-size choice govern,
so both Letter and A4 work.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PRINT_CSS = REPO_ROOT / "css" / "print.css"
STYLES_CSS = REPO_ROOT / "styles.css"


def test_styles_css_has_no_competing_print_block() -> None:
    content = STYLES_CSS.read_text(encoding="utf-8")
    assert "@media print" not in content


def test_print_css_is_the_single_print_stylesheet() -> None:
    content = PRINT_CSS.read_text(encoding="utf-8")
    assert content.count("@media print") == 1


def test_print_css_retains_laymans_terms_print_rules() -> None:
    content = PRINT_CSS.read_text(encoding="utf-8")
    assert ".laymans-terms {" in content
    assert ".laymans-terms-header {" in content


def test_print_page_size_supports_letter_and_a4() -> None:
    """The @page rule must not force a4-only; let the printer/OS choose."""
    content = PRINT_CSS.read_text(encoding="utf-8")
    assert "size: a4" not in content
    assert "size: auto" in content
