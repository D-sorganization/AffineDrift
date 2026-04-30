"""Tests for src.core.contracts.definitions.

Targets the largely-uncovered code paths: tri-state enforcement (OFF/WARN/
ENFORCE), exception hierarchy, decorators, ContractChecker invariants, and
the WARN/OFF branches of the violation handler.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pytest

from src.core.contracts.definitions import (
    ContractChecker,
    ContractLevel,
    ContractViolationError,
    InvariantError,
    PostconditionError,
    PreconditionError,
    _resolve_contract_level,
    ensure,
    get_contract_level,
    invariant,
    invariant_checked,
    postcondition,
    precondition,
    require,
    set_contract_level,
)


@pytest.fixture(autouse=True)
def _restore_level():
    """Restore the global contract level after each test."""
    saved = get_contract_level()
    yield
    set_contract_level(saved)


# ── Enforcement level resolution ──────────────────────────────────────────


class TestContractLevelResolution:
    def test_resolve_default_when_env_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("DBC_LEVEL", raising=False)
        # default depends on __debug__; either ENFORCE or OFF, but it's deterministic
        result = _resolve_contract_level()
        assert result in (ContractLevel.ENFORCE, ContractLevel.OFF)

    @pytest.mark.parametrize(
        "env_value,expected",
        [
            ("off", ContractLevel.OFF),
            ("OFF", ContractLevel.OFF),
            ("warn", ContractLevel.WARN),
            ("ENFORCE", ContractLevel.ENFORCE),
            ("  enforce  ", ContractLevel.ENFORCE),
        ],
    )
    def test_resolve_from_env(
        self, monkeypatch: pytest.MonkeyPatch, env_value: str, expected: ContractLevel
    ) -> None:
        monkeypatch.setenv("DBC_LEVEL", env_value)
        assert _resolve_contract_level() == expected

    def test_resolve_invalid_env_falls_back(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DBC_LEVEL", "garbage")
        # Not a recognized value -> default branch
        assert _resolve_contract_level() in (ContractLevel.ENFORCE, ContractLevel.OFF)

    def test_set_and_get_level_round_trip(self) -> None:
        set_contract_level(ContractLevel.WARN)
        assert get_contract_level() is ContractLevel.WARN
        set_contract_level(ContractLevel.OFF)
        assert get_contract_level() is ContractLevel.OFF
        set_contract_level(ContractLevel.ENFORCE)
        assert get_contract_level() is ContractLevel.ENFORCE


# ── Exception hierarchy ────────────────────────────────────────────────────


class TestExceptionHierarchy:
    def test_precondition_is_contract_violation(self) -> None:
        e = PreconditionError("x must be positive", value=-1)
        assert isinstance(e, ContractViolationError)
        assert isinstance(e, AssertionError)
        assert isinstance(e, ValueError)
        assert e.condition_type == "pre-condition"
        assert "x must be positive" in str(e)
        assert "-1" in str(e)

    def test_postcondition_message(self) -> None:
        e = PostconditionError("result must be non-empty")
        assert "post-condition" in str(e)
        assert e.value is None

    def test_invariant_message(self) -> None:
        e = InvariantError("inv", value=42)
        assert e.condition_type == "invariant"
        assert "42" in str(e)

    def test_numpy_array_value_in_detail(self) -> None:
        arr = np.zeros((2, 3), dtype=np.float64)
        e = ContractViolationError("pre-condition", "bad", value=arr)
        msg = str(e)
        assert "shape=(2, 3)" in msg
        assert "float64" in msg


# ── require / ensure / invariant primitives ────────────────────────────────


class TestPrimitives:
    def test_require_passes_when_true(self) -> None:
        set_contract_level(ContractLevel.ENFORCE)
        require(True, "always")  # no raise

    def test_require_raises_in_enforce(self) -> None:
        set_contract_level(ContractLevel.ENFORCE)
        with pytest.raises(ContractViolationError):
            require(False, "must be true", value=0)

    def test_require_warns_in_warn_level(self, caplog: pytest.LogCaptureFixture) -> None:
        set_contract_level(ContractLevel.WARN)
        with caplog.at_level(logging.WARNING):
            require(False, "warn me", value="bad")
        assert any("warn me" in rec.message for rec in caplog.records)

    def test_require_silent_when_off(self, caplog: pytest.LogCaptureFixture) -> None:
        set_contract_level(ContractLevel.OFF)
        with caplog.at_level(logging.WARNING):
            require(False, "should not raise or warn")
        assert not any("should not raise" in rec.message for rec in caplog.records)

    def test_ensure_raises_post(self) -> None:
        set_contract_level(ContractLevel.ENFORCE)
        with pytest.raises(ContractViolationError) as exc:
            ensure(False, "post fail")
        assert "post-condition" in str(exc.value)

    def test_invariant_raises(self) -> None:
        set_contract_level(ContractLevel.ENFORCE)
        with pytest.raises(ContractViolationError) as exc:
            invariant(False, "inv fail")
        assert "invariant" in str(exc.value)

    def test_invariant_off_returns_none(self) -> None:
        set_contract_level(ContractLevel.OFF)
        assert invariant(False, "ignored") is None
        assert ensure(False, "ignored") is None


# ── precondition / postcondition decorators ────────────────────────────────


class TestPreconditionDecorator:
    def test_passes_when_condition_true(self) -> None:
        set_contract_level(ContractLevel.ENFORCE)

        @precondition(lambda x: x > 0, "x must be positive")
        def sqrt_(x: float) -> float:
            return x**0.5

        assert sqrt_(4.0) == 2.0

    def test_raises_when_condition_false(self) -> None:
        set_contract_level(ContractLevel.ENFORCE)

        @precondition(lambda x: x > 0, "x must be positive")
        def sqrt_(x: float) -> float:
            return x**0.5

        with pytest.raises(ContractViolationError):
            sqrt_(-1.0)

    def test_handles_predicate_exception(self) -> None:
        set_contract_level(ContractLevel.ENFORCE)

        def bad_pred(x: Any) -> bool:
            raise TypeError("cannot evaluate")

        @precondition(bad_pred, "bad predicate")
        def f(x: Any) -> int:
            return 1

        # The TypeError inside the predicate is handled and reported via
        # _handle_violation; in ENFORCE mode that raises.
        with pytest.raises(ContractViolationError):
            f(123)

    def test_off_returns_func_unchanged(self) -> None:
        set_contract_level(ContractLevel.OFF)

        def raw(x: int) -> int:
            return x + 1

        decorated = precondition(lambda x: False, "ignored")(raw)
        # In OFF mode the decorator returns the original function
        assert decorated is raw
        assert decorated(2) == 3


class TestPostconditionDecorator:
    def test_passes_when_result_valid(self) -> None:
        set_contract_level(ContractLevel.ENFORCE)

        @postcondition(lambda r: r >= 0, "must be non-negative")
        def square(x: int) -> int:
            return x * x

        assert square(-3) == 9

    def test_raises_when_result_invalid(self) -> None:
        set_contract_level(ContractLevel.ENFORCE)

        @postcondition(lambda r: r >= 0, "must be non-negative")
        def negate(x: int) -> int:
            return -abs(x)

        with pytest.raises(ContractViolationError):
            negate(5)

    def test_predicate_exception_handled(self) -> None:
        set_contract_level(ContractLevel.WARN)

        def bad_post(r: Any) -> bool:
            raise ValueError("explodes")

        @postcondition(bad_post, "bad postcondition")
        def f() -> int:
            return 1

        # Should NOT raise in WARN mode even when predicate explodes
        assert f() == 1

    def test_off_returns_func_unchanged(self) -> None:
        set_contract_level(ContractLevel.OFF)

        def raw() -> int:
            return 1

        assert postcondition(lambda r: False)(raw) is raw


# ── ContractChecker mixin & invariant_checked decorator ────────────────────


class _Counter(ContractChecker):
    def __init__(self) -> None:
        self.value = 0

    def _get_invariants(self):  # type: ignore[no-untyped-def]
        return [
            (lambda: self.value >= 0, "value must be non-negative"),
        ]

    @invariant_checked
    def increment(self) -> None:
        self.value += 1

    @invariant_checked
    def break_(self) -> None:
        self.value = -1  # violates invariant


class _BadInvariant(ContractChecker):
    def _get_invariants(self):  # type: ignore[no-untyped-def]
        # Predicate that raises to exercise the except branch
        def boom() -> bool:
            raise RuntimeError("boom in predicate")

        return [(boom, "exploding predicate")]


class TestContractChecker:
    def test_invariants_hold_after_valid_method(self) -> None:
        set_contract_level(ContractLevel.ENFORCE)
        c = _Counter()
        c.increment()
        assert c.value == 1
        assert c.verify_invariants() is True

    def test_invariant_violation_raises(self) -> None:
        set_contract_level(ContractLevel.ENFORCE)
        c = _Counter()
        with pytest.raises(InvariantError):
            c.break_()

    def test_invariant_violation_warn_does_not_raise(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        set_contract_level(ContractLevel.WARN)
        c = _Counter()
        c.value = -5  # set directly to bypass decorator
        with caplog.at_level(logging.WARNING):
            assert c.verify_invariants() is True
        assert any("non-negative" in rec.message for rec in caplog.records)

    def test_off_mode_skips_check(self) -> None:
        set_contract_level(ContractLevel.OFF)
        c = _Counter()
        c.value = -100  # invalid
        assert c.verify_invariants() is True

    def test_predicate_exception_wrapped_in_invariant_error(self) -> None:
        set_contract_level(ContractLevel.ENFORCE)
        b = _BadInvariant()
        with pytest.raises(InvariantError) as exc:
            b.verify_invariants()
        assert "Failed to evaluate invariant" in str(exc.value)

    def test_default_get_invariants_is_empty(self) -> None:
        set_contract_level(ContractLevel.ENFORCE)

        class Plain(ContractChecker):
            pass

        assert Plain().verify_invariants() is True

    def test_invariant_checked_off_mode_returns_func(self) -> None:
        set_contract_level(ContractLevel.OFF)

        def f(self: Any) -> int:
            return 7

        decorated = invariant_checked(f)
        assert decorated is f
