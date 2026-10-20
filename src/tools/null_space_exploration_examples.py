"""Companion examples for the null-space exploration propositions P1-P5 and P7 (#5094).

Self-contained (numpy and scipy only) numerical companion to the article "After One Solution:
Exploring Dynamically Equivalent Force Allocations".  Every number the article quotes about the
*linear* propositions is generated here:

- P1  affine completeness and emptiness: :func:`affine_fibre`.
- P2  weighted selection and the W-self-adjoint projector: :func:`weighted_representative`;
  unit rescaling moves the representative inside the fibre, never off it:
  :func:`rescaled_representative`.
- P3  reduction equivalence and the reduced Hessian ``Z^T H Z``: :func:`reduced_quadratic`,
  checked against a full KKT solve (:func:`kkt_minimiser`).
- P4  functional invariance and attainable intervals: :func:`functional_invariance` (a
  *numerical* test at a declared tolerance; the exact theorem is ``Z^T c = 0``) and
  :func:`functional_interval` (an LP over the polyhedral fibre, with infeasible and unbounded
  outcomes reported explicitly).
- P5  approximate-null leakage bound: :func:`leakage_bound`.
- P7  temporal containment: :func:`framewise_vs_coupled_envelope` (rate coupling never widens
  an envelope and is equal to the frame-wise envelope without coupling).

Envelopes here are LP extrema over the *declared polyhedral* constraints only.

JSON layout
-----------
``scripts/build_null_space_exploration_examples.py`` writes
``data/null_space_exploration/examples.json`` as::

    {"schema_version": 1, "sections": {"<name>": {...}, ...}}

where each ``<name>`` is produced by one callable registered in that script's
``SECTION_BUILDERS``.  This module owns the section ``"linear"`` (:func:`linear_section`); the
nonlinear-continuation companion registers its own section next to it.
"""

import math
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import linprog

type Array = NDArray[np.float64]
type Interval = tuple[float, float]

SEED = 5094  # Seeds every random draw in :func:`linear_section`.
PSD_RTOL = 1e-12  # Relative eigenvalue floor for "positive definite" checks.
PINV_RCOND = 1e-12  # Truncation for the Gram-matrix pseudo-inverse in P2.
CONSISTENCY_RTOL = 1e-8  # Relative residual under which A u = b counts as solved (P2).
CONTAINMENT_ATOL = (
    1e-6  # Slack when comparing LP envelopes: 10x HiGHS primal feasibility tol (1e-7).
)
FRICTION_COEFFICIENT = 0.5  # Declared polygonal friction cone of the grip toy.
GRIP_HALF_SPAN_M = 0.1  # Hand offset from the club centre along the shaft, metres.
GRIP_LOAD_N = 40.0  # Declared vertical net force carried by the two hands, newtons.


# ------------------------------------------------------------------------------ contracts


def _matrix(name: str, value: object, rows: int | None = None, cols: int | None = None) -> Array:
    """Return ``value`` as a finite 2-D float array of the declared shape, or raise."""
    if not isinstance(value, np.ndarray):
        raise TypeError(f"{name} must be a numpy array")
    if value.ndim != 2:
        raise ValueError(f"{name} must be 2-D")
    if (rows is not None and value.shape[0] != rows) or (
        cols is not None and value.shape[1] != cols
    ):
        raise ValueError(f"{name} has shape {value.shape}, expected ({rows}, {cols})")
    if not np.isfinite(value).all():
        raise ValueError(f"{name} must be finite")
    return np.asarray(value, dtype=float)


def _vector(name: str, value: object, size: int | None = None) -> Array:
    """Return ``value`` as a finite 1-D float array of the declared length, or raise."""
    if not isinstance(value, np.ndarray):
        raise TypeError(f"{name} must be a numpy array")
    if value.ndim != 1 or (size is not None and value.shape[0] != size):
        raise ValueError(f"{name} must be a vector of length {size}")
    if not np.isfinite(value).all():
        raise ValueError(f"{name} must be finite")
    return np.asarray(value, dtype=float)


