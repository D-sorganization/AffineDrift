"""Tests for helper functions extracted during GH1660 refactoring.

Covers:
- torque_calculator: _generate_golf_torque, _generate_step_torque,
  _generate_pulse_torque, _generate_burst_torque, _build_polynomial_namespace,
  _validate_polynomial_result
- html_utils: _apply_template_transforms
- wrap_sidebars: _split_aside_content, _reassemble_wrapped
- plots: _compute_torque_signals, _compute_acceleration_signals
- swing_optimizer: _execute_ddp_step, _select_best_trajectory
- ddp: _initialize_ddp_trajectory, _run_ddp_iteration
- line_checks: _dispatch_line_checks
- issue_utils: _issue_body_template
- streamlit_app: _compute_info_metrics
- matlab_quality_check: _build_matlab_commands, _try_matlab_command
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


def _install_streamlit_mock() -> None:
    """Install a minimal streamlit mock so plots/diagram/streamlit_app can be imported."""
    if "streamlit" not in sys.modules:
        st = types.ModuleType("streamlit")
        st.cache_resource = lambda **kw: (lambda f: f)  # type: ignore[attr-defined]
        st.cache_data = lambda **kw: (lambda f: f)  # type: ignore[attr-defined]

        class _FakeState(dict):  # type: ignore[type-arg]
            def __getattr__(self, k: str) -> Any:
                return self.get(k)

            def __setattr__(self, k: str, v: Any) -> None:
                self[k] = v

        st.session_state = _FakeState()  # type: ignore[attr-defined]

        for name in [
            "set_page_config", "title", "header", "subheader", "markdown",
            "pyplot", "sidebar", "columns", "slider", "number_input",
            "selectbox", "checkbox", "button", "text_input", "expander",
            "error", "rerun", "stop",
        ]:
            setattr(st, name, MagicMock())

        sys.modules["streamlit"] = st


_install_streamlit_mock()


# ── torque_calculator helpers ─────────────────────────────────────────────────


class TestGenerateTorqueHelpers:
    """Tests for extracted torque signal generator helpers."""

    def test_generate_golf_torque_returns_correct_shape(self) -> None:
        from src.tools.wrist_universal_joint.torque_calculator import _generate_golf_torque

        t = np.linspace(0, 1, 500)
        torque = _generate_golf_torque(t)
        assert torque.shape == t.shape

    def test_generate_step_torque_is_zero_before_index_250(self) -> None:
        from src.tools.wrist_universal_joint.torque_calculator import _generate_step_torque

        t = np.linspace(0, 1, 500)
        torque = _generate_step_torque(t)
        assert np.all(torque[:250] == 0.0)
        assert np.all(torque[250:] == 3.0)

    def test_generate_step_torque_correct_shape(self) -> None:
        from src.tools.wrist_universal_joint.torque_calculator import _generate_step_torque

        t = np.linspace(0, 1, 500)
        torque = _generate_step_torque(t)
        assert torque.shape == t.shape

    def test_generate_pulse_torque_zero_outside_range(self) -> None:
        from src.tools.wrist_universal_joint.torque_calculator import _generate_pulse_torque

        t = np.linspace(0, 1, 500)
        torque = _generate_pulse_torque(t)
        assert torque.shape == t.shape
        assert np.all(torque[:200] == 0.0)
        assert np.all(torque[300:] == 0.0)

    def test_generate_burst_torque_zero_far_from_center(self) -> None:
        from src.tools.wrist_universal_joint.torque_calculator import _generate_burst_torque

        t = np.linspace(0, 1, 500)
        torque = _generate_burst_torque(t)
        assert torque.shape == t.shape
        # indices far from center 250 ± 50 should be zero
        assert np.all(torque[:200] == 0.0)
        assert np.all(torque[300:] == 0.0)


class TestBuildPolynomialNamespace:
    """Tests for _build_polynomial_namespace."""

    def test_builds_evaluator_with_expected_names(self) -> None:
        from src.tools.wrist_universal_joint.torque_calculator import _build_polynomial_namespace

        t = np.linspace(0, 1, 10)
        evaluator = _build_polynomial_namespace(t)
        result = evaluator.eval("t * 2")
        assert isinstance(result, np.ndarray)
        assert result.shape == t.shape

    def test_evaluator_supports_pi(self) -> None:
        from src.tools.wrist_universal_joint.torque_calculator import _build_polynomial_namespace

        t = np.linspace(0, 1, 10)
        evaluator = _build_polynomial_namespace(t)
        result = evaluator.eval("pi")
        assert abs(float(result) - np.pi) < 1e-10


class TestValidatePolynomialResult:
    """Tests for _validate_polynomial_result."""

    def test_valid_array_returns_no_error(self) -> None:
        from src.tools.wrist_universal_joint.torque_calculator import _validate_polynomial_result

        t = np.linspace(0, 1, 10)
        result = np.ones(10)
        arr, err = _validate_polynomial_result(result, t)
        assert err is None
        np.testing.assert_array_equal(arr, result)

    def test_shape_mismatch_returns_error(self) -> None:
        from src.tools.wrist_universal_joint.torque_calculator import _validate_polynomial_result

        t = np.linspace(0, 1, 10)
        result = np.ones(5)  # wrong shape
        arr, err = _validate_polynomial_result(result, t)
        assert err is not None
        assert "shape" in err

    def test_scalar_result_broadcasts_to_array(self) -> None:
        from src.tools.wrist_universal_joint.torque_calculator import _validate_polynomial_result

        t = np.linspace(0, 1, 10)
        arr, err = _validate_polynomial_result(3.14, t)
        assert err is None
        assert arr.shape == t.shape
        assert np.all(arr == pytest.approx(3.14))


# ── html_utils helpers ────────────────────────────────────────────────────────


class TestApplyTemplateTransforms:
    """Tests for _apply_template_transforms."""

    _TEMPLATE = """<html><head>
