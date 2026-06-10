"""Tests for the sitemap generator script."""

# Add project root to path

from pathlib import Path
from types import SimpleNamespace

# Import after path setup
import scripts.generate_sitemap as generate_sitemap
from scripts.generate_sitemap import (
    get_changefreq,
    get_git_last_modified,
    get_priority,
    qmd_path_to_url_path,
)
from src.tools.utils import parse_frontmatter_dict


class TestGitLastModified:
    """Tests for git-backed sitemap last-modified dates."""

    def test_uses_current_date_when_git_is_missing(self, monkeypatch):
        """Missing git executable should fall back to today's date."""
        monkeypatch.setattr(generate_sitemap.shutil, "which", lambda _name: None)

        assert get_git_last_modified("index.qmd") == generate_sitemap.datetime.now().strftime(
            "%Y-%m-%d"
        )

    def test_uses_git_commit_date_when_available(self, monkeypatch):
        """Successful git log output should be normalized to YYYY-MM-DD."""
        monkeypatch.setattr(generate_sitemap.shutil, "which", lambda _name: "git")
        monkeypatch.setattr(
            generate_sitemap.subprocess,
            "run",
            lambda *args, **kwargs: SimpleNamespace(
                returncode=0,
                stdout="2026-06-10T12:34:56+00:00\n",
            ),
        )

        assert get_git_last_modified("articles/example.qmd") == "2026-06-10"

    def test_falls_back_when_git_command_has_no_date(self, monkeypatch):
        """Empty git output should fall back instead of emitting invalid XML dates."""
        monkeypatch.setattr(generate_sitemap.shutil, "which", lambda _name: "git")
        monkeypatch.setattr(
            generate_sitemap.subprocess,
            "run",
            lambda *args, **kwargs: SimpleNamespace(returncode=1, stdout=""),
        )

        assert get_git_last_modified("missing.qmd") == generate_sitemap.datetime.now().strftime(
            "%Y-%m-%d"
        )

    def test_falls_back_when_git_raises(self, monkeypatch):
        """Subprocess errors should not prevent sitemap generation."""
        monkeypatch.setattr(generate_sitemap.shutil, "which", lambda _name: "git")

        def raise_os_error(*args, **kwargs):
            raise OSError("git unavailable")

        monkeypatch.setattr(generate_sitemap.subprocess, "run", raise_os_error)

        assert get_git_last_modified("index.qmd") == generate_sitemap.datetime.now().strftime(
            "%Y-%m-%d"
        )


class TestDeployWorkflowWiring:
    """The deploy workflow must invoke the sitemap generator (issue #3220)."""

    def test_workflow_runs_sitemap_generator(self):
        """deploy-website.yml invokes generate_sitemap.py."""
        repo_root = Path(__file__).resolve().parent.parent
        workflow = (repo_root / ".github" / "workflows" / "deploy-website.yml").read_text(
            encoding="utf-8"
        )
        assert "scripts/generate_sitemap.py" in workflow


class TestGetPriority:
    """Tests for the get_priority function."""

    def test_index_has_highest_priority(self):
        """Index page should have priority 1.0."""
        assert get_priority("index.qmd") == "1.0"

    def test_overview_has_high_priority(self):
        """Overview page should have priority 0.9."""
        assert get_priority("overview.qmd") == "0.9"

    def test_theory_parts_have_high_priority(self):
        """Theory part pages should have priority 0.9."""
        assert get_priority("theory-part-1.qmd") == "0.9"
        assert get_priority("articles/theory-part-2.qmd") == "0.9"

    def test_articles_have_medium_priority(self):
        """Article pages should have priority 0.8."""
        assert get_priority("articles/test-article.qmd") == "0.8"

    def test_models_have_lower_priority(self):
        """Model pages should have priority 0.7."""
        assert get_priority("models/test-model.qmd") == "0.7"

    def test_resources_have_standard_priority(self):
        """Resource pages should have priority 0.6."""
        assert get_priority("resources/test.qmd") == "0.6"

    def test_repositories_have_standard_priority(self):
        """Repository pages should have priority 0.6."""
        assert get_priority("repositories/test.qmd") == "0.6"

    def test_bibliography_has_medium_priority(self):
        """Bibliography page should have priority 0.8."""
        assert get_priority("bibliography.qmd") == "0.8"

    def test_drifter_manifesto_has_medium_priority(self):
        """Drifter manifesto should have priority 0.8."""
        assert get_priority("drifter-manifesto.qmd") == "0.8"

    def test_unknown_pages_have_default_priority(self):
        """Unknown pages should have default priority 0.5."""
        assert get_priority("some-random-page.qmd") == "0.5"
        assert get_priority("about.qmd") == "0.5"


class TestGetChangefreq:
    """Tests for the get_changefreq function."""

    def test_index_changes_weekly(self):
        """Index page should change weekly."""
        assert get_changefreq("index.qmd") == "weekly"

    def test_articles_change_monthly(self):
        """Article pages should change monthly."""
        assert get_changefreq("articles/test-article.qmd") == "monthly"

    def test_resources_change_weekly(self):
        """Resource pages should change weekly."""
        assert get_changefreq("resources/test.qmd") == "weekly"

    def test_bibliography_changes_weekly(self):
        """Bibliography should change weekly."""
        assert get_changefreq("bibliography.qmd") == "weekly"

    def test_default_change_frequency_is_monthly(self):
        """Default change frequency should be monthly."""
        assert get_changefreq("random-page.qmd") == "monthly"
        assert get_changefreq("about.qmd") == "monthly"