def _positive_definite_weight(weight: object, size: int) -> Array:
    """Return a symmetric positive-definite ``size``-by-``size`` matrix or raise."""
    matrix = _matrix("W", weight, size, size)
    if not np.allclose(matrix, matrix.T, rtol=1e-12, atol=1e-14):
        raise ValueError("W must be symmetric")
    if np.linalg.eigvalsh(matrix).min() <= 0:
        raise ValueError("W must be positive definite")
    return matrix


# ----------------------------------------------------------------------------------- P1


@dataclass(frozen=True, eq=False)
class AffineFibre:
    """The affine solution set ``{u_p + Z z}`` of ``A u = b`` (or its least-squares surrogate)."""

    particular: Array
    kernel: Array
    rank: int
    consistent: bool
    residual: float


def affine_fibre(A: object, b: object, *, rtol: float) -> AffineFibre:
    """Describe the solution set of ``A u = b`` (P1).

    Preconditions: ``A`` is a finite m-by-n array, ``b`` a finite length-m vector and
    ``0 < rtol < 1``; ``rtol`` sets both the numerical-rank cut ``rtol * sigma_max`` and the
    consistency test ``||A u_p - b|| <= rtol * max(1, ||b||)``.

    Postconditions: ``kernel`` has orthonormal columns spanning ``ker A`` (shape ``(n, n - rank)``,
    zero columns when the fibre is a point); ``particular`` is the minimum-norm least-squares
    solution.  If ``consistent`` is false the fibre is empty and ``particular`` is only the
    least-squares surrogate with the reported ``residual``.
    """
    matrix = _matrix("A", A)
    rhs = _vector("b", b, matrix.shape[0])
    if not 0.0 < rtol < 1.0:
        raise ValueError("rtol must lie in (0, 1)")
    left, values, right_t = np.linalg.svd(matrix)
    top = float(values[0]) if values.size else 0.0
    rank = int(np.sum(values > rtol * top)) if top > 0.0 else 0
    pseudo = (right_t[:rank].T / values[:rank]) @ left[:, :rank].T
    particular = pseudo @ rhs
    residual = float(np.linalg.norm(matrix @ particular - rhs))
    return AffineFibre(
        particular=particular,
        kernel=np.asarray(right_t[rank:].T),
        rank=rank,
        consistent=residual <= rtol * max(1.0, float(np.linalg.norm(rhs))),
        residual=residual,
    )


# ----------------------------------------------------------------------------------- P2


@dataclass(frozen=True, eq=False)
class WeightedRepresentative:
    """``u_W`` and the W-self-adjoint projector ``I - W^-1 A^T (A W^-1 A^T)^+ A`` onto ``ker A``."""

    u_w: Array
    projector: Array


def weighted_representative(A: object, b: object, W: object) -> WeightedRepresentative:
    """Return ``u_W = W^-1 A^T (A W^-1 A^T)^+ b`` and its kernel projector (P2).

    Preconditions: ``A`` finite m-by-n, ``b`` a length-m vector in ``range(A)``, ``W`` symmetric
    positive definite n-by-n (``ValueError`` otherwise).

    Postconditions: ``A u_W = b``; the projector is idempotent, maps into ``ker A``, annihilates
    ``u_W`` and is self-adjoint in the ``W`` inner product, ``W P = P^T W``.
    """
    matrix = _matrix("A", A)
    rhs = _vector("b", b, matrix.shape[0])
    metric = _positive_definite_weight(W, matrix.shape[1])
    lifted = np.linalg.solve(metric, matrix.T)
    gram_pinv = np.linalg.pinv(matrix @ lifted, rcond=PINV_RCOND, hermitian=True)
    u_w = lifted @ (gram_pinv @ rhs)
    if np.linalg.norm(matrix @ u_w - rhs) > CONSISTENCY_RTOL * max(1.0, float(np.linalg.norm(rhs))):
        raise ValueError("b is not in range(A): the fibre is empty")
    projector = np.eye(matrix.shape[1]) - lifted @ gram_pinv @ matrix
    return WeightedRepresentative(u_w=u_w, projector=projector)


