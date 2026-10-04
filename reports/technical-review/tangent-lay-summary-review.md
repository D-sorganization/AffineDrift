# Tangent-Framework Lay Summary Technical Review

Issue #4871 continues epic #4009 / corpus #4021. The complete source is
`articles/tangent-hyperplane-articles/LAYMANS_TERMS_SUMMARY.qmd`. This review
addresses the entire article, including its conclusion, examples and reading
links. It does not re-review the linked reference manuscript or establish
empirical golf, robotics or spacecraft outcomes.

## Findings and Corrections

| Finding               | Technical Problem                                                                                                                                              | Correction                                                                                                                                                                                                             |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| First-order structure | The conclusion calls nonlinear systems perfectly linear at an instant, contradicting its own caveat. Pedal doubling conflates total input with deviations.     | Distinguish the derivative, affine local prediction, exact variational sensitivity and finite trajectory difference. Separate exact affine torque dependence at a fixed mechanical state.                              |
| Remainder regularity  | A general quadratic error and exact fourfold scaling are asserted while only C1 is assumed.                                                                    | Give a C1 counterexample; state a Lipschitz-derivative sufficient condition, distinguish bounds from actual error, and separate perturbations from integration time steps.                                             |
| Swing phases          | Independent phase corrections are described as mathematically justified coaching.                                                                              | Derive phase coupling even in a linear model. Explain inherited complete state, feasible directions, instantaneous comparisons, diverging trajectories and retuned controls. Coaching effectiveness remains empirical. |
| Engineering examples  | One hundred local solves allegedly ensure a grasp, and local optimal controls ensure docking. Thrust is said to cause rotation without geometry qualification. | Present illustrative design processes, specify constraints and uncertainty, remove invented successful outcomes, and distinguish force through the center of mass from an offset force.                                |
| Algorithms            | DDP/iLQR/MPC are reduced to a shared move-and-repeat procedure.                                                                                                | Distinguish trajectory optimization passes, second-order dynamics in full DDP, nonlinear rollouts and MPC's replanning architecture.                                                                                   |
| Framing               | Conventional control is caricatured as approximation or simulation on hope. Nonlinearity is defined through unpredictability.                                  | Describe established methods fairly and distinguish nonlinear dependence from model uncertainty. Demote novelty claims to explanatory organization.                                                                    |

The hybrid section now accounts for event timing and reset rules, rather than
merely joining smooth modes. The reading path points first to the canonical
series and retains the longer reference as a secondary source. Acronyms and
the main regularity terms are expanded for the intended audience.

## Independent Mathematical Checks

All examples are dimensionless mathematical models, not fitted swing models.
The exact symbolic check output is
`tangent-lay-summary-independent-checks.json`.

1. For `f(z)=abs(z)^(3/2)`, both one-sided difference quotients at zero and
   derivative limits are zero. The remainder divided by positive `h` tends
   to zero, whereas the remainder divided by `h^2` tends to infinity.
   This disproves the claimed general quadratic bound under C1 regularity.
2. For `xdot=x^2`, direct substitution verifies
   `x(t)=epsilon/(1-epsilon*t)` and the initial condition. On an interval
   where the denominator stays positive, sensitivity at `epsilon=0` is one.
   Subtraction gives `epsilon^2*t/(1-epsilon*t)`, demonstrating finite error
   despite an exact first-order sensitivity.
3. Integrating `qdot=v, vdot=u` from zero over two unit intervals, with inputs
   `a` then `b`, gives `v(2)=a+b`, `q(2)=3*a/2+b/2`. Replacing the inputs by
   `a+d, b-d` preserves final velocity and changes final position by `d`.
   The implication is limited: linearity does not imply independent phases.
   It does not say every output of every dynamical system depends on every
   earlier input, or validate a particular swing compensation.

For the remainder bound, take a differentiable map with a Jacobian that is
Lipschitz with constant `L` throughout a neighborhood containing the whole
segment from `z` to `z+h`. In compatible vector/operator norms,
`R(h)=integral_0^1 [DF(z+s*h)-DF(z)]h ds`. The integrand norm is at most
`L*s*norm(h)^2`, so `norm(R(h)) <= L*norm(h)^2/2`. The same reasoning for
`2h` needs the larger segment inside the same bounded neighborhood. Its
upper bound is four times larger; no ratio between the actual errors is
asserted. Bounded second derivatives suffice, but C2 is not necessary.

## Sources and Evidence Boundaries

- [Tedrake: LQR](https://underactuated.mit.edu/lqr.html) supports the distinction
  between a linear quadratic problem and local application to nonlinear
  dynamics. Its assumptions do not establish a golfer-specific controller.
- [Tedrake: Trajectory Optimization](https://underactuated.mit.edu/trajopt.html)
  supports the algorithm distinctions and horizon-based optimization account.
- [Kong et al.: Saltation Matrices](https://arxiv.org/abs/2306.06862) supports
  the need to account for event timing when propagating hybrid sensitivity.

The elementary examples and integral remainder argument were independently
derived. No experimental efficacy, optimal muscle sequence, grasp success,
docking certification or universal swing technique is inferred from them.

## Delegation and Validation

Four supplied-text agy CLI Gemini 3.8 Flash helpers supported exact-check
preparation, original-claim inventory, revised-copy review and proof
cross-checking. The last two ran in parallel. The lead reviewed all results.
Rejected suggestions included requiring C2 for a quadratic remainder,
requiring an unforced zero equilibrium for any exact input proportionality,
claiming all outputs inherit every earlier input, and unneeded assertions
about ball-impact aerodynamics. Clarity suggestions were applied without
accepting those generalizations.

The initial 48 focused checks and title audit passed. The full regression and
final browser verification are recorded separately when complete. Rendering
is a one-route Quarto 1.8.26 check; the preview combines its updated HTML with
an unchanged, previously verified deployment's supporting assets. It is not
a new full deployment certification. No other publication source is revised.
