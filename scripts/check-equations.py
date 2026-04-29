#!/usr/bin/env python3
r"""Check equation rendering in Quarto documents and HTML files.

This script validates that mathematical equations are properly formatted
for MathJax rendering. It checks for:
- Proper LaTeX delimiters (\[ \], \( \), $$ $$, $ $)
- Balanced brackets and parentheses
- Common syntax errors
- Missing MathJax configuration
"""

import re
import sys
from pathlib import Path

from src.tools.utils import find_html_files, find_qmd_files, setup_logging

logger = setup_logging(__name__)


def _check_display_brackets(line: str, line_num: int, issues: list):
    r"""Check \[ ... \] delimiters."""
    if r"\[" in line or r"\]" in line:
        open_count = line.count(r"\[")
        close_count = line.count(r"\]")
        if open_count != close_count:
            issues.append(
                (
                    line_num,
                    "unbalanced",
                    f"Unbalanced \\[ \\] delimiters: {open_count} open, {close_count} close",
                )
            )
        if r"\[" in line and r"\]" in line:
            matches = re.findall(r"\\\[(.*?)\\\]", line)
            for match in matches:
                if not match.strip():
                    issues.append((line_num, "empty", "Empty equation block \\[\\]"))


def _check_display_dollars(line: str, line_num: int, issues: list):
    """Check $$ ... $$ delimiters."""
    dollar_count = line.count("$$")
    if dollar_count > 0 and dollar_count % 2 != 0:
        issues.append(
            (
                line_num,
                "unbalanced",
                f"Unbalanced $$ delimiters: {dollar_count} found  (should be even)",
            )
        )


def _check_inline_brackets(line: str, line_num: int, issues: list):
    r"""Check \( ... \) delimiters."""
    if r"\(" in line or r"\)" in line:
        open_count = line.count(r"\(")
        close_count = line.count(r"\)")
        if open_count != close_count:
            issues.append(
                (
                    line_num,
                    "unbalanced",
                    f"Unbalanced \\( \\) delimiters: {open_count} open, {close_count} close",
                )
            )


def _check_inline_dollars(line: str, line_num: int, issues: list):
    """Check $ ... $ delimiters."""
    dollar_matches = re.findall(r"(?<!\$)\$([^$]*)\$(?!\$)", line)
    for match in dollar_matches:
        if not match.strip():
            issues.append((line_num, "empty", "Empty inline equation $ $"))


def find_equations(content: str, filepath: str) -> list[tuple[int, str, str]]:
    """Find all equations in content and return line numbers and equations."""
    issues: list[tuple[int, str, str]] = []
    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        _check_display_brackets(line, line_num, issues)
        _check_display_dollars(line, line_num, issues)
        _check_inline_brackets(line, line_num, issues)
        _check_inline_dollars(line, line_num, issues)

    return issues

    return issues


def check_mathjax_config(filepath: str) -> list[str]:
    """Check if MathJax is properly configured in HTML files."""
    issues: list[str] = []

    if not filepath.endswith(".html"):
        return issues

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Check for MathJax script
        if "mathjax" not in content.lower() and "\\[" in content:
            issues.append("MathJax script not found but equations detected")

        # Check for MathJax configuration
        if "MathJax" in content and "tex:" not in content:
            issues.append("MathJax found but tex configuration may be missing")

    except (OSError, UnicodeDecodeError) as e:
        issues.append(f"Error reading file: {e}")

    return issues


def check_quarto_math_config(quarto_yml: Path) -> list[str]:
    """Check if Quarto is configured for MathJax."""
    issues: list[str] = []

    if not quarto_yml.exists():
        return issues

    try:
        with open(quarto_yml, encoding="utf-8") as f:
            content = f.read()

        if "html-math-method" not in content and "mathjax" not in content.lower():
            issues.append("MathJax not configured in _quarto.yml")

        if "html-math-method" in content and "mathjax" not in content.lower():
            issues.append("html-math-method found but not set to mathjax")

    except (OSError, UnicodeDecodeError) as e:
        issues.append(f"Error reading _quarto.yml: {e}")

    return issues


def _check_quarto_config(root: Path) -> bool:
    """Check _quarto.yml config and log issues."""
    quarto_yml = root / "_quarto.yml"
    if not quarto_yml.exists():
        return False
    config_issues = check_quarto_math_config(quarto_yml)
    if config_issues:
        for issue in config_issues:
            logger.warning("_quarto.yml: %s", issue)
        return True
    return False


def _check_qmd_files(root: Path) -> bool:
    """Check equations in all .qmd files and log issues."""
    issues_found = False
    qmd_files = find_qmd_files(root)
    for qmd_file in qmd_files:
        try:
            with open(qmd_file, encoding="utf-8") as f:
                content = f.read()
            equation_issues = find_equations(content, str(qmd_file))
            if equation_issues:
                for line_num, issue_type, message in equation_issues:
                    logger.warning("%s:%d [%s] %s", qmd_file, line_num, issue_type, message)
                issues_found = True
        except (OSError, UnicodeDecodeError) as e:
            logger.error("Error processing %s: %s", qmd_file, e)
            issues_found = True
    return issues_found


def _check_html_files(root: Path) -> bool:
    """Check MathJax in rendered HTML files and log issues."""
    issues_found = False
    html_files = find_html_files(root, limit=10)
    for html_file in html_files:
        config_issues = check_mathjax_config(str(html_file))
        if config_issues:
            for issue in config_issues:
                logger.warning("%s: %s", html_file, issue)
            issues_found = True
    return issues_found


def main() -> int:
    """Main function to check equations in all relevant files."""
    root = Path()
    issues_found = False

    if _check_quarto_config(root):
        issues_found = True

    if _check_qmd_files(root):
        issues_found = True

    if _check_html_files(root):
        issues_found = True

    return 1 if issues_found else 0


if __name__ == "__main__":
    sys.exit(main())
