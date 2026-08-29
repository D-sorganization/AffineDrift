"""Analytic reachability and event-validation contracts used by publications."""

from dataclasses import dataclass, replace
from math import exp, isfinite, sqrt


def _require_finite(values: tuple[float, ...], label: str) -> None:
    if not all(isfinite(value) for value in values):
        raise ValueError(f"{label} must be finite")


def constant_additive_drift_interval(
    initial_state: float,
    drift: float,
    control_bound: float,
    horizon: float,
) -> tuple[float, float]:
    """Return the exact reachable interval for ``x_dot = drift + control``.

    Preconditions:
        All inputs are finite, ``control_bound >= 0``, and ``horizon >= 0``.
        The admissible controls are measurable functions satisfying
        ``abs(control(t)) <= control_bound`` over the declared horizon.

    Postconditions:
        The interval center is ``initial_state + drift * horizon`` and its
        width is ``2 * control_bound * horizon``.
    """
    values = (initial_state, drift, control_bound, horizon)
    if not all(isfinite(value) for value in values):
        raise ValueError("reachability inputs must be finite")
    if control_bound < 0.0:
        raise ValueError("control_bound must be nonnegative")
    if horizon < 0.0:
        raise ValueError("horizon must be nonnegative")

    center = initial_state + drift * horizon
    radius = control_bound * horizon
    if not isfinite(center) or not isfinite(radius):
        raise ValueError("derived reachability interval must be finite")
    interval = (center - radius, center + radius)
    if interval[0] > interval[1]:
        raise ArithmeticError("reachability interval postcondition failed")
    return interval


@dataclass(frozen=True)
class LinearScalarSystem:
    """Scalar system ``x_dot = gradient*x + offset + u`` with bounded input."""

    initial_state: float
    drift_gradient: float
    drift_offset: float
    control_bound: float

    def __post_init__(self) -> None:
        """Require finite coefficients and strictly positive control capacity."""
        _require_finite(
            (self.initial_state, self.drift_gradient, self.drift_offset, self.control_bound),
            "linear-system values",
        )
        if self.control_bound <= 0.0:
            raise ValueError("control_bound must be positive")


def instantaneous_scalar_dcr(system: LinearScalarSystem) -> float:
    """Return the declared scalar absolute-value DCR at the initial state."""
    drift = system.drift_gradient * system.initial_state + system.drift_offset
    return abs(drift) / system.control_bound


def scalar_linear_reachable_interval(
    system: LinearScalarSystem, horizon: float
) -> tuple[float, float]:
    """Return the exact interval for a scalar affine-linear bounded-input system."""
    if not isfinite(horizon) or horizon < 0.0:
        raise ValueError("horizon must be finite and nonnegative")
    if system.drift_gradient == 0.0:
        return constant_additive_drift_interval(
            system.initial_state,
            system.drift_offset,
            system.control_bound,
            horizon,
        )
    try:
        transition = exp(system.drift_gradient * horizon)
    except OverflowError as error:
        raise ValueError("state transition must remain finite") from error
    input_factor = (transition - 1.0) / system.drift_gradient
    center = transition * system.initial_state + input_factor * system.drift_offset
    radius = input_factor * system.control_bound
    _require_finite((center, radius), "reachable interval")
    return (center - radius, center + radius)


@dataclass(frozen=True)
class PlanarRankDeficientSystem:
    """Planar translation with a single bounded input acting on the first axis."""

    initial_state: tuple[float, float]
    drift: tuple[float, float]
    control_bound: float
    horizon: float

    def __post_init__(self) -> None:
        """Require finite state, drift, bound, and horizon values."""
        _require_finite(
            (*self.initial_state, *self.drift, self.control_bound, self.horizon), "system"
        )
        if self.control_bound < 0.0 or self.horizon < 0.0:
            raise ValueError("control_bound and horizon must be nonnegative")


@dataclass(frozen=True)
class ReachableBox:
    """Axis-aligned reachable bounds and input-map rank."""

    lower: tuple[float, float]
    upper: tuple[float, float]
    controllability_rank: int

    @property
    def volume(self) -> float:
        """Return the planar box area, including zero for a collapsed axis."""
        return (self.upper[0] - self.lower[0]) * (self.upper[1] - self.lower[1])


def rank_deficient_reachable_box(system: PlanarRankDeficientSystem) -> ReachableBox:
    """Return the exact reachable box for input map ``G = [[1], [0]]``."""
    first_axis = constant_additive_drift_interval(
        system.initial_state[0],
        system.drift[0],
        system.control_bound,
        system.horizon,
    )
    second_axis = system.initial_state[1] + system.drift[1] * system.horizon
    return ReachableBox(
        lower=(first_axis[0], second_axis),
        upper=(first_axis[1], second_axis),
        controllability_rank=1,
    )


