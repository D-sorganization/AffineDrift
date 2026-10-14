"""Verify link targets added for Deploy Website resolution (issue #5065)."""

from pathlib import Path

from src.tools.check_links import check_links


def test_scope_and_limits_page_exists_and_contains_maturity_key() -> None:
    """Verify pages/scope-and-limits.qmd exists and has the required maturity-key anchor."""
    page_path = Path("pages/scope-and-limits.qmd")
    assert page_path.exists(), "pages/scope-and-limits.qmd must exist"
    content = page_path.read_text(encoding="utf-8")
    assert "{#maturity-key}" in content, "scope-and-limits must define #maturity-key anchor"
    assert 'title: "Scope and Limits"' in content


def test_golf_control_theory_page_exists() -> None:
    """Verify pages/Golf_Control_Theory.qmd exists with correct metadata."""
    page_path = Path("pages/Golf_Control_Theory.qmd")
    assert page_path.exists(), "pages/Golf_Control_Theory.qmd must exist"
    content = page_path.read_text(encoding="utf-8")
    assert 'title: "Golf Control Theory Notes"' in content
    assert "Control-Affine" in content


def test_index_qmd_has_no_broken_internal_links() -> None:
    """Verify that index.qmd has no broken internal links."""
    broken = check_links(".")
    index_broken = [b for b in broken if "index.qmd" in b[0]]
    assert index_broken == [], f"index.qmd contains broken links: {index_broken}"
