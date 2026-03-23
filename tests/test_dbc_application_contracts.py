"""Application-level Design by Contract (DbC) enforcement tests.

Verifies that the contracts added to affine_control and core modules
are correctly enforced at the application level.

Test categories:
1. Contract primitives (require, ensure, invariant)
2. DDP preconditions (state vectors, control trajectories)
3. Residual monitor invariants (mode transitions, hysteresis)
4. Parametrized numerical property sweeps
5. Quarto syntax scanner refactoring verification
"""

from __future__ import annotations

import os
from typing import Any

import numpy as np
import pytest

# Force contract enforcement for testing
os.environ["DBC_LEVEL"] = "enforce"

from src.affine_control.ddp import (  # noqa: E402
    _resample_controls,
    _simulate_trajectory,
    adaptive_timestep_ddp_mock,
    estimate_perturbation_size,
)
from src.affine_control.residuals import (  # noqa: E402
    ResidualMonitor,
    compute_hessian_bound,
    predict_residual_bound,
)
from src.core.contracts import (  # noqa: E402
    ContractViolationError,
    check_finite_array,
    check_positive,
    check_range,
    check_shape,
    require,
)

# ===================================================================
# 1. Contract Primitives
# ===================================================================


class TestContractPrimitives:
    """Test the core contracts module (require, ensure, check_*, etc.)."""

    def test_require_passes_on_true(self) -> None:
        require(True, "should pass")

    def test_require_raises_on_false(self) -> None:
        with pytest.raises(ContractViolationError, match="pre-condition"):
            require(False, "bool is false")

    def test_check_positive_rejects_zero(self) -> None:
        with pytest.raises(ContractViolationError):
            check_positive(0.0, "value")

    def test_check_positive_rejects_negative(self) -> None:
        with pytest.raises(ContractViolationError):
            check_positive(-1.0, "value")

    def test_check_positive_accepts_positive(self) -> None:
        check_positive(0.001, "value")

    def test_check_range_nominal(self) -> None:
        check_range(5.0, 0.0, 10.0, "value")

    def test_check_range_boundary(self) -> None:
        check_range(0.0, 0.0, 10.0, "value")
        check_range(10.0, 0.0, 10.0, "value")

    def test_check_range_rejects_out_of_bounds(self) -> None:
        with pytest.raises(ContractViolationError):
            check_range(11.0, 0.0, 10.0, "value")

    def test_check_finite_array_accepts_valid(self) -> None:
        check_finite_array(np.array([1.0, 2.0, 3.0]), "arr")

    def test_check_finite_array_rejects_nan(self) -> None:
        with pytest.raises(ContractViolationError):
            check_finite_array(np.array([1.0, np.nan, 3.0]), "arr")

    def test_check_finite_array_rejects_inf(self) -> None:
        with pytest.raises(ContractViolationError):
            check_finite_array(np.array([1.0, np.inf, 3.0]), "arr")

    def test_check_shape_accepts_correct(self) -> None:
        check_shape(np.zeros((3, 2)), (3, 2), "matrix")

    def test_check_shape_rejects_wrong(self) -> None:
        with pytest.raises(ContractViolationError):
            check_shape(np.zeros((3, 2)), (2, 3), "matrix")


# ===================================================================
# 2. DDP Preconditions
# ===================================================================