@dataclass(frozen=True)
class CorrectionRequest:
    """One-dimensional constrained correction request."""

    required_delta: float
    control_gain: float
    input_bound: float

    def __post_init__(self) -> None:
        """Require a finite nonzero gain and nonnegative symmetric input bound."""
        _require_finite(
            (self.required_delta, self.control_gain, self.input_bound), "correction request"
        )
        if self.control_gain == 0.0:
            raise ValueError("control_gain must be nonzero")
        if self.input_bound < 0.0:
            raise ValueError("input_bound must be nonnegative")


@dataclass(frozen=True)
class CorrectionResult:
    """Applied control, achieved correction, residual, and saturation state."""

    control: float
    achieved_delta: float
    residual: float
    saturated: bool


def bounded_optimal_correction(request: CorrectionRequest) -> CorrectionResult:
    """Solve the scalar least-squares correction under a symmetric input bound."""
    unconstrained = request.required_delta / request.control_gain
    control = min(request.input_bound, max(-request.input_bound, unconstrained))
    achieved = request.control_gain * control
    return CorrectionResult(
        control=control,
        achieved_delta=achieved,
        residual=request.required_delta - achieved,
        saturated=control != unconstrained,
    )


@dataclass(frozen=True)
class ContactEventCase:
    """Constant-acceleration approach to the event surface ``height = 0``."""

    initial_height: float
    initial_velocity: float
    drift_acceleration: float
    control_acceleration: float

    def __post_init__(self) -> None:
        """Require a positive initial height and finite kinematic values."""
        _require_finite(
            (
                self.initial_height,
                self.initial_velocity,
                self.drift_acceleration,
                self.control_acceleration,
            ),
            "contact-event values",
        )
        if self.initial_height <= 0.0:
            raise ValueError("initial_height must be positive")


@dataclass(frozen=True)
class ContactEventResult:
    """First positive event time and event velocity."""

    time: float
    velocity: float


def solve_contact_event(case: ContactEventCase) -> ContactEventResult:
    """Solve the first future crossing of the constant-acceleration event surface."""
    acceleration = case.drift_acceleration + case.control_acceleration
    if acceleration == 0.0:
        if case.initial_velocity >= 0.0:
            raise ValueError("declared trajectory does not reach the event")
        event_time = -case.initial_height / case.initial_velocity
        return ContactEventResult(event_time, case.initial_velocity)
    discriminant = case.initial_velocity**2 - 2.0 * acceleration * case.initial_height
    if discriminant < 0.0:
        raise ValueError("declared trajectory does not reach the event")
    root = sqrt(discriminant)
    candidates = tuple(
        value
        for value in (
            (-case.initial_velocity - root) / acceleration,
            (-case.initial_velocity + root) / acceleration,
        )
        if value > 0.0
    )
    if not candidates:
        raise ValueError("declared trajectory has no future event crossing")
    event_time = min(candidates)
    return ContactEventResult(
        time=event_time,
        velocity=case.initial_velocity + acceleration * event_time,
    )


def contact_event_control_sensitivity(case: ContactEventCase, perturbation: float) -> float:
    """Return a central-difference event-velocity sensitivity to control acceleration."""
    if not isfinite(perturbation) or perturbation <= 0.0:
        raise ValueError("perturbation must be finite and positive")
    plus = solve_contact_event(
        replace(case, control_acceleration=case.control_acceleration + perturbation)
    )
    minus = solve_contact_event(
        replace(case, control_acceleration=case.control_acceleration - perturbation)
    )
    return (plus.velocity - minus.velocity) / (2.0 * perturbation)


@dataclass(frozen=True)
class ParameterEnvelope:
    """Min/max center and width over declared model-parameter cases."""

    center_interval: tuple[float, float]
    width_interval: tuple[float, float]


def parameter_reachability_envelope(
    systems: tuple[LinearScalarSystem, ...], horizon: float
) -> ParameterEnvelope:
    """Return a deterministic reachability envelope over declared parameter cases."""
    if not systems:
        raise ValueError("at least one parameter case is required")
    intervals = tuple(scalar_linear_reachable_interval(system, horizon) for system in systems)
    centers = tuple((lower + upper) / 2.0 for lower, upper in intervals)
    widths = tuple(upper - lower for lower, upper in intervals)
    return ParameterEnvelope(
        center_interval=(min(centers), max(centers)),
        width_interval=(min(widths), max(widths)),
    )
