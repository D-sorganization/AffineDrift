"""Deterministic reduced-order impact models for protocol comparison.

The solvers operate only in the planar contact coordinates declared by
``ImpactProtocol``. Their outputs are manufactured feasibility evidence, not a
qualified club, ball, shaft, participant, or population model.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import hypot, isfinite

from src.affine_control.impact_contact_protocol import (
    ContactParameters,
    EventPolicy,
    ImpactProtocol,
    ImpactState,
    ModelId,
)


class ContactCaseError(ValueError):
    """Raised when the declared single-contact model cannot own the event."""


class ContactSolverError(RuntimeError):
    """Raised when a compliant solve fails before a qualified separation."""


@dataclass(frozen=True)
class ImpactOutcome:
    """One model-conditioned post-impact state and balance evidence."""

    model_id: ModelId
    club_velocity_m_s: tuple[float, float]
    ball_velocity_m_s: tuple[float, float]
    ball_spin_rad_s: float
    normal_impulse_n_s: float
    tangential_impulse_n_s: float
    contact_time_s: float
    peak_force_n: float
    energy_before_j: float
    energy_after_j: float
    momentum_residual_kg_m_s: float
    slip_before_m_s: float
    slip_after_m_s: float
    event_time_offset_s: float
    evidence_origin: str = "synthetic-fixture"

    def __post_init__(self) -> None:
        """Reject a partial or nonfinite solver product."""
        numeric = (
            *self.club_velocity_m_s,
            *self.ball_velocity_m_s,
            self.ball_spin_rad_s,
            self.normal_impulse_n_s,
            self.tangential_impulse_n_s,
            self.contact_time_s,
            self.peak_force_n,
            self.energy_before_j,
            self.energy_after_j,
            self.momentum_residual_kg_m_s,
            self.slip_before_m_s,
            self.slip_after_m_s,
            self.event_time_offset_s,
        )
        if not all(isfinite(value) for value in numeric):
            raise ValueError("impact outcome must be finite")
        if self.normal_impulse_n_s <= 0.0:
            raise ValueError("impact outcome must carry positive normal impulse")
        if min(self.contact_time_s, self.peak_force_n, self.energy_after_j) < 0.0:
            raise ValueError("impact time, force, and energy must be nonnegative")


@dataclass(frozen=True)
class ModelComparison:
    """Outcome-specific comparison without a universal model ranking."""

    outcomes: tuple[ImpactOutcome, ...]
    compliant_convergence_error_m_s: float
    preferred_model: None
    comparison_limit: str


def _kinetic_energy(state: ImpactState, parameters: ContactParameters) -> float:
    """Return planar translational plus ball rotational kinetic energy."""
    club_speed_sq = sum(value * value for value in state.club_velocity_m_s)
    ball_speed_sq = sum(value * value for value in state.ball_velocity_m_s)
    return (
        0.5 * parameters.club_mass_kg * club_speed_sq
        + 0.5 * parameters.ball_mass_kg * ball_speed_sq
        + 0.5 * parameters.ball_inertia_kg_m2 * state.ball_spin_rad_s**2
    )


def _validate_contact_case(state: ImpactState, policy: EventPolicy) -> float:
    """Return closing speed or reject an unsupported event topology."""
    if state.contact_count != 1:
        status = "multiple-contact" if state.contact_count > 1 else "no-contact"
        raise ContactCaseError(f"{status}: the single-contact map is unavailable")
    closing_speed = state.club_velocity_m_s[0] - state.ball_velocity_m_s[0]
    if closing_speed <= 0.0:
        raise ContactCaseError("separating: the event guard is not closing")
    if closing_speed <= policy.grazing_speed_threshold_m_s:
        raise ContactCaseError("grazing: event-time sensitivity is singular or ill-conditioned")
    return closing_speed


def _post_state(
    state: ImpactState,
    parameters: ContactParameters,
    normal_impulse: float,
) -> tuple[ImpactState, float, float, float]:
    """Apply paired normal and Coulomb-limited tangential impulses."""
    slip_before = (
        state.ball_velocity_m_s[1]
        - parameters.ball_radius_m * state.ball_spin_rad_s
        - state.club_velocity_m_s[1]
    )
    inverse_tangent_mass = (
        1.0 / parameters.ball_mass_kg
        + 1.0 / parameters.club_mass_kg
        + parameters.ball_radius_m**2 / parameters.ball_inertia_kg_m2
    )
    sticking_impulse = -slip_before / inverse_tangent_mass
    friction_limit = parameters.friction * normal_impulse
    tangent_impulse = min(max(sticking_impulse, -friction_limit), friction_limit)
    club_velocity = (
        state.club_velocity_m_s[0] - normal_impulse / parameters.club_mass_kg,
        state.club_velocity_m_s[1] - tangent_impulse / parameters.club_mass_kg,
    )
    ball_velocity = (
        state.ball_velocity_m_s[0] + normal_impulse / parameters.ball_mass_kg,
        state.ball_velocity_m_s[1] + tangent_impulse / parameters.ball_mass_kg,
    )
    ball_spin = (
        state.ball_spin_rad_s
        - parameters.ball_radius_m * tangent_impulse / parameters.ball_inertia_kg_m2
    )
    post = replace(
        state,
        club_velocity_m_s=club_velocity,
        ball_velocity_m_s=ball_velocity,
        ball_spin_rad_s=ball_spin,
    )
    slip_after = ball_velocity[1] - parameters.ball_radius_m * ball_spin - club_velocity[1]
    return post, tangent_impulse, slip_before, slip_after


def _momentum_residual(
    before: ImpactState,
    after: ImpactState,
    parameters: ContactParameters,
) -> float:
    """Return the norm of paired-body linear-momentum imbalance."""
    residuals = []
    for axis in range(2):
        initial = (
            parameters.club_mass_kg * before.club_velocity_m_s[axis]
            + parameters.ball_mass_kg * before.ball_velocity_m_s[axis]
        )
        final = (
            parameters.club_mass_kg * after.club_velocity_m_s[axis]
            + parameters.ball_mass_kg * after.ball_velocity_m_s[axis]
        )
        residuals.append(final - initial)
    return hypot(*residuals)


def _make_outcome(
    model_id: ModelId,
    state: ImpactState,
    parameters: ContactParameters,
    normal_impulse: float,
    contact_time_s: float,
    peak_force_n: float,
    event_time_offset_s: float = 0.0,
) -> ImpactOutcome:
    """Create one balance-checked immutable solver product."""
    post, tangent_impulse, slip_before, slip_after = _post_state(state, parameters, normal_impulse)
    return ImpactOutcome(
        model_id=model_id,
        club_velocity_m_s=post.club_velocity_m_s,
        ball_velocity_m_s=post.ball_velocity_m_s,
        ball_spin_rad_s=post.ball_spin_rad_s,
        normal_impulse_n_s=normal_impulse,
        tangential_impulse_n_s=tangent_impulse,
        contact_time_s=contact_time_s,
        peak_force_n=peak_force_n,
        energy_before_j=_kinetic_energy(state, parameters),
        energy_after_j=_kinetic_energy(post, parameters),
        momentum_residual_kg_m_s=_momentum_residual(state, post, parameters),
        slip_before_m_s=abs(slip_before),
        slip_after_m_s=abs(slip_after),
        event_time_offset_s=event_time_offset_s,
    )


def solve_rigid_impulse(
    state: ImpactState,
    parameters: ContactParameters,
    policy: EventPolicy,
) -> ImpactOutcome:
    """Apply an instantaneous Newton/Coulomb single-contact reset."""
    closing_speed = _validate_contact_case(state, policy)
    inverse_normal_mass = 1.0 / parameters.club_mass_kg + 1.0 / parameters.ball_mass_kg
    normal_impulse = (1.0 + parameters.restitution) * closing_speed / inverse_normal_mass
    return _make_outcome("rigid-impulse", state, parameters, normal_impulse, 0.0, 0.0)


def _contact_force(
    compression_m: float,
    compression_rate_m_s: float,
    parameters: ContactParameters,
) -> float:
    """Evaluate the declared Hunt--Crossley-like regularized normal law."""
    if compression_m <= 0.0:
        return 0.0
    elastic = float(
        parameters.contact_stiffness_n_m_exp * compression_m**parameters.contact_exponent
    )
    damping_factor = max(0.0, 1.0 + parameters.contact_damping_s_m * compression_rate_m_s)
    return elastic * damping_factor


def _contact_derivative(
    compression_m: float,
    compression_rate_m_s: float,
    parameters: ContactParameters,
) -> tuple[float, float, float]:
    """Return compression rate, acceleration, and force."""
    force = _contact_force(compression_m, compression_rate_m_s, parameters)
    inverse_mass = 1.0 / parameters.club_mass_kg + 1.0 / parameters.ball_mass_kg
    return compression_rate_m_s, -force * inverse_mass, force


def _rk4_step(
    compression_m: float,
    compression_rate_m_s: float,
    parameters: ContactParameters,
) -> tuple[float, float, float]:
    """Advance the compliant relative state by one fixed RK4 step."""
    step = parameters.solver_step_s
    k1_x, k1_v, force_1 = _contact_derivative(compression_m, compression_rate_m_s, parameters)
    k2_x, k2_v, force_2 = _contact_derivative(
        compression_m + 0.5 * step * k1_x,
        compression_rate_m_s + 0.5 * step * k1_v,
        parameters,
    )
    k3_x, k3_v, force_3 = _contact_derivative(
        compression_m + 0.5 * step * k2_x,
        compression_rate_m_s + 0.5 * step * k2_v,
        parameters,
    )
    k4_x, k4_v, force_4 = _contact_derivative(
        compression_m + step * k3_x,
        compression_rate_m_s + step * k3_v,
        parameters,
    )
    next_compression = compression_m + step * (k1_x + 2 * k2_x + 2 * k3_x + k4_x) / 6
    next_rate = compression_rate_m_s + step * (k1_v + 2 * k2_v + 2 * k3_v + k4_v) / 6
    impulse_increment = step * (force_1 + 2 * force_2 + 2 * force_3 + force_4) / 6
    return next_compression, next_rate, impulse_increment


def solve_compliant_contact(
    state: ImpactState,
    parameters: ContactParameters,
    policy: EventPolicy,
) -> ImpactOutcome:
    """Integrate one finite-duration normal contact until separation."""
    closing_speed = _validate_contact_case(state, policy)
    compression = 0.0
    compression_rate = closing_speed
    impulse = 0.0
    peak_force = 0.0
    elapsed = 0.0
    for _ in range(parameters.maximum_contact_steps):
        compression, compression_rate, impulse_increment = _rk4_step(
            compression, compression_rate, parameters
        )
        impulse += impulse_increment
        elapsed += parameters.solver_step_s
        peak_force = max(peak_force, _contact_force(compression, compression_rate, parameters))
        if elapsed > parameters.maximum_contact_time_s:
            break
        if compression <= 0.0 and compression_rate < 0.0 and impulse > 0.0:
            return _make_outcome(
                "compliant-contact", state, parameters, impulse, elapsed, peak_force
            )
    raise ContactSolverError("compliant contact did not reach separation within declared limits")


def _propagate_velocity(
    velocity_m_s: tuple[float, float],
    acceleration_m_s2: tuple[float, float],
    time_s: float,
) -> tuple[float, float]:
    """Propagate a constant-acceleration contact-frame velocity."""
    values = (*acceleration_m_s2, time_s)
    if len(acceleration_m_s2) != 2 or not all(isfinite(value) for value in values):
        raise ValueError("hybrid flow inputs must be finite planar values")
    return (
        velocity_m_s[0] + acceleration_m_s2[0] * time_s,
        velocity_m_s[1] + acceleration_m_s2[1] * time_s,
    )


def solve_hybrid_event(
    state: ImpactState,
    parameters: ContactParameters,
    policy: EventPolicy,
    *,
    event_time_offset_s: float,
    club_acceleration_m_s2: tuple[float, float],
    ball_acceleration_m_s2: tuple[float, float],
) -> ImpactOutcome:
    """Flow to an uncertain guard time, then apply the rigid reset map."""
    propagated = replace(
        state,
        club_velocity_m_s=_propagate_velocity(
            state.club_velocity_m_s, club_acceleration_m_s2, event_time_offset_s
        ),
        ball_velocity_m_s=_propagate_velocity(
            state.ball_velocity_m_s, ball_acceleration_m_s2, event_time_offset_s
        ),
    )
    rigid = solve_rigid_impulse(propagated, parameters, policy)
    return replace(
        rigid,
        model_id="hybrid-event",
        event_time_offset_s=event_time_offset_s,
    )


def compare_contact_models(state: ImpactState, protocol: ImpactProtocol) -> ModelComparison:
    """Compare declared outputs while refusing a universal winner."""
    rigid = solve_rigid_impulse(state, protocol.parameters, protocol.event_policy)
    compliant = solve_compliant_contact(state, protocol.parameters, protocol.event_policy)
    hybrid = solve_hybrid_event(
        state,
        protocol.parameters,
        protocol.event_policy,
        event_time_offset_s=0.0,
        club_acceleration_m_s2=(120.0, 0.0),
        ball_acceleration_m_s2=(0.0, 0.0),
    )
    refined = solve_compliant_contact(
        state,
        replace(protocol.parameters, solver_step_s=protocol.parameters.solver_step_s / 2.0),
        protocol.event_policy,
    )
    error = abs(compliant.ball_velocity_m_s[0] - refined.ball_velocity_m_s[0])
    return ModelComparison(
        outcomes=(rigid, compliant, hybrid),
        compliant_convergence_error_m_s=error,
        preferred_model=None,
        comparison_limit=(
            "Outcome-specific qualification only; no contact model is universally correct."
        ),
    )