def rescaled_representative(A: object, b: object, scale: object) -> Array:
    """Minimum-norm solution after the unit change ``u = diag(scale) v`` (P2).

    Equal to ``u_W`` with ``W = diag(scale)^-2``.  It differs from the unscaled minimum-norm
    solution (the unit choice selects the representative) but always lies in the same fibre.

    Preconditions: as :func:`weighted_representative`; ``scale`` is positive and finite.
    """
    matrix = _matrix("A", A)
    factors = _vector("scale", scale, matrix.shape[1])
    if np.any(factors <= 0):
        raise ValueError("scale must be positive")
    return weighted_representative(matrix, b, np.diag(factors**-2)).u_w


# ----------------------------------------------------------------------------------- P3


@dataclass(frozen=True, eq=False)
class ReducedQuadratic:
    """Reduced Hessian ``Z^T H Z`` and the minimiser of ``1/2 u^T H u + g^T u`` on the fibre."""

    hessian: Array
    z_star: Array
    u_star: Array


def reduced_quadratic(H: object, g: object, u_p: object, Z: object) -> ReducedQuadratic:
    """Minimise ``1/2 u^T H u + g^T u`` over ``u = u_p + Z z`` (P3).

    Preconditions: ``H`` symmetric n-by-n, ``g`` and ``u_p`` length-n, ``Z`` n-by-k; the *reduced*
    Hessian ``Z^T H Z`` must be positive definite (``ValueError`` otherwise).  ``H`` itself may
    be indefinite.

    Postconditions: ``u_star`` solves ``Z^T H Z z = -Z^T (H u_p + g)`` and does not depend on
    the choice of ``u_p`` within the fibre or of the basis ``Z`` of ``ker A``.
    """
    hessian = _matrix("H", H)
    size = hessian.shape[0]
    if hessian.shape[1] != size or not np.allclose(hessian, hessian.T):
        raise ValueError("H must be square and symmetric")
    gradient, particular = _vector("g", g, size), _vector("u_p", u_p, size)
    basis = _matrix("Z", Z, size)
    reduced = basis.T @ hessian @ basis
    if reduced.size and np.linalg.eigvalsh(reduced).min() <= PSD_RTOL * max(
        1.0, np.abs(reduced).max()
    ):
        raise ValueError("reduced Hessian Z^T H Z must be positive definite")
    step: Array = (
        np.asarray(np.linalg.solve(reduced, -basis.T @ (hessian @ particular + gradient)))
        if reduced.size
        else np.zeros(0)
    )
    return ReducedQuadratic(hessian=reduced, z_star=step, u_star=particular + basis @ step)


def kkt_minimiser(H: object, g: object, A: object, b: object) -> Array:
    """Solve ``[[H, A^T], [A, 0]] [u; lambda] = [-g; b]`` and return ``u`` (P3 cross-check).

    Preconditions: ``A`` has full row rank and the KKT matrix is nonsingular (``ValueError``
    otherwise).
    """
    hessian, matrix = _matrix("H", H), _matrix("A", A)
    size, rows = hessian.shape[0], matrix.shape[0]
    gradient, rhs = _vector("g", g, size), _vector("b", b, rows)
    system = np.block([[hessian, matrix.T], [matrix, np.zeros((rows, rows))]])
    try:
        return np.asarray(np.linalg.solve(system, np.concatenate([-gradient, rhs]))[:size])
    except np.linalg.LinAlgError as error:
        raise ValueError("KKT matrix is singular") from error


# ----------------------------------------------------------------------------------- P4


@dataclass(frozen=True)
class InvarianceReport:
    """Numerical verdict that ``c^T u`` is constant on the fibre, with its residual and tolerance."""

    invariant: bool
    residual: float
    tol: float


