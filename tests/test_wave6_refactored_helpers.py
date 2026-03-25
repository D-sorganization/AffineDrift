"""Tests for wave-6 extracted helper functions (issue #1635).

Covers:
- _wrap_aside (wrap_sidebars)
- _dispatch_line_checks, _is_number_in_code (line_checks)
- _apply_template_transforms (html_utils)
- _precompute_lqr_gains, _compute_tracking_metrics, _setup_comparison (rl_funnel_benchmark)
- MockDDPSolver._initialize_ddp_trajectory, MockDDPSolver._run_ddp_iteration (ddp)
"""

from __future__ import annotations

import unittest
from typing import Any

import numpy as np

from src.tools.matlab_utilities.scripts.line_checks import (
    _dispatch_line_checks,
    _is_number_in_code,
)
from src.tools.rl_funnel_benchmark import (
    _compute_tracking_metrics,
    _precompute_lqr_gains,
    _setup_comparison,
)
from src.tools.utils.html_utils import _apply_template_transforms
from src.tools.wrap_sidebars import _wrap_aside


class TestWrapAsideWave6(unittest.TestCase):
    def test_wrap_adds_sticky_div(self) -> None:
        content = '<aside class="left-sidebar">  inner content  </aside>'
        result = _wrap_aside(content, "left-sidebar")
        assert "sidebar-sticky-content" in result
        assert "inner content" in result

    def test_wrap_skips_when_already_wrapped(self) -> None:
        content = (
            '<aside class="right-sidebar">\n'
            '        <div class="sidebar-sticky-content"> already </div>\n'
            "      </aside>"
        )
        result = _wrap_aside(content, "right-sidebar", check_already_wrapped=True)
        # Should not double-wrap
        assert result.count("sidebar-sticky-content") == 1

    def test_wrap_returns_original_when_aside_missing(self) -> None:
        content = "<p>No sidebar here</p>"
        result = _wrap_aside(content, "left-sidebar")
        assert result == content

    def test_wrap_check_disabled_always_wraps(self) -> None:
        content = '<aside class="left-sidebar">content</aside>'
        result = _wrap_aside(content, "left-sidebar", check_already_wrapped=False)
        assert "sidebar-sticky-content" in result


class TestLineChecksHelpersWave6(unittest.TestCase):
    def test_is_number_in_code_before_comment(self) -> None:
        assert _is_number_in_code("x = 42 % this is 99", "42") is True

    def test_is_number_in_code_only_in_comment(self) -> None:
        assert _is_number_in_code("x = y % use 42 here", "42") is False

    def test_is_number_in_code_no_comment(self) -> None:
        assert _is_number_in_code("x = 42", "42") is True

    def test_dispatch_flags_banned_pattern(self) -> None:
        issues: list[str] = []
        _dispatch_line_checks(
            lines=["% TODO: fix this"],
            line_number=1,
            line="% TODO: fix this",
            is_comment=True,
            in_function=False,
            file_name="test.m",
            issues=issues,
        )
        assert any("Backlog marker" in i for i in issues)

    def test_dispatch_flags_magic_number_in_code(self) -> None:
        issues: list[str] = []
        _dispatch_line_checks(
            lines=["x = 42.5"],
            line_number=1,
            line="x = 42.5",
            is_comment=False,
            in_function=False,
            file_name="test.m",
            issues=issues,
        )
        assert any("42.5" in i for i in issues)

    def test_dispatch_skips_anti_patterns_in_comments(self) -> None:
        issues: list[str] = []
        _dispatch_line_checks(
            lines=["% eval('something')"],
            line_number=1,
            line="% eval('something')",
            is_comment=True,
            in_function=True,
            file_name="test.m",
            issues=issues,
        )
        # Anti-patterns should not be flagged in comments
        assert not any("eval()" in i for i in issues)


class TestApplyTemplateTransforms(unittest.TestCase):
    _MINIMAL_TEMPLATE = (
        "<html><head>"
        "<title>Old – AffineDrift</title>"
        '<meta name="description" content="old desc">'
        "</head><body>"
        '<h1 class="title">Old Title</h1>'
        '<div class="description">\n    Old desc\n  </div>'
        '<section class="article-section content">'
        "<p>body</p>"
        "</section>"
        "</body></html>"
    )

    def test_title_updated(self) -> None:
        result = _apply_template_transforms(
            self._MINIMAL_TEMPLATE,
            title="New Title",
            description="New desc",
            body_html="<p>new</p>",
            page_type="articles",
            fix_paths=False,
            path_depth=1,
        )
        assert "<title>New Title" in result

    def test_non_articles_removes_update_script(self) -> None:
        template_with_script = (
            self._MINIMAL_TEMPLATE + "\n<script>function updateArticlesHistory() { var x = 1; }"
            "\nupdateArticlesHistory();</script>"
        )
        result = _apply_template_transforms(
            template_with_script,
            title="T",
            description="D",
            body_html="<p>b</p>",
            page_type="models",
            fix_paths=False,
            path_depth=1,
        )
        assert "updateArticlesHistory" not in result

    def test_body_html_injected(self) -> None:
        result = _apply_template_transforms(
            self._MINIMAL_TEMPLATE,
            title="T",
            description="D",
            body_html="<p>injected content</p>",
            page_type="articles",
            fix_paths=False,
            path_depth=1,
        )
        assert "injected content" in result