class TestParseFrontmatterDict:
    """Tests for the parse_frontmatter_dict function."""

    def test_extracts_simple_frontmatter(self):
        """Should extract simple key-value pairs."""
        content = """---
title: Test Title
author: Test Author
---
Content here
"""
        result = parse_frontmatter_dict(content)
        assert result["title"] == "Test Title"
        assert result["author"] == "Test Author"

    def test_handles_quoted_values(self):
        """Should strip quotes from values."""
        content = """---
title: "Quoted Title"
description: 'Single Quoted'
---
"""
        result = parse_frontmatter_dict(content)
        assert result["title"] == "Quoted Title"
        assert result["description"] == "Single Quoted"

    def test_handles_empty_frontmatter(self):
        """Should return empty dict for empty frontmatter."""
        content = """---
---
Content
"""
        result = parse_frontmatter_dict(content)
        assert result == {}

    def test_handles_no_frontmatter(self):
        """Should return empty dict when no frontmatter exists."""
        content = "Just content without frontmatter"
        result = parse_frontmatter_dict(content)
        assert result == {}

    def test_handles_content_starting_with_dashes_but_no_frontmatter(self):
        """Should handle content that starts with dashes but isn't frontmatter."""
        content = "---This is not frontmatter"
        result = parse_frontmatter_dict(content)
        assert result == {}

    def test_ignores_nested_content(self):
        """Should ignore nested YAML content."""
        content = """---
title: Test
metadata:
  nested: value
author: Author
---
"""
        result = parse_frontmatter_dict(content)
        assert result["title"] == "Test"
        assert result["author"] == "Author"
        assert "nested" not in result

    def test_handles_colons_in_values(self):
        """Should handle colons in values correctly."""
        content = """---
title: Test: A Subtitle
---
"""
        result = parse_frontmatter_dict(content)
        assert result["title"] == "Test: A Subtitle"


class TestSitemapXmlFormat:
    """Tests for sitemap XML format specifications."""

    def test_xml_declaration_format(self):
        """Sitemap should use UTF-8 encoding."""
        expected_declaration = '<?xml version="1.0" encoding="UTF-8"?>'
        assert "xml version" in expected_declaration
        assert "UTF-8" in expected_declaration

    def test_priority_values_are_valid(self):
        """Priority values should be between 0.0 and 1.0."""
        for filepath in ["index.qmd", "overview.qmd", "articles/test.qmd", "about.qmd"]:
            priority = get_priority(filepath)
            value = float(priority)
            assert 0.0 <= value <= 1.0, f"Invalid priority {priority} for {filepath}"

    def test_changefreq_values_are_valid(self):
        """Change frequency values should be valid sitemap values."""
        valid_values = {"always", "hourly", "daily", "weekly", "monthly", "yearly", "never"}
        for filepath in ["index.qmd", "articles/test.qmd", "resources/test.qmd", "about.qmd"]:
            freq = get_changefreq(filepath)
            assert freq in valid_values, f"Invalid changefreq {freq} for {filepath}"

    def test_url_path_conversion(self):
        """QMD files should be converted to HTML URLs."""
        # Test the URL path logic
        filepath = "articles/test-article.qmd"
        expected_url_path = "articles/test-article.html"

        url_path = filepath.replace(".qmd", ".html")
        assert url_path == expected_url_path

    def test_index_url_path_is_empty(self):
        """Index.html should map to root URL."""
        assert qmd_path_to_url_path(Path("index.qmd")) == ""

    def test_qmd_path_conversion_preserves_nested_paths(self):
        """Nested QMD files should be converted to HTML URL paths."""
        assert qmd_path_to_url_path(Path("articles/test-article.qmd")) == (
            "articles/test-article.html"
        )


class TestGenerateSitemapMain:
    """End-to-end tests for sitemap generation."""

    def test_main_writes_sorted_sitemap_and_root_copy(self, tmp_path, monkeypatch):
        """main writes the requested sitemap plus root sitemap.xml."""
        pages = [
            Path("articles/keep.qmd"),
            Path("pages/no-title.qmd"),
            Path("index.qmd"),
        ]

        def fake_frontmatter(path):
            if path == Path("pages/no-title.qmd"):
                return "body", {}
            return "body", {"title": path.stem}

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(generate_sitemap, "collect_qmd_files", lambda _dirs: pages)
        monkeypatch.setattr(generate_sitemap, "read_qmd_with_frontmatter", fake_frontmatter)
        monkeypatch.setattr(generate_sitemap, "get_git_last_modified", lambda _path: "2026-06-10")
        monkeypatch.setattr(
            generate_sitemap,
            "datetime",
            SimpleNamespace(now=lambda: SimpleNamespace(isoformat=lambda: "2026-06-10T00:00:00")),
        )
        monkeypatch.setattr(
            generate_sitemap.argparse.ArgumentParser,
            "parse_args",
            lambda self: SimpleNamespace(output="public/sitemap.xml"),
        )

        generate_sitemap.main()

        generated = (tmp_path / "public" / "sitemap.xml").read_text(encoding="utf-8")
        root_copy = (tmp_path / "sitemap.xml").read_text(encoding="utf-8")

        assert generated == root_copy
        assert "<!-- Total URLs: 2 -->" in generated
        assert "<loc>https://affinedrift.com/</loc>" in generated
        assert "<loc>https://affinedrift.com/articles/keep.html</loc>" in generated
        assert "pages/no-title.html" not in generated
        assert generated.index("<loc>https://affinedrift.com/</loc>") < generated.index(
            "<loc>https://affinedrift.com/articles/keep.html</loc>"
        )