def functional_invariance(Z: object, c: object, *, tol: float) -> InvarianceReport:
    """Numerical test that ``c^T u`` is invariant on ``u_p + range(Z)`` (P4).

    This is a test *at the declared tolerance* ``tol``, not the exact theorem.  The theorem is
    ``Z^T c = 0`` (equivalently ``c in range(A^T)``).  Here ``residual = ||Z^T c|| / ||c||``
    (zero for ``c = 0``) and ``invariant = residual <= tol``; the verdict therefore depends on
    ``tol`` and a tiny nonzero residual still permits unbounded variation on an unbounded fibre.

    Preconditions: ``Z`` n-by-k with orthonormal columns, ``c`` length-n, ``tol >= 0``.
    """
    basis = _matrix("Z", Z)
    functional = _vector("c", c, basis.shape[0])
    if tol < 0:
        raise ValueError("tol must be nonnegative")
    scale = float(np.linalg.norm(functional))
    residual = float(np.linalg.norm(basis.T @ functional)) / scale if scale > 0 else 0.0
    return InvarianceReport(invariant=residual <= tol, residual=residual, tol=tol)


@dataclass(frozen=True)
class FunctionalInterval:
    """Attainable range of ``c^T u`` on a polyhedral fibre; ``nan`` bounds when infeasible."""

    feasible: bool
    lower: float
    upper: float

    @property
    def bounded(self) -> bool:
        """True when the fibre is feasible and both extrema are finite."""
        return self.feasible and math.isfinite(self.lower) and math.isfinite(self.upper)


@dataclass(frozen=True, eq=False)
class _Polyhedron:
    """``{x : A_ub x <= b_ub, A_eq x = b_eq}`` (rows may be absent)."""

    a_ub: Array
    b_ub: Array
    a_eq: Array | None = None
    b_eq: Array | None = None


def _lp(cost: Array, region: _Polyhedron) -> Any:
    """Solve one free-variable LP over ``region`` with HiGHS."""
    has_eq = region.a_eq is not None and region.a_eq.shape[0] > 0
    has_ub = region.a_ub.shape[0] > 0
    return linprog(
        cost,
        A_ub=region.a_ub if has_ub else None,
        b_ub=region.b_ub if has_ub else None,
        A_eq=region.a_eq if has_eq else None,
        b_eq=region.b_eq if has_eq else None,
        bounds=(None, None),
        method="highs",
    )


def _extremum(cost: Array, region: _Polyhedron) -> float:
    """Minimum of ``cost . x`` on a region already known feasible; ``-inf`` if unbounded."""
    result = _lp(cost, region)
    status = result.status
    if status == 0:
        return float(result.fun)
    if status in (2, 3):  # feasible region, so "infeasible-or-unbounded" means unbounded
        return -math.inf
    raise RuntimeError(f"linprog failed with status {status}")


def _lp_range(cost: Array, region: _Polyhedron) -> Interval | None:
    """Range of ``cost . x`` on ``region``; ``None`` when the region is empty."""
    if _lp(np.zeros_like(cost), region).status == 2:
        return None
    return _extremum(cost, region), -_extremum(-cost, region)


def functional_interval(
    c: object, u_p: object, Z: object, G: object, h: object, *, tol: float = 1e-9
) -> FunctionalInterval:
    """Range of ``c^T u`` over ``{u_p + Z z : G u <= h}`` by linear programming (P4).

    Preconditions: ``c`` and ``u_p`` length-n, ``Z`` n-by-k, ``G`` p-by-n (p may be 0) and ``h``
    length-p, all finite.  ``tol`` is the feasibility slack used only when ``k = 0``.

    Postconditions: ``feasible`` is false (bounds ``nan``) for an empty set; an unbounded
    direction gives ``-inf``/``+inf``.  An invariant ``c`` gives ``lower == upper``.  The result
    certifies extrema over the *declared polyhedron* only.
    """
    basis = _matrix("Z", Z)
    size = basis.shape[0]
    cost, particular = _vector("c", c, size), _vector("u_p", u_p, size)
    rows, bound = _matrix("G", G, cols=size), _vector("h", h)
    if bound.shape[0] != rows.shape[0]:
        raise ValueError("h must have one entry per row of G")
    offset, slack = float(cost @ particular), bound - rows @ particular
    if basis.shape[1] == 0:
        inside = bool(np.all(slack >= -tol))
        return FunctionalInterval(
            inside, offset if inside else math.nan, offset if inside else math.nan
        )
    span = _lp_range(basis.T @ cost, _Polyhedron(rows @ basis, slack))
    if span is None:
        return FunctionalInterval(False, math.nan, math.nan)
    return FunctionalInterval(True, offset + span[0], offset + span[1])


