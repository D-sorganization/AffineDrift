"""Tests for the equation-rendering checker (issue #3230).

The script file is ``scripts/check-equations.py`` (hyphenated), so it is loaded
via importlib rather than a normal import.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check-equations.py"


@pytest.fixture(scope="module")
def check_equations():
    spec = importlib.util.spec_from_file_location("check_equations_under_test", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_balanced_display_dollars_have_no_issues(check_equations):
    # Balanced $$ on its own line: even count of $$, no empty/unbalanced flags.
    issues = check_equations.find_equations("$$x=y$$\n", "f.qmd")
    assert not any(kind == "unbalanced" for _, kind, _ in issues)


def test_unbalanced_display_dollars_flagged(check_equations):
    issues = check_equations.find_equations("$$ x = y\n", "f.qmd")
    assert any(kind == "unbalanced" for _, kind, _ in issues)


def test_empty_display_bracket_block_flagged(check_equations):
    issues = check_equations.find_equations(r"\[\]" + "\n", "f.qmd")
    assert any(kind == "empty" for _, kind, _ in issues)


def test_unbalanced_inline_brackets_flagged(check_equations):
    issues = check_equations.find_equations(r"\( x = y" + "\n", "f.qmd")
    assert any(kind == "unbalanced" for _, kind, _ in issues)


def test_empty_inline_dollars_flagged(check_equations):
    issues = check_equations.find_equations("text $ $ more\n", "f.qmd")
    assert any(kind == "empty" for _, kind, _ in issues)


def test_check_mathjax_config_ignores_non_html(check_equations):
    assert check_equations.check_mathjax_config("foo.qmd") == []


def test_check_mathjax_config_flags_missing_script(check_equations, tmp_path):
    html = tmp_path / "page.html"
    html.write_text(r"<html><body>\[ x \]</body></html>", encoding="utf-8")
    issues = check_equations.check_mathjax_config(str(html))
    assert any("MathJax script not found" in i for i in issues)


def test_check_quarto_math_config_missing_file_is_empty(check_equations, tmp_path):
    assert check_equations.check_quarto_math_config(tmp_path / "absent.yml") == []


def test_check_quarto_math_config_flags_missing_mathjax(check_equations, tmp_path):
    yml = tmp_path / "_quarto.yml"
    yml.write_text("project:\n  type: website\n", encoding="utf-8")
    issues = check_equations.check_quarto_math_config(yml)
    assert any("MathJax not configured" in i for i in issues)
