"""Property-based tests for the contracts and validators modules.

Uses Hypothesis to generate random inputs and verify invariant properties
of the Design by Contract (DbC) system:

- Contract primitives (require, ensure, invariant) are consistent
- Validators maintain their algebraic properties
- Exception hierarchy is well-formed
- Level switching is consistent
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

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

# ─── Helpers ──────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _enforce_contracts() -> Generator[None, None, None]:
    """Ensure all tests run with contracts enforced, then restore."""
    original = get_contract_level()
    set_contract_level(ContractLevel.ENFORCE)
    yield
    set_contract_level(original)


# ─── Strategies ───────────────────────────────────────────────

# Finite floats (no NaN, no Inf)
finite_floats = st.floats(allow_nan=False, allow_infinity=False)
positive_floats = st.floats(min_value=1e-300, allow_nan=False, allow_infinity=False)
non_negative_floats = st.floats(min_value=0.0, allow_nan=False, allow_infinity=False)


# ─── Contract Primitive Properties ────────────────────────────


class TestRequireProperties:
    """Property tests for the require() primitive."""

    @given(condition=st.booleans())
    def test_true_conditions_never_raise(self, condition: bool) -> None:
        """require(True, ...) never raises regardless of message."""
        if condition:
            require(condition, "always satisfied")
            # If we reach here, the property holds

    @given(message=st.text(min_size=1))
    def test_false_condition_always_raises(self, message: str) -> None:
        """require(False, message) always raises with the message embedded."""
        with pytest.raises(ContractViolationError) as exc_info:
            require(False, message)
        assert message in str(exc_info.value)

    @given(message=st.text(), value=st.integers() | st.floats() | st.text())
    def test_violation_preserves_value(self, message: str, value: Any) -> None:
        """The violation exception captures the offending value."""
        with pytest.raises(ContractViolationError) as exc_info:
            require(False, message, value)
        assert exc_info.value.value is value

    @given(condition=st.booleans(), message=st.text())
    def test_off_level_never_raises(self, condition: bool, message: str) -> None:
        """When level is OFF, require never raises regardless of condition."""
        original = get_contract_level()
        try:
            set_contract_level(ContractLevel.OFF)
            require(condition, message)  # Should never raise
        finally:
            set_contract_level(original)


class TestEnsureProperties:
    """Property tests for the ensure() primitive."""

    @given(condition=st.booleans())
    def test_ensure_mirrors_require_on_true(self, condition: bool) -> None:
        """ensure() should behave identically to require() for True conditions."""
        if condition:
            ensure(condition, "postcondition satisfied")

    @given(message=st.text(min_size=1))
    def test_ensure_raises_on_false(self, message: str) -> None:
        """ensure(False, msg) raises with 'post-condition' label."""
        with pytest.raises(ContractViolationError) as exc_info:
            ensure(False, message)
        assert "post-condition" in str(exc_info.value)


class TestInvariantProperties:
    """Property tests for the invariant() primitive."""

    @given(message=st.text(min_size=1))
    def test_invariant_raises_on_false(self, message: str) -> None:
        """invariant(False, msg) raises with 'invariant' label."""
        with pytest.raises(ContractViolationError) as exc_info:
            invariant(False, message)
        assert "invariant" in str(exc_info.value)


# ─── Exception Hierarchy Properties ──────────────────────────


class TestExceptionHierarchy:
    """Verify the exception hierarchy is well-formed."""

    def test_all_violations_are_assertion_errors(self) -> None:
        """All contract violations inherit from AssertionError."""
        assert issubclass(ContractViolationError, AssertionError)
        assert issubclass(PreconditionError, ContractViolationError)
        assert issubclass(PostconditionError, ContractViolationError)
        assert issubclass(InvariantError, ContractViolationError)

    def test_all_violations_are_value_errors(self) -> None:
        """All contract violations also inherit from ValueError."""
        assert issubclass(ContractViolationError, ValueError)

    @given(message=st.text(min_size=1))
    def test_precondition_error_labels_correctly(self, message: str) -> None:
        """PreconditionError always labels as 'pre-condition'."""
        err = PreconditionError(message)
        assert "pre-condition" in str(err)

    @given(message=st.text(min_size=1))
    def test_postcondition_error_labels_correctly(self, message: str) -> None:
        """PostconditionError always labels as 'post-condition'."""
        err = PostconditionError(message)
        assert "post-condition" in str(err)

    @given(message=st.text(min_size=1))
    def test_invariant_error_labels_correctly(self, message: str) -> None:
        """InvariantError always labels as 'invariant'."""
        err = InvariantError(message)
        assert "invariant" in str(err)


# ─── Level Switching Properties ──────────────────────────────


class TestLevelSwitching:
    """Property tests for contract level management."""

    @given(level=st.sampled_from(list(ContractLevel)))
    def test_set_get_roundtrip(self, level: ContractLevel) -> None:
        """set_contract_level(x); get_contract_level() == x."""
        original = get_contract_level()
        try:
            set_contract_level(level)
            assert get_contract_level() == level
        finally:
            set_contract_level(original)

    @given(level=st.sampled_from(list(ContractLevel)))
    def test_level_idempotent(self, level: ContractLevel) -> None:
        """Setting the same level twice is the same as setting it once."""
        original = get_contract_level()
        try:
            set_contract_level(level)
            first = get_contract_level()
            set_contract_level(level)
            second = get_contract_level()
            assert first == second
        finally:
            set_contract_level(original)


# ─── Validator Properties ─────────────────────────────────────


class TestCheckPositiveProperties:
    """Property tests for check_positive validator."""

    @given(value=positive_floats)
    def test_positive_values_pass(self, value: float) -> None:
        """All strictly positive finite values must pass."""
        check_positive(value, "test_value")

    @given(value=st.floats(max_value=0.0, allow_nan=False, allow_infinity=False))
    def test_non_positive_values_fail(self, value: float) -> None:
        """All non-positive values must raise."""
        with pytest.raises(ContractViolationError):
            check_positive(value, "test_value")


class TestCheckNonNegativeProperties:
    """Property tests for check_non_negative validator."""

    @given(value=non_negative_floats)
    def test_non_negative_values_pass(self, value: float) -> None:
        """All non-negative finite values must pass."""
        check_non_negative(value, "test_value")

    @given(value=st.floats(max_value=-1e-300, allow_nan=False, allow_infinity=False))
    def test_negative_values_fail(self, value: float) -> None:
        """All negative values must raise."""
        with pytest.raises(ContractViolationError):
            check_non_negative(value, "test_value")


class TestCheckRangeProperties:
    """Property tests for check_range validator."""

    @given(
        bounds=st.tuples(finite_floats, finite_floats).filter(lambda t: t[0] <= t[1]),
    )
    def test_bounds_include_endpoints(self, bounds: tuple[float, float]) -> None:
        """Endpoints of the range must always pass."""
        low, high = bounds
        check_range(low, low, high, "test_low")
        check_range(high, low, high, "test_high")

    @given(
        vals=st.tuples(finite_floats, finite_floats, finite_floats)
        .filter(lambda t: t[0] <= t[1])
        .filter(lambda t: t[0] <= t[2] <= t[1]),
    )
    def test_interior_values_pass(self, vals: tuple[float, float, float]) -> None:
        """Values between low and high (inclusive) must pass."""
        low, high, value = vals
        check_range(value, low, high, "test_value")

    @given(
        vals=st.tuples(finite_floats, finite_floats, finite_floats)
        .filter(lambda t: t[0] < t[1])
        .filter(lambda t: t[2] < t[0] or t[2] > t[1]),
    )
    def test_exterior_values_fail(self, vals: tuple[float, float, float]) -> None:
        """Values outside [low, high] must raise."""
        low, high, value = vals
        with pytest.raises(ContractViolationError):
            check_range(value, low, high, "test_value")


class TestCheckFiniteArrayProperties:
    """Property tests for check_finite_array validator."""

    @given(
        values=st.lists(
            st.floats(allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=100,
        )
    )
    def test_finite_arrays_pass(self, values: list[float]) -> None:
        """Arrays with only finite values must pass."""
        arr = np.array(values)
        check_finite_array(arr, "test_array")

    @given(
        values=st.lists(
            st.floats(allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=50,
        ),
        special=st.sampled_from([float("nan"), float("inf"), float("-inf")]),
    )
    def test_arrays_with_special_values_fail(self, values: list[float], special: float) -> None:
        """Arrays containing NaN or Inf must raise."""
        arr = np.array(values + [special])
        with pytest.raises(ContractViolationError):
            check_finite_array(arr, "test_array")


class TestCheckShapeProperties:
    """Property tests for check_shape validator."""

    @given(
        shape=st.tuples(
            st.integers(min_value=1, max_value=10),
            st.integers(min_value=1, max_value=10),
        )
    )
    def test_correct_shape_passes(self, shape: tuple[int, int]) -> None:
        """Arrays with the expected shape must pass."""
        arr = np.zeros(shape)
        check_shape(arr, shape, "test_array")

    @given(
        shape=st.tuples(
            st.integers(min_value=1, max_value=10),
            st.integers(min_value=1, max_value=10),
        )
    )
    def test_wrong_shape_fails(self, shape: tuple[int, int]) -> None:
        """Arrays with a different shape must raise."""
        wrong_shape = (shape[0] + 1, shape[1])
        arr = np.zeros(wrong_shape)
        with pytest.raises(ContractViolationError):
            check_shape(arr, shape, "test_array")


# ─── Decorator Properties ─────────────────────────────────────


class TestDecoratorProperties:
    """Property tests for precondition/postcondition decorators."""

    @given(x=positive_floats)
    def test_precondition_passes_valid_input(self, x: float) -> None:
        """Decorated function executes normally with valid input."""

        @precondition(lambda x: x > 0, "x must be positive")
        def square(x: float) -> float:
            return x * x

        result = square(x)
        assert result == x * x

    @given(x=st.floats(max_value=0.0, allow_nan=False, allow_infinity=False))
    def test_precondition_rejects_invalid_input(self, x: float) -> None:
        """Decorated function raises with invalid input."""

        @precondition(lambda x: x > 0, "x must be positive")
        def square(x: float) -> float:
            return x * x

        with pytest.raises(ContractViolationError):
            square(x)

    @given(x=positive_floats)
    def test_postcondition_accepts_valid_output(self, x: float) -> None:
        """Postcondition passes when return value satisfies condition."""

        @postcondition(lambda result: result >= 0, "result must be non-negative")
        def square(x: float) -> float:
            return x * x

        result = square(x)
        assert result >= 0


# ─── ContractChecker Mixin Properties ─────────────────────────


class TestContractCheckerProperties:
    """Property tests for the ContractChecker mixin."""

    @given(value=positive_floats)
    def test_valid_invariant_passes(self, value: float) -> None:
        """ContractChecker with satisfied invariants returns True."""

        class TestClass(ContractChecker):
            def __init__(self, v: float) -> None:
                self.value = v

            def _get_invariants(self) -> list[tuple[Any, str]]:
                return [(lambda: self.value > 0, "value must be positive")]

        obj = TestClass(value)
        assert obj.verify_invariants() is True

    @given(value=st.floats(max_value=0.0, allow_nan=False, allow_infinity=False))
    def test_violated_invariant_raises(self, value: float) -> None:
        """ContractChecker with violated invariants raises InvariantError."""

        class TestClass(ContractChecker):
            def __init__(self, v: float) -> None:
                self.value = v

            def _get_invariants(self) -> list[tuple[Any, str]]:
                return [(lambda: self.value > 0, "value must be positive")]

        obj = TestClass(value)
        with pytest.raises(InvariantError):
            obj.verify_invariants()

    @given(value=positive_floats)
    def test_invariant_checked_decorator(self, value: float) -> None:
        """invariant_checked decorator verifies invariants after method call."""

        class TestClass(ContractChecker):
            def __init__(self, v: float) -> None:
                self.value = v

            def _get_invariants(self) -> list[tuple[Any, str]]:
                return [(lambda: self.value > 0, "value must be positive")]

            @invariant_checked
            def double(self) -> float:
                self.value *= 2
                return self.value

        obj = TestClass(value)
        result = obj.double()
        assert result == value * 2