# ----------------------------------------------------------------------------------- P5


@dataclass(frozen=True)
class LeakageBound:
    """Actual constraint leakage and the P5 bound ``||A u_p - b|| + ||A Z|| ||z||``."""

    actual: float
    bound: float

    @property
    def slack(self) -> float:
        """Nonnegative when the bound holds."""
        return self.bound - self.actual


def leakage_bound(A: object, Z: object, u_p: object, b: object, z: object) -> LeakageBound:
    """Leakage of the step ``u_p + Z z`` for an only approximately null basis (P5).

    Preconditions: finite arrays of conforming shapes (``A`` m-by-n, ``Z`` n-by-k, ``z`` length k).
    Postconditions: ``actual <= bound`` for every step length, however large; the bound is tight
    when ``A u_p = b`` and ``A Z z`` is aligned with ``A Z``'s top singular direction.
    """
    matrix = _matrix("A", A)
    basis = _matrix("Z", Z, matrix.shape[1])
    particular, rhs = _vector("u_p", u_p, matrix.shape[1]), _vector("b", b, matrix.shape[0])
    step = _vector("z", z, basis.shape[1])
    actual = float(np.linalg.norm(matrix @ (particular + basis @ step) - rhs))
    gain = float(np.linalg.norm(matrix @ basis, 2)) if basis.shape[1] else 0.0
    return LeakageBound(
        actual,
        float(np.linalg.norm(matrix @ particular - rhs)) + gain * float(np.linalg.norm(step)),
    )


# ----------------------------------------------------------------------------------- P7


@dataclass(frozen=True, eq=False)
class ForceFrame:
    """One frame's feasible set ``{u : A u = b, G u <= h}``."""

    A: Array
    b: Array
    G: Array
    h: Array

    def __post_init__(self) -> None:
        """Check conforming shapes (the frame's dimension is the column count of ``G``)."""
        size = _matrix("G", self.G).shape[1]
        _matrix("A", self.A, cols=size)
        _vector("b", self.b, self.A.shape[0])
        _vector("h", self.h, self.G.shape[0])

    def region(self) -> _Polyhedron:
        """This frame's polyhedron."""
        return _Polyhedron(self.G, self.h, self.A, self.b)


@dataclass(frozen=True)
class EnvelopeComparison:
    """Frame-wise versus rate-coupled envelopes of ``c^T u`` in the two frames."""

    framewise: tuple[Interval, Interval]
    coupled: tuple[Interval, Interval]

    @property
    def contained(self) -> bool:
        """True when each coupled envelope lies inside its frame-wise envelope."""
        return all(
            free[0] - CONTAINMENT_ATOL <= tied[0] and tied[1] <= free[1] + CONTAINMENT_ATOL
            for free, tied in zip(self.framewise, self.coupled, strict=True)
        )


def _joint_region(frames: tuple[ForceFrame, ForceFrame], delta: float) -> _Polyhedron:
    """Polyhedron over ``(u1, u2)`` with each frame's constraints and ``|u2 - u1|_inf <= delta``."""
    size = frames[0].G.shape[1]
    first, second = frames

    def stack(one: Array, two: Array) -> Array:
        """Block-diagonal stack of two frames' constraint rows over ``(u1, u2)``."""
        out = np.zeros((one.shape[0] + two.shape[0], 2 * size))
        out[: one.shape[0], :size], out[one.shape[0] :, size:] = one, two
        return out

    a_ub, b_ub = stack(first.G, second.G), np.concatenate([first.h, second.h])
    if math.isfinite(delta):
        link = np.hstack([np.eye(size), -np.eye(size)])
        a_ub, b_ub = np.vstack([a_ub, link, -link]), np.concatenate(
            [b_ub, np.full(2 * size, delta)]
        )
    return _Polyhedron(a_ub, b_ub, stack(first.A, second.A), np.concatenate([first.b, second.b]))


