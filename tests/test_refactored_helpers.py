"""Tests for helper functions extracted during GH1635 refactoring.

Covers the new private helper functions introduced in:
- src/affine_control/swing_optimizer.py  (_build_initial_conditions, _package_result)
- src/tools/wrap_sidebars.py             (_wrap_aside)
- src/tools/matlab_utilities/scripts/line_checks.py  (_is_number_in_code, module constants)
- src/tools/publish_manual_article.py    (_apply_inline_formatting, _process_header_line,
                                           _process_list_item)
- src/tools/code_quality/ast_analyzer.py (_should_skip_docstring_checks,
                                           _check_function_docstrings, _SKIP_AST_CHECK_NAMES)
- src/tools/utils/file_utils.py          (_search_paths)
- src/tools/rl_funnel_benchmark.py       (_precompute_lqr_gains)
- src/tools/matlab_utilities/scripts/matlab_quality_check.py (_print_text_results)
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

import numpy as np

# ---------------------------------------------------------------------------
# swing_optimizer helpers
# ---------------------------------------------------------------------------


class TestSwingOptimizerHelpers(unittest.TestCase):
    """Tests for SwingOptimizer private helper methods."""

    def _make_optimizer(self, n_joints: int = 2) -> Any:
        """Return a minimal SwingOptimizer for testing."""
        from src.affine_control.swing_optimizer import SwingOptimizationConfig, SwingOptimizer

        cfg = SwingOptimizationConfig(n_joints=n_joints, horizon_steps=5, max_iterations=3)
        return SwingOptimizer(cfg)

    def test_build_initial_conditions_shapes(self) -> None:
        """_build_initial_conditions returns correctly shaped arrays."""
        opt = self._make_optimizer(n_joints=2)
        cfg = opt.config
        x_target, u_init = opt._build_initial_conditions(cfg)
        self.assertEqual(x_target.shape, (cfg.state_dim,))
        self.assertEqual(u_init.shape, (cfg.horizon_steps, cfg.control_dim))

    def test_build_initial_conditions_target_velocity(self) -> None:
        """Velocity portion of x_target equals target_velocity."""
        opt = self._make_optimizer(n_joints=2)
        cfg = opt.config
        x_target, _ = opt._build_initial_conditions(cfg)
        velocity_part = x_target[cfg.n_joints :]
        np.testing.assert_array_equal(velocity_part, cfg.target_velocity)

    def test_build_initial_conditions_zero_positions(self) -> None:
        """Position portion of x_target is zero."""
        opt = self._make_optimizer(n_joints=2)
        cfg = opt.config
        x_target, _ = opt._build_initial_conditions(cfg)
        position_part = x_target[: cfg.n_joints]
        np.testing.assert_array_equal(position_part, 0.0)

    def test_build_initial_conditions_zero_controls(self) -> None:
        """u_init is all zeros."""
        opt = self._make_optimizer(n_joints=3)
        cfg = opt.config
        _, u_init = opt._build_initial_conditions(cfg)
        np.testing.assert_array_equal(u_init, 0.0)

    def test_package_result_final_velocity(self) -> None:
        """_package_result computes final velocity as L2 norm of velocity portion."""
        from src.affine_control.swing_optimizer import SwingOptimizationConfig, SwingOptimizer

        cfg = SwingOptimizationConfig(n_joints=2, horizon_steps=5, max_iterations=2)
        opt = SwingOptimizer(cfg)

        # Construct trajectories that satisfy trajectory_cost constraints
        # (T+1 states for T controls)
        n = cfg.state_dim
        m = cfg.control_dim
        T = 5
        x_arr = np.zeros((T + 1, n))
        x_arr[-1, cfg.n_joints :] = [3.0, 4.0]  # velocity = [3, 4] → norm = 5
        u_arr = np.zeros((T, m))

        result = opt._package_result(x_arr, u_arr, 1.5, True, 2, cfg)
        self.assertAlmostEqual(result.final_velocity, 5.0, places=10)
        self.assertEqual(result.cost, 1.5)
        self.assertTrue(result.converged)
        self.assertEqual(result.iterations, 2)


# ---------------------------------------------------------------------------
# wrap_sidebars helpers
# ---------------------------------------------------------------------------


class TestWrapAside(unittest.TestCase):
    """Tests for the _wrap_aside helper in wrap_sidebars."""

    def setUp(self) -> None:
        """Set up common tag constants."""
        lt, gt = chr(60), chr(62)
        self.aside_close = f"{lt}/aside{gt}"
        self.sticky_div_start = f'{lt}div class="sidebar-sticky-content"{gt}'
        self.sticky_div_end = f"{lt}/div{gt}"

    def _call(
        self, content: str, aside_open_tag: str, *, check_already_wrapped: bool = True
    ) -> str:
        """Call _wrap_aside with common parameters."""
        from src.tools.wrap_sidebars import _wrap_aside

        return _wrap_aside(
            content,
            aside_open_tag,
            self.sticky_div_start,
            self.sticky_div_end,
            self.aside_close,
            check_already_wrapped=check_already_wrapped,
        )

    def test_wraps_aside_tag(self) -> None:
        """Content with an aside tag gets wrapped with sticky div."""
        aside_open = '<aside class="left-sidebar">'
        content = f"{aside_open}inner content</aside>"
        result = self._call(content, aside_open, check_already_wrapped=False)
        self.assertIn(self.sticky_div_start, result)
        self.assertIn("inner content", result)

    def test_no_aside_tag_returns_unchanged(self) -> None:
        """Content without the aside tag is returned unchanged."""
        from src.tools.wrap_sidebars import _wrap_aside

        content = "<p>no aside here</p>"
        result = _wrap_aside(
            content,
            '<aside class="left-sidebar">',
            self.sticky_div_start,
            self.sticky_div_end,
            self.aside_close,
        )
        self.assertEqual(result, content)

    def test_already_wrapped_skipped(self) -> None:
        """When check_already_wrapped=True, already-wrapped content is not double-wrapped."""
        aside_open = '<aside class="right-sidebar">'
        content = f"{aside_open}\n        {self.sticky_div_start}inner</aside>"
        result = self._call(content, aside_open, check_already_wrapped=True)
        self.assertEqual(result.count(self.sticky_div_start), 1)


# ---------------------------------------------------------------------------
# line_checks helpers
# ---------------------------------------------------------------------------


class TestLineChecksHelpers(unittest.TestCase):
    """Tests for helpers in matlab_utilities/scripts/line_checks.py."""

    def test_is_number_in_code_no_comment(self) -> None:
        """Number with no comment delimiter is in code."""
        from src.tools.matlab_utilities.scripts.line_checks import _is_number_in_code

        self.assertTrue(_is_number_in_code("x = 42;", "42"))

    def test_is_number_in_code_after_comment(self) -> None:
        """Number appearing only after '%' is not in code."""
        from src.tools.matlab_utilities.scripts.line_checks import _is_number_in_code

        self.assertFalse(_is_number_in_code("x = 1; % magic is 99", "99"))

    def test_is_number_in_code_before_comment(self) -> None:
        """Number appearing before '%' delimiter is in code."""
        from src.tools.matlab_utilities.scripts.line_checks import _is_number_in_code

        self.assertTrue(_is_number_in_code("x = 99; % other", "99"))

    def test_acceptable_numbers_frozenset(self) -> None:
        """_ACCEPTABLE_NUMBERS contains expected values and is a frozenset."""
        from src.tools.matlab_utilities.scripts.line_checks import _ACCEPTABLE_NUMBERS

        self.assertIsInstance(_ACCEPTABLE_NUMBERS, frozenset)
        self.assertIn("0", _ACCEPTABLE_NUMBERS)
        self.assertIn("1", _ACCEPTABLE_NUMBERS)
        self.assertIn("100", _ACCEPTABLE_NUMBERS)

    def test_known_constants_dict(self) -> None:
        """_KNOWN_CONSTANTS is a dict with pi and gravity entries."""
        from src.tools.matlab_utilities.scripts.line_checks import _KNOWN_CONSTANTS

        self.assertIsInstance(_KNOWN_CONSTANTS, dict)
        self.assertIn("9.81", _KNOWN_CONSTANTS)
        self.assertIn("3.14159", _KNOWN_CONSTANTS)


# ---------------------------------------------------------------------------
# publish_manual_article helpers
# ---------------------------------------------------------------------------


class TestPublishManualArticleHelpers(unittest.TestCase):
    """Tests for helper functions in publish_manual_article."""

    def test_apply_inline_formatting_bold(self) -> None:
        """Bold markdown converts to <strong> tags."""
        from src.tools.publish_manual_article import _apply_inline_formatting

        result = _apply_inline_formatting("This is **bold** text.")
        self.assertEqual(result, "This is <strong>bold</strong> text.")

    def test_apply_inline_formatting_italic(self) -> None:
        """Italic markdown converts to <em> tags."""
        from src.tools.publish_manual_article import _apply_inline_formatting

        result = _apply_inline_formatting("This is *italic* text.")
        self.assertEqual(result, "This is <em>italic</em> text.")

    def test_apply_inline_formatting_no_markup(self) -> None:
        """Plain text is returned unchanged."""
        from src.tools.publish_manual_article import _apply_inline_formatting

        result = _apply_inline_formatting("plain text")
        self.assertEqual(result, "plain text")

    def test_process_header_line_no_open_list(self) -> None:
        """Header with no open list emits h2 without closing ul."""
        from src.tools.publish_manual_article import _process_header_line

        html_lines: list[str] = []
        in_list = _process_header_line("## My Header", html_lines, False)
        self.assertFalse(in_list)
        self.assertEqual(len(html_lines), 1)
        self.assertIn("<h2", html_lines[0])
        self.assertIn("My Header", html_lines[0])

    def test_process_header_line_closes_open_list(self) -> None:
        """Header closes an open list before emitting h2."""
        from src.tools.publish_manual_article import _process_header_line

        html_lines: list[str] = []
        in_list = _process_header_line("## Header", html_lines, True)
        self.assertFalse(in_list)
        self.assertIn("</ul>", html_lines)

    def test_process_list_item_opens_list(self) -> None:
        """First list item opens a <ul>."""
        from src.tools.publish_manual_article import _process_list_item

        html_lines: list[str] = []
        in_list = _process_list_item("- item one", html_lines, False)
        self.assertTrue(in_list)
        self.assertIn("<ul>", html_lines)
        self.assertIn("<li>item one</li>", html_lines)

    def test_process_list_item_no_double_open(self) -> None:
        """Second list item does not open a second <ul>."""
        from src.tools.publish_manual_article import _process_list_item

        html_lines: list[str] = ["<ul>"]
        in_list = _process_list_item("- item two", html_lines, True)
        self.assertTrue(in_list)
        self.assertEqual(html_lines.count("<ul>"), 1)


# ---------------------------------------------------------------------------
# ast_analyzer helpers
# ---------------------------------------------------------------------------


class TestAstAnalyzerHelpers(unittest.TestCase):
    """Tests for helper functions in code_quality/ast_analyzer.py."""

    def test_skip_ast_check_names_contains_expected(self) -> None:
        """_SKIP_AST_CHECK_NAMES includes the known excluded filenames."""
        from src.tools.code_quality.ast_analyzer import _SKIP_AST_CHECK_NAMES

        self.assertIn("matlab_quality_check.py", _SKIP_AST_CHECK_NAMES)
        self.assertIn("code_quality_check.py", _SKIP_AST_CHECK_NAMES)

    def test_should_skip_docstring_checks_tests_dir(self) -> None:
        """Files in tests/ directories skip docstring checks."""
        from src.tools.code_quality.ast_analyzer import _should_skip_docstring_checks

        self.assertTrue(_should_skip_docstring_checks(Path("tests/test_foo.py")))

    def test_should_skip_docstring_checks_scripts_dir(self) -> None:
        """Files in scripts/ directories skip docstring checks."""
        from src.tools.code_quality.ast_analyzer import _should_skip_docstring_checks

        self.assertTrue(_should_skip_docstring_checks(Path("src/scripts/foo.py")))

    def test_should_not_skip_docstring_checks_regular_src(self) -> None:
        """Regular src files do not skip docstring checks."""
        from src.tools.code_quality.ast_analyzer import _should_skip_docstring_checks

        self.assertFalse(_should_skip_docstring_checks(Path("src/tools/my_tool.py")))

    def test_check_function_docstrings_detects_missing(self) -> None:
        """_check_function_docstrings flags functions missing docstrings."""
        from src.tools.code_quality.ast_analyzer import _check_function_docstrings

        source = "def foo():\n    pass\n"
        tree = ast.parse(source)
        issues: list[tuple[int, str, str]] = []
        _check_function_docstrings(tree, issues)
        self.assertEqual(len(issues), 1)
        self.assertIn("foo", issues[0][1])

    def test_check_function_docstrings_passes_with_docstring(self) -> None:
        """_check_function_docstrings does not flag functions that have docstrings."""
        from src.tools.code_quality.ast_analyzer import _check_function_docstrings

        source = 'def bar():\n    """Docstring."""\n    pass\n'
        tree = ast.parse(source)
        issues: list[tuple[int, str, str]] = []
        _check_function_docstrings(tree, issues)
        self.assertEqual(len(issues), 0)

    def test_check_function_docstrings_exempts_stub(self) -> None:
        """_check_function_docstrings skips stub functions (body is only ...)."""
        from src.tools.code_quality.ast_analyzer import _check_function_docstrings

        source = "def stub() -> None: ...\n"
        tree = ast.parse(source)
        issues: list[tuple[int, str, str]] = []
        _check_function_docstrings(tree, issues)
        self.assertEqual(len(issues), 0)


# ---------------------------------------------------------------------------
# file_utils helpers
# ---------------------------------------------------------------------------


class TestSearchPaths(unittest.TestCase):
    """Tests for _search_paths in file_utils."""

    def test_search_paths_finds_file_with_extension(self) -> None:
        """_search_paths returns a matching file when given its direct path."""
        import tempfile

        from src.tools.utils.file_utils import _search_paths

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            tmp = Path(f.name)
        try:
            result = _search_paths([tmp], [".txt"], recursive=False)
            self.assertIn(tmp, result)
        finally:
            tmp.unlink(missing_ok=True)

    def test_search_paths_skips_nonexistent(self) -> None:
        """_search_paths silently skips paths that do not exist."""
        from src.tools.utils.file_utils import _search_paths

        result = _search_paths([Path("/nonexistent/path/file.txt")], [".txt"], recursive=False)
        self.assertEqual(result, [])

    def test_search_paths_wrong_extension_excluded(self) -> None:
        """_search_paths does not return files with non-matching extensions."""
        import tempfile

        from src.tools.utils.file_utils import _search_paths

        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            tmp = Path(f.name)
        try:
            result = _search_paths([tmp], [".txt"], recursive=False)
            self.assertNotIn(tmp, result)
        finally:
            tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# matlab_quality_check helpers
# ---------------------------------------------------------------------------


class TestPrintTextResults(unittest.TestCase):
    """Tests for _print_text_results in matlab_quality_check."""

    def test_print_text_results_calls_logger(self) -> None:
        """_print_text_results logs key fields from the results dict."""
        from src.tools.matlab_utilities.scripts.matlab_quality_check import _print_text_results

        results: dict[str, object] = {
            "timestamp": "2026-01-01",
            "total_files": 5,
            "passed": True,
            "summary": "All checks passed",
            "issues": [],
        }
        # Should not raise
        with patch("src.tools.matlab_utilities.scripts.matlab_quality_check.logger") as mock_logger:
            _print_text_results(results)
            self.assertTrue(mock_logger.info.called)

    def test_print_text_results_with_issues(self) -> None:
        """_print_text_results logs issues when they are present."""
        from src.tools.matlab_utilities.scripts.matlab_quality_check import _print_text_results

        results: dict[str, object] = {
            "timestamp": "2026-01-01",
            "total_files": 2,
            "passed": False,
            "summary": "Issues found",
            "issues": ["issue one", "issue two"],
        }
        with patch("src.tools.matlab_utilities.scripts.matlab_quality_check.logger") as mock_logger:
            _print_text_results(results)
            # Check that info was called multiple times (header + per-issue lines)
            self.assertGreater(mock_logger.info.call_count, 3)


if __name__ == "__main__":
    unittest.main()
