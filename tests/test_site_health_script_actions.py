"""Keep Quarto script controls out of filesystem-link health checks."""

from pathlib import Path

import pytest
from bs4 import BeautifulSoup, Tag

from src.tools.check_site_health import SiteHealthLinkCandidate, check_site_health, main

SCRIPT_ACTIONS = (
    "javascript:void(0)",
    "JAVASCRIPT:void(0);",
    "   JavaScript:void(0)",
    "\tjavascript:window.print()",
)


@pytest.mark.parametrize("href", SCRIPT_ACTIONS)
def test_script_actions_are_not_file_candidates(tmp_path: Path, href: str) -> None:
    """Classify action links without interpreting or executing their scripts."""
    anchor = BeautifulSoup(f'<a href="{href}">Show All Code</a>', "html.parser").find("a")
    assert isinstance(anchor, Tag)
    candidate = SiteHealthLinkCandidate.from_anchor(
        anchor=anchor,
        source_file=Path("index.html"),
        docs_dir=tmp_path,
        ignore_quarto_alternate_formats=True,
    )
    assert candidate is None


@pytest.mark.parametrize("href", SCRIPT_ACTIONS)
def test_script_actions_do_not_fail_the_scan(tmp_path: Path, href: str) -> None:
    """The scanner shares the candidate API's case and whitespace handling."""
    (tmp_path / "index.html").write_text(f'<a href="{href}">Code</a>', encoding="utf-8")
    assert (
        check_site_health(
            docs_dir=tmp_path,
            fail_on={"broken"},
            ignore_quarto_alternate_formats=True,
        )
        == 0
    )


@pytest.mark.parametrize("include_missing", [False, True])
def test_quarto_menu_keeps_real_link_failures(
    tmp_path: Path, caplog: pytest.LogCaptureFixture, include_missing: bool
) -> None:
    """The deployed menu passes while an actual missing article still fails the CLI."""
    article_dir = tmp_path / "articles"
    article_dir.mkdir()
    controls = "".join(
        f'<a class="dropdown-item" href="javascript:void(0)">{label}</a>'
        for label in ("Show All Code", "Hide All Code", "View Source")
    )
    missing = '<a href="missing.html">Missing</a>' if include_missing else ""
    (article_dir / "chapter.html").write_text(
        controls + '<a href="../index.html">Home</a>' + missing, encoding="utf-8"
    )
    (tmp_path / "index.html").write_text(
        '<a href="articles/chapter.html">Chapter</a>', encoding="utf-8"
    )

    assert main(["--docs-dir", str(tmp_path), "--fail-on", "broken"]) == int(include_missing)
    assert "articles/javascript:" not in caplog.text
    if include_missing:
        assert "Found 1 broken links" in caplog.text
        assert "missing.html" in caplog.text