def _solved_interval(cost: Array, region: _Polyhedron, label: str) -> Interval:
    """Bounded range of ``cost . x`` on ``region`` or ``ValueError`` naming the failure."""
    span = _lp_range(cost, region)
    if span is None:
        raise ValueError(f"{label} is infeasible")
    if not all(math.isfinite(end) for end in span):
        raise ValueError(f"{label} has an unbounded envelope")
    return span


def framewise_vs_coupled_envelope(
    frames: tuple[ForceFrame, ForceFrame], c: object, delta: float
) -> EnvelopeComparison:
    """Compare frame-wise envelopes of ``c^T u`` with the rate-coupled ones (P7).

    Coupling is ``|u2 - u1|_inf <= delta`` between the two frames' allocations.

    Preconditions: both frames feasible and bounded for ``c`` and share dimension ``n``;
    ``delta >= 0`` (``inf`` means no coupling).  Violations raise ``ValueError`` (a coupling too
    tight to link the frames is reported as infeasible).

    Postconditions: each coupled interval lies inside its frame-wise interval, with equality
    when ``delta`` is infinite.
    """
    size = frames[0].G.shape[1]
    cost = _vector("c", c, size)
    if frames[1].G.shape[1] != size:
        raise ValueError("frames must share a dimension")
    if not delta >= 0:
        raise ValueError("delta must be nonnegative")
    free = tuple(_solved_interval(cost, f.region(), "frame") for f in frames)
    joint, zero = _joint_region(frames, delta), np.zeros(size)
    tied = tuple(
        _solved_interval(np.concatenate(parts), joint, "coupled problem")
        for parts in ((cost, zero), (zero, cost))
    )
    return EnvelopeComparison((free[0], free[1]), (tied[0], tied[1]))


# --------------------------------------------------------------------------- worked examples


def _interval_list(frame_fibre: AffineFibre, c: Array, G: Array, h: Array) -> list[float]:
    """Interval of ``c^T u`` on a fibre as a JSON-ready ``[lower, upper]``."""
    span = functional_interval(c, frame_fibre.particular, frame_fibre.kernel, G, h)
    return [span.lower, span.upper]


def _all_rows_invariant(fibre: AffineFibre, rows: Array) -> bool:
    """True when every row of ``rows`` is numerically invariant on the fibre."""
    return all(functional_invariance(fibre.kernel, row, tol=1e-9).invariant for row in rows)


def three_muscle_example() -> dict[str, object]:
    """Three-muscle toy ``u = (3 - t, 3 - t, t), t in [0, 3]`` and its disabled-muscle collapse.

    Constraints ``u1 = u2`` and ``u1 + u3 = 3`` with ``0 <= u <= 3``.  Disabling muscle 3
    (``u3 <= 0``) collapses the one-parameter family to the single point ``(3, 3, 0)``.
    """
    matrix, rhs = np.array([[1.0, -1.0, 0.0], [1.0, 0.0, 1.0]]), np.array([0.0, 3.0])
    box, bound = np.vstack([np.eye(3), -np.eye(3)]), np.array([3.0] * 3 + [0.0] * 3)
    disabled = np.vstack([box, [0.0, 0.0, 1.0]]), np.append(bound, 0.0)
    fibre = affine_fibre(matrix, rhs, rtol=1e-10)
    first, third = np.array([1.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0])
    return {
        "A": matrix.tolist(),
        "b": rhs.tolist(),
        "nullity": int(fibre.kernel.shape[1]),
        "net_invariant": _all_rows_invariant(fibre, matrix),
        "muscle_1_interval": _interval_list(fibre, first, box, bound),
        "muscle_3_interval": _interval_list(fibre, third, box, bound),
        "muscle_1_disabled_interval": _interval_list(fibre, first, *disabled),
        "muscle_3_disabled_interval": _interval_list(fibre, third, *disabled),
    }


