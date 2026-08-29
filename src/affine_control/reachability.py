"""Small analytic reachability contracts used by AffineDrift publications."""

from math import isfinite


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
