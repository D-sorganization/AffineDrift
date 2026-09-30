"""Tests for the search maturity index generator script (#4504)."""

from pathlib import Path
from types import SimpleNamespace

import scripts.generate_search_maturity_index as generate_search_maturity_index
from scripts.generate_search_maturity_index import build_index, variant_from_status


class TestVariantFromStatus:
    """Tests for deriving a CSS badge variant from a status string.

    Must match the derivation in scripts/filters/page-header-card.lua so the
    same status string always maps to the same `.badge--<variant>` class.
    """

    def test_lowercases_and_dashes_spaces(self):
        assert variant_from_status("Reviewed") == "reviewed"
        assert variant_from_status("In Review") == "in-review"

    def test_strips_non_alphanumeric_characters(self):
        assert variant_from_status("Draft!") == "draft"


class TestBuildIndex:
    """Tests for scanning front matter into a href -> maturity map."""

    def test_only_includes_pages_with_status_or_maturity(self, monkeypatch):
        pages = [
            Path("articles/has-status.qmd"),
            Path("articles/no-status.qmd"),
            Path("pages/has-maturity.qmd"),
        ]

        def fake_frontmatter(path):
            if path == Path("articles/has-status.qmd"):
                return "body", {"status": "Reviewed"}
            if path == Path("pages/has-maturity.qmd"):
                return "body", {"maturity": "Canonical"}
            return "body", {"title": "No status here"}

        monkeypatch.setattr(
            generate_search_maturity_index, "collect_qmd_files", lambda _dirs: pages
        )
        monkeypatch.setattr(
            generate_search_maturity_index, "read_qmd_with_frontmatter", fake_frontmatter
        )

        index = build_index(["articles", "pages"])

        assert index == {
            "articles/has-status.html": {"label": "Reviewed", "variant": "reviewed"},
            "pages/has-maturity.html": {"label": "Canonical", "variant": "canonical"},
        }

    def test_status_takes_precedence_over_maturity(self, monkeypatch):
        pages = [Path("articles/both.qmd")]

        monkeypatch.setattr(
            generate_search_maturity_index, "collect_qmd_files", lambda _dirs: pages
        )
        monkeypatch.setattr(
            generate_search_maturity_index,
            "read_qmd_with_frontmatter",
            lambda _path: ("body", {"status": "Reviewed", "maturity": "Draft"}),
        )

        index = build_index(["articles"])

        assert index["articles/both.html"]["label"] == "Reviewed"

    def test_index_maps_root_index_to_empty_string(self, monkeypatch):
        monkeypatch.setattr(
            generate_search_maturity_index, "collect_qmd_files", lambda _dirs: [Path("index.qmd")]
        )
        monkeypatch.setattr(
            generate_search_maturity_index,
            "read_qmd_with_frontmatter",
            lambda _path: ("body", {"status": "Canonical"}),
        )

        index = build_index(["."])

        assert index == {"": {"label": "Canonical", "variant": "canonical"}}


class TestGenerateSearchMaturityIndexMain:
    """End-to-end tests for the CLI entry point."""

    def test_main_writes_json_index(self, tmp_path, monkeypatch):
        pages = [Path("articles/reviewed.qmd")]

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(
            generate_search_maturity_index, "collect_qmd_files", lambda _dirs: pages
        )
        monkeypatch.setattr(
            generate_search_maturity_index,
            "read_qmd_with_frontmatter",
            lambda _path: ("body", {"status": "Reviewed"}),
        )
        monkeypatch.setattr(
            generate_search_maturity_index.argparse.ArgumentParser,
            "parse_args",
            lambda self: SimpleNamespace(output="public/search-maturity.json"),
        )

        generate_search_maturity_index.main()

        import json

        generated = json.loads((tmp_path / "public" / "search-maturity.json").read_text("utf-8"))
        assert generated == {"articles/reviewed.html": {"label": "Reviewed", "variant": "reviewed"}}


class TestDeployWorkflowWiring:
    """The deploy workflow must invoke the search maturity index generator."""

    def test_workflow_runs_search_maturity_generator(self):
        repo_root = Path(__file__).resolve().parent.parent
        workflow = (repo_root / ".github" / "workflows" / "deploy-website.yml").read_text(
            encoding="utf-8"
        )
        assert "scripts/generate_search_maturity_index.py" in workflow