def _grip_system() -> tuple[Array, Array, Array, Array]:
    """Net-wrench map, declared wrench and friction polygon of the planar two-hand grip.

    Unknowns are ``(f_lead_x, f_lead_y, f_trail_x, f_trail_y)`` with the hands a distance
    ``GRIP_HALF_SPAN_M`` either side of the club centre along x; the wrench is ``(F_x, F_y, tau)``.
    """
    span = GRIP_HALF_SPAN_M
    matrix = np.array([[1.0, 0, 1, 0], [0, 1, 0, 1], [0, -span, 0, span]])
    cone = np.array([[1.0, -FRICTION_COEFFICIENT], [-1.0, -FRICTION_COEFFICIENT]])
    friction = np.zeros((4, 4))
    friction[:2, :2], friction[2:, 2:] = cone, cone
    return matrix, np.array([0.0, GRIP_LOAD_N, 0.0]), friction, np.zeros(4)


def grip_example() -> dict[str, object]:
    """Planar two-hand closed-loop grip: net wrench invariant, lead/trail split an interval.

    The hands may squeeze the club along x without changing the net wrench; the friction
    polygon ``|f_x| <= mu f_y`` bounds the squeeze.  The vertical lead/trail split is fixed by
    the torque balance, so only the squeeze (lead x-force) has a nondegenerate interval.
    """
    matrix, wrench, friction, limit = _grip_system()
    fibre = affine_fibre(matrix, wrench, rtol=1e-10)
    squeeze, vertical = np.array([1.0, 0, 0, 0]), np.array([0.0, 1, 0, 0])
    return {
        "nullity": int(fibre.kernel.shape[1]),
        "net_wrench": (matrix @ fibre.particular).tolist(),
        "net_wrench_invariant": _all_rows_invariant(fibre, matrix),
        "lead_squeeze_interval": _interval_list(fibre, squeeze, friction, limit),
        "lead_squeeze_invariant": functional_invariance(fibre.kernel, squeeze, tol=1e-9).invariant,
        "lead_vertical_interval": _interval_list(fibre, vertical, friction, limit),
    }


# ------------------------------------------------------------------------- the linear section


def _random_rank_matrix(rng: np.random.Generator, shape: tuple[int, int], rank: int) -> Array:
    """Well-conditioned matrix of exact ``rank`` (singular values in [1, 10])."""
    rows, cols = shape
    if rank == 0:
        return np.zeros(shape)
    left = np.linalg.qr(rng.standard_normal((rows, rows)))[0][:, :rank]
    right = np.linalg.qr(rng.standard_normal((cols, cols)))[0][:, :rank]
    return np.asarray(left @ np.diag(rng.uniform(1.0, 10.0, rank)) @ right.T)


def _p1_section() -> dict[str, object]:
    """Seeded survey over full, deficient and zero rank, plus an empty fibre."""
    rng, survey = np.random.default_rng(SEED), []
    for rows, cols, rank in [(3, 5, 3), (3, 5, 2), (4, 4, 4), (4, 4, 0), (2, 3, 1)]:
        matrix = _random_rank_matrix(rng, (rows, cols), rank)
        fibre = affine_fibre(matrix, matrix @ rng.standard_normal(cols), rtol=1e-10)
        survey.append(
            {
                "m": rows,
                "n": cols,
                "rank": fibre.rank,
                "nullity": cols - fibre.rank,
                "consistent": fibre.consistent,
            }
        )
    empty = affine_fibre(np.ones((2, 2)), np.array([1.0, 2.0]), rtol=1e-10)
    return {"survey": survey, "empty": {"consistent": empty.consistent, "residual": empty.residual}}


