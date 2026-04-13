"""Test suite that verifies docstring coverage across the src/ package.

This test ensures the project maintains ≥ 95% docstring coverage on
public functions, classes, and modules — as required by GH1636.
"""

from __future__ import annotations

import ast
from pathlib import Path

# Minimum coverage threshold (%)
DOCSTRING_COVERAGE_THRESHOLD = 95.0

# Ignore empty __init__.py stubs (they have no symbols at all)
IGNORE_EMPTY_FILES = True


def _collect_docstring_stats(src_root: Path) -> tuple[int, int, list[tuple[str, int, str]]]:
    """Walk *src_root* and count docstring coverage.

    Returns:
        Tuple of (items_with_docstring, total_items, missing_list) where
        *missing_list* is a list of ``(filepath, lineno, name)`` tuples for
        items that are missing a docstring.
    """
    total = 0
    with_doc = 0
    missing: list[tuple[str, int, str]] = []

    for py_file in sorted(src_root.rglob("*.py")):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(
                node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef | ast.Module
            ):
                continue

            # Skip dunder methods and private helpers (they are not public API)
            name = getattr(node, "name", "<module>")
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and name.startswith("_"):
                continue

            total += 1
            has_doc = (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            )
            if has_doc:
                with_doc += 1
            else:
                lineno = getattr(node, "lineno", 0)
                missing.append((str(py_file.relative_to(src_root.parent)), lineno, name))

    return with_doc, total, missing


class TestDocstringCoverage:
    """Verify that src/ docstring coverage meets the 95%+ target."""

    def test_docstring_coverage_threshold(self) -> None:
        """Docstring coverage across src/ must be ≥ DOCSTRING_COVERAGE_THRESHOLD."""
        src_root = Path(__file__).parent.parent / "src"
        assert src_root.exists(), f"src/ not found at {src_root}"

        with_doc, total, missing = _collect_docstring_stats(src_root)

        assert total > 0, "No Python symbols found in src/"

        coverage_pct = (with_doc / total) * 100.0
        missing_report = "\n".join(
            f"  {path}:{lineno} — {name}" for path, lineno, name in missing[:20]
        )
        if len(missing) > 20:
            missing_report += f"\n  ... and {len(missing) - 20} more"

        assert coverage_pct >= DOCSTRING_COVERAGE_THRESHOLD, (
            f"Docstring coverage {coverage_pct:.1f}% is below threshold "
            f"{DOCSTRING_COVERAGE_THRESHOLD}%.\n"
            f"Missing docstrings ({len(missing)} items):\n{missing_report}"
        )

    def test_no_public_functions_missing_docstrings_in_affine_control(self) -> None:
        """All public functions in src/affine_control/ must have docstrings."""
        src_root = Path(__file__).parent.parent / "src" / "affine_control"
        _, _, missing = _collect_docstring_stats(src_root)
        # Filter out module-level items (lineno == 0)
        public_missing = [(p, ln, n) for p, ln, n in missing if ln > 0]
        assert public_missing == [], (
            "Public functions/classes missing docstrings in affine_control:\n"
            + "\n".join(f"  {p}:{ln} — {n}" for p, ln, n in public_missing)
        )

    def test_benchmark_result_has_docstring(self) -> None:
        """BenchmarkResult dataclass must have a class docstring."""
        from src.tools.rl_funnel_benchmark import BenchmarkResult

        assert BenchmarkResult.__doc__ is not None, "BenchmarkResult is missing a class docstring"
        assert len(BenchmarkResult.__doc__.strip()) > 0, "BenchmarkResult docstring is empty"
