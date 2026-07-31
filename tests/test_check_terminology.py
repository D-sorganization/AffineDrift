"""Tests for the acronym terminology gate (issue #3526).

The gate is only worth having if it fails on a reintroduced variant, so most of
these construct a violation and assert it is caught.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_terminology import BANNED, key, main, scan

pytestmark = pytest.mark.content_lint


def write(root: Path, relative: str, body: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


class TestScan:
    def test_canonical_expansion_is_clean(self, tmp_path: Path) -> None:
        write(tmp_path, "articles/ch.tex", "The Zero Torque Counterfactual (ZTCF) is...\n")
        assert scan(tmp_path) == []

    @pytest.mark.parametrize(
        "variant",
        [
            "Zero Torque Control Fraction",
            "Zero-Torque Controlled Flight",
            "Zero-Torque-Contribution-to-Force",
            "zero-torque constraint force analysis",
            "Drift-Correction-Response",
            "Disturbance Rejection vs. Control",
        ],
    )
    def test_each_variant_is_detected(self, tmp_path: Path, variant: str) -> None:
        write(tmp_path, "articles/ch.tex", f"Recall the {variant} (ZTCF).\n")
        findings = scan(tmp_path)
        assert len(findings) == 1, variant
        assert findings[0]["line"] == 1

    def test_dangling_cross_reference_is_detected(self, tmp_path: Path) -> None:
        write(tmp_path, "articles/ch.tex", "See Chapter~\\ref{ch:control_affine_decomposition}.\n")
        assert [f["rule"] for f in scan(tmp_path)] == ["dangling cross-reference"]

    def test_scans_qmd_as_well_as_tex(self, tmp_path: Path) -> None:
        write(tmp_path, "articles/ch.qmd", "The Zero Torque Control Fraction (ZTCF).\n")
        assert len(scan(tmp_path)) == 1

    def test_ignores_files_outside_the_search_roots(self, tmp_path: Path) -> None:
        write(tmp_path, "notes/scratch.tex", "Zero Torque Control Fraction\n")
        assert scan(tmp_path) == []

    def test_ignores_other_suffixes(self, tmp_path: Path) -> None:
        write(tmp_path, "articles/readme.md", "Zero Torque Control Fraction\n")
        assert scan(tmp_path) == []

    def test_reports_every_occurrence(self, tmp_path: Path) -> None:
        write(
            tmp_path,
            "articles/ch.tex",
            "Zero Torque Control Fraction\nfiller\nZero-Torque Controlled Flight\n",
        )
        assert sorted(f["line"] for f in scan(tmp_path)) == [1, 3]

    def test_hyphen_and_space_forms_both_match(self, tmp_path: Path) -> None:
        write(tmp_path, "articles/a.tex", "Zero-Torque Control Fraction\n")
        write(tmp_path, "articles/b.tex", "Zero Torque Control Fraction\n")
        assert len(scan(tmp_path)) == 2


class TestBaseline:
    def test_key_excludes_the_line_number(self, tmp_path: Path) -> None:
        """Otherwise an unrelated edit above a permitted mention reads as new."""
        write(tmp_path, "articles/ch.tex", "Drift-Correction-Response\n")
        first = key(scan(tmp_path)[0])
        write(tmp_path, "articles/ch.tex", "padding\npadding\nDrift-Correction-Response\n")
        assert key(scan(tmp_path)[0]) == first

    def test_baselined_occurrence_passes(self, tmp_path: Path, capsys) -> None:
        write(tmp_path, "articles/ch.tex", "Drift-Correction-Response\n")
        baseline = tmp_path / "baseline.json"
        baseline.write_text(json.dumps([key(scan(tmp_path)[0])]), encoding="utf-8")
        assert main_with(tmp_path, baseline) == 0

    def test_unbaselined_occurrence_fails(self, tmp_path: Path) -> None:
        write(tmp_path, "articles/ch.tex", "Drift-Correction-Response\n")
        baseline = tmp_path / "baseline.json"
        baseline.write_text(json.dumps([]), encoding="utf-8")
        assert main_with(tmp_path, baseline) == 1

    def test_baseline_does_not_excuse_a_different_file(self, tmp_path: Path) -> None:
        """A permitted mention in one chapter must not silence another."""
        write(tmp_path, "articles/allowed.tex", "Drift-Correction-Response\n")
        baseline = tmp_path / "baseline.json"
        baseline.write_text(json.dumps([key(scan(tmp_path)[0])]), encoding="utf-8")
        write(tmp_path, "articles/other.tex", "Drift-Correction-Response\n")
        assert main_with(tmp_path, baseline) == 1


def main_with(root: Path, baseline: Path) -> int:
    """Invoke the CLI entry point against a temporary tree."""
    import sys

    argv = sys.argv
    sys.argv = ["check_terminology.py", "--root", str(root), "--baseline", str(baseline)]
    try:
        return main()
    finally:
        sys.argv = argv


def test_every_banned_pattern_has_a_suggested_fix() -> None:
    """A gate that says 'no' without saying 'use this instead' just annoys people."""
    for pattern, rule, fix in BANNED:
        assert pattern and rule and fix
        assert len(fix) > 5