def _p2_section() -> dict[str, object]:
    """Weighted versus Euclidean versus rescaled representative of ``u1 + u2 = 2``."""
    matrix, rhs = np.array([[1.0, 1.0]]), np.array([2.0])
    weighted = weighted_representative(matrix, rhs, np.diag([1.0, 4.0]))
    return {
        "weight_diagonal": [1.0, 4.0],
        "u_weighted": weighted.u_w.tolist(),
        "u_euclidean": weighted_representative(matrix, rhs, np.eye(2)).u_w.tolist(),
        "u_rescaled_half": rescaled_representative(matrix, rhs, np.array([1.0, 0.5])).tolist(),
        "projector": weighted.projector.tolist(),
    }


def _p3_section() -> dict[str, object]:
    """Indefinite ``H`` with positive reduced Hessian; reduced solve versus full KKT."""
    hessian, gradient = np.diag([1.0, -1.0]), np.array([-1.0, 0.0])
    matrix, rhs = np.array([[0.0, 1.0]]), np.array([3.0])
    fibre = affine_fibre(matrix, rhs, rtol=1e-10)
    reduced = reduced_quadratic(hessian, gradient, fibre.particular, fibre.kernel)
    return {
        "reduced_hessian": reduced.hessian.tolist(),
        "u_star": reduced.u_star.tolist(),
        "u_kkt": kkt_minimiser(hessian, gradient, matrix, rhs).tolist(),
    }


def _p4_section() -> dict[str, object]:
    """Net force versus its split on ``u1 + u2 = 1`` over the unit box, plus the free case."""
    matrix, rhs = np.array([[1.0, 1.0]]), np.array([1.0])
    fibre = affine_fibre(matrix, rhs, rtol=1e-10)
    box, bound = np.vstack([np.eye(2), -np.eye(2)]), np.array([1.0, 1.0, 0.0, 0.0])
    free = functional_interval(
        np.array([1.0, 0.0]), fibre.particular, fibre.kernel, np.zeros((0, 2)), np.zeros(0)
    )
    return {
        "split_interval": _interval_list(fibre, np.array([1.0, 0.0]), box, bound),
        "net_interval": _interval_list(fibre, np.array([1.0, 1.0]), box, bound),
        "split_unbounded_without_limits": not free.bounded,
        "split_residual": functional_invariance(
            fibre.kernel, np.array([1.0, 0.0]), tol=1e-9
        ).residual,
    }


def _p5_section() -> dict[str, object]:
    """Tight leakage bound for a basis that is null only to ``eps``."""
    eps, rows = 1e-3, []
    for step in (1.0, 1e3, 1e6):
        result = leakage_bound(
            np.array([[eps]]), np.array([[1.0]]), np.zeros(1), np.zeros(1), np.array([step])
        )
        rows.append({"step": step, "actual": result.actual, "bound": result.bound})
    return {"epsilon": eps, "steps": rows}


def _p7_section() -> dict[str, object]:
    """Two scalar frames ``[0, 1]`` and ``[0.5, 2]`` with a rate bound of 0.2."""

    def frame(low: float, high: float) -> ForceFrame:
        """Scalar frame with no balance rows and the bounds ``low <= u <= high``."""
        return ForceFrame(
            np.zeros((0, 1)), np.zeros(0), np.array([[1.0], [-1.0]]), np.array([high, -low])
        )

    result = framewise_vs_coupled_envelope((frame(0.0, 1.0), frame(0.5, 2.0)), np.array([1.0]), 0.2)
    return {
        "delta": 0.2,
        "framewise": [list(span) for span in result.framewise],
        "coupled": [list(span) for span in result.coupled],
        "contained": result.contained,
    }


def linear_section() -> dict[str, object]:
    """Assemble the ``"linear"`` JSON section: every number quoted for P1-P5, P7 and the toys."""
    return {
        "p1": _p1_section(),
        "p2": _p2_section(),
        "p3": _p3_section(),
        "p4": _p4_section(),
        "p5": _p5_section(),
        "p7": _p7_section(),
        "three_muscle": three_muscle_example(),
        "planar_grip": grip_example(),
    }