class TestDDPContracts:
    """Test DbC contracts on DDP module entry points."""

    def _linear_dynamics(
        self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]
    ) -> np.ndarray[Any, Any]:
        """Simple linear dynamics for testing: dx = -x + u."""
        return -x + u

    def test_estimate_perturbation_rejects_nan_state(self) -> None:
        with pytest.raises(ContractViolationError):
            estimate_perturbation_size(np.array([np.nan, 0.0]), np.array([0.0]))

    def test_estimate_perturbation_rejects_negative_noise(self) -> None:
        with pytest.raises(ContractViolationError):
            estimate_perturbation_size(
                np.array([1.0, 0.0]),
                np.array([0.0]),
                base_noise=-0.1,
            )

    @pytest.mark.parametrize(
        "x,expected_min",
        [
            (np.array([0.0, 0.0]), 0.01),  # base_noise only
            (np.array([10.0, 0.0]), 1.01),  # base + 0.1*10
            (np.array([1.0, 1.0]), 0.01 + 0.1 * np.sqrt(2)),  # base + 0.1*sqrt(2)
        ],
        ids=["zero_state", "large_state", "unit_state"],
    )
    def test_estimate_perturbation_parametrized(
        self, x: np.ndarray[Any, Any], expected_min: float
    ) -> None:
        result = estimate_perturbation_size(x, np.array([0.0]))
        assert result >= expected_min - 1e-10
        assert result >= 0

    def test_ddp_rejects_empty_control(self) -> None:
        with pytest.raises(ContractViolationError, match="u_init must not be empty"):
            adaptive_timestep_ddp_mock(
                self._linear_dynamics,
                np.array([1.0, 0.0]),
                np.array([0.0, 0.0]),
                np.array([]),
            )

    def test_ddp_rejects_mismatched_x0_xf(self) -> None:
        with pytest.raises(ContractViolationError, match="same shape"):
            adaptive_timestep_ddp_mock(
                self._linear_dynamics,
                np.array([1.0, 0.0]),
                np.array([0.0, 0.0, 0.0]),  # wrong shape
                np.array([[0.0, 0.0]]),
            )

    def test_ddp_rejects_negative_eps_residual(self) -> None:
        with pytest.raises(ContractViolationError):
            adaptive_timestep_ddp_mock(
                self._linear_dynamics,
                np.array([1.0, 0.0]),
                np.array([0.0, 0.0]),
                np.array([[0.0, 0.0]]),
                eps_residual=-0.01,
            )

    def test_simulate_trajectory_rejects_length_mismatch(self) -> None:
        with pytest.raises(ContractViolationError, match="t_grid length"):
            _simulate_trajectory(
                self._linear_dynamics,
                np.array([1.0]),
                np.array([[0.0]]),
                np.array([0.0, 0.01, 0.02, 0.03]),  # too many time points
            )

    def test_resample_empty_u_old(self) -> None:
        with pytest.raises(ContractViolationError, match="u_old must not be empty"):
            _resample_controls(
                np.array([]),
                np.array([0.0, 1.0]),
                np.array([0.5]),
            )


# ===================================================================
# 3. Residual Monitor Invariants
# ===================================================================


class TestResidualMonitorContracts:
    """Test DbC contracts and invariants on ResidualMonitor."""

    def test_monitor_rejects_negative_eps_warning(self) -> None:
        with pytest.raises(ContractViolationError):
            ResidualMonitor(eps_warning=-0.01)

    def test_monitor_rejects_critical_le_warning(self) -> None:
        with pytest.raises(ContractViolationError, match="exceed"):
            ResidualMonitor(eps_warning=0.05, eps_critical=0.01)

    def test_monitor_initial_mode_is_lqr(self) -> None:
        m = ResidualMonitor()
        assert m.mode == "LQR"

    def test_monitor_invariants_hold_after_update(self) -> None:
        m = ResidualMonitor(eps_warning=0.01, eps_critical=0.05)
        mode, r = m.update(np.array([0.001]), np.array([0.0]))
        assert mode in ("LQR", "MPC_WARN", "MPC_FULL")
        assert r >= 0

    @pytest.mark.parametrize(
        "n_high_updates",
        [1, 2, 3, 5],
        ids=["1_update", "2_updates", "3_updates", "5_updates"],
    )
    def test_monitor_mode_transition_with_high_residuals(self, n_high_updates: int) -> None:
        """Mode transitions through MPC_WARN before reaching MPC_FULL.

        With the three-state machine (LQR -> MPC_WARN -> MPC_FULL), n_hyst critical
        updates trigger LQR->MPC_WARN and another n_hyst trigger MPC_WARN->MPC_FULL.
        """
        n_hyst = 3
        m = ResidualMonitor(eps_warning=0.01, eps_critical=0.05, n_hysteresis=n_hyst)
        for _ in range(n_high_updates):
            mode, _ = m.update(np.array([1.0]), np.array([0.0]))  # r=1.0 >> eps_critical

        if n_high_updates >= 2 * n_hyst:
            assert mode == "MPC_FULL"
        elif n_high_updates >= n_hyst:
            assert mode == "MPC_WARN"
        else:
            assert mode == "LQR"

    def test_monitor_update_rejects_mismatched_shapes(self) -> None:
        m = ResidualMonitor()
        with pytest.raises(ContractViolationError, match="same shape"):
            m.update(np.array([1.0, 0.0]), np.array([0.0]))

    def test_monitor_update_rejects_nan(self) -> None:
        m = ResidualMonitor()
        with pytest.raises(ContractViolationError):
            m.update(np.array([np.nan]), np.array([0.0]))


# ===================================================================
# 4. Residual Bound Contracts
# ===================================================================


