"""Tests for check_style_discipline lint tool."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src/tools"))
from check_style_discipline import check_file


def test_clean_file_returns_no_violations(tmp_path):
    f = tmp_path / "clean.qmd"
    f.write_text("# Clean\n\nNo inline styles here.\n")
    assert check_file(f) == []


def test_inline_style_detected(tmp_path):
    f = tmp_path / "bad.qmd"
    f.write_text('<div style="color: red;">text</div>\n')
    violations = check_file(f)
    assert any("inline style=" in v for v in violations)


def test_gradient_detected(tmp_path):
    f = tmp_path / "bad.qmd"
    f.write_text("background: linear-gradient(135deg, red, blue);\n")
    violations = check_file(f)
    assert any("gradient" in v for v in violations)


def test_hardcoded_hex_detected(tmp_path):
    f = tmp_path / "bad.qmd"
    f.write_text("color: #2563eb;\n")
    violations = check_file(f)
    assert any("hardcoded hex" in v for v in violations)
