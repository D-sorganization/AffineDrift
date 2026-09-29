# Secondary-Axis Mechanics and Design Inference — #4467

## Scope and Argument

Complete review of `articles/secondary-axis-stability.qmd` and both governed
critiques: `intermediate_axis_fallacy.md` and
`misattribution_of_stability_gravity.md`. Read the full technical article,
accessible explanation, critic/author dialogue, synthesis and related links.
Preserve the three public routes and the principal section destinations.

The corrected argument connects four distinct questions: free-spin perturbations,
the supported stroke, gravitational balance, and collision response. Equipment
parameters can affect all four, but neither an inertia table nor a static balance
test establishes face-delivery accuracy, muscle effort or scoring improvement.
The central-spine proposal remains a design hypothesis, not a demonstrated benefit.

## Corrected Findings

1. **P1 — Free Versus Forced Dynamics.** Derive the transverse intermediate-axis
   Jacobian and rate; the nominal-axis equation has no first-order perturbation
   term. Require distinct moments and torque-free conditions. Extreme-axis
   oscillatory modes do not supply damping or attraction. The supported club
   requires hand forces/couples, support acceleration and any flexible states.
2. **P1 — Frames, Origins and Units.** Separate center-of-mass and support-point
   moment balances. Add parallel-axis translations when aggregating inertias.
   A deforming shaft is not described completely by a rotated head tensor.
   Distinguish vertical from face-normal axes, physical alignment from a change
   of coordinates, and torque in N·m from force in newtons.
3. **P1 — Unsupported Numerical Provenance and Ranking.** No reproducible grid
   geometry/calculation supports the original table's architecture labels.
   Retain its numbers only as hypothetical inertia spectra, with the correct
   conversion and realizability boundary. A halved moment gap is not a halved
   growth rate. At fixed spin B's rate is 36.7% lower; at fixed angular momentum
   it is 15.3% higher. Neither condition establishes putting performance.
4. **P1 — Impact and Stroke Tradeoffs.** Use full inverse inertia to map angular
   impulse into angular-velocity change; qualify the scalar yaw reduction.
   High inertia reduces one specified impulse response but increases the moment
   for one specified acceleration. Remove unsupported commercial MOI ranges,
   player recommendations, score correlations and guaranteed steering benefits.
5. **P1 — Gravity, Impedance and Evidence.** Correct the critique's missing sine
   factor and implicit zero-acceleration assumption in its low-speed limit.
   A maximum gravity-moment ratio is not universal. Two zero-moment equilibria
   have opposite stiffness; restoring action is distinct from damping. Finite
   co-contraction/impedance is not automatically an exact constraint change.
6. **P1 — Control-Theory and Accessible Claims.** Remove the unsupported
   topological-invariance claim, generic positive-Lyapunov-exponent region,
   subconscious effort explanation and fictional authoritative critic claims.
   State a concrete invariant-set tangency condition and the intervention
   boundary for zero input. Correct the critiques' own overclaims rather than
   replacing an unverified inertial mechanism with an unverified gravity mechanism.

## Independent Verification

`tests/test_secondary_axis_rigor.py` has 13 numerical cases and six source
regressions. The initial run had twelve numerical passes and six expected source
failures. A further independently expanded moving-origin check was added to verify
the newly explicit support-acceleration term. All nineteen cases now pass.

- Central differences of the vector Euler balance reproduce the real intermediate
  and imaginary extreme-axis transverse eigenvalues for both spectra; the
  longitudinal mode is zero in each of the six principal-axis cases.
- Exact integer ratios verify growth coefficients, the reversed fixed-momentum
  comparison, triangle inequalities and invariance under uniform inertia scaling.
- Nonprincipal spin has a nonzero gyroscopic moment with zero instantaneous work.
- A shifted point-mass sum independently verifies parallel-axis translation.
- Coordinate congruence preserves energy and transformed torque response. Holding
  torque components fixed instead produces the stated transverse acceleration.
- Direct particle accelerations verify the moving-body-point moment balance.
- Gravity derivatives distinguish the two zero-moment equilibria; the energy
  derivative vanishes without damping, and the maximum comparison is 137.34.
- A non-diagonal tensor couples a pure yaw impulse into other angular velocity;
  the diagonal counterpart yields the scalar special case.

These fixtures verify algebra and model distinctions. They contain no measured
putter geometry, participant observations, physiological inference or clinical
claim. Render and repository-wide results are recorded separately in the
verification receipt; the local production build includes its existing legacy
polyfill cleanup before browser checks.

## Sources Actually Checked

- [MIT 8.09, Chapter 2](https://ocw.mit.edu/courses/8-09-classical-mechanics-iii-fall-2014/6fe39e8d5ce4ce746ca256dfea665eda_MIT8_09F14_Chapter_2.pdf):
  center-of-mass conventions, inertia transformation/translation and the Euler
  principal-axis perturbation derivation, especially physical pages 10–17.
- [Peraire and Widnall, MIT 16.07 Lecture 28](https://ocw.mit.edu/courses/16-07-dynamics-fall-2009/5e1d8699338146e5127080b880b906d6_MIT16_07F09_Lec28.pdf):
  external-moment balance and free-motion stability, physical pages 1–5.

The worked comparisons and checks are independently derived from the declared
models. Neither source supplies empirical support for putter superiority.

## Delegation and Adjudication

Six supplied-text-only agy `gemini-3.8-flash-high` calls ran in parallel pairs
for claim/arithmetic inventory, numerical-test proposals and final consistency. The lead wrote and
checked the adopted mathematics and tests. Reject the invented conformance limit,
commercial mass/MOI statements, alleged impossibility of unchanged minimum inertia,
and assumed mappings from principal moments to head axes. Correct the fixture
proposal's factor-of-ten rational typo and inconsistent decimal constants.
General realizability inequalities are non-strict; these examples satisfy strict
ones. Principal-axis alignment is sufficient for the scalar yaw response for all
impulses, not a necessary condition for every individual impulse by itself.

No agent accessed files/network or bypassed permissions. The broader unattended
agy tool mode remains unavailable under Repository_Management#1800. The governed
critique disposition must distinguish a mathematical response from unresolved
empirical equipment claims; the review does not turn either into observed results.

Final review clarified the impact arm as center-of-mass referenced, used
“off-diagonal matrix entry” to avoid product-of-inertia sign conventions, and
made the fixed horizontal pivot and common gravity frame explicit. Reject the
reviewer's invented shaft lie angle and club dimensions: the pendulum parameters
are synthetic and never identified as measured putter geometry. Gravity may be
a zero term about the COM; its explicit separation does not require a nonzero
moment. The impulse paragraph already declares and bounds other impulses.

The final CI follow-up names the unchanged 9.81 m/s² test parameter
`GRAVITY_M_S2`. All 19 cases pass again; this is a test-style correction,
with no source, numerical value, rendered output or scientific conclusion change.
