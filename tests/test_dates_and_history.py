"""Tests for Real Dates and Per-Article Change History (WEB-07.3 #4545).

Enforces:
1. Zero `date: today` in any rendered QMD source.
2. Every emitted `date` has a recorded verification source (`date-source:`).
3. Revision history (`changes:`) appears on core pages.
4. Revision history Lua filter renders accessible semantic HTML.
5. CSS and print stylesheet registration.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from src.tools.utils.frontmatter import split_frontmatter

ROOT = Path(__file__).resolve().parents[1]
ARTICLES_DIR = ROOT / "articles"

CORE_PAGES = [
    "articles/theory-part1.qmd",
    "articles/theory-part2.qmd",
    "articles/theory-part3.qmd",
    "articles/theory-part4.qmd",
    "articles/theory-part5.qmd",
    "articles/drifter-manifesto.qmd",
    "articles/degrees-of-freedom-and-dimensionality.qmd",
    "articles/zero-torque-counterfactual.qmd",
    "articles/passive-distributed-control.qmd",
    "articles/superposition.qmd",
]

VALID_DATE_SOURCES = {
    "initial-publication-record",
    "archive-record",
    "editorial-board-review",
    "manuscript-release-record",
    "unverified",
}

DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def get_all_qmd_files() -> list[Path]:
    """Return all tracked/renderable QMD files in the project."""
    files = []
    for path in ROOT.glob("**/*.qmd"):
        # Exclude build, cache, temp, or git directories
        if any(
            part in path.parts
            for part in [
                ".git",
                "node_modules",
                "_site",
                "docs",
                ".quarto",
                "build",
                "proximal_distal_energy_transfer",
            ]
        ):
            continue
        files.append(path)
    return sorted(files)


class TestRealDatesContract:
    """Zero `date: today` and mandatory verification source for all dates."""

    def test_zero_date_today_in_all_sources(self) -> None:
        """Zero `date: today` in any QMD source across the repository."""
        offending_files: list[str] = []
        for path in get_all_qmd_files():
            content = path.read_text(encoding="utf-8")
            fm, _ = split_frontmatter(content)
            date_val = str(fm.get("date", "")).strip().lower()
            if date_val == "today":
                offending_files.append(str(path.relative_to(ROOT)).replace("\\", "/"))

        assert not offending_files, (
            f"Found {len(offending_files)} file(s) with 'date: today'. "
            f"Dates must be verified with date-source or marked 'Date unverified':\n"
            + "\n".join(f"  - {f}" for f in offending_files)
        )

    def test_every_emitted_date_has_verification_source(self) -> None:
        """Every file with a `date:` field must have a valid `date-source:`."""
        missing_source: list[str] = []
        invalid_source: list[str] = []

        for path in get_all_qmd_files():
            content = path.read_text(encoding="utf-8")
            fm, _ = split_frontmatter(content)
            if "date" not in fm:
                continue

            date_val = fm["date"]
            date_str = str(date_val).strip()
            date_source = fm.get("date-source")

            rel_path = str(path.relative_to(ROOT)).replace("\\", "/")

            if not date_source:
                missing_source.append(f"{rel_path}: date='{date_str}' but missing date-source")
                continue

            date_source_str = str(date_source).strip()

            if date_str.lower() in ("date unverified", "unverified"):
                if date_source_str != "unverified":
                    invalid_source.append(
                        f"{rel_path}: date is unverified but date-source is '{date_source_str}'"
                    )
            elif DATE_REGEX.match(date_str) or hasattr(date_val, "strftime"):
                if date_source_str not in VALID_DATE_SOURCES:
                    invalid_source.append(
                        f"{rel_path}: date='{date_str}' has unrecognized date-source '{date_source_str}'"
                    )
                elif date_source_str == "unverified":
                    invalid_source.append(
                        f"{rel_path}: concrete date='{date_str}' cannot have date-source='unverified'"
                    )

        assert not missing_source, (
            f"Found {len(missing_source)} file(s) with emitted date but missing date-source:\n"
            + "\n".join(f"  - {m}" for m in missing_source)
        )
        assert (
            not invalid_source
        ), f"Found {len(invalid_source)} file(s) with invalid date-source pairing:\n" + "\n".join(
            f"  - {i}" for i in invalid_source
        )


class TestCorePagesRevisionHistory:
    """Core pages carry structured revision history."""

    @pytest.mark.parametrize("rel_path", CORE_PAGES)
    def test_core_page_has_revision_history(self, rel_path: str) -> None:
        path = ROOT / rel_path
        assert path.is_file(), f"Core page {rel_path} does not exist"

        content = path.read_text(encoding="utf-8")
        fm, _ = split_frontmatter(content)

        assert "changes" in fm, f"{rel_path} is missing 'changes:' front matter"
        changes = fm["changes"]
        assert isinstance(changes, list), f"{rel_path} 'changes:' must be a list"
        assert len(changes) >= 1, f"{rel_path} 'changes:' must have at least one entry"

        for idx, entry in enumerate(changes):
            assert isinstance(entry, dict), f"{rel_path} changes[{idx}] must be a dict"
            assert "date" in entry, f"{rel_path} changes[{idx}] missing 'date'"
            assert (
                "description" in entry or "summary" in entry
            ), f"{rel_path} changes[{idx}] missing 'description' or 'summary'"
            date_str = str(entry["date"]).strip()
            assert DATE_REGEX.match(date_str) or hasattr(
                entry["date"], "strftime"
            ), f"{rel_path} changes[{idx}] date '{date_str}' is not YYYY-MM-DD"


class TestRevisionHistoryRendering:
    """Lua filter and stylesheet integration."""

    def test_filter_renders_revision_history_section(self) -> None:
        """Pandoc Lua filter renders changes into an accessible section."""
        filter_path = ROOT / "scripts" / "filters" / "revision-history.lua"
        assert filter_path.is_file(), "scripts/filters/revision-history.lua must exist"

        sample_qmd = (
            "---\n"
            'title: "Test"\n'
            "changes:\n"
            '  - date: "2026-09-29"\n'
            '    description: "Added critique annotations."\n'
            '  - date: "2026-08-20"\n'
            '    description: "Standardized definitions."\n'
            "---\n\n"
            "Main body paragraph.\n\n"
            "::: {#references}\n## References\n:::\n"
        )

        pandoc_bin = shutil.which("pandoc")
        if pandoc_bin is None:
            pytest.skip("Pandoc is required for the revision-history rendering check")
        res = subprocess.run(
            [
                pandoc_bin,
                "-f",
                "markdown",
                "-t",
                "html",
                "--wrap=none",
                "--lua-filter",
                str(filter_path),
            ],
            input=sample_qmd,
            capture_output=True,
            text=True,
            check=True,
        )

        html = res.stdout
        assert '<section id="revision-history"' in html or '<div id="revision-history"' in html
        assert "Revision History</h2>" in html
        assert '<span class="revision-history-date">2026-09-29</span>' in html
        assert "Added critique annotations." in html
        assert '<span class="revision-history-date">2026-08-20</span>' in html
        assert "Standardized definitions." in html

    def test_filter_registered_in_quarto_yml(self) -> None:
        """_quarto.yml includes scripts/filters/revision-history.lua."""
        quarto_yml = (ROOT / "_quarto.yml").read_text(encoding="utf-8")
        assert "scripts/filters/revision-history.lua" in quarto_yml

    def test_css_imported_in_styles_css(self) -> None:
        """css/components/revision-history.css exists and is imported."""
        css_file = ROOT / "css" / "components" / "revision-history.css"
        assert css_file.is_file(), "css/components/revision-history.css must exist"
        styles_css = (ROOT / "styles.css").read_text(encoding="utf-8")
        assert "css/components/revision-history.css" in styles_css

    def test_print_stylesheet_has_avoid_break_rule(self) -> None:
        """css/print.css includes .revision-history rule avoiding page breaks."""
        print_css = (ROOT / "css" / "print.css").read_text(encoding="utf-8")
        assert ".revision-history" in print_css
        assert "break-inside: avoid" in print_css
