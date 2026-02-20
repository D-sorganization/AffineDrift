"""Tests for tests.helpers.numerical — shared numerical test utilities.

We follow TDD: these tests were written *before* the helpers, then the
helpers were iterated until all tests passed.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from tests.helpers.numerical import (
    assert_all_finite,
    assert_close,
    assert_conserved,
    assert_lyapunov_stable,
    assert_monotonic,
    assert_positive_definite,
    is_finite,
)


# ======================================================================
# assert_close
# ======================================================================

class TestAssertClose:
    """Tests for assert_close."""

    def test_exact_match(self) -> None:
        assert_close(1.0, 1.0, label="exact")

    def test_within_relative_tolerance(self) -> None:
        assert_close(1.0000001, 1.0, rtol=1e-6, label="rtol")

    def test_within_absolute_tolerance(self) -> None:
        assert_close(0.0001, 0.0, atol=1e-3, label="atol")

    def test_fails_outside_tolerance(self) -> None:
        with pytest.raises(AssertionError, match="expected 1.0"):
            assert_close(2.0, 1.0, rtol=1e-7, label="mismatch")

    def test_negative_rtol_rejected(self) -> None:
        with pytest.raises(ValueError, match="rtol must be >= 0"):
            assert_close(1.0, 1.0, rtol=-0.1)

    def test_negative_atol_rejected(self) -> None:
        with pytest.raises(ValueError, match="atol must be >= 0"):
            assert_close(1.0, 1.0, atol=-0.1)

    def test_diagnostic_message_includes_label(self) -> None:
        with pytest.raises(AssertionError, match="my_quantity"):
            assert_close(10.0, 1.0, label="my_quantity")

    def test_zero_expected_with_atol(self) -> None:
        """When expected is zero, rtol alone is useless; need atol."""
        assert_close(1e-10, 0.0, atol=1e-9, label="near_zero")


# ======================================================================
# assert_conserved
# ======================================================================

class TestAssertConserved:
    """Tests for assert_conserved."""

    def test_conserved_quantity(self) -> None:
        assert_conserved(100.0, 100.0, "energy")

    def test_small_drift_within_tolerance(self) -> None:
        assert_conserved(100.0, 100.00005, "mass", rtol=1e-5)

    def test_large_drift_fails(self) -> None:
        with pytest.raises(AssertionError, match="Conservation of energy"):
            assert_conserved(100.0, 110.0, "energy", rtol=1e-3)

    def test_negative_rtol_rejected(self) -> None:
        with pytest.raises(ValueError, match="rtol must be >= 0"):
            assert_conserved(1.0, 1.0, "x", rtol=-1.0)


# ======================================================================
# assert_monotonic
# ======================================================================

class TestAssertMonotonic:
    """Tests for assert_monotonic."""

    def test_increasing(self) -> None:
        assert_monotonic([1, 2, 3, 4, 5], increasing=True)

    def test_decreasing(self) -> None:
        assert_monotonic([5, 4, 3, 2, 1], increasing=False)

    def test_non_strict_allows_equal(self) -> None:
        assert_monotonic([1, 1, 2, 2, 3], increasing=True, strict=False)

    def test_strict_rejects_equal(self) -> None:
        with pytest.raises(AssertionError, match="not strictly increasing"):
            assert_monotonic([1, 1, 2], increasing=True, strict=True)

    def test_not_monotonic_fails(self) -> None:
        with pytest.raises(AssertionError, match="not.*increasing"):
            assert_monotonic([1, 3, 2], increasing=True)

    def test_too_few_values_rejected(self) -> None:
        with pytest.raises(ValueError, match="at least 2"):
            assert_monotonic([1], increasing=True)

    def test_strict_decreasing(self) -> None:
        assert_monotonic([5, 4, 3], increasing=False, strict=True)

    def test_strict_decreasing_rejects_equal(self) -> None:
        with pytest.raises(AssertionError, match="not strictly decreasing"):
            assert_monotonic([5, 5, 3], increasing=False, strict=True)


# ======================================================================
# is_finite
# ======================================================================

class TestIsFinite:
    """Tests for is_finite."""

    def test_normal_float(self) -> None:
        assert is_finite(3.14) is True

    def test_nan(self) -> None:
        assert is_finite(float("nan")) is False

    def test_positive_inf(self) -> None:
        assert is_finite(float("inf")) is False

    def test_negative_inf(self) -> None:
        assert is_finite(float("-inf")) is False

    def test_zero(self) -> None:
        assert is_finite(0.0) is True

    def test_numpy_scalar(self) -> None:
        assert is_finite(np.float64(1.5)) is True

    def test_numpy_nan(self) -> None:
        assert is_finite(np.nan) is False


# ======================================================================
# assert_all_finite
# ======================================================================

class TestAssertAllFinite:
    """Tests for assert_all_finite."""

    def test_all_finite(self) -> None:
        assert_all_finite([1.0, 2.0, 3.0])

    def test_contains_nan(self) -> None:
        with pytest.raises(AssertionError, match=r"values\[1\] is not finite"):
            assert_all_finite([1.0, float("nan"), 3.0])

    def test_empty_rejected(self) -> None:
        with pytest.raises(ValueError, match="empty sequence"):
            assert_all_finite([])


# ======================================================================
# assert_positive_definite
# ======================================================================

class TestAssertPositiveDefinite:
    """Tests for assert_positive_definite."""

    def test_identity_is_pd(self) -> None:
        assert_positive_definite(np.eye(3), label="I_3")

    def test_scaled_identity_is_pd(self) -> None:
        assert_positive_definite(5 * np.eye(4), label="5I_4")

    def test_negative_definite_fails(self) -> None:
        with pytest.raises(AssertionError, match="not positive definite"):
            assert_positive_definite(-np.eye(3))

    def test_singular_fails(self) -> None:
        m = np.array([[1, 0], [0, 0]], dtype=float)
        with pytest.raises(AssertionError, match="not positive definite"):
            assert_positive_definite(m)

    def test_non_symmetric_fails(self) -> None:
        m = np.array([[1, 2], [3, 4]], dtype=float)
        with pytest.raises(AssertionError, match="not symmetric"):
            assert_positive_definite(m)

    def test_non_square_rejected(self) -> None:
        with pytest.raises(ValueError, match="must be square"):
            assert_positive_definite(np.ones((2, 3)))

    def test_1d_rejected(self) -> None:
        with pytest.raises(ValueError, match="must be 2-D"):
            assert_positive_definite(np.array([1, 2, 3]))

    def test_real_spd_matrix(self) -> None:
        """A real symmetric positive-definite matrix from control theory."""
        A = np.array([[2, -1], [-1, 2]], dtype=float)
        assert_positive_definite(A, label="control_gain")


# ======================================================================
# assert_lyapunov_stable
# ======================================================================

class TestAssertLyapunovStable:
    """Tests for assert_lyapunov_stable."""

    def test_decreasing_values(self) -> None:
        assert_lyapunov_stable([10.0, 8.0, 5.0, 3.0, 1.0])

    def test_constant_values(self) -> None:
        """Constant V is marginal stability — should pass."""
        assert_lyapunov_stable([5.0, 5.0, 5.0, 5.0])

    def test_increasing_values_fail(self) -> None:
        with pytest.raises(AssertionError, match="increased"):
            assert_lyapunov_stable([1.0, 2.0, 3.0])

    def test_negative_value_fails(self) -> None:
        with pytest.raises(AssertionError, match="negative"):
            assert_lyapunov_stable([1.0, -0.5])

    def test_too_few_values_rejected(self) -> None:
        with pytest.raises(ValueError, match="at least 2"):
            assert_lyapunov_stable([1.0])

    def test_tiny_numerical_increase_tolerated(self) -> None:
        """Floating-point noise should not trigger a failure."""
        V = [1.0, 1.0 + 1e-15, 0.9]
        assert_lyapunov_stable(V, rtol=1e-12)

    def test_negative_rtol_rejected(self) -> None:
        with pytest.raises(ValueError, match="rtol must be >= 0"):
            assert_lyapunov_stable([1.0, 0.5], rtol=-1.0)

    def test_converging_to_zero(self) -> None:
        """Exponential decay is Lyapunov stable."""
        V = [math.exp(-t * 0.1) for t in range(20)]
        assert_lyapunov_stable(V, label="exp_decay")
