"""Tests for the optimizer factory (src/core/optimizers/optimizer_factory.py) — issue #3230."""

import numpy as np
import pytest

from src.core.optimizers.optimizer_factory import (
    ILQRSolver,
    get_default_optimizer,
    ilqr_solver_wrapper,
)


class TestGetDefaultOptimizer:
    def test_returns_ilqr_solver(self):
        # TrajectoryOptimizer is a (non-runtime-checkable) Protocol; assert the
        # concrete default implementation type instead.
        assert isinstance(get_default_optimizer(), ILQRSolver)

    def test_default_optimizer_exposes_optimize(self):
        opt = get_default_optimizer()
        assert hasattr(opt, "optimize")
        assert callable(opt.optimize)


class TestIlqrSolverWrapperContracts:
    """DbC: invalid inputs must raise clear errors, not silently misbehave."""

    def _args(self):
        x0 = np.zeros(2)
        xf = np.ones(2)
        u_init = np.zeros((3, 1))
        return x0, xf, u_init

    def test_non_callable_dynamics_raises(self):
        x0, xf, u_init = self._args()
        with pytest.raises((ValueError, AssertionError, TypeError)):
            ilqr_solver_wrapper("not callable", x0, xf, u_init)

    def test_mismatched_shapes_raise(self):
        _x0, _xf, u_init = self._args()
        x0 = np.zeros(2)
        xf = np.ones(3)  # shape mismatch

        def f(x, u):
            return x

        with pytest.raises((ValueError, AssertionError)):
            ilqr_solver_wrapper(f, x0, xf, u_init)

    def test_empty_u_init_raises(self):
        x0, xf, _u = self._args()

        def f(x, u):
            return x

        with pytest.raises((ValueError, AssertionError)):
            ilqr_solver_wrapper(f, x0, xf, np.zeros((0, 1)))

    def test_nonpositive_eps_residual_raises(self):
        x0, xf, u_init = self._args()

        def f(x, u):
            return x

        with pytest.raises((ValueError, AssertionError)):
            ilqr_solver_wrapper(f, x0, xf, u_init, eps_residual=0.0)

    def test_max_iters_below_one_raises(self):
        x0, xf, u_init = self._args()

        def f(x, u):
            return x

        with pytest.raises((ValueError, AssertionError)):
            ilqr_solver_wrapper(f, x0, xf, u_init, max_iters=0)