class TestResidualBoundContracts:
    """Test DbC on predict_residual_bound."""

    def test_rejects_empty_dt_traj(self) -> None:
        with pytest.raises(ContractViolationError, match="dt_traj must not be empty"):
            predict_residual_bound(
                np.array([1.0]),
                np.array([0.1]),
                np.array([]),
            )

    def test_rejects_nan_in_m_traj(self) -> None:
        with pytest.raises(ContractViolationError):
            predict_residual_bound(
                np.array([np.nan]),
                np.array([0.1]),
                np.array([0.01]),
            )

    @pytest.mark.parametrize(
        "M,dx,dt,expected_bound",
        [
            (np.array([2.0]), np.array([0.1]), np.array([0.01]), 0.0001),
            (np.array([0.0]), np.array([0.1]), np.array([0.01]), 0.0),
            (np.array([1.0, 1.0]), np.array([0.1, 0.2]), np.array([0.01, 0.01]), None),
        ],
        ids=["simple", "zero_hessian", "multi_step"],
    )
    def test_residual_bound_parametrized(
        self,
        M: np.ndarray[Any, Any],
        dx: np.ndarray[Any, Any],
        dt: np.ndarray[Any, Any],
        expected_bound: float | None,
    ) -> None:
        result = predict_residual_bound(M, dx, dt)
        assert result >= 0  # postcondition: non-negative
        if expected_bound is not None:
            assert abs(result - expected_bound) < 1e-10

    def test_residual_bound_monotonic_with_hessian(self) -> None:
        """Larger Hessian bound → larger residual bound."""
        dx = np.array([0.1])
        dt = np.array([0.01])
        r1 = predict_residual_bound(np.array([1.0]), dx, dt)
        r2 = predict_residual_bound(np.array([10.0]), dx, dt)
        assert r2 > r1


# ===================================================================
# 5. Hessian Bound Contracts
# ===================================================================


class TestHessianBoundContracts:
    """Test DbC on compute_hessian_bound."""

    def _linear_f(self, x: np.ndarray[Any, Any], u: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        return -x + u

    def test_rejects_nan_state(self) -> None:
        with pytest.raises(ContractViolationError):
            compute_hessian_bound(self._linear_f, np.array([np.nan]), np.array([0.0]))

    def test_rejects_negative_epsilon(self) -> None:
        with pytest.raises(ContractViolationError):
            compute_hessian_bound(
                self._linear_f,
                np.array([1.0]),
                np.array([0.0]),
                epsilon=-1e-5,
            )

    def test_linear_system_near_zero_hessian(self) -> None:
        """A linear system f(x,u) = -x+u has zero Hessian (d²f/dx² = 0)."""
        M = compute_hessian_bound(
            self._linear_f,
            np.array([1.0]),
            np.array([0.0]),
        )
        assert M >= 0
        assert M < 1e-3  # should be numerically near zero for linear dynamics


# ===================================================================
# 6. Quarto Syntax Scanner (Refactored)
# ===================================================================


class TestQuartoSyntaxScanner:
    """Test the refactored QuartoSyntaxScanner preserves behavior."""

    def test_clean_file_no_errors(self, tmp_path: Any) -> None:
        from scripts.scan_quarto_syntax import check_file

        p = tmp_path / "clean.qmd"
        p.write_text("# Title\n\nSome text with $x^2$ math.\n\n$$E=mc^2$$\n")
        assert check_file(p) == []

    def test_detects_escaped_underscore_inline(self, tmp_path: Any) -> None:
        from scripts.scan_quarto_syntax import check_file

        p = tmp_path / "bad.qmd"
        p.write_text("Math: $x\\_i$\n")
        errors = check_file(p)
        assert len(errors) == 1
        assert "Escaped underscore" in errors[0][1]

    def test_detects_leading_space_inline(self, tmp_path: Any) -> None:
        from scripts.scan_quarto_syntax import check_file

        p = tmp_path / "bad.qmd"
        p.write_text("Math: $ x^2$\n")
        errors = check_file(p)
        assert len(errors) == 1
        assert "Leading space" in errors[0][1]

    def test_detects_deprecated_delimiters(self, tmp_path: Any) -> None:
        from scripts.scan_quarto_syntax import check_file

        p = tmp_path / "bad.qmd"
        p.write_text("Math: \\(x^2\\)\n")
        errors = check_file(p)
        assert any("\\(" in e[1] for e in errors)

    def test_ignores_code_blocks(self, tmp_path: Any) -> None:
        from scripts.scan_quarto_syntax import check_file

        p = tmp_path / "code.qmd"
        p.write_text("```\n$ x^2$\n```\n")
        assert check_file(p) == []

    def test_detects_unclosed_display_math(self, tmp_path: Any) -> None:
        from scripts.scan_quarto_syntax import check_file

        p = tmp_path / "unclosed.qmd"
        p.write_text("$$x^2\n")
        errors = check_file(p)
        assert any("Unclosed" in e[1] for e in errors)

    def test_detects_empty_inline_math(self, tmp_path: Any) -> None:
        from scripts.scan_quarto_syntax import check_file

        p = tmp_path / "empty.qmd"
        p.write_text("Empty: $$\n")
        errors = check_file(p)
        assert any("Empty" in e[1] or "Unclosed" in e[1] for e in errors)
