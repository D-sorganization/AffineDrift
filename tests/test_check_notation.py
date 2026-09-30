"""Tests for the $G(x)$ notation gate (issue #4582).

NOTATION.md reserves lowercase $g$ for gravity and requires uppercase $G(x)$
for the control-affine input map. The gate is only worth having if it fails on
a reintroduced lowercase $g(x)$, so most of these construct a violation and
assert it is caught.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_notation import BANNED, REPO_ROOT, key, main, scan

pytestmark = pytest.mark.content_lint


def write(root: Path, relative: str, body: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


class TestScan:
    def test_clean_uppercase_notation_passes(self, tmp_path: Path) -> None:
        write(tmp_path, "articles/ch.qmd", "$$\\dot{x} = f(x) + G(x)u$$\n")
        assert scan(tmp_path) == []

    def test_lowercase_input_map_is_detected(self, tmp_path: Path) -> None:
        write(tmp_path, "articles/ch.qmd", "$$\\dot{x} = f(x) + g(x)u$$\n")
        findings = scan(tmp_path)
        assert len(findings) == 1
        assert findings[0]["rule"] == "control-affine input map uses lowercase g(x)"

    def test_detects_in_tex_and_md_as_well_as_qmd(self, tmp_path: Path) -> None:
        write(tmp_path, "articles/ch.tex", "g(x)u\n")
        write(tmp_path, "critiques/c.md", "g(x)u\n")
        write(tmp_path, "articles/ch.qmd", "g(x)u\n")
        findings = scan(tmp_path)
        assert {f["file"] for f in findings} == {
            "articles/ch.tex",
            "critiques/c.md",
            "articles/ch.qmd",
        }

    def test_scans_the_home_page_at_the_repo_root(self, tmp_path: Path) -> None:
        write(tmp_path, "index.qmd", "$$\\dot{x} = f(x) + g(x)u$$\n")
        assert any(f["file"] == "index.qmd" for f in scan(tmp_path))

    def test_scans_critiques_directory(self, tmp_path: Path) -> None:
        write(tmp_path, "critiques/some_critique.md", "the input $g(x)u$ term\n")
        assert any(f["file"] == "critiques/some_critique.md" for f in scan(tmp_path))

    def test_scans_models_directory(self, tmp_path: Path) -> None:
        write(tmp_path, "models/models-drake.qmd", "f(x) + g(x)u\n")
        assert any(f["file"] == "models/models-drake.qmd" for f in scan(tmp_path))

    def test_ignores_files_outside_the_search_roots(self, tmp_path: Path) -> None:
        write(tmp_path, "docs/development/notes.md", "g(x)u\n")
        assert scan(tmp_path) == []

    def test_ignores_other_suffixes(self, tmp_path: Path) -> None:
        write(tmp_path, "articles/readme.rst", "g(x)u\n")
        assert scan(tmp_path) == []

    def test_uppercase_g_of_x_is_not_flagged(self, tmp_path: Path) -> None:
        write(tmp_path, "articles/ch.qmd", "f(x) + G(x)u\n")
        assert scan(tmp_path) == []

    def test_reports_every_occurrence(self, tmp_path: Path) -> None:
        write(tmp_path, "articles/ch.tex", "g(x)u\nfiller\ng(x)u\n")
        assert sorted(f["line"] for f in scan(tmp_path)) == [1, 3]

    def test_catches_derivative_form_dg_of_x(self, tmp_path: Path) -> None:
        """The Lie-bracket derivation differentiates the input map: Dg(x), not Df(x)."""
        write(tmp_path, "articles/ch.qmd", "[f,g](x)=Dg(x)f(x)-Df(x)g(x).\n")
        assert len(scan(tmp_path)) == 1


class TestBaseline:
    def test_key_excludes_the_line_number(self, tmp_path: Path) -> None:
        """Otherwise an unrelated edit above a permitted mention reads as new."""
        write(tmp_path, "articles/ch.qmd", "g(x)u\n")
        first = key(scan(tmp_path)[0])
        write(tmp_path, "articles/ch.qmd", "padding\npadding\ng(x)u\n")
        assert key(scan(tmp_path)[0]) == first

    def test_baselined_occurrence_passes(self, tmp_path: Path) -> None:
        """A genuinely different g(x), such as an optimal-control constraint, is allowlisted."""
        write(tmp_path, "articles/ch05_optimal_control.qmd", "guarantee $g(x)\\le0$\n")
        baseline = tmp_path / "baseline.json"
        baseline.write_text(json.dumps([key(scan(tmp_path)[0])]), encoding="utf-8")
        assert main_with(tmp_path, baseline) == 0

    def test_unbaselined_occurrence_fails(self, tmp_path: Path) -> None:
        write(tmp_path, "articles/ch.qmd", "f(x) + g(x)u\n")
        baseline = tmp_path / "baseline.json"
        baseline.write_text(json.dumps([]), encoding="utf-8")
        assert main_with(tmp_path, baseline) == 1

    def test_baseline_does_not_excuse_a_different_file(self, tmp_path: Path) -> None:
        """A permitted mention in one chapter must not silence another."""
        write(tmp_path, "articles/allowed.qmd", "g(x)u\n")
        baseline = tmp_path / "baseline.json"
        baseline.write_text(json.dumps([key(scan(tmp_path)[0])]), encoding="utf-8")
        write(tmp_path, "articles/other.qmd", "g(x)u\n")
        assert main_with(tmp_path, baseline) == 1


def main_with(root: Path, baseline: Path) -> int:
    """Invoke the CLI entry point against a temporary tree."""
    import sys

    argv = sys.argv
    sys.argv = ["check_notation.py", "--root", str(root), "--baseline", str(baseline)]
    try:
        return main()
    finally:
        sys.argv = argv


def test_every_banned_pattern_has_a_suggested_fix() -> None:
    """A gate that says 'no' without saying 'use this instead' just annoys people."""
    for pattern, rule, fix in BANNED:
        assert pattern and rule and fix
        assert len(fix) > 5


def test_real_corpus_matches_notation_baseline() -> None:
    """The actual repository content: every g(x) is either fixed or baselined.

    This is the live enforcement for issue #4582 -- it scans the real .qmd,
    .md, and .tex sources rather than a synthetic tmp_path tree.
    """
    baseline_path = REPO_ROOT / "config" / "notation-baseline.json"
    permitted = set(json.loads(baseline_path.read_text(encoding="utf-8")))

    findings = scan(REPO_ROOT)
    new = [f for f in findings if key(f) not in permitted]

    assert new == [], (
        f"{len(new)} lowercase g(x) occurrence(s) not covered by "
        f"config/notation-baseline.json: {new}"
    )