class TestPrecomputeLqrGains(unittest.TestCase):
    def test_returns_correct_shape(self) -> None:
        n, m = 4, 2
        t_ref = np.linspace(0.0, 0.1, 5)
        x_ref = np.zeros((4, 5))
        Q = np.eye(n)
        R = np.eye(m)
        gains = _precompute_lqr_gains(t_ref, x_ref, n, m, Q, R)
        assert gains.shape == (5, m, n)

    def test_gains_finite(self) -> None:
        n, m = 4, 2
        t_ref = np.linspace(0.0, 0.1, 3)
        x_ref = np.zeros((4, 3))
        Q = np.diag([10.0, 10.0, 1.0, 1.0])
        R = 0.1 * np.eye(m)
        gains = _precompute_lqr_gains(t_ref, x_ref, n, m, Q, R)
        assert np.all(np.isfinite(gains))


class TestComputeTrackingMetrics(unittest.TestCase):
    def test_zero_error_when_tracking_perfectly(self) -> None:
        t_ref = np.linspace(0.0, 0.1, 5)
        x_ref = np.zeros((4, 5))
        t_eval = t_ref
        x_sim = np.zeros((4, 5))

        def ctrl(t: float, x: np.ndarray) -> np.ndarray:  # type: ignore[type-arg]
            return np.zeros(2)

        err, effort = _compute_tracking_metrics(ctrl, x_sim, t_eval, t_ref, x_ref)
        assert err == 0.0
        assert effort == 0.0

    def test_nonzero_error_when_off_track(self) -> None:
        t_ref = np.linspace(0.0, 0.1, 5)
        x_ref = np.zeros((4, 5))
        x_sim = np.ones((4, 5))
        t_eval = t_ref

        def ctrl(t: float, x: np.ndarray) -> np.ndarray:  # type: ignore[type-arg]
            return np.zeros(2)

        err, _ = _compute_tracking_metrics(ctrl, x_sim, t_eval, t_ref, x_ref)
        assert err > 0.0


class TestSetupComparison(unittest.TestCase):
    def test_returns_correct_shapes(self) -> None:
        x0_p, t_ref, x_ref, x_target = _setup_comparison(
            perturbation_scale=0.0,
            t_span=(0.0, 0.2),
            dt=0.01,
            seed=0,
            control_limit=50.0,
        )
        assert x0_p.shape == (4,)
        assert t_ref.ndim == 1
        assert x_ref.shape == (4, len(t_ref))
        assert x_target.shape == (4,)

    def test_perturbation_zero_equals_nominal(self) -> None:
        x0_p, _, _, _ = _setup_comparison(
            perturbation_scale=0.0,
            t_span=(0.0, 0.2),
            dt=0.01,
            seed=42,
            control_limit=50.0,
        )
        nominal = np.array([np.pi / 2, np.pi / 4, 0.0, 0.0])
        np.testing.assert_array_equal(x0_p, nominal)


class TestMockDdpHelpers(unittest.TestCase):
    def _make_solver(self) -> Any:
        import os

        os.environ.setdefault("PYTEST_CURRENT_TEST", "wave6_test")
        from src.affine_control.ddp import MockDDPSolver

        return MockDDPSolver()

    def test_initialize_returns_correct_lengths(self) -> None:
        solver = self._make_solver()
        u_init = np.zeros((5, 1))

        def f(x: np.ndarray, u: np.ndarray) -> np.ndarray:  # type: ignore[type-arg]
            return np.zeros_like(x)

        x0 = np.zeros(2)
        u_traj, x_traj, t = solver._initialize_ddp_trajectory(f, x0, u_init)
        assert len(u_traj) == 5
        assert len(x_traj) == 6  # N+1 states
        assert len(t) == 6

    def test_run_ddp_iteration_preserves_u_length(self) -> None:
        solver = self._make_solver()
        u_init = np.zeros((5, 1))

        def f(x: np.ndarray, u: np.ndarray) -> np.ndarray:  # type: ignore[type-arg]
            return np.zeros_like(x)

        x0 = np.zeros(2)
        u_traj, x_traj, t = solver._initialize_ddp_trajectory(f, x0, u_init)
        u_new, x_new, t_new = solver._run_ddp_iteration(f, x0, x_traj, u_traj, t, eps_residual=0.1)
        assert len(u_new) == len(u_traj)
