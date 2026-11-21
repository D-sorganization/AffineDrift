"""Tests for the articles/*.qmd control-character gate."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_article_control_characters import REPO_ROOT, scan_articles

pytestmark = pytest.mark.content_lint


def write(root: Path, relative: str, body: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


class TestScanArticles:
    def test_clean_utf8_passes(self, tmp_path: Path) -> None:
        write(tmp_path, "articles/clean.qmd", "Line one\nLine two\n")
        assert scan_articles(tmp_path) == []

    def test_tab_is_rejected(self, tmp_path: Path) -> None:
        path = tmp_path / "articles/bad.qmd"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"c^\x09op x\n")
        findings = scan_articles(tmp_path)
        assert len(findings) == 1
        assert findings[0]["byte"] == "0x09"

    def test_vertical_tab_is_rejected(self, tmp_path: Path) -> None:
        path = tmp_path / "articles/bad.qmd"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"$=\\Omega_\\ell=\x0barnothing$\n")
        findings = scan_articles(tmp_path)
        assert len(findings) == 1
        assert findings[0]["byte"] == "0x0b"

    def test_real_corpus_is_clean(self) -> None:
        assert scan_articles(REPO_ROOT) == []


def test_main_exits_zero_on_clean_repo() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_article_control_characters.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
