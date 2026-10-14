"""Tests for Design System Audit, Reset Removal, and Component Gallery (#4553)."""

from __future__ import annotations

import re
from pathlib import Path

from scripts.check_title_case import findings_for_text

REPO_ROOT = Path(__file__).resolve().parent.parent
STYLES_CSS = REPO_ROOT / "styles.css"
GALLERY_MD = REPO_ROOT / "docs" / "development" / "design-system-component-gallery.md"


class TestStylesCssReset:
    """Verifies that the global reset in styles.css respects Bootstrap spacing."""

    def test_global_star_does_not_reset_margin_and_padding(self) -> None:
        """The global * selector must not zero margin or padding (#4553)."""
        content = STYLES_CSS.read_text(encoding="utf-8")

        # Match any rule block starting with a lone `* {` that declares margin or padding 0
        naked_star_reset = re.search(
            r"^\s*\*\s*\{[^}]*(?:margin:\s*0|padding:\s*0)[^}]*\}",
            content,
            re.MULTILINE,
        )
        assert naked_star_reset is None, (
            f"styles.css must not contain a global * margin/padding reset: "
            f"{naked_star_reset.group(0) if naked_star_reset else ''}"
        )

    def test_box_sizing_border_box_is_retained(self) -> None:
        """Universal selector and pseudo-elements must retain box-sizing: border-box."""
        content = STYLES_CSS.read_text(encoding="utf-8")

        # Match *, *::before, *::after box-sizing declaration
        box_sizing_pattern = re.search(
            r"\*,\s*\*::before,\s*\*::after\s*\{\s*box-sizing:\s*border-box;\s*\}",
            content,
        )
        assert (
            box_sizing_pattern is not None
        ), "styles.css must declare box-sizing: border-box on *, *::before, *::after"


class TestDesignSystemComponentGalleryDocumentation:
    """Verifies existence, completeness, and title casing of the component gallery."""

    def test_gallery_file_exists_and_is_non_empty(self) -> None:
        """The gallery markdown document must exist under docs/development/."""
        assert GALLERY_MD.exists(), f"Missing expected file: {GALLERY_MD}"
        assert GALLERY_MD.stat().st_size > 0, "Gallery markdown file must not be empty"

    def test_gallery_documents_core_token_files(self) -> None:
        """Gallery must document all core token architecture files."""
        content = GALLERY_MD.read_text(encoding="utf-8")
        core_tokens = [
            "colors.css",
            "typography.css",
            "spacing.css",
            "breakpoints.css",
        ]
        for token_file in core_tokens:
            assert token_file in content, f"Gallery must document token file: {token_file}"

    def test_gallery_documents_component_primitives(self) -> None:
        """Gallery must document core component primitives."""
        content = GALLERY_MD.read_text(encoding="utf-8")
        core_primitives = [
            "site-card",
            "status-badge",
            "laymans-terms",
            "caveats-block",
        ]
        for primitive in core_primitives:
            assert primitive in content, f"Gallery must document component primitive: {primitive}"

    def test_gallery_documents_additional_required_primitives_and_policies(self) -> None:
        """Gallery must document extended primitives, @media literal-px rule, and CSS budgets."""
        content = GALLERY_MD.read_text(encoding="utf-8")
        extended_topics = [
            "site-button",
            "callouts",
            "golfers-coaches-box",
            "page-header-card",
            "scientific-trust-panel",
            "drift-plus-control",
            "#3326",
            "max_lines: 3400",
            "max_important: 10",
        ]
        for topic in extended_topics:
            assert topic in content, f"Gallery must document topic: {topic}"

    def test_gallery_headings_conform_to_title_case(self) -> None:
        """All headings in the gallery file must strictly conform to project title case."""
        content = GALLERY_MD.read_text(encoding="utf-8")
        findings = findings_for_text(GALLERY_MD.relative_to(REPO_ROOT), content)
        violations = [
            f"Line {f.line} ({f.kind}): '{f.actual}' -> expected '{f.expected}'" for f in findings
        ]
        assert violations == [], f"Found title case violations in {GALLERY_MD}:\n" + "\n".join(
            violations
        )
