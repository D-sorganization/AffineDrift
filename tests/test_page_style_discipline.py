"""Per-page style discipline (EPIC #3140 Phase C).

This file is the live punch list for the page-by-page cleanup. As each
page is migrated off inline styles / gradients / hardcoded hex, add its
path to ``CLEAN_PAGES``. The test then guards against regressions on
that page going forward. Pages not yet in ``CLEAN_PAGES`` are tracked in
``PENDING_PAGES`` so the test suite tells us at a glance how much work
remains.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_style_discipline import (
    StyleDisciplineConfig,
    check_repository,
    find_violations_in_text,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

# Pages that have been swept clean of all forbidden patterns. Add new
# entries to this list (relative to repo root) once a cleanup PR ships.
CLEAN_PAGES: tuple[str, ...] = (
    "index.qmd",
    "pages/about.qmd",
    "pages/collaborate.qmd",
    "pages/contact.qmd",
    "pages/overview.qmd",
    "pages/tools.qmd",
    "pages/book-reviews.qmd",
    "pages/daydreams-doodles.qmd",
    "pages/drifter-manifesto.qmd",
    "resources/articles.qmd",
    "resources/bibliography.qmd",
    "resources/research-reviews.qmd",
    "resources/resources-books.qmd",
    "resources/resources-datasets.qmd",
    "resources/resources-notebooklm.qmd",
    "resources/resources-papers.qmd",
    "resources/resources-researchers.qmd",
    "resources/resources-software.qmd",
    "resources/resources-videos.qmd",
    "resources/resources-websites.qmd",
    "resources/resources.qmd",
    "models/models.qmd",
    "models/models-drake.qmd",
    "models/models-mujoco.qmd",
    "models/models-myosim.qmd",
    "models/models-opensim.qmd",
    "models/models-pendulum.qmd",
    "models/models-pinocchio.qmd",
    "models/models-simulink.qmd",
    "repositories/repositories.qmd",
    "books/index.qmd",
    "critiques/index.qmd",
)


@pytest.mark.parametrize("rel_path", CLEAN_PAGES)
class TestCleanPagesStayClean:
    """A page on the clean list must continue to pass every rule."""

    def test_page_exists(self, rel_path: str) -> None:
        assert (REPO_ROOT / rel_path).is_file(), f"CLEAN_PAGES references missing file: {rel_path}"

    def test_no_inline_style(self, rel_path: str) -> None:
        text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
        offenders = [
            v for v in find_violations_in_text(text, suffix=".qmd") if v.rule == "inline-style"
        ]
        assert offenders == [], (
            f"{rel_path}: inline style= at line(s) " f"{[v.line for v in offenders[:5]]}"
        )

    def test_no_linear_gradient(self, rel_path: str) -> None:
        text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
        offenders = [
            v for v in find_violations_in_text(text, suffix=".qmd") if v.rule == "gradient"
        ]
        assert offenders == [], (
            f"{rel_path}: linear/radial gradient at line(s) " f"{[v.line for v in offenders[:5]]}"
        )

    def test_no_hardcoded_hex(self, rel_path: str) -> None:
        text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
        offenders = [
            v for v in find_violations_in_text(text, suffix=".qmd") if v.rule == "hardcoded-hex"
        ]
        assert offenders == [], (
            f"{rel_path}: hardcoded hex at line(s) "
            f"{[v.line for v in offenders[:5]]}: "
            f"{offenders[0].snippet if offenders else ''}"
        )


def test_top_level_pages_pass_discipline_check() -> None:
    """End-to-end: the discipline checker is happy with the QMD scope."""
    config = StyleDisciplineConfig(
        repo_root=REPO_ROOT,
        css_globs=(),  # CSS hygiene tracked separately in B1/B4.
    )
    violations = check_repository(config)
    if violations:
        msg = "\n".join(v.format() for v in violations[:25])
        pytest.fail(
            f"{len(violations)} style-discipline violation(s) in top-level "
            f"QMD pages. First 25:\n{msg}"
        )