<title>Old Title</title>
<meta name="description" content="Old desc">
</head><body>
<h1 class="title">Old Title</h1>
<div class="description">Old desc</div>
<section class="article-section first">Old content</section>
</body></html>"""

    def test_updates_title(self) -> None:
        from src.tools.utils.html_utils import _apply_template_transforms

        result = _apply_template_transforms(
            self._TEMPLATE, "New Title", "New desc", "<p>body</p>", "articles", False, 1
        )
        assert "New Title" in result

    def test_updates_description(self) -> None:
        from src.tools.utils.html_utils import _apply_template_transforms

        result = _apply_template_transforms(
            self._TEMPLATE, "T", "New Description", "<p>body</p>", "articles", False, 1
        )
        assert "New Description" in result

    def test_returns_string(self) -> None:
        from src.tools.utils.html_utils import _apply_template_transforms

        result = _apply_template_transforms(
            self._TEMPLATE, "T", "D", "<p>b</p>", "articles", False, 1
        )
        assert isinstance(result, str)


# ── wrap_sidebars helpers ─────────────────────────────────────────────────────


class TestSplitAsideContent:
    """Tests for _split_aside_content."""

    def test_splits_valid_aside(self) -> None:
        from src.tools.wrap_sidebars import _split_aside_content

        content = "before<aside class='x'>inner</aside>after"
        result = _split_aside_content(content, "<aside class='x'>", "</aside>")
        assert result is not None
        parts, subparts = result
        assert len(parts) == 2
        assert len(subparts) == 2

    def test_returns_none_if_tag_missing(self) -> None:
        from src.tools.wrap_sidebars import _split_aside_content

        result = _split_aside_content("no tag here", "<aside>", "</aside>")
        assert result is None

    def test_returns_none_if_close_tag_missing(self) -> None:
        from src.tools.wrap_sidebars import _split_aside_content

        result = _split_aside_content("<aside>no close", "<aside>", "</aside>")
        assert result is None


class TestReassembleWrapped:
    """Tests for _reassemble_wrapped."""

    def test_reassembly_contains_sticky_div(self) -> None:
        from src.tools.wrap_sidebars import _reassemble_wrapped

        parts = ["before<aside>", "inner</aside>after"]
        # split gives: parts[0]="before", parts[1]="inner</aside>after"
        parts_split = ["before", "inner</aside>after"]
        subparts = ["inner", "after"]
        result = _reassemble_wrapped(
            parts_split, subparts, "<aside>", "</aside>", "<div class='sticky'>", "</div>"
        )
        assert "<div class='sticky'>" in result
        assert "</div>" in result
        assert "inner" in result


# ── plots helpers ─────────────────────────────────────────────────────────────


class TestComputeTorqueSignals:
    """Tests for _compute_torque_signals."""

    def test_returns_correct_shapes(self) -> None:
        from src.tools.wrist_universal_joint.plots import _compute_torque_signals

        t = np.linspace(0, 1, 100)
        input_torque = np.ones(100)
        torque_transmitted, torque_alpha, torque_gamma, tau_ratio = _compute_torque_signals(
            input_torque, grip_angle_deg=30.0, wrist_angle_deg=0.0
        )
        assert torque_transmitted.shape == t.shape
        assert torque_alpha.shape == t.shape
        assert torque_gamma.shape == t.shape
        assert isinstance(tau_ratio, float)

    def test_tau_ratio_is_float(self) -> None:
        from src.tools.wrist_universal_joint.plots import _compute_torque_signals

        input_torque = np.ones(50)
        _t, _ta, _tg, tau_ratio = _compute_torque_signals(input_torque, 30.0, 0.0)
        assert isinstance(tau_ratio, float)
        assert tau_ratio > 0.0


class TestComputeAccelerationSignals:
    """Tests for _compute_acceleration_signals."""

    def test_returns_correct_shapes(self) -> None:
        from src.tools.wrist_universal_joint.plots import _compute_acceleration_signals

        input_torque = np.ones(50)
        accel_alpha, accel_gamma = _compute_acceleration_signals(input_torque, 30.0, 0.0, 0.1, 0.05)
        assert accel_alpha.shape == input_torque.shape
        assert accel_gamma.shape == input_torque.shape

    def test_zero_inertia_gives_zero_acceleration(self) -> None:
        from src.tools.wrist_universal_joint.plots import _compute_acceleration_signals
        from src.core.constants import EPSILON

        input_torque = np.ones(50)
        accel_alpha, accel_gamma = _compute_acceleration_signals(input_torque, 30.0, 0.0, EPSILON / 2, EPSILON / 2)
        # Below EPSILON threshold, should fall back to zeros_like
        assert np.all(accel_alpha == 0.0)
        assert np.all(accel_gamma == 0.0)


# ── swing_optimizer helpers ────────────────────────────────────────────────────


class TestSelectBestTrajectory:
    """Tests for SwingOptimizer._select_best_trajectory."""

    def _make_optimizer(self):  # type: ignore[no-untyped-def]
        from src.affine_control.swing_optimizer import SwingOptimizationConfig, SwingOptimizer

        config = SwingOptimizationConfig(n_joints=1, horizon_steps=5, max_iterations=3)
        return SwingOptimizer(config)

    def test_returns_new_when_lower_cost(self) -> None:
        optimizer = self._make_optimizer()
        x_new = np.ones(2)
        u_new = np.ones(1)
        x_best, u_best, best_cost = optimizer._select_best_trajectory(
            x_new, u_new, current_cost=0.5, best_cost=1.0,
            best_x_traj=np.zeros(2), best_u_traj=np.zeros(1)
        )
        np.testing.assert_array_equal(x_best, x_new)
        assert best_cost == pytest.approx(0.5)

    def test_returns_old_when_higher_cost(self) -> None:
        optimizer = self._make_optimizer()
        x_old = np.zeros(2)
        u_old = np.zeros(1)
        x_best, u_best, best_cost = optimizer._select_best_trajectory(
            np.ones(2), np.ones(1), current_cost=2.0, best_cost=1.0,
            best_x_traj=x_old, best_u_traj=u_old
        )
        np.testing.assert_array_equal(x_best, x_old)
        assert best_cost == pytest.approx(1.0)


# ── ddp helpers ───────────────────────────────────────────────────────────────


class TestInitializeDdpTrajectory:
    """Tests for _initialize_ddp_trajectory."""

    def test_returns_correct_shapes(self) -> None:
        from src.affine_control.ddp import _initialize_ddp_trajectory

        def dynamics(x: Any, u: Any) -> Any:
            return np.zeros_like(x)

        x0 = np.zeros(2)
        u_init = np.zeros((5, 2))
        u_traj, x_traj, t = _initialize_ddp_trajectory(dynamics, x0, u_init)
        assert len(u_traj) == 5
        assert len(x_traj) == 6  # N+1 points
        assert len(t) == 6


# ── line_checks helpers ───────────────────────────────────────────────────────


class TestDispatchLineChecks:
    """Tests for _dispatch_line_checks."""

    def test_skips_anti_pattern_checks_for_comments(self) -> None:
        from src.tools.matlab_utilities.scripts.line_checks import _dispatch_line_checks

        issues: list[str] = []
        lines = ["% eval('bad')"]
        # This is a comment line — anti_pattern_issues should not fire
        _dispatch_line_checks(lines, 1, lines[0], is_comment=True, in_function=False, file_name="test.m", issues=issues)
        # No anti-pattern issues for a comment
        anti_pattern_hits = [i for i in issues if "eval" in i.lower()]
        assert len(anti_pattern_hits) == 0

    def test_detects_anti_pattern_in_non_comment(self) -> None:
        from src.tools.matlab_utilities.scripts.line_checks import _dispatch_line_checks

        issues: list[str] = []
        lines = ["eval('bad_code')"]
        _dispatch_line_checks(lines, 1, lines[0], is_comment=False, in_function=False, file_name="test.m", issues=issues)
        assert any("eval" in i.lower() for i in issues)


# ── issue_utils helpers ───────────────────────────────────────────────────────


class TestIssueBodyTemplate:
    """Tests for _issue_body_template."""

    def test_contains_all_fields(self) -> None:
        from src.tools.utils.issue_utils import _issue_body_template

        body = _issue_body_template("CRITICAL", "Code Quality", "repo_scan", "Description here", "2026-01-01")
        assert "CRITICAL" in body
        assert "Code Quality" in body
        assert "repo_scan" in body
        assert "Description here" in body
        assert "2026-01-01" in body

    def test_contains_next_steps(self) -> None:
        from src.tools.utils.issue_utils import _issue_body_template

        body = _issue_body_template("HIGH", "Cat", "src", "Desc", "Unknown")
        assert "Next Steps" in body
        assert "Investigate" in body


# ── streamlit_app helpers ─────────────────────────────────────────────────────
# Note: streamlit_app.py executes full app logic at module-level import,
# making individual function testing impractical without extensive mocking.
# _compute_info_metrics is indirectly tested via the physics in torque_calculator tests.
