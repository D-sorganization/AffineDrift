"""Tests for the Design-by-Contract enforcement module.

Validates all contract primitives, decorators, the ContractChecker mixin,
domain-specific helpers, and the tri-state enforcement level system.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from unittest.mock import patch

import numpy as np
import pytest

from src.core.contracts import (
    ContractChecker,
    ContractLevel,
    ContractViolationError,
    InvariantError,
    PostconditionError,
    PreconditionError,
    check_finite_array,
    check_non_negative,
    check_positive,
    check_range,
    check_shape,
    ensure,
    get_contract_level,
    invariant,
    invariant_checked,
    postcondition,
    precondition,
    require,
    set_contract_level,
)

# _enforce_contracts fixture is inherited from tests/conftest.py (issue #1251)


# ─── Exception Hierarchy ───────────────────────────────────────


class TestExceptionHierarchy:
    """Verify exception types and inheritance."""

    def test_contract_violation_inherits_assertion_and_value_error(self) -> None:
        err = ContractViolationError("pre-condition", "oops")
        assert isinstance(err, AssertionError)
        assert isinstance(err, ValueError)

    def test_precondition_error_type(self) -> None:
        err = PreconditionError("bad input", value=42)
        assert err.condition_type == "pre-condition"

    def test_postcondition_error_type(self) -> None:
        err = PostconditionError("bad output", value=-1)
        assert err.condition_type == "post-condition"

    def test_invariant_error_type(self) -> None:
        err = InvariantError("state broken")
        assert err.condition_type == "invariant"


# ─── Core Primitives ──────────────────────────────────────────


class TestRequire:
    """Tests for the require() function."""

    def test_passes_on_true(self) -> None:
        require(True, "should not fail")

    def test_raises_on_false(self) -> None:
        with pytest.raises(ContractViolationError, match="pre-condition"):
            require(False, "value must be positive", -1)

    def test_skipped_when_off(self) -> None:
        set_contract_level(ContractLevel.OFF)
        require(False, "should not raise")

    def test_warns_when_warn(self) -> None:
        set_contract_level(ContractLevel.WARN)
        require(False, "check warning mode")


class TestEnsure:
    """Tests for the ensure() function."""

    def test_passes_on_true(self) -> None:
        ensure(True, "ok")

    def test_raises_on_false(self) -> None:
        with pytest.raises(ContractViolationError, match="post-condition"):
            ensure(False, "result must be finite", float("nan"))


class TestInvariant:
    """Tests for the invariant() function."""

    def test_passes_on_true(self) -> None:
        invariant(True, "ok")

    def test_raises_on_false(self) -> None:
        with pytest.raises(ContractViolationError, match="invariant"):
            invariant(False, "state must be consistent", -10)


# ─── Decorator Contracts ──────────────────────────────────────


class TestPreconditionDecorator:
    """Tests for @precondition decorator."""

    def test_passes_valid_args(self) -> None:
        @precondition(lambda x: x > 0, "x must be positive")
        def sqrt(x: float) -> float:
            return x**0.5

        assert sqrt(4.0) == 2.0

    def test_raises_on_invalid_args(self) -> None:
        @precondition(lambda x: x > 0, "x must be positive")
        def sqrt(x: float) -> float:
            return x**0.5

        with pytest.raises(ContractViolationError, match="pre-condition"):
            sqrt(-1.0)


class TestPostconditionDecorator:
    """Tests for @postcondition decorator."""

    def test_passes_valid_result(self) -> None:
        @postcondition(lambda r: r >= 0, "result must be non-negative")
        def abs_val(x: float) -> float:
            return abs(x)

        assert abs_val(-5.0) == 5.0

    def test_raises_on_invalid_result(self) -> None:
        @postcondition(lambda r: r >= 0, "result must be non-negative")
        def bad_func(x: float) -> float:
            return -x

        with pytest.raises(ContractViolationError, match="post-condition"):
            bad_func(5.0)


# ─── ContractChecker Mixin ────────────────────────────────────


class TestContractChecker:
    """Tests for the ContractChecker mixin class."""

    def test_verify_invariants_pass(self) -> None:
        class Monitor(ContractChecker):
            def __init__(self) -> None:
                self.eps = 0.01

            def _get_invariants(
                self,
            ) -> list[tuple[Callable[[], bool], str]]:
                return [
                    (lambda: self.eps > 0, "eps must be positive"),
                ]

        m = Monitor()
        assert m.verify_invariants() is True

    def test_verify_invariants_fail(self) -> None:
        class Monitor(ContractChecker):
            def __init__(self) -> None:
                self.eps = -1.0

            def _get_invariants(
                self,
            ) -> list[tuple[Callable[[], bool], str]]:
                return [
                    (lambda: self.eps > 0, "eps must be positive"),
                ]

        m = Monitor()
        with pytest.raises(InvariantError, match="eps must be positive"):
            m.verify_invariants()

    def test_invariant_checked_decorator(self) -> None:
        class Monitor(ContractChecker):
            def __init__(self) -> None:
                self.count = 0

            def _get_invariants(
                self,
            ) -> list[tuple[Callable[[], bool], str]]:
                return [
                    (lambda: self.count >= 0, "count must be non-negative"),
                ]

            @invariant_checked
            def set_count(self, n: int) -> None:
                self.count = n

        m = Monitor()
        m.set_count(5)
        with pytest.raises(InvariantError):
            m.set_count(-1)


# ─── Array/Numeric Helpers ────────────────────────────────────


class TestArrayHelpers:
    """Tests for numeric/array contract helpers."""

    def test_check_finite_array_pass(self) -> None:
        check_finite_array(np.array([1.0, 2.0, 3.0]), "x")

    def test_check_finite_array_nan(self) -> None:
        with pytest.raises(ContractViolationError):
            check_finite_array(np.array([1.0, np.nan, 3.0]), "x")

    def test_check_finite_array_inf(self) -> None:
        with pytest.raises(ContractViolationError):
            check_finite_array(np.array([1.0, np.inf, 3.0]), "x")

    def test_check_positive_pass(self) -> None:
        check_positive(1.0, "x")

    def test_check_positive_fail(self) -> None:
        with pytest.raises(ContractViolationError):
            check_positive(-1.0, "x")

    def test_check_non_negative_pass(self) -> None:
        check_non_negative(0.0, "x")

    def test_check_non_negative_fail(self) -> None:
        with pytest.raises(ContractViolationError):
            check_non_negative(-0.1, "x")

    def test_check_range_pass(self) -> None:
        check_range(5.0, 0.0, 10.0, "x")

    def test_check_range_fail(self) -> None:
        with pytest.raises(ContractViolationError):
            check_range(11.0, 0.0, 10.0, "x")

    def test_check_shape_pass(self) -> None:
        check_shape(np.zeros((3, 3)), (3, 3), "matrix")

    def test_check_shape_fail(self) -> None:
        with pytest.raises(ContractViolationError):
            check_shape(np.zeros((3, 3)), (2, 2), "matrix")


# ─── Contract Level Controls ──────────────────────────────────


class TestContractLevelControls:
    """Tests for the tri-state enforcement level system."""

    def test_set_and_get(self) -> None:
        set_contract_level(ContractLevel.WARN)
        assert get_contract_level() == ContractLevel.WARN

    def test_off_skips_all_checks(self) -> None:
        set_contract_level(ContractLevel.OFF)
        require(False, "should not raise")
        ensure(False, "should not raise")
        invariant(False, "should not raise")

    def test_enforce_raises(self) -> None:
        set_contract_level(ContractLevel.ENFORCE)
        with pytest.raises(ContractViolationError):
            require(False, "should raise")

    def test_env_var_controls_level(self) -> None:
        with patch.dict(os.environ, {"DBC_LEVEL": "warn"}):
            from src.core.contracts.definitions import _resolve_contract_level

            level = _resolve_contract_level()
            assert level == ContractLevel.WARN


# ─── Integration: ResidualMonitor ─────────────────────────────


@pytest.mark.integration
class TestResidualMonitorContracts:
    """Tests that ResidualMonitor enforces contracts."""

    def test_constructor_rejects_invalid_eps(self) -> None:
        from src.affine_control.residuals import ResidualMonitor

        with pytest.raises(ContractViolationError):
            ResidualMonitor(eps_warning=-0.01)

    def test_constructor_rejects_eps_ordering(self) -> None:
        from src.affine_control.residuals import ResidualMonitor

        with pytest.raises(ContractViolationError):
            ResidualMonitor(eps_warning=0.1, eps_critical=0.05)

    def test_valid_construction(self) -> None:
        from src.affine_control.residuals import ResidualMonitor

        m = ResidualMonitor(eps_warning=0.01, eps_critical=0.05)
        assert m.verify_invariants() is True

    def test_update_maintains_invariants(self) -> None:
        from src.affine_control.residuals import ResidualMonitor

        m = ResidualMonitor()
        x_meas = np.array([1.0, 0.0])
        x_nom = np.array([1.0, 0.001])
        mode, r = m.update(x_meas, x_nom)
        assert isinstance(mode, str)
        assert r >= 0
        assert m.verify_invariants() is True
