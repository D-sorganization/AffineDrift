"""Tests for check_scaffolding_styling.py (WEB-02.6 / #4500).

Enforces:
1. Scaffolding/stub pages must never use success styling (status-banner--success,
   callout-success, alert-success, status-pill--success, status-badge--success).
2. No hub card links to a page under 300 words unless it carries a Planned badge.
"""

from __future__ import annotations

from pathlib import Path

from scripts.check_scaffolding_styling import (
    check_hub_cards,
    check_scaffolding_styling,
    count_prose_words,
    is_scaffolding_page,
    run_checks,
)


class TestCountProseWords:
    """Verifying word count and include expansion logic."""

    def test_counts_words_in_simple_qmd(self, tmp_path: Path) -> None:
        file = tmp_path / "test.qmd"
        file.write_text(
            "---\ntitle: 'Test Page'\ndescription: 'Five descriptive header words here'\n---\n\n"
            "This is a paragraph with exactly eight more words.\n",
            encoding="utf-8",
        )
        # description has 5; body has 9 -> 14
        assert count_prose_words(file) == 14

    def test_expands_includes_recursively(self, tmp_path: Path) -> None:
        inc = tmp_path / "_inc.qmd"
        inc.write_text("Included fragment containing six words here.", encoding="utf-8")

        main_file = tmp_path / "main.qmd"
        main_file.write_text(
            "---\ntitle: 'Main'\n---\nMain file introductory sentence.\n\n"
            "{{< include _inc.qmd >}}\n",
            encoding="utf-8",
        )
        # 4 words in main + 6 words in included = 10 words
        assert count_prose_words(main_file) == 10

    def test_handles_circular_includes_gracefully(self, tmp_path: Path) -> None:
        file_a = tmp_path / "a.qmd"
        file_b = tmp_path / "b.qmd"
        file_a.write_text("Alpha one two. {{< include b.qmd >}}", encoding="utf-8")
        file_b.write_text("Beta three four. {{< include a.qmd >}}", encoding="utf-8")

        count = count_prose_words(file_a)
        assert count == 6  # Alpha one two (3) + Beta three four (3)


class TestIsScaffoldingPage:
    """Detecting designated or indicator-marked scaffolding pages."""

    def test_explicit_pages_are_recognized(self) -> None:
        assert is_scaffolding_page("resources/research-reviews.qmd", "")
        assert is_scaffolding_page("pages/book-reviews.qmd", "")

    def test_content_indicators_are_recognized(self) -> None:
        assert is_scaffolding_page(
            "custom.qmd",
            "Status: In Progress (Scaffolding Phase — Expected: 2026-Q4)",
        )
        assert is_scaffolding_page("custom.qmd", "Status: Planned")

    def test_completed_pages_are_not_scaffolding(self) -> None:
        assert not is_scaffolding_page(
            "articles/theory-part1.qmd", "Status: Complete and verified."
        )


class TestCheckScaffoldingStyling:
    """Ensuring scaffolding pages never use success styling."""

    def test_rejects_success_banner_on_scaffolding_page(self, tmp_path: Path) -> None:
        file = tmp_path / "resources" / "research-reviews.qmd"
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(
            '---\ntitle: "Reviews"\n---\n<div class="status-banner status-banner--success">Good</div>',
            encoding="utf-8",
        )
        violations = check_scaffolding_styling(tmp_path)
        assert len(violations) == 1
        assert violations[0].rule == "scaffolding-no-success-styling"

    def test_allows_warning_banner_on_scaffolding_page(self, tmp_path: Path) -> None:
        file = tmp_path / "resources" / "research-reviews.qmd"
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(
            '---\ntitle: "Reviews"\n---\n<div class="status-banner status-banner--warning">Stub</div>',
            encoding="utf-8",
        )
        violations = check_scaffolding_styling(tmp_path)
        assert len(violations) == 0


class TestCheckHubCards:
    """Ensuring hub cards link to substantive content or carry a Planned badge."""

    def test_rejects_stub_target_without_planned_badge(self, tmp_path: Path) -> None:
        hub_dir = tmp_path / "pages"
        hub_dir.mkdir(parents=True, exist_ok=True)
        hub = hub_dir / "tools.qmd"
        target = hub_dir / "stub.qmd"
        target.write_text("---\ntitle: 'Stub'\n---\nShort stub.\n", encoding="utf-8")
        hub.write_text(
            '<div class="card">\n<h3><a href="stub.html">Stub Title</a></h3>\n</div>\n',
            encoding="utf-8",
        )
        violations = check_hub_cards(tmp_path)
        assert len(violations) == 1
        assert violations[0].rule == "hub-card-stub-needs-planned-badge"

    def test_allows_stub_target_with_planned_badge(self, tmp_path: Path) -> None:
        hub_dir = tmp_path / "pages"
        hub_dir.mkdir(parents=True, exist_ok=True)
        hub = hub_dir / "tools.qmd"
        target = hub_dir / "stub.qmd"
        target.write_text("---\ntitle: 'Stub'\n---\nShort stub.\n", encoding="utf-8")
        hub.write_text(
            '<div class="card">\n'
            '<span class="status-badge status-badge--planned">Planned</span>\n'
            '<h3><a href="stub.html">Stub Title</a></h3>\n'
            "</div>\n",
            encoding="utf-8",
        )
        violations = check_hub_cards(tmp_path)
        assert len(violations) == 0

    def test_allows_substantive_target_without_badge(self, tmp_path: Path) -> None:
        hub_dir = tmp_path / "pages"
        hub_dir.mkdir(parents=True, exist_ok=True)
        hub = hub_dir / "tools.qmd"
        target = hub_dir / "article.qmd"
        # 350 words
        target.write_text(
            "---\ntitle: 'Article'\n---\n" + (" substantive word" * 350) + "\n",
            encoding="utf-8",
        )
        hub.write_text(
            '<div class="card">\n<h3><a href="article.html">Article Title</a></h3>\n</div>\n',
            encoding="utf-8",
        )
        violations = check_hub_cards(tmp_path)
        assert len(violations) == 0

    def test_allows_utility_page(self, tmp_path: Path) -> None:
        pages_dir = tmp_path / "pages"
        pages_dir.mkdir(parents=True, exist_ok=True)
        hub = pages_dir / "collaborate.qmd"
        contact = pages_dir / "contact.qmd"
        contact.write_text("---\ntitle: 'Contact'\n---\nContact form.\n", encoding="utf-8")
        hub.write_text(
            '<div class="card">\n<h3><a href="contact.html">Contact Us</a></h3>\n</div>\n',
            encoding="utf-8",
        )
        violations = check_hub_cards(tmp_path)
        assert len(violations) == 0


class TestRepositoryClean:
    """Verifying clean run against the actual repository tree."""

    def test_clean_repository(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        violations = run_checks(repo_root)
        assert violations == []
