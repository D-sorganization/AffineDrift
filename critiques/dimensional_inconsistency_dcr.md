# Critique: Dimensional Inconsistency of the Drift-Control Ratio

## Summary of Concern

The definition of the Drift-Control Ratio (DCR) relies on the Euclidean norm of the state vector derivative $\dot{x}$, which contains components with disparate physical units (angular velocity in $\text{rad}/s$ and angular acceleration in $\text{rad}/s^2$). This dimensional inhomogeneity renders the scalar value of DCR dependent on the arbitrary choice of time units (e.g., seconds vs. milliseconds), effectively making the metric physically meaningless in its current form.

## Location

- **Page:** `articles/controllability-drift-ratio.qmd`
- **Section:** 3. Drift–Control Ratio (DCR)
- **Claim or Equation:** $\mathrm{DCR}(t) = \frac{\|f(x(t))\|}{\|g(x(t))u(t)\|}$ and the approximation $\|f\| \sim a\|\dot{q}\| + b\|\dot{q}\|^2$.

## Nature of the Issue

- **Logical gap:** Mathematical definition fails dimensional analysis.
- **Unstated assumption:** Implicit reliance on a specific unit system (SI seconds) without justification.
- **Methodological fragility:** The metric is not invariant to trivial coordinate transformations.

## Why This Is a Problem

In physics and control theory, valid scalar metrics must be dimensionless or dimensionally consistent. The current definition sums a velocity term ($\dot{q}$) and an acceleration term ($M^{-1}(-C\dot{q}-G)$) within a single norm:
$$ \|f(x)\| = \sqrt{ \|\dot{q}\|^2 + \|\ddot{q}_{drift}\|^2 } $$
This operation is akin to adding meters to meters per second.
If the time unit is changed from seconds to milliseconds:

- Velocity $\dot{q}$ scales by $10^{-3}$.
- Acceleration $\ddot{q}$ scales by $10^{-6}$.
  The relative contribution of "kinematic drift" (velocity) versus "dynamic drift" (acceleration) to the numerator changes by three orders of magnitude. Consequently, the DCR trajectory itself—not just its magnitude, but its shape and peak timing—will distort purely based on the choice of units. A reviewer will flag this as a fundamental error in formulation.

## Evidence / References

- **Dimensional Analysis (Buckingham $\pi$ theorem):** Physical equations must be dimensionally homogeneous.
- **Control Theory Norms:** Standard metrics like the Controllability Gramian use weighted norms (e.g., energy metrics) to ensure consistency.
- **Robotics Literature:** Murray, Li, Sastry (1994) define metrics on the tangent bundle using the Riemannian metric (kinetic energy), not Euclidean norms of state derivatives.

## Severity

- **High** (Core metric is mathematically invalid).

## Suggested Remedies

1.  **Redefine DCR on the Dynamic Fiber:** Restrict the definition to the fiber of the tangent bundle (accelerations/forces) where units are consistent. Compare the generalized forces of drift to the generalized forces of control:
    $$ \mathrm{DCR}(t) = \frac{\| M(q)^{-1}( -C(q,\dot{q})\dot{q} - G(q) ) \|_M}{\| M(q)^{-1} \tau \|_M} $$
    Or simply comparing torques: $\|\tau_{drift}\| / \|\tau_{control}\|$.
2.  **Nondimensionalization:** Introduce a characteristic time constant $\tau_c$ (e.g., swing duration $\approx 0.2\text{s}$) to nondimensionalize the state vector before computing norms:
    $$ \tilde{\dot{q}} = \tau_c \dot{q}, \quad \tilde{\ddot{q}} = \tau_c^2 \ddot{q} $$
3.  **Explicit Caveat:** If the current definition is retained for simplicity, an explicit caveat must be added stating that the metric is valid only under the specific SI unit system (seconds, radians) and acts as a heuristic rather than a rigorous tensor quantity.
