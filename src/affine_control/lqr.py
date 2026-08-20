"""Discrete-time LQR, solved rather than asserted.

The textbooks print worked LQR examples whose matrices were typed in by hand. In
Volume I chapter 6 the printed gain produced a closed loop with spectral radius
1.043 -- unstable -- directly beneath the sentence "Both eigenvalues lie inside
the unit circle, confirming stability", and the printed ``S`` was not a solution
of the Riccati equation at all (residual norm 16.25).

This module exists so those numbers come from a solve. Every quantity the text
quotes is returned by :func:`discrete_lqr` and carries a checkable property:
``S`` symmetric positive definite, the Riccati residual at machine precision,
and the closed-loop spectral radius strictly inside the unit circle.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

__all__ = ["LQRSolution", "discrete_lqr"]


type Array = NDArray[np.float64]
type ComplexArray = NDArray[np.complex128]

# The recursion converges linearly; 10_000 iterations is far past the point where
# a stabilisable, detectable pair has settled to machine precision.
_MAX_ITERATIONS = 10_000
_TOLERANCE = 1e-14
# Well past any physically meaningful cost-to-go, but far below overflow, so a
# diverging recursion is reported as such rather than as inf or NaN.
_DIVERGENCE_LIMIT = 1e12


@dataclass(frozen=True)
class LQRSolution:
    """Steady-state solution of the discrete-time LQR problem.

    Attributes mirror the quantities a worked example quotes, so a chapter can
    be generated from this object instead of from a transcription of it.
    """

    riccati: Array
    """``S``, the stabilising solution of the discrete algebraic Riccati equation."""

    gain: Array
    """``K = (R + B'SB)^-1 B'SA``."""

    closed_loop: Array
    """``A - BK``."""

    def eigenvalues_riccati(self) -> Array:
        """Eigenvalues of ``S``, ascending. Real, since ``S`` is symmetric."""
        return np.linalg.eigvalsh(self.riccati)

    def eigenvalues_closed_loop(self) -> ComplexArray:
        """Eigenvalues of ``A - BK``.

        Typed complex because a real closed loop with an oscillatory mode has a
        conjugate pair; callers that need reals must take magnitudes or use
        :func:`numpy.real_if_close` deliberately rather than by assumption.
        """
        return np.asarray(np.linalg.eigvals(self.closed_loop), dtype=np.complex128)

    def spectral_radius(self) -> float:
        """Largest closed-loop eigenvalue magnitude. Stability requires ``< 1``."""
        return float(np.max(np.abs(self.eigenvalues_closed_loop())))

    def condition_number(self) -> float:
        """``lambda_max(S) / lambda_min(S)``."""
        eigenvalues = self.eigenvalues_riccati()
        return float(eigenvalues.max() / eigenvalues.min())

    def residual(self, a: Array, b: Array, q: Array, r: Array) -> float:
        """Frobenius norm of the Riccati residual. Zero for a true solution."""
        s = self.riccati
        gain_term = a.T @ s @ b @ np.linalg.solve(r + b.T @ s @ b, b.T @ s @ a)
        return float(np.linalg.norm(a.T @ s @ a - s - gain_term + q))

    def stage_cost(self, q: Array, r: Array) -> Array:
        """``Q + K'RK``, the stage cost along the closed loop."""
        return q + self.gain.T @ r @ self.gain

    def contraction_rate(self, q: Array, r: Array) -> float:
        """``1 - lambda_min(Q + K'RK) / lambda_max(S)``.

        The standard Riccati bound on the decay of ``V_k = x' S x`` per step. It
        is a *bound*: an actual trajectory usually decays faster, which is why a
        table of ``V_k`` must be simulated rather than filled in with ``rho^k``.
        """
        alpha = float(np.min(np.linalg.eigvalsh(self.stage_cost(q, r))))
        return 1.0 - alpha / float(self.eigenvalues_riccati().max())

    def value_trajectory(self, x0: Array, steps: int) -> list[tuple[int, float, float]]:
        """Simulate ``(k, V_k, ||x_k||)`` under the closed loop.

        Returns ``steps + 1`` rows starting at ``k = 0``.
        """
        x = np.asarray(x0, dtype=float).reshape(-1)
        rows: list[tuple[int, float, float]] = []
        for k in range(steps + 1):
            rows.append((k, float(x @ self.riccati @ x), float(np.linalg.norm(x))))
            x = self.closed_loop @ x
        return rows


def discrete_lqr(a: Array, b: Array, q: Array, r: Array) -> LQRSolution:
    """Solve the discrete-time algebraic Riccati equation by value iteration.

    Iterates ``S <- Q + A'S(A - BK)`` to a fixed point. Value iteration rather
    than a Schur solve keeps the dependency surface at numpy alone, and for the
    small, well-conditioned systems the textbooks use it converges to machine
    precision well inside the iteration cap.

    Raises:
        ValueError: if the recursion does not converge, which for a stabilisable
            and detectable pair means the problem data is malformed.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    q = np.asarray(q, dtype=float)
    r = np.asarray(r, dtype=float)

    s = q.copy()
    for _ in range(_MAX_ITERATIONS):
        gain = np.linalg.solve(r + b.T @ s @ b, b.T @ s @ a)
        s_next = q + a.T @ s @ (a - b @ gain)
        s_next = 0.5 * (s_next + s_next.T)  # keep it symmetric against drift
        # An unreachable unstable mode makes S grow without bound. Catch that
        # here rather than letting it overflow to inf and then to NaN, which
        # would still terminate but only by accident and with warnings.
        if not np.all(np.isfinite(s_next)) or np.max(np.abs(s_next)) > _DIVERGENCE_LIMIT:
            raise ValueError(
                "Riccati recursion diverged; (A, B) is not stabilisable "
                "(an unstable mode is unreachable from the input)."
            )
        if np.max(np.abs(s_next - s)) < _TOLERANCE:
            s = s_next
            break
        s = s_next
    else:
        raise ValueError(
            f"Riccati recursion did not converge in {_MAX_ITERATIONS} iterations; "
            "check that (A, B) is stabilisable and (A, Q^1/2) detectable."
        )

    gain = np.linalg.solve(r + b.T @ s @ b, b.T @ s @ a)
    return LQRSolution(riccati=s, gain=gain, closed_loop=a - b @ gain)
