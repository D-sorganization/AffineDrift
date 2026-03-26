"""Extended tests for src.tools.publish_manual_article — main() coverage."""

from __future__ import annotations

from pathlib import Path

import pytest


class TestPublishManualArticleMainPaths:
    """Cover main() paths that require qmd + template to exist."""

    def test_main_exits_1_when_template_missing(self, tmp_path: Path) -> None:
        """main() should exit 1 when template file is missing (qmd exists, template doesn't)."""
        import os

        from src.tools.publish_manual_article import main

        # Create the articles directory and qmd file
        articles_dir = tmp_path / "articles"
        articles_dir.mkdir()
        qmd_file = articles_dir / "intentional-constraint-collapse.qmd"
        qmd_file.write_text(
            '---\ntitle: "Test"\ndescription: "Desc"\n---\nBody content.',
            encoding="utf-8",
        )
        # No template file — main() should exit 1
        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1
        finally:
            os.chdir(original)

    def test_main_publishes_article_when_all_files_present(self, tmp_path: Path) -> None:
        """main() should publish article when qmd + template both exist."""
        import os

        from src.tools.publish_manual_article import main

        # Create the full expected directory structure
        articles_dir = tmp_path / "articles"
        articles_dir.mkdir()
        docs_articles = tmp_path / "docs" / "articles"
        docs_articles.mkdir(parents=True)

        qmd_file = articles_dir / "intentional-constraint-collapse.qmd"
        qmd_file.write_text(
            '---\ntitle: "Test Article"\ndescription: "A test"\n---\nBody content.',
            encoding="utf-8",
        )

        # Create a minimal template file
        template_file = tmp_path / "docs" / "articles.html"
        template_file.write_text(
            "<html><head><title>Old Title</title>"
            '<meta name="description" content="old">'
            '</head><body><section class="article-section">old</section></body></html>',
            encoding="utf-8",
        )

        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            # Should not raise — publishes the article
            main()
            output = docs_articles / "intentional-constraint-collapse.html"
            assert output.exists()
        finally:
            os.chdir(original)
